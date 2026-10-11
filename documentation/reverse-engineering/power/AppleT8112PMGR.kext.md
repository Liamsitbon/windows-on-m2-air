# AppleT8112PMGR.kext

Bundle ID: `com.apple.driver.AppleT8112PMGR`; version `1`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **3177**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleT8112PMGR",
    "IONameMatch": "pmgr1,t8112",
    "IOProviderClass": "AppleARMIODevice",
    "name": "AppleT8112PMGR"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.ApplePMGR` >= `1.0`
- `com.apple.kec.Libm` >= `1.0.0`
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

Metadata SHA-256: `141e48dd33d6292935f2a68a8c8abf5ddce845d99178c65f5c37faa51d338671`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
