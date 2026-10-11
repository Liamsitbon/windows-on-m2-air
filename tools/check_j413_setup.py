#!/usr/bin/env python3
"""Read-only structural preflight; not firmware, BCD or Windows runtime proof."""
from pathlib import Path
import json
import struct
import sys

PATHS = ('efi/boot/bootaa64.efi', 'efi/microsoft/boot/bcd', 'sources/boot.wim', 'boot/boot.sdi')


def inspect(volume):
    root = Path(volume)
    result = {'files': {}, 'errors': [], 'qualification': 'headers-only-no-runtime-proof'}
    for rel in PATHS:
        p = root / rel
        try:
            size = p.stat().st_size
            with p.open('rb') as f:
                header = f.read(4096)
                if rel.endswith('.efi'):
                    if len(header) < 64 or header[:2] != b'MZ':
                        raise ValueError('missing DOS header')
                    offset = struct.unpack_from('<I', header, 60)[0]
                    if offset < 64 or offset > size - 94:
                        raise ValueError('PE header outside file')
                    f.seek(offset)
                    pe = f.read(94)
                    if pe[:4] != b'PE\0\0' or struct.unpack_from('<H', pe, 4)[0] != 0xaa64:
                        raise ValueError('loader is not ARM64 PE')
                    if struct.unpack_from('<H', pe, 24)[0] != 0x20b or struct.unpack_from('<H', pe, 92)[0] != 10:
                        raise ValueError('loader is not a PE32+ EFI application')
                elif rel.endswith('/bcd'):
                    if size < 4096 or header[:4] != b'regf':
                        raise ValueError('BCD registry hive header absent/truncated')
                elif rel.endswith('boot.wim'):
                    if len(header) < 12 or header[:8] != b'MSWIM\0\0\0':
                        raise ValueError('WIM header absent')
                    length = struct.unpack_from('<I', header, 8)[0]
                    if length < 208 or length > size:
                        raise ValueError('WIM declared header outside file')
                elif size < 512 or header[:8] != b'$SDI0001':
                    raise ValueError('SDI header absent/truncated')
            result['files'][rel] = {'size': size, 'header_valid': True}
        except (OSError, ValueError, struct.error) as error:
            result['errors'].append(f'{rel}: {error}')
    return result


if __name__ == '__main__':
    if len(sys.argv) != 2: raise SystemExit('usage: check_j413_setup.py mounted-volume')
    report = inspect(sys.argv[1])
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report['errors']))
