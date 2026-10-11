# Official Asahi source ports for the M2 investigation

The source reference is the official Asahi Linux `asahi` branch, resolved on
2026-10-11 to `77cb8f24c2381a8abb7272d7bbdec548d6426a8a`. Source adaptations
preserve upstream attribution and select the offered MIT license. No Gemini
source changes or extracted Apple code were imported.

| Source at that commit | Portable implementation | Verified boundary |
| --- | --- | --- |
| [rtkit.c](https://github.com/AsahiLinux/linux/blob/77cb8f24c2381a8abb7272d7bbdec548d6426a8a/drivers/soc/apple/rtkit.c) | [RTKit management](../drivers/apple-rtkit/README.md) | Version negotiation, endpoint bitmap/start plans, power ACKs; host checks and Windows ARM64 COFF compilation |
| [dockchannel.c](https://github.com/AsahiLinux/linux/blob/77cb8f24c2381a8abb7272d7bbdec548d6426a8a/drivers/soc/apple/dockchannel.c) | [FIFO core](../drivers/apple-dockchannel/core/dockchannel.c) | Bounded word/byte transfers behind callbacks; fake-register tests |
| [dockchannel-hid.c](https://github.com/AsahiLinux/linux/blob/77cb8f24c2381a8abb7272d7bbdec548d6426a8a/drivers/hid/dockchannel-hid/dockchannel-hid.c) | [HID packet core](../drivers/apple-dockchannel/README.md) | Command framing/checksum, partial-frame assembly and initialization block views; ASan/UBSan and Windows ARM64 COFF compilation |

The FIFO core predates these adaptations and is an original implementation of
the inspected register contract. The management and HID framing cores are
actual C source adaptations with Linux scheduling, allocation and transport
removed from the portable layer. No automatic converter for arbitrary kexts or
Linux drivers is supplied. Each hardware protocol still needs a Windows adapter.

## Read-only resource translation checkpoint

`tools/collect_j413.py` now preserves parent paths while translating selected
Apple ADT register extents. It follows the little-endian cell representation
and parent traversal in pinned m1n1 `rust/src/adt.rs::get_reg_container`. It
skips only IORegistry's explicitly identified wrapper above the `device-tree`
root, rejects missing/overlapping/out-of-range mappings, and retains raw
addresses. Null physical entries denote disabled placeholders. Tests exercise
mixed cell widths and multiple parent buses as well as malformed ranges.

Observed addresses can be compared with official
[T8112 DTS](https://github.com/AsahiLinux/linux/blob/77cb8f24c2381a8abb7272d7bbdec548d6426a8a/arch/arm64/boot/dts/apple/t8112.dtsi):

| Resource | Translated physical base | Observed AIC IRQ | Scope |
| --- | --- | --- | --- |
| UART0 | `0x235200000` | 739 | Matches DTS base; live ADT extent differs from guest's smaller UART resource |
| AIC | `0x23b0c0000` | controller | Physical controller, not the guest virtual GIC |
| USB0 DWC3 | `0x382280000` | 1031 | SSD's currently observed port; absent from the current guest ACPI |
| USB1 DWC3 | `0x502280000` | 1112 | Exposed guest controller; separate route to virtual 857 |
| MTP DockChannel IRQ bank | `0x24eb14000` | 850 | Matches DTS IRQ-bank base; ADT and DTS describe different aggregate extents |
| MTP HID configuration/data | `0x24eb30000` / `0x24eb34000` | via DockChannel | Derived from live ADT and DTS child ranges; not mapped or exercised |
| MTP DART bank 0 | `0x24e808000` | 848 | Translation only; no DMA mapping established |

The collector does not establish clocks, power, USB role, DART stream ownership,
guest mapping, running coprocessor state or firmware-buffer reservations.
Resources are evidence for the next platform work, not addresses to write from
macOS. The inherited J313 autonomous launch reservations remain unqualified on
M2; the compiled Mu component and these protocol cores do not resolve them.

## Remaining integration boundaries

RTKit system endpoints need bounded shared-buffer/log handlers, mailbox IRQ/RX,
transport failure recovery and reset ownership. DockChannel HID now has packet assembly and bounded initialization descriptor parsing. It still needs outstanding-command matching, multi-event discovery accumulation, helper CPU,
GPIO, device firmware and Windows HID publication. Trackpad firmware must be
validated and loaded under an established DART contract. GPU/DCP needs its own
firmware ABI, queues, synchronization and WDDM/display implementation; management
messages alone do not provide graphics acceleration.

EXP018 records physical progress to Windows Boot Manager Recovery 0xc000000f; the exact installed artifact is unknown. The next hardware checkpoint is complete readable Setup media selection and Windows Setup, with USB ownership still unqualified. No device has been driven by these components in this checkpoint.
