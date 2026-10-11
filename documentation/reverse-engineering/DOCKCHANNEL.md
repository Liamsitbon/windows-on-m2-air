# DockChannel: observed code and portable FIFO core

## Apple binary observation

The locally emitted boot collection identified
`com.apple.driver.AppleDockChannel` and the symbol
`__ZN16AppleDockChannel10flushFifosEh` (`AppleDockChannel::flushFifos(unsigned char)`).
With the collection hash recorded in the [research index](README.md), its virtual
address is `0xfffffe00093655c8`; the mapped `__TEXT_EXEC` file offset is
`0x23615c8`. A bounded local AArch64 disassembly with LLVM `llvm-mc` found:

- Selector values 1 through 3 are accepted; zero or values >= 4 return
  `0xe00002c2`. Apple's SDK `IOReturn.h` defines the corresponding common error
  `0x2c2` as `kIOReturnBadArgument`.
- The initial call resolves by its branch address to
  `AppleDockChannel::_enterTrace(unsigned int, unsigned int)`, with arguments
  17 and 0. This is a trace entry, not a demonstrated firmware handshake.
- Selector bit zero causes a 32-bit write of 1 at offset `0x10` through the
  pointer held at object offset `0x108`.
- A selector >= 2 causes a 32-bit write of 1 at offset `0x10` through the pointer
  held at object offset `0x118`. Successful paths return zero.
- PACIBSP and RETAB authenticate the return path. These Apple ARM64e
  instructions/object offsets do not establish a Windows kernel ABI.

The two object fields appear to identify register banks, but their physical
mapping and exact bank roles are **not established**. In particular, equal
numeric register offsets in different banks do not prove equal semantics.
No flush operation or object-layout offset was copied into the Windows core.
The local disassembly is `analysis/AppleDockChannel-flushFifos.asm`.

## Independently inspected FIFO protocol

The [Asahi DockChannel implementation](https://github.com/AsahiLinux/linux/blob/asahi/drivers/soc/apple/dockchannel.c)
was read independently. The local reference has SHA-256
`83cc73986312a06d99f7e5828a078964a581be00dc5826195e4622d5c6a7bede`.
Its SPDX license is `GPL-2.0-only OR MIT`. This repository's implementation is
original code using the observed register contract; no Linux implementation was
copied. The referenced T8112 device tree supplies a FIFO size of `0x800`.

| Data-bank offset | Operation / contract |
| --- | --- |
| `0x04` | TX8 byte write |
| `0x10` | TX32 little-endian word write |
| `0x14` | TX free capacity, in bytes |
| `0x1c` | RX8 32-bit read; byte is in bits 15:8 |
| `0x28` | RX32 little-endian word read |
| `0x2c` | RX available capacity, in bytes |

The byte-read shift matters: returning the low byte of RX8 corrupts tails of
one, two or three bytes. Four-byte transfers also need unaligned-safe packing.
The Linux driver waits for interrupts with a timeout when capacity is zero;
that policy belongs to the future Windows transport, not this portable core.

## Implemented boundary

[drivers/apple-dockchannel/core](../../drivers/apple-dockchannel/core/dockchannel.h)
provides `dc_try_send` and `dc_try_receive`. Each operation samples availability
once, transfers at most the request, available capacity and caller byte budget,
and returns without polling. Capacity above the configured FIFO size fails
without data-register access. Zero-byte requests perform no MMIO. Buffers need
no word alignment; receive byte tails explicitly select bits 15:8.

Callbacks are relative to a caller-provided **data bank**, not physical MMIO
addresses. A future KMDF adapter must use WDK register access primitives with
appropriate memory ordering, hold the device powered and serialize access. It
must implement IRQ masking/acknowledgement, waits/deadlines, RTKit/AFK shared
memory, DART mapping, DMA, cancellation and reset before publishing HID reports.
The current m1n1 baseline has a keyboard path lookup in `kboot.c`, but no M2
DockChannel Windows transport. The J413 Mu overlay deliberately exposes no M1
SPI input device.

Host fake-FIFO tests exercise byte tails, unaligned buffers, little-endian words,
partial capacity, empty/full FIFOs, operation budgets and corrupt capacity.
They validate software semantics, not physical MMIO mapping, firmware readiness,
interrupt delivery or a Windows device. No `.sys`, signing package or real
keyboard/touchpad qualification is claimed.

The next falsifiable hardware step is a read-only, bounded capacity-register
trace after power/resource ownership is established. Expected counts must be
within `0x800`; failure or inaccessible MMIO stops the experiment. No flush,
firmware upload or live FIFO consumption should precede a verified recovery
path and recorded experiment.
