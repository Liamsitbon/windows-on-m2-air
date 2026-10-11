# AGXFirmwareKextG14GRTBuddy.kext

Bundle ID: `com.apple.AGXFirmwareKextG14GRTBuddy`; version `1`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **434**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AGXFirmwareKextG14RTBuddy",
    "IOPropertyMatch": {
      "role": "GFX"
    },
    "IOProviderClass": "RTBuddyService",
    "name": "Firmware"
  }
]
```

## Dependencies

- `com.apple.AGXFirmwareKextRTBuddy64` >= `1.0`
- `com.apple.driver.RTBuddy` >= `1.0.0`
- `com.apple.kpi.bsd` >= `8.0`
- `com.apple.kpi.iokit` >= `8.0`
- `com.apple.kpi.libkern` >= `8.0`
- `com.apple.kpi.mach` >= `8.0`

## Windows implementation target

WDDM kernel display miniport plus Direct3D user-mode driver; GPU VA, queues, fences, TDR and residency must be reimplemented.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `aaddaf69647fc6b99391f29a8376d9b8476cc65747121862d5a59e9069a2aca0`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
