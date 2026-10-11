#!/usr/bin/env python3
"""Collect selected macOS device-tree resources without IDs or firmware bytes."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import plistlib
import struct
import subprocess

NODES = {"aic", "usb-drd0", "usb-drd1", "sgx", "gfx-asc",
         "dockchannel-mtp", "dart-mtp", "mtp", "uart0", "ans", "dart-usb0", "dart-usb1"}


def walk(node, parents=()):
    if isinstance(node, list):
        for item in node:
            yield from walk(item, parents)
    elif isinstance(node, dict):
        yield node, parents
        yield from walk(node.get("IORegistryEntryChildren", []), parents + (node,))


def node_name(node):
    name = node.get("name", node.get("IORegistryEntryName", ""))
    if isinstance(name, bytes):
        name = name.rstrip(b"\0").decode("ascii")
    return name.split("@", 1)[0]


def decode_cells(data, width):
    if not isinstance(data, bytes) or len(data) % width:
        raise ValueError(f"malformed {width}-byte device-tree cells")
    return list(struct.unpack("<" + ("Q" if width == 8 else "I") * (len(data) // width), data))


def cell_count(node, property_name, allow_zero=False):
    cells = decode_cells(node.get(property_name), 4)
    if len(cells) != 1 or cells[0] not in ((0, 1, 2) if allow_zero else (1, 2)):
        raise ValueError(f"invalid {property_name}")
    return cells[0]


def register_pairs(node, parent):
    address_cells = cell_count(parent, "#address-cells")
    size_cells = cell_count(parent, "#size-cells", allow_zero=True)
    data = node.get("reg")
    stride = (address_cells + size_cells) * 4
    if not isinstance(data, bytes) or not data or len(data) % stride:
        raise ValueError("malformed reg containers")
    return [(int.from_bytes(data[i:i + address_cells * 4], "little"),
             int.from_bytes(data[i + address_cells * 4:i + stride], "little"))
            for i in range(0, len(data), stride)]


def translate_registers(node, parents):
    """Resolve little-endian Apple ADT cells, never infer an absent bus map.

    The pinned m1n1 rust/src/adt.rs get_reg_container defines this format.
    Unlike a permissive fallback, require one range covering the entire extent.
    Empty ranges mean identity. Missing/ambiguous/out-of-range mappings fail.
    """
    # IORegistry adds a synthetic Root above the actual Apple ADT root. It has
    # no address cells and is not an address bus. Trim only an explicitly named
    # device-tree boundary, never silently drop arbitrary unmapped ancestors.
    boundaries = [i for i, parent in enumerate(parents) if node_name(parent) == "device-tree"]
    if len(boundaries) > 1:
        raise ValueError("ambiguous device-tree root")
    if boundaries:
        parents = parents[boundaries[0]:]
    if not parents:
        raise ValueError("register node has no parent")
    pairs = register_pairs(node, parents[-1])
    translated = []
    for address, size in pairs:
        if address == 0 and size == 0:
            translated.append(None)  # Disabled placeholder, never MMIO.
            continue
        if not size or address + size > 1 << 64:
            raise ValueError("invalid register extent")
        for index in range(len(parents) - 1, 0, -1):
            bus, parent = parents[index], parents[index - 1]
            ca = cell_count(bus, "#address-cells") * 4
            pa = cell_count(parent, "#address-cells") * 4
            sz = cell_count(bus, "#size-cells", allow_zero=True) * 4
            ranges = bus.get("ranges")
            if not isinstance(ranges, bytes):
                raise ValueError(f"missing ranges on {node_name(bus)}")
            if not ranges:
                if address + size > 1 << (8 * pa):
                    raise ValueError("identity range exceeds parent address width")
                continue
            stride = ca + pa + sz
            if len(ranges) % stride:
                raise ValueError("malformed ranges")
            matches = []
            for start in range(0, len(ranges), stride):
                child = int.from_bytes(ranges[start:start + ca], "little")
                base = int.from_bytes(ranges[start + ca:start + ca + pa], "little")
                length = int.from_bytes(ranges[start + ca + pa:start + stride], "little")
                if child + length > 1 << (8 * ca) or base + length > 1 << (8 * pa):
                    raise ValueError("range exceeds address width")
                if child <= address and address + size <= child + length:
                    matches.append(base + address - child)
            if len(matches) != 1:
                raise ValueError("register extent has no unique covering range")
            address = matches[0]
        translated.append([hex(address), hex(size)])
    return translated


def collect(tree):
    nodes = list(walk(tree))
    chosen = next((n for n, _ in nodes if node_name(n) == "chosen"), None)
    if chosen is None or decode_cells(chosen.get("chip-id"), 4) != [0x8112]:
        raise ValueError("capture is not T8112")
    result = {}
    for node, parents in nodes:
        name = node_name(node)
        if name not in NODES:
            continue
        entry = {}
        if "compatible" in node:
            entry["compatible"] = node["compatible"].rstrip(b"\0").decode("ascii").split("\0")
        if "reg" in node:
            try:
                pairs = register_pairs(node, parents[-1]) if parents else []
            except ValueError:
                pairs = []
            if not pairs:
                # Legacy incomplete captures can retain raw 64-bit pairs; they
                # must never acquire a physical address by guessing cell widths.
                cells = decode_cells(node["reg"], 8)
                if len(cells) % 2:
                    raise ValueError(f"incomplete reg pairs: {name}")
                pairs = list(zip(cells[::2], cells[1::2]))
            entry["adt_reg_pairs"] = [[hex(address), hex(size)] for address, size in pairs]
            try:
                entry["physical_reg_pairs"] = translate_registers(node, parents)
            except ValueError as error:
                entry["address_resolution_error"] = str(error)
        if "interrupts" in node:
            entry["aic_irqs"] = decode_cells(node["interrupts"], 4)
        if "aic-iack-offset" in node:
            entry["iack_offset"] = hex(decode_cells(node["aic-iack-offset"], 8)[0])
        if name in result:
            raise ValueError(f"ambiguous device-tree node: {name}")
        result[name] = entry
    missing = {"aic", "usb-drd1", "sgx", "gfx-asc", "dockchannel-mtp"} - result.keys()
    if missing:
        raise ValueError(f"required nodes missing: {sorted(missing)}")
    return {"format_version": 2, "chip_id": "0x8112", "nodes": result,
            "address_semantics": "adt_reg_pairs are parent-relative. physical_reg_pairs are strictly translated through all parent ranges; null denotes a disabled placeholder. Missing physical pairs remain unresolved, never MMIO-qualified.",
            "validation": "macOS resource inventory; no Windows boot or GPU execution"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-plist", type=Path, help="offline ioreg capture")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.input_plist:
            raw = args.input_plist.read_bytes()
        else:
            model = subprocess.check_output(["sysctl", "-n", "hw.model"], text=True).strip()
            if model != "Mac14,2":
                raise ValueError(f"expected Mac14,2, got {model}")
            raw = subprocess.check_output(["ioreg", "-a", "-l", "-p", "IODeviceTree"])
        data = collect(plistlib.loads(raw))
        data["captured_at_utc"] = datetime.now(timezone.utc).isoformat()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        print(args.output)
    except (ValueError, OSError, subprocess.CalledProcessError, plistlib.InvalidFileException) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
