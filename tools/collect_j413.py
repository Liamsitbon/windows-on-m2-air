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
         "dockchannel-mtp", "dart-mtp", "mtp", "uart0", "ans", "dart-usb1"}


def walk(node):
    if isinstance(node, list):
        for item in node:
            yield from walk(item)
    elif isinstance(node, dict):
        yield node
        yield from walk(node.get("IORegistryEntryChildren", []))


def node_name(node):
    name = node.get("name", node.get("IORegistryEntryName", ""))
    if isinstance(name, bytes):
        name = name.rstrip(b"\0").decode("ascii")
    return name.split("@", 1)[0]


def decode_cells(data, width):
    if not isinstance(data, bytes) or len(data) % width:
        raise ValueError(f"malformed {width}-byte device-tree cells")
    return list(struct.unpack("<" + ("Q" if width == 8 else "I") * (len(data) // width), data))


def collect(tree):
    nodes = list(walk(tree))
    chosen = next((n for n in nodes if node_name(n) == "chosen"), None)
    if chosen is None or decode_cells(chosen.get("chip-id"), 4) != [0x8112]:
        raise ValueError("capture is not T8112")
    result = {}
    for node in nodes:
        name = node_name(node)
        if name not in NODES:
            continue
        entry = {}
        if "compatible" in node:
            entry["compatible"] = node["compatible"].rstrip(b"\0").decode("ascii").split("\0")
        if "reg" in node:
            cells = decode_cells(node["reg"], 8)
            if len(cells) % 2:
                raise ValueError(f"incomplete reg pairs: {name}")
            entry["adt_reg_pairs"] = [[hex(cells[i]), hex(cells[i+1])] for i in range(0, len(cells), 2)]
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
    return {"format_version": 1, "chip_id": "0x8112", "nodes": result,
            "address_semantics": "Raw Apple ADT reg cells; resolve parent ranges before MMIO use.",
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
