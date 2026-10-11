# Read-only exFAT Setup discovery on J413

The operator reached the UEFI Shell without usable built-in input. The exact installed hash and USB port are unobserved. The confirmed SanDisk stores complete Setup files on exFAT; the J413 firmware previously included FAT only. Its small FAT ESP cannot hold boot.wim. Neither Shell entry nor this source correction proves USB enumeration or Windows kernel startup.

## Owning change

J413 embeds a separate EFI boot-service filesystem driver from [EfiFs v1.12](https://github.com/pbatard/EfiFs/releases/tag/v1.12). It is loaded by DXE without Shell commands. Existing WindowsAutoBootDxe checks the same four Setup paths and starts BOOTAA64.EFI when the filesystem is exposed. No partition reconstruction is needed for this experiment.

`tools/prepare_j413_exfat.py` pins the official 53,248-byte ARM64 release binary to SHA-256 `629e567847ba028cb6ba1f75af12b1ace2094a6b1e70cddbfe1a99a82cdd0511`, verifies PE32+, ARM64 machine and EFI boot-service-driver subsystem, and generates TRUE/END DXE dependency bytecode. A mismatched cached binary fails rather than being used. Build preparation is automatic; first download requires network access. The generated binary stays outside public source overlays.

## License and reproducibility

EfiFs is a separate GPLv3+ read-only driver, not relabeled as the repository's MIT code. Its release source is pinned to [bfc6ae29ac15516bddb97928eaf1eda187a6d242](https://github.com/pbatard/EfiFs/tree/bfc6ae29ac15516bddb97928eaf1eda187a6d242); upstream README documents builds and required GRUB/gnu-efi submodules. Preparation puts LICENSE, README.md, binary and source provenance in `dist/j413/third-party/efifs`. Preserve these with experimental artifact copies; no combined firmware binary is published to GitHub by this change.

## Qualification boundary

This fixes filesystem availability only. The current USB1 driver must still initialize successfully and enumerate the SSD; USB0 remains excluded. Windows Boot Manager must separately be able to consume the selected BCD and ramdisk files. Windows Setup and built-in DockChannel input remain unqualified. Xbox controller input is not implemented. No partition, ESP, boot policy or firmware installation is performed by the build script. See EXP-20261011-J413-023 for build and hardware evidence.
