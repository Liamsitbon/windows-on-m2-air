# J413 / MacBook Air M2: local kext research

This is an inventory and the start of protocol analysis of this Mac14,2/T8112
machine, captured on macOS 27.0 build 26A5425a. It is not a collection of working
Windows drivers. The clean fork is the implementation base; none of Gemini's
changes or captures were imported.

27 bundles are grouped by hardware function. [inventory.json](inventory.json)
records bundle IDs, metadata hashes, IOKit matching, dependencies, presence in the
boot kernel collection and symbol counts. A packaged entry does not prove that
its service attached. A symbol name does not prove that its protocol was decoded.

| Directory | Hardware / next Windows interface |
| --- | --- |
| [gpu](gpu/AGXG14G.kext.md) | G14G firmware, UAT and queues; WDDM kernel miniport plus Direct3D user-mode driver |
| [display](display/AppleDCP.kext.md) | DCP scanout firmware; WDDM present and VidPn |
| [input](input/AppleDockChannel.kext.md) | DockChannel, RTKit and HID FIFO; KMDF transport and VHF HID devices |
| [iommu](iommu/AppleT8110DART.kext.md) | DART address translation; platform/hypervisor DMA ownership |
| [power](power/AppleT8112PMGR.kext.md) | PMGR, SMC, clocks and thermal recovery |
| [audio](audio/AppleAOPAudio.kext.md) | AOP, codecs and measured speaker protection; Windows audio framework |
| [network](network/AppleBCMWLANCoreMac.kext.md) | WLAN firmware and PCIe; NDIS/NetAdapterCx |
| [coprocessors](coprocessors/RTBuddy.kext.md) | RTKit mailbox transport; SEP/Touch ID optional |
| [storage](storage/IONVMeFamily.kext.md) | ANS/NVMe; preserve the existing bridge before a native miniport |

## Local binary copies

The ignored `.local/kext-research/` directory contains `bundles/<group>/`, the
active kernelcache copy, emitted `BootKernelCollection.kc`, per-ID
`analysis/<bundle-id>/symbols.json` and `snapshot-hashes.json`. Apple binaries and
complete symbol tables are retained locally, outside the public Git repository.
Most bundles here have no standalone executable: their executable is embedded in
the boot kernel collection. `AGXMetalG14G.bundle` has no executable in this copy
and is absent from the boot collection; its user-mode implementation has not
been extracted or analyzed.

The native `kmutil inspect --show-fileset-entries -M -z` indexed the active
collection. `kmutil emit-macho` emitted the boot Mach-O successfully, then exited
71 because the separately supplied system/auxiliary collection paths were
absent. Only the emitted boot collection was used, not an assumed successful
three-collection export. Its SHA-256 is:

`e9ae6b36085aed3622dc0f80d71154164ef5ee9d19ab53c0ea5d73f62c8f0d59`

The parser uses Apple's `mach-o/loader.h` and `mach-o/nlist.h` layouts, validates
command/table bounds, resolves LC_FILESET_ENTRY bundle IDs and reads embedded
LC_SYMTAB entries with collection-relative file offsets. It does not execute
Apple code, infer missing executables, or produce a `.sys`.

```sh
python3 tools/analyze_kext.py --target-j413 \
  --kernel-macho .local/kext-research/BootKernelCollection.kc
# Repeat only when existing snapshots remain byte-identical:
python3 tools/analyze_kext.py --target-j413 --resume \
  --kernel-macho .local/kext-research/BootKernelCollection.kc
```

A supplied bundle can be inventoried with `--bundle /path/Example.kext`.
The extractor receives an already unwrapped Mach-O, not an IMG4 container.
Public reports include metadata and conclusions; complete disassembly remains
local. [DockChannel findings](DOCKCHANNEL.md) distinguish instruction-level
observations from hypotheses and explain the portable FIFO implementation.

## Porting boundary and ownership

A macOS kext links against IOKit/libkern, uses Apple object lifetimes and firmware
ABIs, and on this machine uses ARM64e pointer authentication. A Windows kernel
driver uses Windows ARM64 calling conventions, WDK device/power/DMA APIs and a
supported driver model. Renaming or translating machine instructions cannot
supply those contracts. This tool automates discovery and organization; a
functional port must reimplement the hardware protocol and Windows integration.

The platform/m1n1 layer owns physical MMIO visibility, interrupts, stage-2
mapping and DART assignment. Mu/ACPI describes only resources established by
that launch contract. A future KMDF transport owns serialization, powered access,
interrupt handling, bounded waits, cancellation and recovery. VHF consumes
verified HID reports. GPU work separately needs firmware-compatible G14G queues,
address spaces, synchronization, residency, a WDDM KMD and a matching UMD.

Primary interface references: [Microsoft WDDM architecture](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/windows-vista-and-later-display-driver-model-architecture),
[Virtual HID Framework](https://learn.microsoft.com/en-us/windows-hardware/drivers/hid/virtual-hid-framework--vhf-),
[NDIS miniports](https://learn.microsoft.com/en-us/windows-hardware/drivers/network/ndis-miniport-drivers2),
[Storport](https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/storport-driver).

Next hardware checkpoint: qualify a reversible J413 firmware launch with an
observable log/recovery path before enabling DMA or writing new hardware
registers. Only this Air is available, so external-host assisted procedures from
the M1 documentation are not a usable recovery path yet. No installation,
partition changes, Windows boot or GPU execution were performed in this work.
