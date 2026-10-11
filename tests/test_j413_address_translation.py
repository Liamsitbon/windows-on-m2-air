import copy
import struct
import unittest

from tools.collect_j413 import translate_registers


def bus(address_cells, size_cells, ranges=None):
    result = {"name": b"bus", "#address-cells": struct.pack("<I", address_cells),
              "#size-cells": struct.pack("<I", size_cells)}
    if ranges is not None:
        result["ranges"] = ranges
    return result


class J413AddressTranslationTests(unittest.TestCase):
    def fixture(self):
        root = bus(2, 2)
        arm_io = bus(2, 2, struct.pack("<QQQ", 0, 0x200000000, 0x100000000))
        nested = bus(1, 1, struct.pack("<IQI", 0x100, 0x5000, 0x10000))
        node = {"reg": struct.pack("<II", 0x110, 0x10)}
        return node, [root, arm_io, nested]

    def test_nested_mixed_cell_widths_translate_the_entire_extent(self):
        node, parents = self.fixture()
        self.assertEqual([["0x200005010", "0x10"]], translate_registers(node, parents))
        self.assertEqual(struct.pack("<II", 0x110, 0x10), node["reg"])

    def test_ioreg_wrapper_is_not_a_physical_address_bus(self):
        node, parents = self.fixture()
        parents[0]["name"] = b"device-tree"
        wrapper = {"name": b"Root"}
        self.assertEqual([["0x200005010", "0x10"]],
                         translate_registers(node, [wrapper] + parents))
        parents[1]["name"] = b"device-tree"
        with self.assertRaisesRegex(ValueError, "ambiguous device-tree root"):
            translate_registers(node, [wrapper] + parents)

    def test_identity_ranges_and_disabled_placeholders(self):
        root = bus(2, 2)
        identity = bus(2, 2, b"")
        node = {"reg": struct.pack("<QQQQ", 0x502280000, 0x11800, 0, 0)}
        self.assertEqual([["0x502280000", "0x11800"], None],
                         translate_registers(node, [root, identity]))

    def test_missing_and_ambiguous_ranges_never_return_guessed_addresses(self):
        node, parents = self.fixture()
        del parents[-1]["ranges"]
        with self.assertRaisesRegex(ValueError, "missing ranges"):
            translate_registers(node, parents)
        node, parents = self.fixture()
        parents[-1]["ranges"] *= 2
        with self.assertRaisesRegex(ValueError, "no unique"):
            translate_registers(node, parents)

    def test_a_range_must_cover_size_not_only_the_start_address(self):
        node, parents = self.fixture()
        node["reg"] = struct.pack("<II", 0x100f0, 0x20)
        with self.assertRaisesRegex(ValueError, "no unique"):
            translate_registers(node, parents)

    def test_reject_malformed_cells_ranges_and_overflow(self):
        node, parents = self.fixture()
        bad = copy.deepcopy(parents)
        bad[-1]["ranges"] += b"x"
        with self.assertRaisesRegex(ValueError, "malformed ranges"):
            translate_registers(node, bad)
        bad = copy.deepcopy(parents)
        bad[-1]["#address-cells"] = struct.pack("<I", 3)
        with self.assertRaisesRegex(ValueError, "invalid #address-cells"):
            translate_registers(node, bad)
        bad = copy.deepcopy(parents)
        bad[-1]["ranges"] = struct.pack("<IQI", 0xffffff00, 0, 0x10000)
        with self.assertRaisesRegex(ValueError, "range exceeds"):
            translate_registers(node, bad)
        with self.assertRaisesRegex(ValueError, "no parent"):
            translate_registers(node, [])
