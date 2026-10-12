# General EFI application boot on J413

EXP-20261012-J413-031 broadens automatic boot selection beyond Windows Setup.
It retains the USB aperture correction from EXP030. Neither candidate is yet
qualified by a new physical boot.

Complete Windows Setup remains the first preference. If absent or its loader
returns, firmware looks for `\EFI\BOOT\BOOTAA64.EFI` and
`\EFI\Microsoft\Boot\bootmgfw.efi` across every already readable filesystem,
then recursively discovers `.efi` files anywhere on those filesystems. Generic
selection does not require BCD, WIM, SDI, a particular partition type, a volume
name, BlockIo, an external disk, or a vendor. Applications on internal, external
and virtual filesystems are eligible whenever a SimpleFS driver exposes them.
This does not add APFS support or initialize currently unsupported controllers.

Each generic candidate must have an ARM64 PE32+ EFI application header. x86/x64
images and EFI drivers are not boot applications for this ARM64 firmware. The
header preflight does not establish authenticity or executable validity: standard
`EfiBootManagerBoot` still performs loading, complete image validation, security
policy and ReadyToBoot sequencing. No security policy is changed.

Console output shows discovered and selected paths, each attempted application's
path and returned status. Returned or failed applications advance to the next
candidate once, including security-rejected images without retry or bypass. A
loader that takes over or hangs cannot be forcibly interrupted by this scanner.
After candidates are exhausted normal BootNext/BootOrder behavior continues; the
scanner creates ephemeral options and writes no persistent BootOrder. Built-in
keyboard/trackpad and Xbox console input remain unsupported.

To bound memory and damaged-filesystem traversal, the scanner permits 32 directory
levels, paths under 1024 characters, 100000 entries per filesystem, and 256 generic
applications per scan. Directory records and names are checked against returned
buffer lengths, `.`/`..` are skipped, and handles/buffers are closed/freed. Limit
messages identify truncation; directory errors may prevent descendants being
examined. Preferred-path duplicates are removed case-insensitively on each handle,
and the complete Setup path already attempted is not retried.

Actual-function sanitizer tests cover nested nonstandard paths, root applications,
multiple filesystems without BlockIo selection, extension case, architecture and
subsystem rejection, malformed entries, buffer growth, failed reads/options,
deduplication, cleanup and the standard BDS retry loop. Native firmware and artifact
verification are software evidence; SSD enumeration and OS boot require hardware
confirmation. Sources: [UEFI media/file protocols](https://uefi.org/specs/UEFI/2.10/13_Protocols_Media_Access.html),
[UEFI image overview](https://uefi.org/specs/UEFI/2.10/02_Overview.html), pinned Mu
`FileInfo.h`, `UefiBootManagerLib/BmBoot.c` and `MsPlatform.c`.
