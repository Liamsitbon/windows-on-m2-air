# RTBuddyV3.kext

Bundle ID: `com.apple.driver.RTBuddyV3`; version `1.0.0`.

Executable in bundle: **False**. Entry in this boot collection: **False**. Available symbol names: **0**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "RTBuddyV3",
    "IOProviderClass": "AppleRemoteIOP",
    "name": "RTBuddyV3"
  }
]
```

## Dependencies

- `com.apple.driver.AppleA7IOP` >= `1.0`
- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleRemoteIOP` >= `1.0`
- `com.apple.driver.IOSlaveProcessor` >= `1.0.0`
- `com.apple.driver.RTBuddy` >= `1.0`
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

Metadata SHA-256: `eff1325aaec80c0d403a6cb9e4241000731bbfede384c1d692a28f29d53c2b9c`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
