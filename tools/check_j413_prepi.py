#!/usr/bin/env python3
"""Reject Mu outputs that silently compiled out the J413 boot-memory fixes."""
from pathlib import Path
import re
import sys


def verify_prepi_contract(preprocessed: str, linked: bytes):
    begin=preprocessed.index('_GetStackBase:')
    end=preprocessed.index('_NeverReturn:',begin)
    block=preprocessed[begin:end]
    instructions=[' '.join(line.strip().split()) for line in block.splitlines()]
    required=('mov x23, x12','mov x24, x2','cmp x12, x1','b.lo _ClearStack','mov x0, x23','mov x1, x24')
    if any(x not in instructions for x in required) or 'b.lt _ClearStack' in instructions:
        raise ValueError('J413 PrePi stack fix compiled out; check PP_FLAGS')
    if re.search(r'sub\s+x(?:1|12),\s*x(?:1|12),\s*#0x40',block):
        raise ValueError('J413 PrePi still uses the legacy stack adjustment')
    if b'J413 BOOTDATA HOB: reserved' not in linked or b'J413 STOP: invalid boot-data HOB bounds' not in linked:
        raise ValueError('J413 boot-data reservation code missing from linked Sec')


def main():
    path=Path(sys.argv[1])
    verify_prepi_contract((path/'OUTPUT/AArch64/ModuleEntryPoint.ii').read_text(),(path/'DEBUG/Sec.dll').read_bytes())
    print('J413 PrePi: stack loop and linked boot-data reservations present')


if __name__=='__main__':main()
