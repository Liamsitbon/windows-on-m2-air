from pathlib import Path
import plistlib
import struct
import tempfile
import unittest

from tools.analyze_kext import MachO, analyze_bundle


def header(commands):
    return struct.pack('<8I', 0xfeedfacf, 0x100000c, 2, 12, len(commands),
                       sum(len(c) for c in commands), 0, 0) + b''.join(commands)


class KextAnalysisTests(unittest.TestCase):
    def test_fileset_symbol_offsets_are_collection_relative(self):
        name = b'com.example.driver\0'
        command = struct.pack('<IIQQII', 0x80000035, 56, 0x1000, 128, 32, 0) + name.ljust(24, b'\0')
        blob = bytearray(header([command]).ljust(128, b'\0'))
        blob += header([struct.pack('<6I', 2, 24, 192, 1, 208, 9)])
        blob.extend(b'\0' * (192-len(blob)))
        blob += struct.pack('<IBBHQ', 1, 0xf, 1, 0, 0x1234)
        blob += b'\0_symbol\0'
        parser = MachO(bytes(blob))
        self.assertEqual(parser.filesets()['com.example.driver']['file_offset'], 128)
        self.assertEqual(parser.symbols(128)[0]['name'], '_symbol')
        self.assertEqual(parser.symbols(128)[0]['address'], '0x1234')

    def test_rejects_truncated_commands_and_bad_symbol_offsets(self):
        malformed = [b'\xcf\xfa', header([struct.pack('<II', 2, 0)]),
                     header([struct.pack('<6I', 2, 24, 0xffff, 1, 0, 1)])]
        for blob in malformed:
            with self.subTest(blob=blob), self.assertRaises(ValueError):
                MachO(blob).symbols(0)

    def test_metadata_only_bundle_is_not_reported_as_converted_driver(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / 'Sample.kext'
            (bundle / 'Contents').mkdir(parents=True)
            info = bundle / 'Contents/Info.plist'
            info.write_bytes(plistlib.dumps({'CFBundleIdentifier': 'com.example.driver',
                                            'CFBundleExecutable': 'Missing', 'CFBundleVersion': '1'}))
            record = analyze_bundle(bundle, 'custom', root / 'local')
            self.assertFalse(record['executable_in_bundle'])
            self.assertFalse(record['present_in_boot_collection'])
            self.assertEqual(record['symbol_count'], 0)
            self.assertIn('unqualified', record['status'])
            analyze_bundle(bundle, 'custom', root / 'local', resume=True)
            info.write_bytes(plistlib.dumps({'CFBundleIdentifier': 'com.example.driver', 'changed': True}))
            with self.assertRaisesRegex(ValueError, 'differs from source'):
                analyze_bundle(bundle, 'custom', root / 'local', resume=True)
