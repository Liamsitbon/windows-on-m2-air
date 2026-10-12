# Persistent J413 EFI phase diagnostics

The Windows Setup selector captures a bounded ASCII diagnostic buffer in the guest EFI driver. At application-level checkpoints it saves the buffer to `\m1n1\j413uefi.log` on an internal NVMe filesystem that contains the existing `\m1n1\boot.bin` anchor. Removable/external USB filesystems are not selected as the log target. A read-only block device is skipped. The target is the existing internal FAT ESP, not an APFS macOS filesystem.

The file uses a fixed 16,384-byte write with zero padding. It is the latest phase snapshot, overwritten across attempts, with no unbounded append/history. The logger checks position, write status, short writes and flush, and closes all file/volume handles. Saving does not change Setup selection or security policy. The boot continues if logging fails; the console reports the save error. A successful file flush is required before the console claims the log was saved.

Recorded phases include controller connection completion, presence/status of the USB DART readiness protocol and controller mask, readable filesystem count, the first missing Setup prerequisite on each examined volume, and final option-selection status. This is a **phase log**, not complete UART/DXE/kernel output. It begins when BDS invokes the selector; a failure before that point or before internal writable storage is available cannot be persisted by this mechanism. A power failure or failed underlying NVMe write may leave a partial previous/current snapshot; persistence requires a hardware attempt to qualify.

After installing the current candidate and attempting boot, return to macOS and run:

```sh
cd "/Users/liamsitbon/Documents/ChatGPT/windows m1n1/windows-on-m2-air"
sudo ./scripts/read-efi-log.sh --disk disk0s4
```

The command opens `/dev/rdisk0s4` **read only**, parses the FAT32 partition and extracts only `M1N1/J413UEFI.LOG`. It does not mount, format or modify the partition. FAT geometry, active FAT, cluster ranges, directory traversal bounds, cycles and file size are checked. It also supports an existing FAT32 partition image through `python3 tools/read_efi_log.py image.img`. The short 8.3 filename intentionally avoids depending on long-filename reconstruction.

The copied macOS text file is `.local/efi-logs/latest.log` in the repository. No EFI log exists until the new candidate has reached a saving checkpoint on hardware; an older installed candidate will not produce one. Keep logs private since device paths/status can be machine-specific. Exact build/qualification evidence is recorded in EXP-20261011-J413-025.

The EXP-20261012-J413-026 candidate also prints console-only `UEFI TRACE` markers around TPM confirmation, AfterConsole return, priority boot entry, Setup protocol lookup, and controller connection entry/return. These markers deliberately perform no disk write before connecting controllers: early storage writes could themselves obscure the hang. A stationary final marker narrows the entered operation but is not by itself an exception or proof of a specific hardware driver failure. The persistent phase log still requires connection completion and writable internal storage.

EXP-20261012-J413-027 narrows a confirmed stationary ConnectAll entry marker with `UEFI CONNECT` console output around initial/final default console connection, each recursive controller connection (index, handle and device path), and DXE dispatch. The J413 helper preserves the pinned UefiBootManagerLib connection algorithm and Intel BSD-2-Clause-Patent attribution, checking enumeration failure before using the handle list. It does not bypass a driver or interrupt a running driver Start function. A last controller path identifies the outer recursive connection; the failing child driver still needs owning-layer investigation.
