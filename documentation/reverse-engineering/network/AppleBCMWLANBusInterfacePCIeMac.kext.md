# AppleBCMWLANBusInterfacePCIeMac.kext

Bundle ID: `com.apple.driver.AppleBCMWLANBusInterfacePCIeMac`; version `1`.

Executable in bundle: **False**. Entry in this boot collection: **False**. Available symbol names: **0**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleBCMWLANBusInterfacePCIe",
    "IONameMatch": [
      "pci14e4,4425"
    ],
    "IOProviderClass": "IOPCIDevice",
    "name": "80211PCI"
  },
  {
    "IOClass": "AppleBCMWLANBusInterfacePCIe",
    "IONameMatch": "APP00DA",
    "IOProviderClass": "IOACPIPlatformDevice",
    "name": "80211PCI-AMFM"
  }
]
```

## Dependencies

- `com.apple.driver.AppleBCMWLANCoreMac` >= `1.0.0`
- `com.apple.driver.AppleOLYHALMac` >= `1.0`
- `com.apple.driver.IOImageLoader` >= `1.0`
- `com.apple.driver.corecapture` >= `1.0.0`
- `com.apple.iokit.CoreAnalyticsFamily` >= `1.0`
- `com.apple.iokit.IO80211Family` >= `1.5.0`
- `com.apple.iokit.IONetworkingFamily` >= `1.5.0`
- `com.apple.iokit.IOPCIFamily` >= `1.0.0`
- `com.apple.iokit.IOSkywalkFamily` >= `1.0`
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

Metadata SHA-256: `84553c3882ac619fc4ee7d46976eab832ac2c3b8170443cb58f0b7e8e3ced0bc`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
