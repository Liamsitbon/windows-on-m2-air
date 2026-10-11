# AppleDCPDPDisplayProxy.kext

Bundle ID: `com.apple.driver.AppleDCPDPDisplayProxy`; version `1`.

Executable in bundle: **False**. Entry in this boot collection: **False**. Available symbol names: **0**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleDCPDPDisplayProxy",
    "IOProbeScore": 100000,
    "IOPropertyMatch": {
      "EPICLocation": "Embedded",
      "EPICName": "dcpav-service-epic"
    },
    "IOProviderClass": "AFKEndpointInterface",
    "name": "AppleDCPDPDisplayProxy"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.2`
- `com.apple.driver.AppleSMC` >= `1.0`
- `com.apple.driver.DCPAVFamilyProxy` >= `1.0`
- `com.apple.iokit.IOAVFamily` >= `1.0`
- `com.apple.kpi.iokit` >= `20.4`
- `com.apple.kpi.libkern` >= `20.4`

## Windows implementation target

DCP firmware protocol plus WDDM VidPn/present/scanout ownership; rendering and scanout require separate qualification.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `f9a46c8c6292d4fc244af912ded04051046fb038f0ae8f43d725f435aa12f88f`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
