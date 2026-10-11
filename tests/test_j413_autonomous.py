import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / 'platforms/j413/m1n1'
M1N1 = ROOT / 'm1n1_windows/src'
HARNESS = r'''
#include <assert.h>
#include <string.h>
#include "hv_autonomous_target.h"
#include "hv_j413_boot_data.h"
#include "hv_j413_expected.h"
int main(void) {
    /* Independently observed live ADT values; architectural MPIDRs differ. */
    for (unsigned i=0;i<4;i++) {
        assert(hv_j413_cpu_index(i) == (int)i);
        assert(hv_j413_cpu_index(0x100+i) == (int)i+4);
    }
    assert(hv_j413_cpu_index(4) == -1);
    assert(hv_j413_cpu_index(0x104) == -1);
    assert(hv_j413_cpu_index(0x10100) == -1);
    assert(hv_autonomous_target_matches(0x8112,"J413",5));
    assert(!hv_autonomous_target_matches(0x8103,"J413",5));
    assert(!hv_autonomous_target_matches(0x8112,"J313",5));
    assert(!hv_autonomous_target_matches(0x8112,"J413extra",10));
    assert(!hv_autonomous_target_matches(0x8112,"J413",4));
    assert(!hv_autonomous_target_matches(0x8112,NULL,5));
    const struct hv_j413_boot_slots slots = {
        0x851000000ULL, 0x8510b4000ULL, 0x8533e8000ULL, 0x85e000000ULL,
        0x1e00000ULL, 0xb4000ULL
    };
    struct hv_assisted_layout p, unchanged;
    memset(&p,0xa5,sizeof(p)); unchanged=p;
    /* Different ADT sizes preserve Mu pointers, not the J313 packed offsets. */
    assert(hv_j413_boot_data_plan(&slots,0x5941c,0x1000,30965760,0x200000,0x1000,&p));
    assert(p.adt_base == 0x851000000ULL && p.trust_cache_base == 0x8533ec000ULL);
    assert(p.firmware_base == 0x8510b4000ULL && p.boot_args_base == 0x8533e8000ULL);
    assert(p.sepfw_base == 0x8533f0000ULL);
    assert(p.top_of_kernel_data == 0x8535f4000ULL);
    assert(hv_j413_boot_data_plan(&slots,0x70000,0x4000,30965760,0x200000,0,&p));
    assert(p.trust_cache_base == 0x8533ec000ULL);
    p=unchanged;
    /* No artificial TC gap or 0x534000 SEP gap; real live sizes unknown.
     * These independent test sizes reproduce both old narrow-gap failures. */
    assert(hv_j413_boot_data_plan(&slots,0xb4000,0x100000,30965760,0x750000,0x1000,&p));
    assert(p.trust_cache_base == 0x8533ec000ULL);
    assert(p.sepfw_base == 0x8534ec000ULL);
    assert(p.top_of_kernel_data == 0x853c40000ULL);
    struct hv_j413_boot_slots tight=slots;
    tight.data_limit=p.top_of_kernel_data;
    assert(hv_j413_boot_data_plan(&tight,0xb4000,0x100000,30965760,0x750000,0x1000,&p));
    p=unchanged;
    tight.data_limit-=0x4000;
    assert(!hv_j413_boot_data_plan(&tight,0xb4000,0x100000,30965760,0x750000,0x1000,&p));
    assert(!memcmp(&p,&unchanged,sizeof(p)));
    assert(!hv_j413_boot_data_plan(&slots,0xb4001,0,30965760,0,0,&p));
    assert(!hv_j413_boot_data_plan(&slots,1,0,0x1e00001,0,0,&p));
    assert(!hv_j413_boot_data_plan(&slots,1,0,30965760,UINT64_MAX,0,&p));
    assert(!hv_j413_boot_data_plan(&slots,1,0,30965760,0,UINT64_MAX,&p));
    assert(!hv_j413_boot_data_plan(NULL,1,0,1,0,0,&p));
    assert(!hv_j413_boot_data_plan(&slots,1,0,1,0,0,NULL));
    assert(hv_j413_range_inside(10,10,10,20));
    assert(!hv_j413_range_inside(9,1,10,20));
    assert(!hv_j413_range_inside(19,2,10,20));
    assert(!hv_j413_range_inside(UINT64_MAX,2,0,UINT64_MAX));
    assert(hv_j413_ranges_disjoint(10,10,20,10));
    assert(!hv_j413_ranges_disjoint(10,11,20,10));
    assert(!hv_j413_ranges_disjoint(UINT64_MAX,1,10,10));
    struct hv_contract_snapshot expected[4];
    assert(hv_j413_expected_init(expected,0xa00000000ULL,0x70000,30965760));
    for (unsigned i=0;i<4;i++) {
        assert(expected[i].identity.target == 0x3331344aU);
        assert(expected[i].header.checkpoint == i && expected[i].header.sequence == i+1);
        assert(expected[i].boot.ram_size == 0x1b0000000ULL);
        assert(expected[i].devices.display_height == 1664);
        assert(expected[i].devices.display_base == 0x85e000000ULL);
        assert(expected[i].irq_route_count == 1 && expected[i].irq_routes[0].physical_irq == 1112);
        assert(expected[i].irq_routes[0].vintid == 857);
        assert(expected[i].cpu_count == 8 && expected[i].cpus[4].mpidr == 0x10100);
        /* No M1 ADT digest or M1 initial AMX bits are pretended to be observed. */
        for (unsigned b=0;b<32;b++) assert(!expected[i].adt_digest[b]);
        if (i) assert(expected[i].cpus[0].hacr == 0x317000000014000ULL);
    }
    return 0;
}
'''


class J413AutonomousTests(unittest.TestCase):
    def test_planner_and_source_contract_with_sanitizers(self):
        cc = shutil.which(os.environ.get('CC', 'cc'))
        if not cc:
            self.skipTest('C compiler unavailable')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p/'types.h').write_text('#include <stdint.h>\ntypedef uint32_t u32; typedef uint64_t u64;\n')
            (p/'test.c').write_text(HARNESS)
            subprocess.run([cc, '-std=c11','-Wall','-Wextra','-Werror',
                '-fsanitize=address,undefined', '-DM1N1_J413', '-I',str(p),
                '-I',str(OVERLAY), '-I',str(M1N1), str(p/'test.c'),
                str(OVERLAY/'hv_j413_boot_data.c'), str(OVERLAY/'hv_j413_expected.c'),
                str(M1N1/'hv_guest_cpu_state.c'), str(M1N1/'hv_launch_contract.c'),
                '-o',str(p/'test')], check=True)
            subprocess.run([str(p/'test')],check=True,timeout=10)

    def test_m1_guard_rejects_m2(self):
        cc = shutil.which('cc')
        if not cc:
            self.skipTest('C compiler unavailable')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'test.c').write_text('''#include <assert.h>
#include "hv_autonomous_target.h"
int main(void) {
assert(hv_autonomous_target_matches(0x8103,"J313",5));
assert(!hv_autonomous_target_matches(0x8112,"J413",5));
return 0;
}''')
            subprocess.run([cc,'-std=c11','-Wall','-Werror','-I',str(OVERLAY),str(p/'test.c'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True,timeout=10)


if __name__ == '__main__':
    unittest.main()
