# AppleHIDTransportSCMCommon.kext

Bundle ID: `com.apple.driver.AppleHIDTransportSCMCommon`; version `1000.41`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **591**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[]
```

## Dependencies

- `com.apple.driver.AppleA7IOP` >= `1.0.0`
- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleHIDTransport` >= `1.0`
- `com.apple.driver.AppleInputDeviceSupport` >= `1.0`
- `com.apple.driver.IOSlaveProcessor` >= `1.0.0`
- `com.apple.driver.RTBuddy` >= `1.0.0`
- `com.apple.kpi.bsd` >= `14.0`
- `com.apple.kpi.iokit` >= `14.0`
- `com.apple.kpi.libkern` >= `14.0`
- `com.apple.kpi.mach` >= `14.0`
- `com.apple.kpi.private` >= `22.0`

## Windows implementation target

KMDF DockChannel/RTKit transport plus VHF keyboard and Precision Touchpad HID reports; no J313 SPI reuse.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `474062c6b4c5c4766bceab5225be51c946b1fff15cb3c903a7501ac2ff71128b`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
