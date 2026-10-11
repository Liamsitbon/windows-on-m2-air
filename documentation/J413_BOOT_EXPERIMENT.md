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

The available Air must be rebooted to its **paired recoveryOS in 1TR** to
personalize a raw boot kernel for the existing UEFI stub. The locally inspected
Asahi `Finish Installation.app/.../step2.sh` enforces that pairing, requests
owner credentials for bputil/kmutil and ends with a user-confirmed reboot. Do
not invoke it unattended or apply its command to the active macOS system volume.
[Official Asahi boot-process documentation](https://asahilinux.org/docs/alt/boot-process-guide/)
explains the machine-specific signing and internal bootstrap requirement.

The internal ESP currently cannot be mounted. This experiment can instead be
personalized directly as the stub's raw kernel through Recovery, after staging
it in that stub's Finish Installation resources. This is a different boot path
from the old Asahi stage-1 reader loading `/m1n1/boot.bin` from the ESP. Its use
must be recorded as a new hardware experiment; do not claim the ESP was repaired.
The mounted APFS stub is currently read only, so no replacement was performed.

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
