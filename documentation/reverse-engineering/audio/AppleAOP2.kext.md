# AppleAOP2.kext

Bundle ID: `com.apple.driver.AppleAOP2`; version `1.0`.

Executable in bundle: **False**. Entry in this boot collection: **False**. Available symbol names: **0**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleAOP2KextTightbeamEndpoint",
    "IONameMatch": [
      "aop2.system-iopm-aop2.system-iopm.ap.client-rev"
    ],
    "IOProviderClass": "AFKEndpointInterface",
    "name": "AOP2AFKTightbeamEndpoints"
  },
  {
    "IOClass": "AFKEPKextV2",
    "IONameMatch": [
      "AOP2Endpoint1",
      "AOP2Endpoint2",
      "AOP2Endpoint3",
      "AOP2Endpoint4",
      "AOP2Endpoint5",
      "AOP2Endpoint6",
      "AOP2Endpoint7",
      "AOP2Endpoint8",
      "AOP2Endpoint9",
      "AOP2Endpoint10",
      "AOP2Endpoint11",
      "AOP2Endpoint12",
      "AOP2Endpoint13",
      "AOP2Endpoint14",
      "AOP2Endpoint15",
      "AOP2Endpoint16",
      "AOP2Endpoint17",
      "AOP2Endpoint18",
      "AOP2Endpoint19",
      "AOP2Endpoint20",
      "AOP2Endpoint21",
      "AOP2Endpoint22",
      "AOP2Endpoint23",
      "AOP2Endpoint24"
    ],
    "IOProviderClass": "RTBuddyEndpointService",
    "name": "AOP2Endpoints"
  },
  {
    "IOClass": "AFKFirmwareService",
    "IOPropertyMatch": {
      "role": "AOP2"
    },
    "IOProviderClass": "RTBuddyService",
    "name": "AOP2FirmwareService"
  },
  {
    "IOClass": "AppleAOP2IOPMService",
    "IONameMatch": [
      "aop2.system-iopm-aop2.system-iopm.ap.client-rev"
    ],
    "IOProviderClass": "AppleAOP2KextTightbeamEndpoint",
    "name": "AppleAOP2IOPMService"
  },
  {
    "IOClass": "AppleAOP2SystemDriver",
    "IONameMatch": [
      "system-manager"
    ],
    "IOProviderClass": "AFKMailboxEndpointInterface",
    "name": "AppleAOP2SystemDriver"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleFirmwareKit` >= `1.0.0`
- `com.apple.driver.RTBuddy` >= `1.0.0`
- `com.apple.kpi.iokit` >= `14.0`
- `com.apple.kpi.libkern` >= `14.0`

## Windows implementation target

Windows audio driver plus AOP/codec/amp protocol, DMA and measured speaker protection.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `3d560a92dab0569a002a15ffeee995557d76c1644915e702a2986fcbbd8a70cd`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
