# AppleHIDTransportFIFO.kext

Bundle ID: `com.apple.driver.AppleHIDTransportFIFO`; version `1000.41`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **888**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleHIDTransportDeviceFIFO",
    "IONameMatch": [
      "hid-transport,dc"
    ],
    "IOProviderClass": "AppleDockChannelDevice",
    "name": "AppleHIDTransportDeviceFIFO"
  },
  {
    "IOClass": "AppleHIDTransportHibernator",
    "IONameMatch": [
      "aht-hibernator"
    ],
    "IOProviderClass": "IOService",
    "name": "AppleHIDTransportHibernator"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleDockChannel` >= `1.0`
- `com.apple.driver.AppleHIDTransport` >= `1.0`
- `com.apple.driver.AppleHIDTransportSCMCommon` >= `1.0`
- `com.apple.driver.AppleInputDeviceSupport` >= `1.0`
- `com.apple.driver.IOSlaveProcessor` >= `1.0.0`
- `com.apple.driver.RTBuddy` >= `1.0.0`
- `com.apple.kpi.bsd` >= `8.0`
- `com.apple.kpi.iokit` >= `8.0`
- `com.apple.kpi.libkern` >= `8.0`
- `com.apple.kpi.mach` >= `8.0`
- `com.apple.kpi.private` >= `8.0`

## Windows implementation target

KMDF DockChannel/RTKit transport plus VHF keyboard and Precision Touchpad HID reports; no J313 SPI reuse.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `fcd2023df795b78dafa25edc0955258f402522fc626a35e651328fa52e8c1e65`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
