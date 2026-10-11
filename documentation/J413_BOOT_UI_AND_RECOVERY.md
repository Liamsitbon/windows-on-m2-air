# J413 boot UI and photographed loader recovery

EXP018 operator images show Mu device-state color bars and then the Windows Boot Manager Recovery screen, 0xc000000f, "A required device isn't connected or can't be accessed." The operator reports approximately one minute of lit black panel beforehand. Installed image hash is unknown. This qualifies progress into the Windows boot manager, not WinPE, Windows kernel, GPU acceleration or input drivers. Only built-in keyboard/trackpad were tried; USB input was not tested.

## Current presentation

Both J413 m1n1 stages draw `UEFI BOOT` using the existing font and show named preparation milestones with a bar based on stages reached. They retain the local framebuffer console and flags=1/no-proxy policy. Before DCP switches to the validated guest XRGB32 surface, the surface contains a blue four-pane mark rather than an entirely blank frame. This is firmware branding, not simulated Windows kernel activity.

The J413 Mu provider generates a BMP with the same four-pane mark, using the existing BootGraphicsLib/BootLogo2 path. Existing temperature/low-battery graphics continue through the original FV resource interface. Device-state collection and Secure Boot configuration are preserved; only the J413 color-bar rendering is replaced with text identifying experimental firmware. Mu reports console readiness, storage discovery, EFI loader loading and handoff. The photo's bars came from ColorbarsDxe + ColorBarDisplayDeviceStateLib, not a failing panel test.

This does not replace an Apple-controlled startup-picker icon or pixels displayed before this m1n1 payload executes. It also cannot guarantee a continuously animated screen: early Mu firmware has no GOP console yet, and Windows owns its display after handoff. No unsafe hypervisor overlay writes to a framebuffer concurrently owned by Windows are added. Real physical visibility and timing of the new presentation remain unverified.

## Windows kernel/driver load text

Microsoft documents [`sos` and `bootlog`](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/bcdedit--set). `sos on` asks Windows to display driver names during boot; `bootlog yes` asks it to record the boot log. These are not a stream of arbitrary kernel printf messages, and do not fix a boot-manager error that precedes kernel entry. Actual display availability on this experimental ARM64 platform remains unverified.

`scripts/windows-boot-details.cmd` defaults to inspecting an explicitly named offline BCD store. An explicit `apply` invocation requires a specific loader identifier and makes a backup before adding these two supported settings. Run it from Windows/WinPE when input and the intended store are accessible. Do not modify macOS or an unrelated system store. It has not been executed here; this macOS run does not contain BCDEdit. Driver text mode may replace Windows' normal spinner/animation.

## Media and built-in input remain separate requirements

The prior internal ESP audit found BCD references to `sources/boot.wim` and `boot/boot.sdi` without those files at the named internal paths. The present photograph is compatible with that defect, but does not identify the chosen volume or BCD object. Current physical SSD data partition is exFAT; a verified FAT32 Setup sparse image was prepared privately but does not itself reconstruct physical installer media. A Windows loader on the small internal ESP is not equivalent to complete reachable Setup media.

J413 built-in input uses DockChannel/RTKit, not the J313 SPI transport. The current firmware/Windows package lacks a linked J413 keyboard/trackpad implementation. Cosmetic changes and `sos` do not add it. USB keyboard/mouse is a separate, untested firmware checkpoint and must use the exposed USB1 path. No universal kext conversion or working M2 input is claimed.
