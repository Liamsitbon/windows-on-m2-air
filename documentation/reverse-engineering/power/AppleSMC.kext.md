# AppleSMC.kext

Bundle ID: `com.apple.driver.AppleSMC`; version `3.1.9`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **1830**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleSMC",
    "IONameMatch": "APP0001",
    "IOProbeScore": 2000,
    "IOProviderClass": "IOACPIPlatformDevice",
    "name": "AppleSMC"
  }
]
```

## Dependencies

- `com.apple.driver.watchdog` >= `1.0.0`
- `com.apple.iokit.IOACPIFamily` >= `1.4`
- `com.apple.kpi.bsd` >= `13.0`
- `com.apple.kpi.iokit` >= `13.0`
- `com.apple.kpi.libkern` >= `13.0`
- `com.apple.kpi.mach` >= `13.0`
- `com.apple.kpi.private` >= `14.0.0`
- `com.apple.kpi.unsupported` >= `8.0.0b2`

## Windows implementation target

Platform ACPI/power integration and bounded SMC/PMGR protocol implementation; thermal limits must be measured.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `a9c1ecf9c5f53ccf43209473835516e4d37c9fb894a3c7059fc11fb350bca8df`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
