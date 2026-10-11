import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "drivers/apple-dockchannel/core"
HARNESS = r'''
#include <assert.h>
#include <string.h>
#include "hid_packet.h"
static uint8_t buffer[65560], data[DCHID_MAX_PAYLOAD];
static void repair_checksum(uint8_t *p, size_t n) {
    uint32_t sum = 0;
    for (size_t i = 0; i < n-4; i+=4)
        sum += (uint32_t)p[i] | (uint32_t)p[i+1]<<8 | (uint32_t)p[i+2]<<16 | (uint32_t)p[i+3]<<24;
    uint32_t tail = UINT32_MAX - sum;
    for (unsigned i = 0; i < 4; ++i) p[n-4+i] = (uint8_t)(tail >> (8*i));
}
int main(void) {
    /* Independent byte fixture for a three-byte command with zero padding. */
    static const uint8_t golden[] = {8,0x11,12,0,7,2,0,0,0x81,0,3,0,0,0,0,0,
                                    1,2,3,0,0x6e,0xea,0xed,0xff};
    const uint8_t small[] = {1,2,3}; size_t written = 99; struct dchid_packet view;
    assert(dchid_encode_command(2,7,0x81,small,3,buffer,sizeof(buffer),&written) == DCHID_OK);
    assert(written == sizeof(golden) && !memcmp(buffer,golden,written));
    assert(dchid_parse_packet(golden,sizeof(golden),&view) == DCHID_OK);
    assert(view.interface_id == 2 && view.sequence == 7 && view.flags == 0x81);
    assert(view.return_code == 0 && view.payload_size == 3 && view.consumed == 24);
    assert(!memcmp(view.payload,small,3));
    for (size_t n = 0; n < sizeof(golden); ++n) {
        assert(dchid_parse_packet(golden,n,&view) == DCHID_INCOMPLETE);
        assert(view.payload == NULL && view.payload_size == 0 && view.consumed == 0);
    }
    buffer[written] = 0xaa;
    assert(dchid_parse_packet(buffer,written+1,&view) == DCHID_OK && view.consumed == written);
    /* Unaligned snapshots, byte tails, maximum 16-bit body and guards. */
    for (size_t n = 0; n <= 17; ++n) {
        for (size_t i = 0; i < n; ++i) data[i] = (uint8_t)(i+1);
        memset(buffer,0xa5,sizeof(buffer));
        assert(dchid_encode_command(15,255,0x40,data,n,buffer+1,sizeof(buffer)-2,&written) == DCHID_OK);
        assert(buffer[0] == 0xa5 && buffer[written+1] == 0xa5);
        assert(dchid_parse_packet(buffer+1,written,&view) == DCHID_OK);
        assert(view.payload_size == n && !memcmp(view.payload,data,n));
        assert(view.consumed == written && view.interface_id == 15);
    }
    assert(dchid_encode_command(1,0,0,data,sizeof(data),buffer,sizeof(buffer),&written) == DCHID_OK);
    assert(written == 65544 && dchid_parse_packet(buffer,written,&view) == DCHID_OK);
    assert(view.payload_size == sizeof(data));
    memset(buffer,0xa5,sizeof(buffer));
    assert(dchid_encode_command(16,0,0,data,3,buffer,sizeof(buffer),&written) == DCHID_INVALID);
    assert(written == 0 && buffer[0] == 0xa5);
    assert(dchid_encode_command(1,0,0,data,65525,buffer,sizeof(buffer),&written) == DCHID_INVALID);
    assert(written == 0 && buffer[0] == 0xa5);
    assert(dchid_encode_command(1,0,0,NULL,1,buffer,sizeof(buffer),&written) == DCHID_INVALID);
    assert(dchid_encode_command(1,0,0,NULL,0,buffer,19,&written) == DCHID_NO_SPACE);
    assert(written == 0 && buffer[0] == 0xa5);
    assert(dchid_parse_packet(NULL,0,&view) == DCHID_INVALID);
    assert(dchid_parse_packet(golden,sizeof(golden),NULL) == DCHID_INVALID);
    memcpy(buffer,golden,sizeof(golden)); buffer[23] ^= 1;
    assert(dchid_parse_packet(buffer,24,&view) == DCHID_BAD_CHECKSUM && !view.payload);
    memcpy(buffer,golden,24); buffer[5] = 16; repair_checksum(buffer,24);
    assert(dchid_parse_packet(buffer,24,&view) == DCHID_BAD_HEADER && !view.payload);
    memcpy(buffer,golden,24); buffer[1] = 0x13; repair_checksum(buffer,24);
    assert(dchid_parse_packet(buffer,24,&view) == DCHID_BAD_HEADER);
    memcpy(buffer,golden,24); buffer[2] = 9; repair_checksum(buffer,24);
    assert(dchid_parse_packet(buffer,24,&view) == DCHID_BAD_HEADER);
    memcpy(buffer,golden,24); buffer[10] = 5; repair_checksum(buffer,24);
    assert(dchid_parse_packet(buffer,24,&view) == DCHID_BAD_HEADER);
    memcpy(buffer,golden,24); buffer[1] = 0x12; buffer[12] = 0x34; repair_checksum(buffer,24);
    assert(dchid_parse_packet(buffer,24,&view) == DCHID_OK && view.channel == 0x12 && view.return_code == 0x34);
    /* Untrusted bounded snapshots: run under ASan/UBSan, never expose an invalid view. */
    uint32_t seed = 0x12345678;
    for (unsigned t = 0; t < 10000; ++t) {
        size_t n = t % 65;
        for (size_t i = 0; i < n; ++i) {
            seed = seed * UINT32_C(1664525) + UINT32_C(1013904223);
            buffer[i] = (uint8_t)(seed >> 24);
        }
        if (dchid_parse_packet(buffer,n,&view) == DCHID_OK) {
            assert(view.consumed <= n && view.payload >= buffer);
            assert(view.payload_size <= (size_t)((buffer+n)-view.payload));
        } else assert(!view.payload && !view.consumed && !view.payload_size);
    }
    return 0;
}
'''


class DockChannelPacketTests(unittest.TestCase):
    def test_framing_and_untrusted_lengths_with_sanitizers(self):
        compiler = shutil.which(os.environ.get("CC", "cc"))
        if not compiler:
            self.skipTest("C compiler unavailable")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "packet.c").write_text(HARNESS)
            subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                            "-I", str(CORE), str(path / "packet.c"), str(CORE / "hid_packet.c"),
                            "-o", str(path / "test")], check=True)
            subprocess.run([str(path / "test")], check=True, timeout=10)

    def test_windows_arm64_coff_compilation(self):
        compiler = shutil.which("clang")
        if not compiler:
            self.skipTest("Clang cross compiler unavailable")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "packet.obj"
            subprocess.run([compiler, "--target=aarch64-pc-windows-msvc", "-ffreestanding",
                            "-std=c11", "-Wall", "-Wextra", "-Werror", "-c",
                            str(CORE / "hid_packet.c"), "-o", str(output)], check=True)
            self.assertEqual(0xaa64, struct.unpack_from("<H", output.read_bytes())[0])
