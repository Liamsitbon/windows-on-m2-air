# DockChannel transport components

`core/dockchannel.c` provides bounded FIFO transfers behind register callbacks.
`core/hid_packet.c` ports command framing and packet validation from official
Asahi [dockchannel-hid.c at 77cb8f24](https://github.com/AsahiLinux/linux/blob/77cb8f24c2381a8abb7272d7bbdec548d6426a8a/drivers/hid/dockchannel-hid/dockchannel-hid.c).
The latter offers GPL-2.0 OR MIT. This adaptation selects MIT, retains Asahi
attribution and uses the [included license](../apple-rtkit/ASAHI-MIT-LICENSE.txt).

The packet core reads little-endian fields without unaligned typed loads. It
validates the eight-byte header, interface range 0–15, recognized channel,
aligned body size, complete packet, additive checksum and subheader payload
bounds before returning a borrowed view. Unknown channels are rejected rather
than treated as reports. Extra input can contain another frame; `consumed`
describes only the validated first frame. Invalid input produces no payload view.

Command encoding follows Asahi's eight-byte outer header, eight-byte subheader,
four-byte payload padding and trailing checksum whose complete word sum is
`0xffffffff`. Payloads over 65524 bytes are rejected before the 16-bit padded
body length can overflow. The encoder does not transmit or advance the sequence.
Buffers and output views must be disjoint as documented in the header.

`core/hid_stream.c` now assembles a frame across partial FIFO reads in caller-owned storage. It stops exactly at one complete frame, preserves extra input for the caller, and latches malformed-header/checksum/capacity failures until explicit transport recovery and reset. A complete view lives until reset; calls must be serialized. The adapter still owns timeouts/removal. Transport framing is not a HID descriptor parser or report delivery driver.
ACK flags, sequence, report number and return status still need matching against
a serialized outstanding command. Firmware loading,
helper-coprocessor startup, GPIO resets and Windows HID enumeration remain absent.
No input device, IRQ, DART mapping or physical register was exercised.

These C files compile into Windows ARM64 COFF objects; no KMDF `.sys` or runtime
hardware support is claimed. See [RTKit adapter ownership](../apple-rtkit/README.md)
and [kext evidence](../../documentation/reverse-engineering/DOCKCHANNEL.md).

## Interface discovery

`core/hid_discovery.c` parses one `EVENT_INIT` payload using the same pinned
Asahi structure definitions and MIT license selection. It returns bounded
interface/name, HID descriptor, GPIO request and product-name views. Fixed-width
names are copied with an added terminator. GPIO data must fit its own block,
not just the enclosing packet. Zero-length product/descriptor blocks, duplicate
known blocks, truncated lengths and invalid interface IDs are rejected without
exposing partial output. Unknown blocks are skipped; a terminator stops parsing
as in upstream. No buffer is allocated and no GPIO is driven.

Discovery can span multiple events (`more_packets`); accumulating descriptors
and atomically publishing an interface remain adapter responsibilities. These
cores are not yet connected to m1n1, Mu or a Windows KMDF device. Consequently
they do not make built-in input usable at Windows Boot Manager Recovery.

`tests/test_dockchannel_discovery.py` exercises every two-part frame split,
concatenated frames, sticky transport errors, untrusted initialization lengths,
fixed-width names and GPIO block boundaries under ASan/UBSan, and compiles both
new cores as Windows ARM64 COFF.
