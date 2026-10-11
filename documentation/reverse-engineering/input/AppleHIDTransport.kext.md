# AppleHIDTransport.kext

Bundle ID: `com.apple.driver.AppleHIDTransport`; version `1000.41`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **3625**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleHIDTransportDeviceDummy",
    "IONameMatch": [
      "hid-transport,dummy"
    ],
    "IOProviderClass": "IOPlatformDevice",
    "name": "AppleHIDTransportDeviceDummy"
  },
  {
    "IOClass": "AppleHIDTransportHIDDevice",
    "IOPropertyMatch": {
      "InterfaceType": "HID"
    },
    "IOProviderClass": "AppleHIDTransportInterface",
    "name": "AppleHIDTransportHIDDevice"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleInputDeviceSupport` >= `1.0`
- `com.apple.driver.AppleSMC` >= `1.0`
- `com.apple.driver.AppleSPU` >= `1.0`
- `com.apple.iokit.IOHIDFamily` >= `1.4`
- `com.apple.kpi.bsd` >= `11.0`
- `com.apple.kpi.iokit` >= `11.0`
- `com.apple.kpi.libkern` >= `11.0`
- `com.apple.kpi.mach` >= `11.0`
- `com.apple.kpi.private` >= `11.0`

## Windows implementation target

KMDF DockChannel/RTKit transport plus VHF keyboard and Precision Touchpad HID reports; no J313 SPI reuse.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `eb25b58a24651f0a9b3afe8a55259470cf2245bb275a0b19c68301902a287b3e`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
