"""Replay the photographed boot-data stop through the actual runtime guard."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class J413SourceMemoryTests(unittest.TestCase):
    def test_photo_values_and_actual_source_guard(self):
        cc=shutil.which(os.environ.get('CC','cc'))
        if not cc:self.skipTest('C compiler unavailable')
        source=(ROOT/'m1n1_windows/src/hv_autonomous_runtime.c').read_text()
        a=source.index('static bool j413_validate_source_region(')
        b=source.index('\n#endif',a)
        harness=r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "hv_j413_boot_data.h"
typedef unsigned long u64;
_Static_assert(sizeof(u64)==8,"64-bit host required");
static u64 ram_base=0x800000000UL, mem_size_actual=0x400000000UL;
static struct {u64 base,size;} mcc_carveouts[] = {
    {0xbde614000UL,0x1d20000UL},{0xbe6db8000UL,0x19000000UL}
};
static size_t mcc_carveout_count=2;
__ACTUAL_FUNCTION__
int main(void) {
    const u64 guest=0x850000000UL,guest_size=0x1b0000000UL;
    const u64 fb=0xbe18b0000UL,fb_size=10240UL*1664;
    /* IMG_5747: source index 2 is above usable-end but inside mapped DRAM.
     * Installed RAM size independently obtained using sysctl hw.memsize.
     * MCC examples are whitelisted prior IORegistry region-id-2/4 values. */
    assert(!hv_j413_range_inside(fb,fb_size,ram_base,0xbde568000UL));
    assert(j413_validate_source_region("photo framebuffer",fb,fb_size,guest,guest_size));
    assert(j413_validate_source_region("exact DRAM end",0xbffffc000UL,0x4000,guest,guest_size));
    assert(!j413_validate_source_region("outside",0xbffffc000UL,0x4001,guest,guest_size));
    assert(!j413_validate_source_region("guest overlap",guest,0x4000,guest,guest_size));
    assert(!j413_validate_source_region("TZ",mcc_carveouts[0].base,0x4000,guest,guest_size));
    assert(!j413_validate_source_region("TZ crossing",mcc_carveouts[1].base-0x1000,0x2000,guest,guest_size));
    assert(!j413_validate_source_region("wrap",UINT64_MAX-0x1000,0x2000,guest,guest_size));
    mem_size_actual=UINT64_MAX;
    assert(!j413_validate_source_region("DRAM wrap",fb,fb_size,guest,guest_size));
    mem_size_actual=0;
    assert(!j413_validate_source_region("unknown DRAM",fb,fb_size,guest,guest_size));
    mem_size_actual=0x400000000UL;
    assert(j413_validate_source_region("absent optional log",0,0,guest,guest_size));
    struct hv_j413_boot_slots slots={0x851000000ULL,0x8510b4000ULL,0x8533e8000ULL,
        0x85e000000ULL,0x1e00000ULL,0xb4000ULL};
    struct hv_assisted_layout p;
    /* Every size/destination below is transcribed from the operator photo. */
    assert(hv_j413_boot_data_plan(&slots,0x5c000,0x58000,0x1d88000,0x5dc000,0x40000,&p));
    assert(p.trust_cache_base==0x8533ec000ULL && p.sepfw_base==0x853444000ULL);
    assert(p.preoslog_base==0x853a20000ULL && p.top_of_kernel_data==0x853a60000ULL);
    assert(hv_j413_range_inside(guest,guest_size,ram_base,0xbde568000UL));
    puts("Photo replay: placement and framebuffer-source guard pass; guest cap unchanged");
    return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'test.c').write_text(harness.replace('__ACTUAL_FUNCTION__',source[a:b]))
            (p/'types.h').write_text('#include <stdint.h>\ntypedef uint64_t u64;\n')
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                '-I',str(ROOT/'platforms/j413/m1n1'),'-I',str(ROOT/'m1n1_windows/src'),
                str(p/'test.c'),str(ROOT/'platforms/j413/m1n1/hv_j413_boot_data.c'),
                '-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True,timeout=10)

if __name__=='__main__':unittest.main()
