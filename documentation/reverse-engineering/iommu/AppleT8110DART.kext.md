# AppleT8110DART.kext

Bundle ID: `com.apple.driver.AppleT8110DART`; version `1`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **554**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleT8110DART",
    "IONameMatch": "dart,t8110",
    "IOProviderClass": "AppleARMIODevice",
    "name": "AppleT8110DART"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.IODARTFamily` >= `1.0.0`
- `com.apple.kpi.bsd` >= `8.4.1`
- `com.apple.kpi.iokit` >= `8.4.1`
- `com.apple.kpi.libkern` >= `8.4.1`
- `com.apple.kpi.mach` >= `8.4.1`
- `com.apple.kpi.private` >= `8.0`
- `com.apple.kpi.unsupported` >= `8.0`

## Windows implementation target

m1n1/platform DART ownership and explicit Windows DMA address translation; IOMapper is not a Windows API.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `f5d13d2c19e8206c4ee1cb679d76cbf601ff870942013b0d553a74ba42420f6d`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
