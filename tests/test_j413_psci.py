"""Exercise inherited PSCI bookkeeping without pretending to test CPU power."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


def body(source,name):
    a=source.index('void '+name+'(')
    start=source.index('{',a);depth=1;i=start+1
    while depth:
        if source[i]=='{':depth+=1
        elif source[i]=='}':depth-=1
        i+=1
    return source[a:i]


class J413PsciTests(unittest.TestCase):
    def test_actual_topology_counting_and_selected_parent_coordination(self):
        cc=shutil.which(os.environ.get('CC','clang'))
        if not cc:self.skipTest('C compiler unavailable')
        source=(ROOT/'m1n1_windows/src/hv_psci.c').read_text()
        harness=r'''
#include <assert.h>
#include <string.h>
#include <stdio.h>
#define PSCI_MAX_POWER_LEVEL 2
#define PSCI_ON_STATE 0
#define OFF 2
typedef unsigned platform_local_state_t;
typedef struct {unsigned power_domain_state[3];} psci_power_state_status_t;
static struct {unsigned first_cpu_idx,num_cpu_siblings,parent_node;} psci_non_cpu_nodes[3];
static struct {unsigned parent_node;} psci_cpu_nodes[8];
static unsigned psci_num_cores=8;
static unsigned active_core=6,counts[3],starts[3],calls,updated;
static unsigned requested[2][24];
void hv_psci_get_parent_nodes(unsigned,unsigned,unsigned*);
static unsigned hv_psci_get_core_position(void){return active_core;}
static void hv_psci_set_requested_local_power_state(unsigned l,unsigned c,unsigned s) {
  assert(l>=1 && l<=2 && c<8);requested[l-1][c]=s;
}
static platform_local_state_t *hv_psci_get_requested_local_power_states(unsigned l,unsigned c) {
  starts[l]=c;return &requested[l-1][c];
}
static unsigned hv_psci_get_target_power_state(unsigned l,platform_local_state_t *p,unsigned n) {
  assert(p==&requested[l-1][starts[l]]);counts[l]=n;calls++;return OFF;
}
static void hv_psci_set_target_local_power_states(unsigned l,psci_power_state_status_t *s) {
  assert(l==2 && s->power_domain_state[1]==OFF && s->power_domain_state[2]==OFF);updated++;
}
__FUNCTIONS__
int main(void) {
  psci_non_cpu_nodes[1].parent_node=0;psci_non_cpu_nodes[2].parent_node=0;
  for(unsigned i=0;i<8;i++)psci_cpu_nodes[i].parent_node=i<4?1:2;
  hv_psci_update_power_level_limits();
  assert(psci_non_cpu_nodes[0].first_cpu_idx==0 && psci_non_cpu_nodes[0].num_cpu_siblings==8);
  assert(psci_non_cpu_nodes[1].first_cpu_idx==0 && psci_non_cpu_nodes[1].num_cpu_siblings==4);
  assert(psci_non_cpu_nodes[2].first_cpu_idx==4 && psci_non_cpu_nodes[2].num_cpu_siblings==4);
  psci_power_state_status_t s={{OFF,OFF,OFF}};
  hv_psci_coordinate_power_states(2,&s);
  assert(calls==2 && updated==1 && counts[1]==4 && counts[2]==8);
  assert(starts[1]==4 && starts[2]==0);
  active_core=2;calls=0;hv_psci_coordinate_power_states(2,&s);
  assert(calls==2 && counts[1]==4 && counts[2]==8 && starts[1]==0);
  return 0;
}
'''
        functions='\n'.join(body(source,n) for n in ('hv_psci_get_parent_nodes','hv_psci_update_power_level_limits','hv_psci_coordinate_power_states'))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'test.c').write_text(harness.replace('__FUNCTIONS__',functions))
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror',
                '-ftrivial-auto-var-init=pattern','-fsanitize=address,undefined',
                str(p/'test.c'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True,timeout=10)


if __name__=='__main__':unittest.main()
