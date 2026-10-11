# AppleDockChannel.kext

Bundle ID: `com.apple.driver.AppleDockChannel`; version `1`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **472**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleDockChannel",
    "IONameMatch": "dockchannel,t8002",
    "IOProviderClass": "AppleARMIODevice",
    "name": "AppleDockChannel"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.kpi.bsd` >= `8.0`
- `com.apple.kpi.iokit` >= `8.0`
- `com.apple.kpi.libkern` >= `8.0`
- `com.apple.kpi.mach` >= `8.0`
- `com.apple.kpi.private` >= `8.0`
- `com.apple.kpi.unsupported` >= `8.0`

## Windows implementation target

KMDF DockChannel/RTKit transport plus VHF keyboard and Precision Touchpad HID reports; no J313 SPI reuse.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `01eff2b5d4fb65acd25db4def7037d7b8908698915fee085cafa2df4dc1ccd71`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
