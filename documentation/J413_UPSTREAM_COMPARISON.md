# Primary-source boot comparison — 2026-10-11

[Original fork README](https://github.com/paulsmir/windows-on-m1) and [stable eight-core/input checkpoint](https://github.com/paulsmir/windows-on-m1/blob/main/documentation/STABLE_8CORE_INPUT.md) document J313 M1 Windows desktop, eight cores, NVMe/USB and SPI HID using an assisted launch. The checkpoint explicitly requires another Mac/proxy and matching firmware/loader. Its standalone cold-boot contract remains separately unqualified; only J313 is supported. Its pinned source revisions match this project's baseline, not a hardware qualification for J413.

The README describes GPU work on a separate J313 branch: observed desktop rendering remains slow and does not establish a usable M2 WDDM driver. An existing Asahi UEFI boot entry on this Air proves an Apple-authorized loader path, not this Mu/hypervisor/Windows chain.

[NT-for-ASi m1n1 fork](https://github.com/NT-for-ASi/m1n1_windows) is the upstream Windows-oriented implementation. [Deprecated project site](https://github.com/amarioguy/NTASPProjectSiteDeprecated/blob/gh-pages/index.md) points to NT-for-ASi; its obsolete pointers are not independent boot evidence. No reproducible autonomous J413 Windows result was found in these searched primary sources. This is a scoped research result, not proof that none exists anywhere.

[Asahi m1n1 memory implementation](https://github.com/AsahiLinux/m1n1/blob/main/src/memory.c) separates physical RAM identity mapping from allocatable memory. The local pinned memory.c maps ram_base through mem_size_actual and mcc.c removes protected TZ ranges. EXP017 corrects the source-read guard to that existing contract, keeps the guest allocation cap, and rejects overlap with MCC protected ranges. No upstream code was copied; exact hardware values come from the operator photo and a private read-only macOS capture.

Remaining physical checkpoints: boot-time source copies, RVBAR/stage-2 setup, Mu entry, external USB storage, Windows loader/timer/CPU progress, and device drivers. Software tests qualify the guarded arithmetic and image composition only.
