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

The caller must assemble a complete immutable snapshot from possibly partial
FIFO reads, handle timeouts/removal and retain the snapshot while the view is in
use. Transport framing is not a HID descriptor parser or report delivery driver.
ACK flags, sequence, report number and return status still need matching against
a serialized outstanding command. Initialization events, firmware loading,
helper-coprocessor startup, GPIO resets and Windows HID enumeration remain absent.
No input device, IRQ, DART mapping or physical register was exercised.

These C files compile into Windows ARM64 COFF objects; no KMDF `.sys` or runtime
hardware support is claimed. See [RTKit adapter ownership](../apple-rtkit/README.md)
and [kext evidence](../../documentation/reverse-engineering/DOCKCHANNEL.md).
