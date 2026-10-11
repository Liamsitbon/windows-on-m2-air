# AppleMultitouchDriver.kext

Bundle ID: `com.apple.driver.AppleMultitouchDriver`; version `1000.44`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **1414**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleMultitouchHIDService",
    "IOProviderClass": "IOHIDInterface",
    "name": "AppleMultitouchHIDService (0x0D,0x04)"
  },
  {
    "IOClass": "AppleMultitouchHIDService",
    "IOProviderClass": "IOHIDInterface",
    "name": "MTUserDevice"
  }
]
```

## Dependencies

- `com.apple.driver.AppleInputDeviceSupport` >= `1.0`
- `com.apple.iokit.IOHIDFamily` >= `1.4`
- `com.apple.iokit.IOReportFamily` >= `1.0`
- `com.apple.kpi.bsd` >= `9.0.0`
- `com.apple.kpi.iokit` >= `9.0.0`
- `com.apple.kpi.libkern` >= `9.0.0`
- `com.apple.kpi.mach` >= `9.0.0`
- `com.apple.kpi.private` >= `12.0.0`
- `com.apple.kpi.unsupported` >= `8.0`

## Windows implementation target

KMDF DockChannel/RTKit transport plus VHF keyboard and Precision Touchpad HID reports; no J313 SPI reuse.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `21023495db4dfa2457e7c17972ad8540cd1d3203f8d9ec287be384e9b27769c2`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
