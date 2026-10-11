# AppleBCMWLANCoreMac.kext

Bundle ID: `com.apple.driver.AppleBCMWLANCoreMac`; version `1.0.0`.

Executable in bundle: **False**. Entry in this boot collection: **False**. Available symbol names: **0**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleBCMWLANCore",
    "IOProviderClass": "AppleBCMWLANBusInterfacePCIe",
    "name": "AppleBCMWLAN PCIe"
  }
]
```

## Dependencies

- `com.apple.driver.AppleMobileFileIntegrity` >= `1.0.1`
- `com.apple.driver.AppleOLYHALMac` >= `1.0`
- `com.apple.driver.IOImageLoader` >= `1.0`
- `com.apple.driver.corecapture` >= `1.0.0`
- `com.apple.driver.mDNSOffloadUserClient` >= `1.0.0d7`
- `com.apple.iokit.CoreAnalyticsFamily` >= `1.0`
- `com.apple.iokit.IO80211Family` >= `1.5.0`
- `com.apple.iokit.IONetworkingFamily` >= `1.5.0`
- `com.apple.iokit.IOPCIFamily` >= `2.7.3`
- `com.apple.iokit.IOSerialFamily` >= `11.0`
- `com.apple.iokit.IOSkywalkFamily` >= `1.0`
- `com.apple.iokit.IOTimeSyncFamily` >= `500.10`
- `com.apple.kec.corecrypto` >= `1.0`
- `com.apple.kpi.bsd` >= `8.0.0`
- `com.apple.kpi.iokit` >= `8.0.0`
- `com.apple.kpi.libkern` >= `8.0.0`
- `com.apple.kpi.mach` >= `8.0.0`
- `com.apple.kpi.private` >= `8.0.0`
- `com.apple.kpi.unsupported` >= `8.0.0`

## Windows implementation target

NDIS or NetAdapterCx network implementation plus PCIe/firmware/power protocol.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `be7462b1387a54512923db3b56969b2db3ebf0edf1df789fa86bde173b484fb1`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
