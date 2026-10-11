# Portable RTKit management port

`core/rtkit_management.c` adapts version negotiation, endpoint enumeration,
system endpoint starts and power acknowledgements from the official Asahi Linux
[RTKit library at 77cb8f24](https://github.com/AsahiLinux/linux/blob/77cb8f24c2381a8abb7272d7bbdec548d6426a8a/drivers/soc/apple/rtkit.c).
Its header and implementation offer `GPL-2.0-only OR MIT`; this adaptation selects
MIT, preserves Asahi attribution and includes the upstream MIT license text.
This is a source port of a defined protocol, not a binary kext converter.

The C11 core has no Linux types, allocation, scheduling or mailbox dependency.
It compiles into a Windows ARM64 COFF object. This is not a linked KMDF driver,
an installed `.sys`, a complete RTKit client or proof of live device operation.

Call `rtkit_plan_management` with a separate output plan. It does not modify the
input state or send a message. A successful plan contains the prospective state
and at most seven endpoint-0 replies. The caller serializes RX, sends every reply
in order, then commits `plan.next`. A partial transport failure requires a
measured recovery path: do not retry a partially sent plan blindly. If sending
can synchronously re-enter RX, queue the input until commit. Zero/reset state
only while its associated coprocessor is held in reset.

Asahi supports protocol versions 11–12. The highest mutually supported version
is selected. This port additionally rejects inverted ranges, repeated HELLOs,
EPMAP before negotiation, and EPMAP after completion. A repeated HELLO can
indicate a restarted coprocessor; the adapter must recover rather than combine
endpoint maps from different boots. Power acknowledgements may arrive before
endpoint enumeration. Application endpoints require both acknowledged power
states and a complete map; unsupported system endpoints are not auto-started.

The six recognized system endpoints can request shared buffers immediately
after their start messages. **Implement their handlers before using this core
on hardware.** Management state being ready does not establish DMA or driver
readiness. No firmware-provided address is mapped by this code.

## Windows adapter still required

| Asahi dependency | Required Windows/platform ownership |
| --- | --- |
| mailbox send/RX and workers | Bound transport operations, serialized RX and cancellation |
| Linux locks/completions | KMDF synchronization, bounded asynchronous timeouts and removal handling |
| coherent allocation / supplied IOVA | Established DART/IOMMU ownership, validated shared-memory bounds and lifetime |
| system log / crash endpoints | Buffer request handling, bounded log parsing and coprocessor recovery |
| reset and power sequencing | A measured per-device resource contract and D0/D3 sequencing |

[Framework interrupt objects](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfinterrupt/nf-wdfinterrupt-wdfinterruptcreate)
must use assigned resources. [Framework locks](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/using-framework-locks)
provide synchronization primitives; this core does not pick an IRQL for the
adapter. [KMDF common buffers](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/using-common-buffers)
provide logical addresses within the DMA adapter contract, which still must be
reconciled with Apple DART. A physical address is not automatically a usable IOVA.

RTKit is used by multiple coprocessor clients. This generic management port does
not implement the separate DockChannel HID framing/AFK transport, GPU firmware
ABI, DCP display protocol or a keyboard/trackpad device.

Verification: `python3 -m unittest tests.test_rtkit_management` checks negotiation
boundaries, all eight bitmap pages, endpoint 255, maximum reply count, ordering,
power gating, crash rejection, unchanged input state, and Windows ARM64 COFF
compilation. Hardware qualification remains absent.
