# J413 preboot corrections

## Image-service execution level

The prior WindowsAutoBootDxe installed filesystem and ReadyToBoot notifications at TPL_CALLBACK, then called LoadImage and StartImage inside them. The [UEFI service execution-level table](https://uefi.org/specs/UEFI/2.10/07_Services_Boot_Services.html) requires both services strictly below TPL_CALLBACK. This is a source-confirmed contract violation; it is not proven to cause the photographed Recovery or Shell result.

J413 now publishes `J413WindowsSetup` with a GetOption method. DeviceBootManagerPriorityBoot invokes it from the ordinary BDS application context when no explicit settings/alternate boot request is selected. It connects controllers, examines complete readable filesystems and creates an ephemeral Windows Setup load option. Mu's existing PlatformBootManagerPriorityBoot and UefiBootManagerBoot execute the option with standard ReadyToBoot/image/security handling. No callback lowers its TPL, launches Windows, or writes BootOrder. Legacy non-J413 code remains conditional.

Successful option selection is attempted once per boot; a returned loader is handled by standard BDS. Allocation and initialization failures release temporary paths/handle arrays. ASan/UBSan tests execute the actual selection function with absent media, missing protocol interfaces, incomplete media, allocation failures and repeated calls. Native build must separately confirm the J413 conditional branch.

## Exact installer image identity

The previous installer validated the neighboring manifest but did not require the requested image to be a recorded standalone-bootstrap artifact. A separately named image could pass nested CRC checks while an unrelated manifest passed its checks.

`tools/verify_install_image.py` now requires exact artifact membership and role, rereads and checks SHA/size of the requested image, and compares both nested launch flags with the manifest display/debug profile before the installer mounts the target. This is local provenance verification, not publisher authenticity or physical hardware qualification. Regressions cover wrong membership, image replacement after manifest checking, and matching nested flags with the wrong manifest profile.

## Offline dependency preparation

EfiFs license and README were redownloaded for every firmware build even with a cached verified driver. Notices are now SHA-pinned and reused when present. The driver, notices and generated DXE dependency are published only after all dependency checks succeed. Missing dependencies still require network access; modified cached dependencies fail. Tests confirm cached builds perform no network requests and invalid notices do not publish the driver/dependency.

## Read-only Setup preflight

Run `python3 tools/check_j413_setup.py '/Volumes/Untitled 2'` before a hardware attempt. It checks that all four required files can be opened, the loader is an ARM64 PE32+ EFI application, BCD has a registry hive header, WIM has a bounded declared header, and SDI has its expected header. It rejects absent, empty, directory and wrong-architecture inputs. These checks are deliberately limited: they do not validate BCD paths, WIM payload/WinPE architecture, signatures, USB enumeration, DART handoff or successful Windows startup.

The current SanDisk passes these header checks. Its previously observed USB0 connection must still move to USB1. Built-in and Xbox input, Windows kernel and Setup remain unqualified. See EXP-20261011-J413-024 for exact artifact/build results.
