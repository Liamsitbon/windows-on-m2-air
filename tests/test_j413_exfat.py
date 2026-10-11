import hashlib
from pathlib import Path
import struct
import unittest
from unittest.mock import patch
from tools import prepare_j413_exfat as exfat

class ExFatDependencyTests(unittest.TestCase):
    def fixture(self):
        data = bytearray(53248)
        data[:2] = b"MZ"
        struct.pack_into("<I", data, 0x3c, 0x80)
        data[0x80:0x84] = b"PE\0\0"
        struct.pack_into("<H", data, 0x84, 0xaa64)
        struct.pack_into("<H", data, 0x98, 0x20b)
        struct.pack_into("<H", data, 0x98+68, 11)
        return data

    def validate_fixture(self, data):
        with patch.object(exfat, "SHA256", hashlib.sha256(data).hexdigest()):
            exfat.validate(data)

    def test_driver_contract_and_rejected_architecture_subsystem(self):
        self.validate_fixture(self.fixture())
        for offset, value in ((0x84, 0x8664), (0x98, 0x10b), (0x98+68, 10)):
            data = self.fixture()
            struct.pack_into("<H", data, offset, value)
            with self.assertRaises(ValueError):
                self.validate_fixture(data)

    def test_modified_or_truncated_dependency_fails(self):
        for data in (self.fixture(), self.fixture()[:-1], b"MZ"):
            with self.assertRaises(ValueError):
                exfat.validate(data)

    def test_fdf_loads_driver_without_shell_and_build_prepares_it(self):
        root = Path(__file__).resolve().parents[1]
        fdf = (root / "platforms/j413/mu/Platform/MacBookAirM2Pkg/MacBookAirM2.fdf").read_text()
        self.assertIn("SECTION DXE_DEPEX = Platform/MacBookAirM2Pkg/ExternalDrivers/exfat.depex", fdf)
        self.assertIn("SECTION PE32 = Platform/MacBookAirM2Pkg/ExternalDrivers/exfat_aa64.efi", fdf)
        self.assertIn('python3 "$ROOT/tools/prepare_j413_exfat.py"', (root / "scripts/build-j413-firmware.sh").read_text())
