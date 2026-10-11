# J413 boot UI and photographed loader recovery

EXP018 operator images show Mu device-state color bars and then the Windows Boot Manager Recovery screen, 0xc000000f, "A required device isn't connected or can't be accessed." The operator reports approximately one minute of lit black panel beforehand. Installed image hash is unknown. This qualifies progress into the Windows boot manager, not WinPE, Windows kernel, GPU acceleration or input drivers. Only built-in keyboard/trackpad were tried; USB input was not tested.

## Current presentation

EXP019 supersedes the graphical presentation after the operator reported frozen stage text and a static bar. J413 now shows UEFI BOOT and text only; the Windows-like mark and both bars are removed. Stage lines carry physical-counter millisecond timestamps. These indicate reached loader stages, not elapsed Windows loading progress.

Before GOP initialization, actual Mu UART output is buffered into bounded lines and drawn on the live validated guest surface. Each line cleans only its own text rows to the point of coherency. The inherited host framebuffer is disabled after the DCP surface switch, so firmware bytes no longer cause full-frame copies to an invisible surface. SimpleFbDxe emits a dedicated takeover marker before touching the guest framebuffer; the hypervisor text renderer stops permanently at that marker. It never draws over firmware GOP or Windows-owned graphics. This protocol and bounds are software-tested, not physically qualified.

The normal Mu boot graphic is skipped; temperature/low-battery warnings retain their original resource interface. Device-state collection and Secure Boot policy remain unchanged. Subsequent UEFI console text describes media selection and handoff. Full kernel printf text and animation are controlled by Windows, not this renderer. No faster hardware boot time is claimed without a measured physical run.

## Setup media selection

EXP020 corrects the J413 automatic Setup selection: the same readable filesystem must contain BOOTAA64.EFI, EFI Microsoft Boot BCD, sources/boot.wim and boot/boot.sdi. Removable BlockIo media are eligible for this target. The inherited J313 selection stays unchanged. Missing paths and no-complete-volume results are printed instead of silently selecting the known incomplete internal Setup layout.

This is a Setup-specific precondition, not a generic installed-Windows discovery policy or semantic BCD/WIM validator. It does not add exFAT support or guarantee external USB/DART enumeration. A physical FAT32 Setup filesystem is still required. Other independent firmware/Windows launch paths are not globally rewritten by this predicate.

## Windows kernel/driver load text

Microsoft documents [`sos` and `bootlog`](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/bcdedit--set). `sos on` asks Windows to display driver names during boot; `bootlog yes` asks it to record the boot log. These are not a stream of arbitrary kernel printf messages, and do not fix a boot-manager error that precedes kernel entry. Actual display availability on this experimental ARM64 platform remains unverified.

`scripts/windows-boot-details.cmd` defaults to inspecting an explicitly named offline BCD store. An explicit `apply` invocation requires a specific loader identifier and makes a backup before adding these two supported settings. Run it from Windows/WinPE when input and the intended store are accessible. Do not modify macOS or an unrelated system store. It has not been executed here; this macOS run does not contain BCDEdit. Driver text mode may replace Windows' normal spinner/animation.

## Media and built-in input remain separate requirements

The prior internal ESP audit found BCD references to `sources/boot.wim` and `boot/boot.sdi` without those files at the named internal paths. The present photograph is compatible with that defect, but does not identify the chosen volume or BCD object. Current physical SSD data partition is exFAT; a verified FAT32 Setup sparse image was prepared privately but does not itself reconstruct physical installer media. A Windows loader on the small internal ESP is not equivalent to complete reachable Setup media.

J413 built-in input uses DockChannel/RTKit, not the J313 SPI transport. The current firmware/Windows package lacks a linked J413 keyboard/trackpad implementation. Cosmetic changes and `sos` do not add it. USB keyboard/mouse is a separate, untested firmware checkpoint and must use the exposed USB1 path. No universal kext conversion or working M2 input is claimed.
