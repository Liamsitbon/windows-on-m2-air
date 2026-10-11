# J413 external Windows Setup preparation

The target is the user's existing SanDisk Extreme 2TB external SSD, volume
`Untitled 2`. This checkpoint prepares installer **files** and a local FAT32
volume image. It does not establish an M2 Windows boot path or authorize an SSD
wipe, installation, reboot or change to Apple boot policy.

## Observed media

The attached disk has a 209715200-byte FAT32 EFI partition and an exFAT data
partition. The latter contains ARM64 `efi/boot/bootaa64.efi` (PE machine 0xaa64),
a 630231583-byte `sources/boot.wim`, and a 7612941295-byte `sources/install.wim`.
The boot WIM declares two ARM64 images, Windows PE and Windows Setup, build
26100.9457. Its contents came from the existing external media, not a newly
verified Microsoft ISO download. WIM integrity checks establish readable image
resources, not the identity of the original publisher.

[Microsoft's installer-media instructions](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/install-windows-from-a-usb-flash-drive?view=windows-11)
use FAT32 and explain its 4GB file limit. The oversized install WIM is therefore
split into `install.swm` and `install2.swm` with wimlib, each below that limit.
[Microsoft documents split-WIM deployment](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe--use-a-single-usb-key-for-winpe-and-a-wim-file---wim?view=windows-11).
The small existing external ESP cannot fit the 630MB boot WIM. No existing
partition was reformatted or resized during this preparation.

## Apple bootstrap and Windows launch are separate requirements

The observed internal disk already has an APFS `UEFI boot` stub and an internal
ESP. [Asahi's boot process](https://asahilinux.org/docs/alt/boot-process-guide/)
loads its first stages through an internal ESP, then a later UEFI stage can load
an external `EFI/BOOT/BOOTAA64.EFI`. The presence of an APFS stub or a Finish
Installation app does not prove its boot policy is installed or its active ESP
contains the desired code. The active ESP has not yet been read: administrator
authentication is needed to mount it read-only.

A conventional Asahi U-Boot environment is not the Windows-specific Project Mu
plus EL2 virtual GIC platform implemented by this repository. Replacing an EFI
file or copying a Windows ISO does not supply those Windows CPU/ACPI/interrupt
contracts.

The clean pinned runtime still references `J313_AUTONOMOUS_LAYOUT`,
`hv_launch_golden_j313_init` and J313 launch schemas in
`m1n1_windows/src/hv_autonomous_runtime.c`. Its golden resources and interrupt
routes describe the M1 checkpoint. The new J413 FD is only a compiled firmware
component. It must not be packed into an M1 launch image and installed as an M2
Windows bootloader. No golden check has been bypassed to try to force it through.

## Prepared local artifact and evidence

Artifacts are under the ignored `.local/external-winsetup/` directory:

- `WINSETUP-M2.sparseimage`: new 10GiB logical GPT disk image with the prepared
  FAT32 Setup filesystem. This is a staging artifact, not a directly selectable
  Apple startup disk. It has not been written over the physical SSD.
- `MEDIA.json`: copied-file hashes, split-WIM hashes and explicit unqualified
  firmware/hardware status.
- `PREFLIGHT.json`: sanitized source inventory; no account credentials.
- `prepare.log`: byte-copy and WIM verification evidence.

All copied files are checked against their source SHA-256. The boot WIM and the
split installation WIM are checked with `wimlib-imagex verify`. The original
`autounattend.xml` is omitted from this manual Setup copy; its account credentials
and automated OOBE settings are neither executed nor published.

The FAT32 filesystem image contains Setup files on its data filesystem. Its
small automatically created GPT ESP is not a complete Apple/M2 bootstrap. Any
later media deployment must deliberately choose the physical partition layout
and fallback EFI path rather than blindly treating this sparse image as a raw
whole-SSD image.

Host commands used only on the newly created local image:

```sh
hdiutil create -size 10g -type SPARSE -fs 'MS-DOS FAT32' \
  -layout GPTSPUD -volname WINSETUP-M2 -nospotlight \
  .local/external-winsetup/WINSETUP-M2.sparseimage
hdiutil attach -nobrowse -owners off \
  .local/external-winsetup/WINSETUP-M2.sparseimage
# After byte copying all source files except install.wim and autounattend.xml:
wimlib-imagex split '/Volumes/Untitled 2/sources/install.wim' \
  /Volumes/WINSETUP-M2/sources/install.swm 3800
wimlib-imagex verify /Volumes/WINSETUP-M2/sources/install.swm \
  '--ref=/Volumes/WINSETUP-M2/sources/install*.swm'
wimlib-imagex verify /Volumes/WINSETUP-M2/sources/boot.wim
```

## Next observable checkpoint

Read the existing internal ESP and preserve exact original boot-file hashes and
copies before proposing a replacement. In this observed disk layout the
read-only mount command is `sudo diskutil mount readOnly disk0s4`; identifiers
must be rechecked if disks change. This command does not format or install.
No administrator password should be supplied in chat.

Complete the J413 autonomous launch contract, validate live reservations and USB
DMA ownership, and arrange a recoverable firmware/logging checkpoint before
attempting Windows. Only then deploy Setup to a deliberately reviewed FAT32
partition. Formatting requires explicit approval for the identified physical
SSD and data preservation. The first Windows experiment targets the Setup
screen only, with no disk selection, partition deletion or OS installation.

See `investigation/EXPERIMENTS.md`, EXP-20261011-J413-003, for the actual
preparation outcome. No Windows logo, kernel start or Setup screen has been
observed on the M2 in this checkpoint.
