# RTBuddy.kext

Bundle ID: `com.apple.driver.RTBuddy`; version `1.0.0`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **4329**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "RTBuddy",
    "IONameMatch": "iop-nub,rtbuddy-v2",
    "IOProviderClass": "AppleA7IOPNub",
    "name": "RTBuddy"
  },
  {
    "IOClass": "RTBuddy64",
    "IONameMatch": "iop-nub,rtbuddy",
    "IOProviderClass": "AppleA7IOPNub",
    "name": "RTBuddy64"
  },
  {
    "IOClass": "RTBuddyARG",
    "IONameMatch": "iop-nub,rtbuddy-arg",
    "IOProviderClass": "AppleA7IOPNub",
    "name": "RTBuddyARG"
  },
  {
    "IOClass": "RTBuddyRouteOnly",
    "IONameMatch": "iop-nub,rtbuddy-route-only",
    "IOProviderClass": "AppleA7IOPNub",
    "name": "RTBuddyRouteOnly"
  },
  {
    "IOClass": "RTBuddyService",
    "IOProbeScore": 1000,
    "IOProviderClass": "RTBuddy",
    "name": "RTBuddyService"
  }
]
```

## Dependencies

- `com.apple.driver.AppleA7IOP` >= `1.0`
- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.IOSlaveProcessor` >= `1.0.0`
- `com.apple.iokit.CoreAnalyticsFamily` >= `1.0`
- `com.apple.iokit.IOReportFamily` >= `1.0`
- `com.apple.kec.corecrypto` >= `1.0`
- `com.apple.kpi.bsd` >= `8.0`
- `com.apple.kpi.iokit` >= `8.0`
- `com.apple.kpi.libkern` >= `8.0`
- `com.apple.kpi.mach` >= `8.0`
- `com.apple.kpi.private` >= `8.0`
- `com.apple.kpi.unsupported` >= `8.0`

## Windows implementation target

Bounded RTKit mailbox transport with firmware ABI qualification; SEP authentication is optional and unimplemented.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `47232263893cea375537491b5249099fc0a2e6668150a6c4a38914119e295ed2`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
