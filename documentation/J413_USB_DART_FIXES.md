# J413 USB firmware and input integration checkpoint

EXP-20261011-J413-022 covers a combined software candidate. The operator's last
physical evidence remains Windows Boot Manager Recovery 0xc000000f (EXP018),
with built-in keyboard/trackpad unresponsive. This candidate is not physically
qualified and no media, ESP or boot policy is changed by its build.

## Confirmed source defects corrected

The owning Mu USB driver returned an EFI status cast to an initialization callback
and passed that result into RegisterNonDiscoverableMmioDevice. Success happened
to become NULL; failure became an invalid function pointer. Initialization now
returns EFI_STATUS, registration follows only a successful init, and the already
initialized controller registers with NULL callback. Registration failure is logged.
The translated ADT controller window is checked before MMIO.

Mu DART bank addresses were consumed without checking dt_node_reg failure, and
unknown or missing compatible strings fell through to an older register layout.
Both bank resources are initialized and checked before use; known string matching
is bounded by property length. Apple MIDR vendor matching is exact. T8110 stream
counts must be 1..256 before register writes. These checks do not grant new hardware
ownership or enable the currently excluded USB0/DFU controller.

The T8110 TLB flush inherited an offset/operand error: it wrote BIT(8) at base+BIT(8),
which is the error register, not the command register. Current official Asahi Linux
[apple-dart.c at 77cb8f24](https://github.com/AsahiLinux/linux/blob/77cb8f24c2381a8abb7272d7bbdec548d6426a8a/drivers/iommu/apple-dart.c)
defines command offset 0x80 and flush-all operation 0. The patch uses those values.
Both DART variants now return EFI_TIMEOUT after a bounded 100 one-us busy polls,
following the source's 100us timeout rather than spinning forever. No boot-time
speed improvement or DMA success has been measured.

J413 USB registration now depends on a private firmware readiness protocol. DART
publishes it only after both USB1 banks have completed flush and entered supported
bypass mode; absent/invalid resources, unknown layout, timeout or unsupported bypass
stop USB registration before controller MMIO. This protocol is not EFI_IOMMU_PROTOCOL, a Windows device
or general DMA approval. The EndOfDxe callback checks readiness through LocateProtocol; legacy platforms retain their registration path.

Primary interface contracts inspected: pinned Mu AppleDTLib, NonDiscoverableDevice
registration/protocol and J413 ACPI; upstream
[registration API](https://github.com/tianocore/edk2/blob/master/MdeModulePkg/Include/Library/NonDiscoverableDeviceRegistrationLib.h)
and [callback signature](https://github.com/tianocore/edk2/blob/master/MdeModulePkg/Include/Protocol/NonDiscoverableDevice.h).
Existing source licensing retained; register corrections are based on inspected
protocol definitions, with no copied third-party implementation.

## Input components added

DockChannel command matching and HIDF firmware preparation extend the already
implemented FIFO, frame/checksum, partial-read assembly and INIT parsing. They
are executable portable C protocol components, not an installed KMDF driver.
The source selects Asahi's offered MIT license and retains attribution.

Remaining integration includes helper-coprocessor startup, measured mailbox/IRQ
and reset ownership, multi-event discovery accumulation, GPIO requests, DMA/DART
firmware transfer and HID publication. Windows Boot Manager input is pre-kernel:
a Windows-only HID driver does not make its Recovery screen interactive. A UEFI
input adapter is also required. J313 SPI input cannot simply be relabelled as M2
DockChannel. GPU G14G firmware/UAT/queues/WDDM, audio, WLAN and power management
remain separate device implementations without M2 runtime qualification.

## Verification and next physical checkpoint

Tests compile the actual patched Mu initialization/bringup/flush functions with
mocked services under ASan/UBSan. They assert exact command address/value, timeout
bounds, absence of MMIO for malformed resources/layout/counts, readiness publication
only on both successful banks, and no USB registration after failed initialization.
DockChannel tests compile actual command and firmware cores, exercise malformed
ACKs and archives, and emit Windows ARM64 COFF objects. Fresh firmware build and
artifact identity are recorded in EXP022.

The next physical checkpoint is DART completion, USB1 registration and readable
complete Setup media discovery. These source changes do not fix an exFAT installer
layout, guarantee kernel entry or establish input/GPU support. Previous boot image
and original ESP recovery remain preserved; no repeated boot experiment is required
merely to qualify these software tests.

## DWC3 family validation (EXP-20261012-J413-029)

Core initialization now accepts both already declared DWC3 (0x5533 upper signature) and DWC31 (0x3331) identities. Unknown, zero and all-ones identities are rejected before reset/write. The pre-1.90a DWC3 workaround only uses revision bits on DWC3; DWC31 GSNPSID is an IP signature and must not trigger that workaround from its low bits. Actual core-function sanitizer tests cover both known identities, old/new DWC3 revisions and invalid signatures. This corrects source behavior, but no physical GSNPSID value has been captured from this boot and it is not proof that identity rejection caused IMG_5765. Linux primary reference: https://raw.githubusercontent.com/torvalds/linux/master/drivers/usb/dwc3/core.c (`dwc3_core_is_valid`, `dwc3_core_setup_global_control`).

The Setup console now reports non-discoverable controller enumeration status/count, matching xHCI count and actual connection result, plus DART readiness protocol presence and mask. A missing Setup file on an examined filesystem is not proof the external SSD is that filesystem. IMG_5765 passed the previous connection hang point but did not show a USB root connection marker; host-side four-file header validation still passes.

## Measured USB aperture (EXP-20261012-J413-030)

IMG_5767 reports DART readiness Success with mask 0x2 but zero registered controllers; the later IMG_5772 Shell exposes internal NVMe only. The captured translated ADT USB1 resource is base 0x502280000, length 0x11800. The previous one-megabyte minimum necessarily rejected that valid resource before initialization. Registration now preserves the measured length, checks that the last accessed global frame-adjustment and Apple CIO registers fit, and checks addition overflow. The generic PCI IO bridge bounds subsequent xHCI accesses by that exact length. No larger BAR is invented. Asahi's t8112.dtsi independently places this controller at the same base and separates core and Apple registers into smaller ranges.

The actual owning callback regression consumes the captured physical pair, includes the real DWC3 header, and verifies the exact registration base/length, truncated registers, addition overflow, failed core initialization and absent DART readiness under sanitizers. Prior mocks used a one-megabyte USB resource and did not expose the measured-window rejection. This corrects the registration guard; physical core initialization, xHCI binding and SSD enumeration still require hardware evidence.
