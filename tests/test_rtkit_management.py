import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "drivers/apple-rtkit/core"
HARNESS = r'''
#include <assert.h>
#include <string.h>
#include "rtkit_management.h"
static uint64_t msg(unsigned type, uint64_t payload) {
    return ((uint64_t)type << 52) | payload;
}
static void accept(struct rtkit_management *s, uint64_t word, struct rtkit_plan *p) {
    struct rtkit_management old = *s;
    assert(rtkit_plan_management(s, (struct rtkit_message){0, word}, p) == RTKIT_OK);
    assert(!memcmp(s, &old, sizeof(old))); /* planning never commits */
    *s = p->next;
}
int main(void) {
    struct rtkit_management s = {0}; struct rtkit_plan p;
    for (unsigned minimum = 0; minimum < 20; ++minimum) {
        for (unsigned maximum = 0; maximum < 20; ++maximum) {
            enum rtkit_status status = rtkit_plan_management(&s,
                (struct rtkit_message){0, msg(1, minimum | ((uint64_t)maximum << 16))}, &p);
            if (minimum > maximum) assert(status == RTKIT_INVALID);
            else if (minimum > 12 || maximum < 11) assert(status == RTKIT_VERSION_MISMATCH);
            else {
                assert(status == RTKIT_OK && p.count == 1);
                unsigned version = maximum < 12 ? maximum : 12;
                assert(p.next.version == version && p.next.hello);
                assert(p.replies[0].endpoint == 0);
                assert(p.replies[0].word == msg(2, version | ((uint64_t)version << 16)));
            }
            assert(!s.hello && !s.version);
            if (status != RTKIT_OK) assert(p.count == 0 && !p.next.hello);
        }
    }
    assert(rtkit_plan_management(&s, (struct rtkit_message){0, msg(8, 1)}, &p) == RTKIT_SEQUENCE_ERROR);
    assert(rtkit_plan_management(&s, (struct rtkit_message){2, msg(1, 11 | (12 << 16))}, &p) == RTKIT_NOT_MANAGEMENT);
    assert(rtkit_plan_management(NULL, (struct rtkit_message){0, 0}, &p) == RTKIT_INVALID);
    assert(rtkit_plan_management(&s, (struct rtkit_message){0, 0}, NULL) == RTKIT_INVALID);
    assert(rtkit_plan_management(&s, (struct rtkit_message){0, msg(255, 0)}, &p) == RTKIT_UNKNOWN_MESSAGE);
    accept(&s, msg(1, 11 | (12 << 16)), &p);
    assert(rtkit_plan_management(&s, (struct rtkit_message){0, msg(1, 11 | (12 << 16))}, &p) == RTKIT_SEQUENCE_ERROR);
    /* Last bitmap need not be base 0. All eight bitmap pages and bit 31 work. */
    for (unsigned base = 0; base < 8; ++base) {
        uint32_t bitmap = base ? UINT32_C(0x80000001) : UINT32_C(0x8000051f);
        uint64_t word = msg(8, bitmap | ((uint64_t)base << 32));
        if (base == 7) word |= UINT64_C(1) << 51;
        accept(&s, word, &p);
        assert(rtkit_has_endpoint(&s, (uint8_t)(base * 32)));
        assert(rtkit_has_endpoint(&s, (uint8_t)(base * 32 + 31)));
        assert(!rtkit_has_endpoint(&s, (uint8_t)(base * 32 + 7)));
        assert(p.replies[0].word == msg(8, ((uint64_t)base << 32) |
               (base == 7 ? UINT64_C(1) << 51 : 1)));
        assert(p.count == (base == 7 ? 7 : 1));
    }
    static const uint8_t system[] = {1, 2, 3, 4, 8, 10};
    for (size_t i = 0; i < sizeof(system); ++i)
        assert(p.replies[i+1].word == msg(5, ((uint64_t)system[i] << 32) | 2));
    assert(s.epmap_complete && !rtkit_management_running(&s));
    assert(rtkit_plan_management(&s, (struct rtkit_message){0, msg(8, 1)}, &p) == RTKIT_SEQUENCE_ERROR);
    assert(rtkit_plan_start_endpoint(&s, 255, &p) == RTKIT_NOT_READY);
    assert(rtkit_plan_start_endpoint(&s, 0, &p) == RTKIT_INVALID);
    assert(rtkit_plan_start_endpoint(&s, 7, &p) == RTKIT_INVALID);
    assert(rtkit_plan_start_endpoint(&s, 2, &p) == RTKIT_OK);
    accept(&s, msg(7, 0x220), &p); assert(!rtkit_management_running(&s));
    accept(&s, msg(11, 0x20), &p); assert(rtkit_management_running(&s));
    assert(rtkit_plan_start_endpoint(&s, 255, &p) == RTKIT_OK);
    assert(p.count == 1 && p.replies[0].word == msg(5, (UINT64_C(255) << 32) | 2));
    accept(&s, msg(11, 0x10), &p); assert(!rtkit_management_running(&s));
    s.crashed = true;
    assert(rtkit_plan_management(&s, (struct rtkit_message){0, msg(7, 0x20)}, &p) == RTKIT_NOT_READY);
    assert(p.count == 0 && p.next.crashed);
    assert(rtkit_plan_start_endpoint(&s, 2, &p) == RTKIT_NOT_READY);
    assert(!rtkit_has_endpoint(NULL, 255) && !rtkit_management_running(NULL));
    return 0;
}
'''


class RTKitManagementTests(unittest.TestCase):
    def test_negotiation_endpoints_power_and_failure_contract(self):
        compiler = shutil.which(os.environ.get("CC", "cc"))
        if not compiler:
            self.skipTest("C compiler unavailable")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "management.c").write_text(HARNESS)
            subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                            "-I", str(CORE), str(path / "management.c"),
                            str(CORE / "rtkit_management.c"), "-o", str(path / "test")], check=True)
            subprocess.run([str(path / "test")], check=True, timeout=5)

    def test_windows_arm64_coff_compilation(self):
        compiler = shutil.which("clang")
        if not compiler:
            self.skipTest("Clang cross compiler unavailable")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "rtkit.obj"
            subprocess.run([compiler, "--target=aarch64-pc-windows-msvc", "-ffreestanding",
                            "-std=c11", "-Wall", "-Wextra", "-Werror", "-c",
                            str(CORE / "rtkit_management.c"), "-o", str(output)], check=True)
            self.assertEqual(0xaa64, struct.unpack_from("<H", output.read_bytes())[0])
