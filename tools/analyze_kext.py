#!/usr/bin/env python3
"""Copy local Apple bundles and inventory their Mach-O/IOKit porting contracts.

This tool reads binaries; it does not run them or generate Windows drivers.
Apple binaries and complete symbol lists go only into --local-output.
"""

import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import struct
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "gpu": ["AGXG14G.kext", "AGXFirmwareKextG14GRTBuddy.kext", "AGXMetalG14G.bundle", "IOGPUFamily.kext"],
    "display": ["AppleDCP.kext", "AppleDCPDPTXProxy.kext", "AppleDCPDPDisplayProxy.kext"],
    "input": ["AppleDockChannel.kext", "AppleHIDTransport.kext", "AppleHIDTransport.kext/Contents/PlugIns/AppleHIDTransportFIFO.kext", "AppleHIDTransport.kext/Contents/PlugIns/AppleHIDTransportSCMCommon.kext", "AppleMultitouchDriver.kext", "AppleHIDKeyboardEmbedded.kext"],
    "iommu": ["IODARTFamily.kext", "AppleT8110DART.kext"],
    "power": ["AppleSMC.kext", "AppleT8112PMGR.kext", "AppleT8112CLPC.kext", "AppleT8112PCIe.kext"],
    "audio": ["AppleAOPAudio.kext", "AppleAOP2.kext"],
    "network": ["AppleBCMWLANBusInterfacePCIeMac.kext", "AppleBCMWLANCoreMac.kext"],
    "coprocessors": ["RTBuddy.kext", "RTBuddyV3.kext", "AppleSEPManager.kext"],
    "storage": ["IONVMeFamily.kext"],
}
WINDOWS_TARGETS = {
    "gpu": "WDDM kernel display miniport plus Direct3D user-mode driver; GPU VA, queues, fences, TDR and residency must be reimplemented.",
    "display": "DCP firmware protocol plus WDDM VidPn/present/scanout ownership; rendering and scanout require separate qualification.",
    "input": "KMDF DockChannel/RTKit transport plus VHF keyboard and Precision Touchpad HID reports; no J313 SPI reuse.",
    "iommu": "m1n1/platform DART ownership and explicit Windows DMA address translation; IOMapper is not a Windows API.",
    "power": "Platform ACPI/power integration and bounded SMC/PMGR protocol implementation; thermal limits must be measured.",
    "audio": "Windows audio driver plus AOP/codec/amp protocol, DMA and measured speaker protection.",
    "network": "NDIS or NetAdapterCx network implementation plus PCIe/firmware/power protocol.",
    "coprocessors": "Bounded RTKit mailbox transport with firmware ABI qualification; SEP authentication is optional and unimplemented.",
    "storage": "Preserve the existing synthetic NVMe bridge first; a native replacement requires Windows storage miniport and ANS protocol qualification.",
    "custom": "Identify the hardware transport and choose the relevant Windows driver model before implementing a port.",
}


class MachO:
    """Bounded little-endian 64-bit Mach-O fileset and symbol-table reader.

    Layouts follow Apple's mach-o/loader.h and mach-o/nlist.h. Offsets in an
    embedded KC image are collection offsets, not offsets relative to its header.
    """
    def __init__(self, data):
        self.data = data

    def unpack(self, fmt, offset):
        if offset < 0 or offset + struct.calcsize(fmt) > len(self.data):
            raise ValueError("truncated Mach-O structure")
        return struct.unpack_from(fmt, self.data, offset)

    def commands(self, offset=0):
        magic, cpu, subtype, kind, count, size, flags, reserved = self.unpack("<8I", offset)
        if magic != 0xFEEDFACF:
            raise ValueError("expected an unwrapped little-endian 64-bit Mach-O")
        cursor, end = offset + 32, offset + 32 + size
        if end > len(self.data):
            raise ValueError("truncated Mach-O command area")
        for _ in range(count):
            cmd, length = self.unpack("<II", cursor)
            if length < 8 or length % 8 or cursor + length > end:
                raise ValueError("invalid Mach-O load command length")
            yield cmd, cursor, length
            cursor += length
        if cursor != end:
            raise ValueError("Mach-O command count/size mismatch")

    def filesets(self):
        result = {}
        for cmd, cursor, length in self.commands():
            if cmd != 0x80000035:
                continue
            if length < 32:
                raise ValueError("short LC_FILESET_ENTRY")
            _, _, vmaddr, fileoff, nameoff, _ = self.unpack("<IIQQII", cursor)
            if not 32 <= nameoff < length:
                raise ValueError("invalid fileset name offset")
            raw_name = self.data[cursor+nameoff:cursor+length]
            if b"\0" not in raw_name:
                raise ValueError("unterminated fileset identifier")
            name = raw_name.split(b"\0", 1)[0].decode("utf-8")
            if name in result:
                raise ValueError("duplicate fileset identifier")
            result[name] = {"file_offset": fileoff, "virtual_address": hex(vmaddr)}
        return result

    def symbols(self, offset):
        symbols = []
        for cmd, cursor, length in self.commands(offset):
            if cmd != 2:
                continue
            if length < 24:
                raise ValueError("short LC_SYMTAB")
            _, _, symoff, count, stroff, strsize = self.unpack("<6I", cursor)
            if symoff + count * 16 > len(self.data) or stroff + strsize > len(self.data):
                raise ValueError("symbol table outside collection")
            strings = self.data[stroff:stroff+strsize]
            for i in range(count):
                index, kind, section, desc, value = self.unpack("<IBBHQ", symoff+i*16)
                if index >= len(strings):
                    raise ValueError("invalid symbol string index")
                end = strings.find(b"\0", index)
                if end < 0:
                    raise ValueError("unterminated symbol name")
                name = strings[index:end].decode("utf-8", errors="replace")
                if name:
                    symbols.append({"name": name, "address": hex(value), "type": kind, "section": section})
        return symbols


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def analyze_bundle(path, group, local, macho=None, entries=None, resume=False):
    metadata = plistlib.loads((path / "Contents/Info.plist").read_bytes())
    identifier = metadata["CFBundleIdentifier"]
    destination = local / "bundles" / group / path.name
    if destination.exists() and not resume:
        raise ValueError(f"snapshot already exists: {destination}")
    if destination.exists():
        original = {f.relative_to(path).as_posix(): sha256(f) for f in path.rglob("*") if f.is_file()}
        snapshot = {f.relative_to(destination).as_posix(): sha256(f) for f in destination.rglob("*") if f.is_file()}
        if original != snapshot:
            raise ValueError(f"existing snapshot differs from source: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Copy bytes, not SIP/immutable flags and system xattrs. Work in a temporary
    # sibling so a failed copy cannot masquerade as a complete snapshot.
    temporary = Path(tempfile.mkdtemp(prefix=".snapshot-", dir=destination.parent))
    try:
        for item in sorted(path.rglob("*")):
            target = temporary / item.relative_to(path)
            if item.is_symlink():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(item.readlink())
            elif item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif item.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(item, target)
        if not destination.exists():
            temporary.rename(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    executable = path / "Contents/MacOS" / metadata.get("CFBundleExecutable", "__absent__")
    entry = (entries or {}).get(identifier)
    symbols = macho.symbols(entry["file_offset"]) if macho and entry else []
    symbol_dir = local / "analysis" / identifier
    symbol_dir.mkdir(parents=True, exist_ok=True)
    (symbol_dir / "symbols.json").write_text(json.dumps(symbols, indent=2) + "\n")
    personalities = []
    for name, properties in metadata.get("IOKitPersonalities", {}).items():
        selected = {key: properties[key] for key in ["IOClass", "IOProviderClass", "IONameMatch", "IOPropertyMatch", "IOProbeScore"] if key in properties}
        personalities.append({"name": name, **selected})
    record = {"bundle": path.name, "group": group, "identifier": identifier,
              "version": metadata.get("CFBundleVersion"),
              "metadata_sha256": sha256(path / "Contents/Info.plist"),
              "executable_in_bundle": executable.is_file(),
              "present_in_boot_collection": entry is not None,
              "fileset": entry, "symbol_count": len(symbols),
              "dependencies": metadata.get("OSBundleLibraries", {}),
              "personalities": personalities, "windows_contract": WINDOWS_TARGETS[group],
              "status": "inventoried; protocol and Windows implementation unqualified"}
    hashes = {f.relative_to(destination).as_posix(): sha256(f) for f in sorted(destination.rglob("*")) if f.is_file()}
    (symbol_dir / "snapshot-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n")
    return record


def markdown(record):
    lines = [f"# {record['bundle']}", "", f"Bundle ID: `{record['identifier']}`; version `{record['version']}`.", "",
             f"Executable in bundle: **{record['executable_in_bundle']}**. Entry in this boot collection: **{record['present_in_boot_collection']}**. Available symbol names: **{record['symbol_count']}**.", "",
             "A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.", "",
             "## Observed IOKit matching", "", "```json", json.dumps(record['personalities'], indent=2, sort_keys=True), "```", "",
             "## Dependencies", ""]
    lines += [f"- `{name}` >= `{version}`" for name, version in record['dependencies'].items()]
    lines += ["", "## Windows implementation target", "", record['windows_contract'], "",
              "## Next reverse-engineering evidence", "",
              "1. Resolve the matched IORegistry service to its live ADT resources.",
              "2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.",
              "3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.",
              "4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.",
              "5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.", "",
              f"Metadata SHA-256: `{record['metadata_sha256']}`.", "",
              "Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, action="append")
    parser.add_argument("--target-j413", action="store_true")
    parser.add_argument("--resume", action="store_true", help="reuse byte-identical local snapshots")
    parser.add_argument("--kernel-macho", type=Path)
    parser.add_argument("--local-output", type=Path, default=ROOT / ".local/kext-research")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "documentation/reverse-engineering")
    args = parser.parse_args()
    paths = [("custom", path) for path in args.bundle or []]
    if args.target_j413:
        paths += [(group, Path("/System/Library/Extensions") / path) for group, names in TARGETS.items() for path in names]
    if not paths:
        parser.error("choose --target-j413 or --bundle")
    macho = MachO(args.kernel_macho.read_bytes()) if args.kernel_macho else None
    entries = macho.filesets() if macho else {}
    records, missing = [], []
    for group, path in paths:
        if not path.is_dir():
            missing.append(str(path))
            continue
        record = analyze_bundle(path, group, args.local_output, macho, entries, args.resume)
        directory = args.report_dir / group
        directory.mkdir(parents=True, exist_ok=True)
        (directory / (path.name + ".md")).write_text(markdown(record))
        records.append(record)
    inventory = {"format_version": 1, "bundles": records, "missing_paths": missing,
                 "kernel_macho_sha256": sha256(args.kernel_macho) if args.kernel_macho else None}
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (args.report_dir / "inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(f"Inventoried {len(records)} bundles; {len(missing)} missing. No Windows driver generated.")


if __name__ == "__main__":
    main()
