#!/usr/bin/env python3
"""Fetch and verify the separately licensed read-only ARM64 EfiFs dependency."""
import hashlib
from pathlib import Path
import struct
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REVISION = "bfc6ae29ac15516bddb97928eaf1eda187a6d242"
SHA256 = "629e567847ba028cb6ba1f75af12b1ace2094a6b1e70cddbfe1a99a82cdd0511"
URL = "https://github.com/pbatard/EfiFs/releases/download/v1.12/exfat_aa64.efi"


def validate(data):
    if len(data) != 53248 or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("EfiFs exFAT release size/SHA-256 mismatch")
    if data[:2] != b"MZ":
        raise ValueError("EfiFs dependency is not PE")
    offset = struct.unpack_from("<I", data, 0x3c)[0]
    if data[offset:offset+4] != b"PE\0\0":
        raise ValueError("EfiFs PE signature missing")
    if struct.unpack_from("<H", data, offset+4)[0] != 0xaa64:
        raise ValueError("EfiFs dependency is not ARM64")
    if struct.unpack_from("<H", data, offset+24)[0] != 0x20b:
        raise ValueError("EfiFs dependency is not PE32+")
    if struct.unpack_from("<H", data, offset+24+68)[0] != 11:
        raise ValueError("EfiFs dependency is not an EFI boot-service driver")


def prepare(root=ROOT):
    target = root / "mu/Platform/MacBookAirM2Pkg/ExternalDrivers"
    target.mkdir(parents=True, exist_ok=True)
    driver = target / "exfat_aa64.efi"
    if driver.exists():
        data = driver.read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=60) as response:
            data = response.read(53249)
    validate(data)
    driver.write_bytes(data)
    # UEFI dependency bytecode: PUSH TRUE (0x06), END (0x08).
    (target / "exfat.depex").write_bytes(bytes([0x06, 0x08]))
    output = root / "dist/j413/third-party/efifs"
    output.mkdir(parents=True, exist_ok=True)
    (output / driver.name).write_bytes(data)
    for name in ("LICENSE", "README.md"):
        with urllib.request.urlopen(f"https://raw.githubusercontent.com/pbatard/EfiFs/{REVISION}/{name}", timeout=60) as response:
            (output / name).write_bytes(response.read())
    (output / "SOURCE.txt").write_text(
        f"Separate GPLv3+ read-only EFI driver; firmware host licensing unchanged.\n"
        f"Release: {URL}\nSHA-256: {SHA256}\n"
        f"Source: https://github.com/pbatard/EfiFs/tree/{REVISION}\n"
        "Build instructions and source submodules: see upstream README.md.\n"
        "Local experimental artifact only; preserve this license/source notice with copies.\n")
    return driver


if __name__ == "__main__":
    print(prepare())
