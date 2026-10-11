"""Executable regressions for the real Mu boot reservations and stack loop."""
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest

from tools.check_j413_prepi import verify_prepi_contract

ROOT=Path(__file__).resolve().parents[1]
MU=ROOT/'mu'
INCLUDE=ROOT/'platforms/j413/mu/Silicon/Apple/AppleSiliconPkg/Include'

HOB_HARNESS=r'''
#include <assert.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <Library/J413BootMemory.h>
#define STATIC static
#define IN
#define TRUE true
#define FALSE false
#define EFI_RESOURCE_SYSTEM_MEMORY 0
#define EFI_RESOURCE_MEMORY_RESERVED 1
#define EFI_HOB_TYPE_RESOURCE_DESCRIPTOR 3
#define MAX_UINT64 UINT64_MAX
typedef bool BOOLEAN;
typedef uint64_t EFI_PHYSICAL_ADDRESS;
typedef uint64_t EFI_RESOURCE_ATTRIBUTE_TYPE;
typedef uint64_t UINT64;
typedef uint32_t UINT32;
struct resource { uint32_t ResourceType; uint64_t PhysicalStart,ResourceLength,ResourceAttribute; };
typedef union { void *Raw; struct resource *ResourceDescriptor; } EFI_PEI_HOB_POINTERS;
static struct resource hobs[32]; static unsigned count;
static void *GetHobList(void) { return hobs; }
static void *GetNextHob(unsigned type,void *p) {
  (void)type; return (struct resource *)p < hobs+count ? p : NULL;
}
#define GET_NEXT_HOB(h) ((h).ResourceDescriptor+1)
static void BuildResourceDescriptorHob(unsigned type,uint64_t attr,uint64_t base,uint64_t size) {
  assert(count<32); hobs[count++]=(struct resource){type,base,size,attr};
}
__RESERVE_FUNCTION__
static void assert_not_allocatable(uint64_t start,uint64_t end) {
  for (unsigned i=0;i<count;i++) if(hobs[i].ResourceType==EFI_RESOURCE_SYSTEM_MEMORY) {
    uint64_t a=hobs[i].PhysicalStart,b=a+hobs[i].ResourceLength;
    assert(b<=start || a>=end);
  }
}
int main(void) {
  struct j413_boot_reservations p, unchanged;
  memset(&p,0xa5,sizeof(p)); unchanged=p;
  const uint64_t ram=0x850000000ULL, adt=0x851000000ULL;
  const uint64_t fd=0x8510b4000ULL, fdsize=0x1e00000ULL;
  const uint64_t ba=0x8533e8000ULL, top=0x853c40000ULL, limit=0x85e000000ULL;
  assert(j413_boot_reservations_plan(ram,0x1b0000000ULL,adt,fd,fdsize,ba,0x4000,top,limit,&p));
  assert(p.before_fd_base==adt && p.before_fd_size==0xb4000);
  assert(p.after_fd_base==0x852eb4000ULL && p.after_fd_size==0xd8c000);
  /* Actual MemoryPeim's three resource descriptors after splitting the FD. */
  BuildResourceDescriptorHob(0,7,ram,fd-ram);
  BuildResourceDescriptorHob(0,7,fd,fdsize);
  BuildResourceDescriptorHob(0,7,fd+fdsize,ram+0x1b0000000ULL-fd-fdsize);
  assert(ReserveMemoryRegion(p.before_fd_base,p.before_fd_size));
  assert(ReserveMemoryRegion(p.after_fd_base,p.after_fd_size));
  assert_not_allocatable(adt,fd);
  assert_not_allocatable(fd+fdsize,top);
  assert(!ReserveMemoryRegion(adt,p.before_fd_size)); /* already reserved */
  assert(!ReserveMemoryRegion(UINT64_MAX-1,4));
  assert(!ReserveMemoryRegion(adt,0));
  /* All branches: start, end and interior; missing HOB is a visible failure. */
  count=0;BuildResourceDescriptorHob(0,7,0x1000,0x4000);
  assert(ReserveMemoryRegion(0x1000,0x1000));
  assert(ReserveMemoryRegion(0x4000,0x1000));
  assert(ReserveMemoryRegion(0x2800,0x800));
  assert(!ReserveMemoryRegion(0x8000,0x1000));
  p=unchanged;
  assert(!j413_boot_reservations_plan(ram,0x1b0000000ULL,adt,fd,fdsize,ba,0x4000,limit+0x1000,limit,&p));
  assert(!memcmp(&p,&unchanged,sizeof(p)));
  assert(!j413_boot_reservations_plan(ram,0x1b0000000ULL,adt,fd,fdsize,ba,0x4000,ba,limit,&p));
  assert(!j413_boot_reservations_plan(ram,UINT64_MAX,adt,fd,fdsize,ba,0x4000,top,limit,&p));
  assert(!j413_boot_reservations_plan(ram,0x1b0000000ULL,adt,fd,UINT64_MAX,ba,0x4000,top,limit,&p));
  assert(!j413_boot_reservations_plan(ram,0x1b0000000ULL,adt,fd,fdsize,ba,0x4000,top+1,limit,&p));
  assert(!j413_boot_reservations_plan(ram,0x1b0000000ULL,adt,fd,fdsize,ba,0x4000,top,limit,NULL));
  return 0;
}
'''

STACK_HARNESS=r'''
#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
uint64_t results[4];
extern void test_stack(void *top);
int main(void) {
  size_t page=(size_t)sysconf(_SC_PAGESIZE), stack=0x20000;
  uint8_t *m=mmap(NULL,stack+2*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
  assert(m!=MAP_FAILED); assert(!mprotect(m,page,PROT_NONE));
  assert(!mprotect(m+page+stack,page,PROT_NONE));
  uint8_t *base=m+page, *top=base+stack;
  memset(base,0xa5,stack);
  test_stack(top);
  assert(results[0]==(uint64_t)base && results[1]==stack);
  assert(results[2]==0x1234 && results[3]==0x5678);
  for(size_t i=0;i<stack;i++) assert(base[i]==0);
  assert(!munmap(m,stack+2*page)); return 0;
}
'''


class J413BootMemoryTests(unittest.TestCase):
    def test_actual_hob_reservation_and_checked_bounds(self):
        cc=shutil.which(os.environ.get('CC','cc'))
        if not cc: self.skipTest('C compiler unavailable')
        source=(MU/'Silicon/Apple/T810XFamilyPkg/Library/MemoryInitPeiLib/MemoryInitPeiLib.c').read_text()
        a=source.index('STATIC BOOLEAN ReserveMemoryRegion')
        b=source.index('//Borrowed from ArmPlatformPkg',a)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'test.c').write_text(HOB_HARNESS.replace('__RESERVE_FUNCTION__',source[a:b]))
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                '-I',str(INCLUDE),str(p/'test.c'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True,timeout=10)

    def test_postbuild_gate_rejects_compiled_out_stack_and_hob_fix(self):
        block='_GetStackBase:\nmov x23, x12\nmov x24, x2\ncmp x12, x1\nb.lo _ClearStack\nmov x0, x23\nmov x1, x24\n_NeverReturn:\n'
        linked=b'J413 BOOTDATA HOB: reserved\0J413 STOP: invalid boot-data HOB bounds'
        verify_prepi_contract(block,linked)
        with self.assertRaisesRegex(ValueError,'PP_FLAGS'):
            verify_prepi_contract(block.replace('cmp x12, x1','cmp x12, x2'),linked)
        with self.assertRaisesRegex(ValueError,'reservation code missing'):
            verify_prepi_contract(block,b'legacy firmware')

    def test_actual_prepi_stack_loop_on_native_arm64(self):
        if platform.system()!='Linux' or platform.machine() not in ('aarch64','arm64'):
            self.skipTest('actual AArch64 ELF assembly regression runs in the native build container')
        cc=shutil.which('clang')
        if not cc: self.skipTest('Mu Clang compiler unavailable')
        source=(MU/'Silicon/Apple/AppleSiliconPkg/PrePi/AArch64/ModuleEntryPoint.S').read_text()
        a=source.index('_GetStackBase:');b=source.index('// if we get here',a)
        # CPP preserves only J413 instructions from the actual patched file.
        # Stub cache calls deliberately clobber all used caller-saved registers.
        assembly='''#define ASM_PFX(x) x
.text
.global test_stack
test_stack:
  stp x20,x22,[sp,#-64]!
  stp x23,x24,[sp,#16]
  stp x26,x29,[sp,#32]
  str x30,[sp,#48]
  mov x20,sp
  mov x1,x0
  mov x26,#0x1234
  mov x22,#0x5678
'''+source[a:b].replace('MOV32 (x2, 0x20000)','mov x2, #0x20000')+'''
ArmEnableInstructionCache:
ArmEnableDataCache:
  mov x0,#0x111
  mov x1,#0x222
  mov x2,#0x333
  mov x12,#0x444
  ret
CEntryPoint:
  adrp x4,results
  add x4,x4,:lo12:results
  stp x0,x1,[x4]
  stp x2,x3,[x4,#16]
  mov sp,x20
  ldp x23,x24,[sp,#16]
  ldp x26,x29,[sp,#32]
  ldr x30,[sp,#48]
  ldp x20,x22,[sp],#64
  ret
.section .note.GNU-stack,"",%progbits
'''
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'loop.S').write_text(assembly);(p/'test.c').write_text(STACK_HARNESS)
            subprocess.run([cc,'-DJ413_BOOT_CONTRACT','-Wall','-Wextra','-Werror',str(p/'loop.S'),str(p/'test.c'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True,timeout=10)


if __name__=='__main__': unittest.main()
