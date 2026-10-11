# AGXG14G.kext

Bundle ID: `com.apple.AGXG14G`; version `360.34.5`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **5354**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AGXArmFirmwareMapper",
    "IONameMatch": "iommu-mapper,gfx",
    "IOProviderClass": "AppleARMIODevice",
    "name": "AGXArmFirmwareMapper"
  },
  {
    "IOClass": "AGXAcceleratorG14G",
    "IONameMatch": [
      "gpu,t8015",
      "gpu,t8027",
      "gpu,t8030",
      "gpu,t8103",
      "gpu,t8110",
      "gpu,t8112"
    ],
    "IOProviderClass": "AppleARMIODevice",
    "name": "AGXG14G"
  },
  {
    "IOClass": "AGXAcceleratorG14G_A0",
    "IONameMatch": [
      "gpu,t8132",
      "gpu,t8015",
      "gpu,t8027",
      "gpu,t8030",
      "gpu,t8103",
      "gpu,t8110",
      "gpu,t8112"
    ],
    "IOProviderClass": "AppleARMIODevice",
    "name": "AGXG14G_A0"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleMobileFileIntegrity` >= `1.0.1`
- `com.apple.driver.RTBuddy` >= `1.0.0`
- `com.apple.iokit.CoreAnalyticsFamily` >= `1.0`
- `com.apple.iokit.IOGPUFamily` >= `2.0.0`
- `com.apple.iokit.IOReportFamily` >= `1.0`
- `com.apple.iokit.IOSurface` >= `52.6.0`
- `com.apple.kec.Libm` >= `1.0.0`
- `com.apple.kpi.bsd` >= `8.0`
- `com.apple.kpi.iokit` >= `8.0`
- `com.apple.kpi.libkern` >= `8.0`
- `com.apple.kpi.mach` >= `8.0`
- `com.apple.kpi.private` >= `8.0`
- `com.apple.kpi.unsupported` >= `8.0`

## Windows implementation target

WDDM kernel display miniport plus Direct3D user-mode driver; GPU VA, queues, fences, TDR and residency must be reimplemented.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `8748c2970a20ae9620828bbf9d57f36e69daca0665955429df38b48bf83a6ed5`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
