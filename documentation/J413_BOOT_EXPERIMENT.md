# J413 autonomous UEFI experiment

This is a compiled, source-checked boot experiment for MacBook Air M2 J413/T8112.
It has not been launched on the Air. Its first success criterion is a visible Mu
UEFI checkpoint; Windows Setup, Windows CPU/timer progress, USB storage/input,
GPU and accelerated display remain unqualified. See EXP-20261011-J413-010.

## Build and identity

```sh
scripts/build-j413-boot-experiment.sh
```

Native ARM64 Docker provides GCC 13.3 and pinned Rust 1.85.1. The Rust pin avoids
a bare-metal `wcslen` dependency emitted by Rust 1.99. Both distinct m1n1 stages
are compiled with `M1N1_J413`; the nested image contains the clean J413 DEBUG Mu
FD. Existing prepared Mu firmware can be reused with `J413_SKIP_MU=1`; its
manifest and bytes are verified first. No disk, boot policy or installer is
changed by this script. Publication replaces the output directory only after
verification, preserving the previous directory on a failed build.

Output: `dist/j413/boot-experiment/boot.bin`, 2,688,096 bytes, SHA-256:
`16020107c5bdf2096fcbf68eab2630e35e52dae1c283014d3485ee759f910806`.
Its manifest includes exact artifacts, submodule pins/diffs, J413 source overlay
and patch hash, DEBUG qualification, display/UART profile, and TOOLCHAINS.json.
Nested decompression/CRC checks pass and the decoded FD matches the previously
built clean firmware byte for byte. These are software checks, not a boot test.

## What changes at launch

The default J313 autonomous path rejects J413/T8112, and a J413 build rejects
J313/T8103, before autonomous USB power setup. J413 runtime also checks live USB1,
DART USB1 and UART register bases/interrupts and the complete CPU ADT topology.
Apple CPU `reg` values 0..3 and 0x100..0x103 are distinct from the architectural
MPIDRs 0..3 and 0x10100..0x10103.

The J413 checkpoint reference is constructed from its guest layout, live RAM
size and shared `hv_guest_cpu_state_prepare` source requirements. It contains
no M1 ADT digest or supposed M2 hardware golden. The wire collector and portable
CPU rules retain their historical J313 names; compiled J413 identity is J413.
The existing collector represents the boot CPU register image intended for
secondaries, not an independent register read from every secondary.

Before copying guest data, a pure planner checks that ADT/TrustCache fit before
the fixed Mu FD, and SEPFW/log fit after its full PcdFdSize reservation and before
fixed bootargs. The unused FD tail is filled using the FDF erase polarity.
The host allocator is capped below guest RAM. Live source buffers, loader,
framebuffer and the five T8112 DCP reservations named by kboot.c must be disjoint
from guest RAM. Oversized, missing or conflicting inputs stop with a message.
Reservations remain runtime-tested hypotheses; a build does not prove that
Apple's live allocations, all firmware carveouts or DMA contracts are safe.

Shared m1n1 CPU/power/vGIC, USB1/DART, NVMe and display code is inherited for this
first experiment. The patch does not establish their M2 runtime correctness.
The independent M2 RTKit/HID protocol cores are not linked Windows drivers.

## Recovery and the next physical checkpoint

An existing Asahi UEFI installation can provide the machine-personalized stage 1;
a new Asahi installation is not a prerequisite. First identify the screen actually
reached by that entry and the payload it loads. An entry named `UEFI boot`, or an
APFS `Bootable` flag, alone does not identify U-Boot, Mu or Windows progress.

EXP-20261011-J413-012 inspected the original Finish Installation resource, not the
active personalized kernel. It has an m1n1 v1.9.9 marker and a `chainload=` setting
whose PARTUUID matches the existing internal ESP and whose path is `m1n1/boot.bin`.
The preserved ESP copy contains a nested autonomous Windows image, SHA-256
`6c6f7c9d7fd532b9475f07ed2828987fc25a9cbe25f6b7f9d7803a43f2d6983e`.
Its two manifests decode correctly, but its flags, Mu FD and provenance differ
from this clean candidate. It is not established as a working M2 baseline.
Neither these bytes nor the stage-1 staging file prove what the current boot
policy actually launches.

The preferred integration path, if that existing stage 1 is active, is a backed-up
replacement of the assigned internal ESP's `m1n1/boot.bin`. It preserves stage-1
personalization. The internal ESP currently cannot be mounted in macOS, so no
such update was performed and no writable/raw-disk workaround is assumed safe.
Verify a writable mount and the live old payload before choosing this path;
retain a byte-identical recovery copy and record a separate install experiment.
The raw nested candidate is not a PE/COFF `BOOTAA64.EFI` executable to copy onto
an external drive or launch from a U-Boot UEFI menu. Mu runs under the m1n1 guest
shim in this project; generic UEFI availability does not qualify Windows.
[Official Asahi boot-process documentation](https://asahilinux.org/docs/alt/boot-process-guide/)
describes the personalized stage 1, assigned internal ESP and external UEFI media.

Direct raw-kernel personalization into the existing APFS stub remains an alternate
route when an ESP update cannot be made. It requires the stub's **paired recoveryOS
in 1TR** and changes the boot kernel/path. The locally inspected Asahi
`Finish Installation.app/.../step2.sh` enforces that pairing, requests owner
credentials for bputil/kmutil and ends with a user-confirmed reboot. Do not invoke
it unattended or target the active macOS system volume. Existing UEFI alone does
not require rerunning this step. The previously prepared private Recovery commands
are conditional on deliberately selecting this alternate route. No replacement
or personalization occurred; the mounted APFS stub stayed read only.

Preserve the original raw-kernel staging file and the separately captured
internal ESP image. Returning to macOS uses the power-button startup picker.
Restoring the original staging file also requires rerunning the appropriate
Recovery personalization; a copied backup alone does not restore LocalPolicy.

First run without starting Windows installation. Capture the last visible
J413/PREFLIGHT line or Mu UEFI screen. A failed gate, black screen or reboot is
an inconclusive experiment requiring the actual trace, not permission to remove
checks. If it reaches UEFI, qualify a firmware-visible USB disk next, then ARM64
Windows Setup. The external SSD is currently on physical USB0, while this guest
exposes USB1. Changing to the other port is a separately recorded physical
checkpoint and does not by itself establish controller/DART correctness.

The external exFAT Setup copy and prepared FAT32 sparse image are unchanged.
A physical FAT32 installer partition is still required by the planned media
route; destructive exFAT reconstruction and Windows deployment have not been
performed. See [external setup evidence](J413_EXTERNAL_SETUP.md).
