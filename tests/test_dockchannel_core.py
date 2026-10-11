import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
#include <assert.h>
#include <string.h>
#include "dockchannel.h"
struct fake { unsigned char bytes[64]; size_t pos; uint32_t capacity; unsigned accesses; };
static uint32_t read32(void *opaque, uint32_t offset) {
    struct fake *f = opaque; ++f->accesses;
    if (offset == 0x14 || offset == 0x2c) return f->capacity;
    if (offset == 0x1c) return ((uint32_t)f->bytes[f->pos++] << 8) | 0xa5;
    assert(offset == 0x28);
    uint32_t word = 0;
    for (unsigned i = 0; i < 4; ++i) word |= (uint32_t)f->bytes[f->pos++] << (8*i);
    return word;
}
static void write32(void *opaque, uint32_t offset, uint32_t value) {
    struct fake *f = opaque; ++f->accesses; assert(offset == 0x10);
    for (unsigned i = 0; i < 4; ++i) f->bytes[f->pos++] = value >> (8*i);
}
static void write8(void *opaque, uint32_t offset, uint8_t value) {
    struct fake *f = opaque; ++f->accesses; assert(offset == 0x04); f->bytes[f->pos++] = value;
}
int main(void) {
    unsigned char source[17], destination[17];
    for (unsigned i = 0; i < sizeof(source); ++i) source[i] = (unsigned char)(0xe1 + i);
    struct fake f = {0};
    struct dc_io io = {&f, read32, write32, write8, 0x800};
    for (size_t n = 1; n <= 12; ++n) {
        memset(&f, 0, sizeof(f)); f.capacity = n;
        struct dc_result r = dc_try_send(&io, source+1, n, n);
        assert(r.status == DC_COMPLETE && r.transferred == n && f.pos == n);
        assert(!memcmp(f.bytes, source+1, n));
        assert(f.accesses == 1 + n/4 + n%4);
        f.pos = 0; f.accesses = 0; memset(destination, 0, sizeof(destination));
        r = dc_try_receive(&io, destination+1, n, n);
        assert(r.status == DC_COMPLETE && r.transferred == n && f.pos == n);
        assert(!memcmp(destination+1, source+1, n));
        assert(destination[0] == 0 && destination[n+1] == 0);
        assert(f.accesses == 1 + n/4 + n%4);
    }
    memset(&f, 0, sizeof(f)); f.capacity = 3;
    struct dc_result r = dc_try_send(&io, source, 12, 12);
    assert(r.status == DC_PARTIAL && r.transferred == 3 && f.pos == 3);
    f.pos = 0; r = dc_try_receive(&io, destination, 12, 12);
    assert(r.status == DC_PARTIAL && r.transferred == 3 && f.pos == 3);
    f.capacity = 64; f.pos = 0; r = dc_try_send(&io, source, 12, 5);
    assert(r.status == DC_PARTIAL && r.transferred == 5 && f.pos == 5);
    f.pos = 0; r = dc_try_receive(&io, destination, 12, 2);
    assert(r.status == DC_PARTIAL && r.transferred == 2 && f.pos == 2);
    f.capacity = 0; f.pos = 0; f.accesses = 0;
    assert(dc_try_send(&io, source, 12, 12).status == DC_WOULD_BLOCK);
    assert(dc_try_receive(&io, destination, 12, 12).status == DC_WOULD_BLOCK);
    assert(f.pos == 0 && f.accesses == 2);
    f.accesses = 0;
    assert(dc_try_send(NULL, NULL, 0, 12).status == DC_COMPLETE);
    assert(dc_try_receive(NULL, NULL, 0, 12).status == DC_COMPLETE);
    assert(dc_try_send(&io, source, 12, 0).status == DC_WOULD_BLOCK);
    assert(dc_try_receive(&io, destination, 12, 0).status == DC_WOULD_BLOCK);
    assert(f.accesses == 0);
    assert(dc_try_send(NULL, source, 12, 12).status == DC_INVALID);
    assert(dc_try_receive(&io, NULL, 12, 12).status == DC_INVALID);
    f.capacity = 0x801; f.accesses = 0;
    assert(dc_try_send(&io, source, 12, 12).status == DC_BAD_CAPACITY);
    assert(dc_try_receive(&io, destination, 12, 12).status == DC_BAD_CAPACITY);
    assert(f.pos == 0 && f.accesses == 2);
    return 0;
}
'''


class DockChannelCoreTests(unittest.TestCase):
    def test_fifo_contract_with_fake_registers(self):
        compiler = shutil.which(os.environ.get("CC", "cc"))
        if not compiler:
            self.skipTest("C compiler unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "fifo.c"
            source.write_text(HARNESS)
            binary = root / "fifo"
            core = ROOT / "drivers/apple-dockchannel/core"
            subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(core),
                            str(source), str(core / "dockchannel.c"), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True, timeout=5)
