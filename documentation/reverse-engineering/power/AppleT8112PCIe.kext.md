# AppleT8112PCIe.kext

Bundle ID: `com.apple.driver.AppleT8112PCIe`; version `1`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **862**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "ApplePCIEHostBridge",
    "IONameMatch": "apcie-bridge",
    "IOProbeScore": 5000,
    "IOProviderClass": "IOPCIDevice",
    "name": "ApplePCIEHostBridge"
  },
  {
    "IOClass": "AppleT8112PCIe",
    "IONameMatch": "apcie,t8112",
    "IOProviderClass": "AppleARMIODevice",
    "name": "AppleT8112PCIe"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleEmbeddedPCIE` >= `1.0.0`
- `com.apple.iokit.IOPCIFamily` >= `2.7`
- `com.apple.iokit.IOReportFamily` >= `1.0`
- `com.apple.kpi.bsd` >= `8.0`
- `com.apple.kpi.iokit` >= `8.0`
- `com.apple.kpi.libkern` >= `8.0`
- `com.apple.kpi.mach` >= `8.0`
- `com.apple.kpi.private` >= `8.0`
- `com.apple.kpi.unsupported` >= `8.0`

## Windows implementation target

Platform ACPI/power integration and bounded SMC/PMGR protocol implementation; thermal limits must be measured.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `7ebda35a3efd09ee89a160167499d4f386c9bd9c8355a127c4fcab4fc7ff3495`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
