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
contains the desired code. The active ESP has now been copied and inspected
offline; see the diagnostic follow-up below. Administrator read-only mounting
failed, so inspection did not rely on a mounted original filesystem.

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

The existing internal ESP has been preserved as a local image and extracted
files. Inspect and qualify a clean J413 launch candidate before proposing an
original-file replacement. No administrator password should be supplied in chat.

Complete the J413 autonomous launch contract, validate live reservations and USB
DMA ownership, and arrange a recoverable firmware/logging checkpoint before
attempting Windows. Only then deploy Setup to a deliberately reviewed FAT32
partition. Formatting requires explicit approval for the identified physical
SSD and data preservation. The first Windows experiment targets the Setup
screen only, with no disk selection, partition deletion or OS installation.

See `investigation/EXPERIMENTS.md`, EXP-20261011-J413-003, for the actual
preparation outcome. No Windows logo, kernel start or Setup screen has been
observed on the M2 in this checkpoint.

## Internal ESP diagnostic follow-up

The user's administrator read-only mount of disk0s4 failed. `verifyVolume` used
`fsck_msdos -n`, returned code 0, and left its dirty flag set. That flag does not
prove structural corruption or conclusively explain the mount failure.
An administrator `dd` read preserved exactly 500170752 bytes, SHA-256
`c3c05822c9bdf82ee3fd977621d5e54158662465527a4b64aa6da3b76398384b`.
The preserved image was opened only for reading during offline extraction;
its SHA-256 was unchanged afterward. Both FAT copies and the backup boot sector
matched. 145 regular files were extracted; filesystem directory entries are
counted separately. No original ESP repair or modification occurred.

The existing `m1n1/boot.bin` has SHA-256
`6c6f7c9d7fd532b9475f07ed2828987fc25a9cbe25f6b7f9d7803a43f2d6983e`.
It parses as the repository's expected outer bootstrap plus inner standalone
image, with matching flags 1 and valid CRCs. **Two m1n1 layers are intentional
in this bootstrap format**, not evidence of a packaging defect. Both contain
J313 strings and automatic Windows entry messages. The decoded firmware has
SHA-256 `fb3f841a18d4e7c1484bc1b697fa559930b60f7696a0628ec7832c20bdf1992b`
and an M2-named debug PDB path, but differs from the newly built clean-source
J413 firmware. A build path and CRC do not qualify the platform contract.

The internal ARM64 fallback EFI file matches the external Setup fallback.
The internal BCD names `sources/boot.wim` and `boot/boot.sdi`, neither of which
is present at those paths on this internal ESP. This is a static observation,
not proof of the device-selection behavior at runtime. No existing payload was
executed and no source from it was imported into the clean fork. Full inventory,
recovery/account metadata, firmware archives and binaries remain private local
evidence under `.local/esp-audit/`. See EXP004 and EXP005.

## External resize request and preserved data

The user requested a smaller installer partition and a separate Windows target.
`diskutil resizeVolume disk7s2 limits` reports that the existing exFAT filesystem
does not support resizing. The local `diskutil` manual restricts `resizeVolume`
to journaled HFS+; `splitPartition` is destructive. A partition-map edit alone
does not shrink an exFAT filesystem. No destructive operation was substituted
for the requested resize.

All 1125 inventoried regular files, including hidden files, were copied into a
new private local backup and checked against source SHA-256, totaling
8533377328 bytes. The private manifest SHA-256 is
`0a1d6f0e0ea2eb2ad622ee185f6e5e1867c21bef19c44a0f53ee4a8424a83079`.
The original unattended account XML is included only in that restricted backup;
its settings were not run or published. This is a file backup of disk7s2, not a
raw GPT backup or a backup of the separate external ESP. See EXP006.

Proposed eventual layout, using 512GB for Windows pending the user's size reply:

| Partition | Proposed size | Filesystem / state |
| --- | --- | --- |
| Existing external EFI | 209715200 bytes | Preserve existing partition |
| WINSETUP | 16GB | FAT32, split WIM installer files |
| Microsoft reserved | 16MB | Reserved; create during qualified deployment |
| Windows | 512GB | NTFS; create/format during qualified deployment |
| Windows recovery | 2GB provisional | Verify actual WinRE size plus servicing headroom before deployment |
| M2DATA | Remaining capacity, about 1.47TB | exFAT, restored original files and workspace artifacts |

Sizes marked GB/MB are decimal. Microsoft documents the
[UEFI/GPT partition requirements](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/configure-uefigpt-based-hard-drive-partitions?view=windows-11).
Any macOS preparation that reserves an exFAT Windows target is only a placeholder,
not a finished NTFS Windows installation. Preserve the existing separate EFI
partition, and require explicit authorization to delete and reconstruct disk7s2
before any destructive layout command. Recheck physical identity, backup hashes,
all source files and free space immediately before reconstruction. Restore the
original files to M2DATA and verify them there before considering the backup
disposable. Prepared manual Setup files omit the unattended XML.

Booting WinPE from USB and installing/running Windows from that same USB SSD
are distinct milestones. Microsoft's former
[Windows To Go feature](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/deployment/windows-to-go/windows-to-go-overview)
was removed starting with Windows 10 version 2004. The modern ARM64 external
installation path requires separate deployment and USB boot qualification;
this project does not promise ordinary Setup will accept the USB target.
That does not change the immediate goal of reaching the Setup screen first.

The recorded SSD path in macOS is under USB0 (`usb-drd0`). The current J413
ACPI exposes USB1 only. Moving the SSD to the other physical port can be a later
controlled checkpoint, but does not itself qualify USB/DART ownership or make
the missing autonomous M2 launch contract valid. No port-role change or hardware
launch was attempted here.

Two verified staging artifacts also reside on the existing SSD filesystem under
`windows-on-m2-workspace/artifact-set-dlqdgi30/`: the prepared FAT32 sparse image
and clean J413 DEBUG FD, with the hashes already recorded above and in
J413_STATUS.md. `STATUS.json` explicitly records that physical Setup partition
creation, Windows installation and boot readiness are false. Local originals
are retained so reconstruction of disk7s2 would not destroy the only copies.
This workspace is a directory, not the requested new physical partitions.
