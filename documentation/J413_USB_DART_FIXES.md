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
