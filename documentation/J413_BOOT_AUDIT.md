# J413 boot-path audit — 2026-10-11

The operator photo (EXP014) shows PRE_HV_INIT PASS and cpufreq PASS, then
`live boot data does not fit fixed Mu slots`, stage=3/error=2. Mu has not been
entered. Its shared failure message did not print sizes and also covered
missing/malformed properties; the precise rejected dimension is unknown.
The image visibly used flags=1 and stopped with proxy disabled. The installed
SHA and duration were not provided; the source/hash match cannot be asserted
from a photo alone. Original photo SHA:
`eb307a72f19d32a338f2d6b82990beca9ce27d7d6d6b933336c8ea3b5077b8ef`.

EXP017 subsequently shows placement passing with ADT=0x5c000, TC=0x58000, SEP=0x5dc000 and log=0x40000, then source region 2 rejected. That region is the framebuffer at 0xbe18b0000, above usable-end 0xbde568000 but within full physical DRAM. The earlier source guard incorrectly equated usable allocation memory with readable DRAM. Photo SHA: `272dcad3f72961191f96bef9c6960017525eb6ca8c694bbe4a936195705d17b5`.

## Confirmed defects and corrections

| Layer | Confirmed source defect | Correction and executable evidence |
|---|---|---|
| m1n1 source bounds | Framebuffer carveout incorrectly rejected above usable-end | Use ram_base + mem_size_actual, as the pinned MMU does; retain overflow, guest-overlap and actual MCC TZ exclusions. Execute the production validator under ASan/UBSan against the exact photographed framebuffer and negative cases. Guest allocation cap stays unchanged. |
| m1n1 placement | TC must fit a <0xb4000 gap; SEP/log must fit a 0x534000 gap even when later guest RAM is available | Keep fixed ADT/FD/BA pointers; pack auxiliary data after BA below 0x85e000000. Sanitized tests use independent oversized TC/SEP values, exact-end and overflow cases. EXP017 photo supplies all dimensions and confirms the new placement passes. |
| m1n1 failure reporting | Missing/malformed properties and arena rejection share the same size-error message | Separate property failures; print live sizes, full FD reservation, destination pointers and arena limit before copying. |
| Mu PEI memory | Boot ADT/BA/TC/SEP/log have no reserved HOBs and can be allocated over | Reserve [ADT,FD) and [FD+PcdFdSize,top_of_kernel_data); actual reservation function tested with realistic split HOBs and uncovered/overflow cases. Bounds are checked and failure returns EFI error. |
| Mu PrePi stack | Clear cursor compared with size instead of end; base depends on cursor hack; caller-saved size used across cache calls | J413 alone clears [base,end), preserves base/size in x23/x24, drops -0x40 adjustment. Actual assembly runs natively in ARM64 build container with guard pages and cache clobber stubs; all 128 KB clear and arguments match. |
| Mu build | ASM_FLAGS does not reach preprocessing, silently leaving legacy stack code | Set PP_FLAGS; verify generated .ii instructions and linked Sec HOB strings before output publication. Native assembly regression uses Mu Clang (GCC rejects the inherited vector-move syntax). |
| Build provenance | J413_SKIP_MU verifies bytes but can reuse firmware built from obsolete overlay source; upstream corrections omitted from digest | Include checked Mu patches in the overlay digest and require equality to current source before packing. Regression rejects changed patch content. |
| PSCI bookkeeping | Uninitialized previous-parent array; coordinator always uses the first node's sibling count | Initialize traversal arrays and index the selected parent. Execute real functions with poisoned automatic variables and sanitizers: cluster counts 4/4, system 8, coordinator sees 4 then 8. |

Root owns all corrections as additive files or patches against exact pinned
m1n1 9cd80ac652ac404e92ae279deeaec8c629d7d184 and Mu
8b4dc4b4e3ff8606d0af36163acf9de79b7b4737. Clean-clone patch application,
reverse checks and byte comparison match the actual compiled sources. No Gemini
checkout changes, guessed registers/IRQs, or Apple/Windows binaries are published.
Mu patches preserve the original BSD-2-Clause-Patent notices; m1n1 patches target
the pinned MIT baseline. ARM Trusted Firmware BSD-3-Clause sources were inspected
as references; no external implementation was copied.

Primary references: [PI HOB definitions](https://uefi.org/specs/PI/1.9/V3_HOB_Code_Definitions.html),
[ARM PSCI setup](https://github.com/ARM-software/arm-trusted-firmware/blob/master/lib/psci/psci_setup.c),
[ARM PSCI coordination](https://github.com/ARM-software/arm-trusted-firmware/blob/master/lib/psci/psci_common.c).
Local primary sources: pinned Asahi hv/load_raw and T8112/J413 DTS; m1n1
hv_autonomous_runtime, heapblock, hv_guest_cpu_state, hv_psci, hv_vgic, kboot and
mcc; Mu ModuleEntryPoint, AdtParser, PrePi, MemoryInitPeiLib, ArmLib cache assembly,
J413 PCD/FDF and ACPI. This is a targeted source audit, not proof of all hardware.

## Remaining qualification gates

| Area inspected | Evidence and next falsifiable checkpoint |
|---|---|
| Host/guest memory and protected regions | Source buffers, DCP carveouts and bounded host heap checked before copies. Photo's guest end lies below observed MCC/TZ high-DRAM regions. Other carveout-map entries include normal DRAM; blanket unmapping would be incorrect. The source guard and full visible placement replay pass in software. Fresh read-only macOS capture checks all eight CPU register-property containers, eleven arm-io ranges and seven protected/DCP regions. See [sanitized source audit](../investigation/j413-source-memory-audit.json); it does not execute RVBAR writes or EL2 mappings. |
| No-proxy policy | Both nested flags=1; previous source/native boundary tests and photographed halt agree. Normal guest IRQ/timer handling remains. |
| CPU/vGIC/PSCI | Target and topology gates passed before the photo's stop. Collection still uses a boot-CPU template for secondaries; CPU_ON and Windows timer progress have no runtime evidence. The generic PSCI unsupported-chip default remains outside this target's preflight gate. |
| Display | macOS physical framebuffer was alive; source checks the guest surface contract. Mu GOP handoff and accelerated Windows output still require real testing. |
| External SSD/xHCI/DART | Guest exposes physical USB1 IRQ 1112 as 857. SSD was observed on USB0; switch to the other port for the firmware storage checkpoint. Port change alone does not prove DMA correctness. |
| Installer media | Private ARM64 Setup files and verified FAT32 sparse image exist. Physical exFAT media has not been reconstructed; its destructive repartition remains pending separate approval. |
| GPU/HID/audio/Wi-Fi/SEP | Protocol investigation and portable cores are not WDDM/KMDF drivers. A kext is not automatically convertible into a working Windows driver; no GPU or built-in-input support is claimed. |

## Candidate and operator checkpoint

Current candidate: `dist/j413/boot-experiment/boot.bin`, 2518496 bytes, SHA
`537dda804f96abbf89e738eb3adeb79dca19e4958c1fc172dcb5ff95a93dce2f`.
The independent EXP014 placement/HOB, EXP015 stack, and EXP016 bookkeeping fixes
were combined in the preceding image. EXP017 changes only the source-range guard on that baseline; a hardware outcome alone cannot isolate one variable.
Previous no-proxy candidate and original ESP/staging-kernel recovery copies are
preserved privately. This run changes no ESP, boot policy, partitions or installer.

Use the existing install-esp script from the clean root. Its validation, scoped
backup and atomic replacement remain unchanged:

```sh
sudo ./scripts/install-esp.sh install --disk disk0s4 --image dist/j413/boot-experiment/boot.bin
```

Next expected text: `J413 SOURCES` physical DRAM/usable-end, then later
preflight/guest entry or a specific `J413 STOP`. Capture the last lines or visible
Mu screen. A successful build is not successful Windows boot. Returning to macOS
uses the power-button startup picker; the script's restore command restores its
scoped ESP backup. No raw partition restore is proposed.

## Upstream qualification

See [primary-source comparison](J413_UPSTREAM_COMPARISON.md). The original verified Windows desktop is J313 M1 via assisted launch; neither that record nor this software replay qualifies autonomous J413 Windows boot.

EXP018 photographs Windows Boot Manager Recovery (0xc000000f) with the preceding candidate; exact installed hash was not supplied. The current candidate additionally changes J413 boot presentation only. See [boot UI and recovery limits](J413_BOOT_UI_AND_RECOVERY.md). It has not been physically launched.

EXP019/020 current candidate is text-only: no Windows-like mark or bar. Pre-GOP firmware UART lines use the guest surface, then stop at explicit GOP takeover; invisible host framebuffer logging is disabled. Automatic J413 Setup selection requires all four payload paths and permits removable BlockIo. External FAT32/DMA and built-in input remain unqualified; see the current [UI and media notes](J413_BOOT_UI_AND_RECOVERY.md).
