# IONVMeFamily.kext

Bundle ID: `com.apple.iokit.IONVMeFamily`; version `2.1.0`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **4735**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleANS2CGNVMeController",
    "IOPropertyMatch": {
      "role": "ANS2"
    },
    "IOProviderClass": "RTBuddyService",
    "name": "AppleANS2CGNVMeController"
  },
  {
    "IOClass": "AppleANS2CGv2Controller",
    "IOPropertyMatch": {
      "role": "ANS2"
    },
    "IOProviderClass": "RTBuddyService",
    "name": "AppleANS2CGv2Controller"
  },
  {
    "IOClass": "AppleANS2DARTNVMeController",
    "IOPropertyMatch": {
      "role": "ANS2"
    },
    "IOProviderClass": "RTBuddyService",
    "name": "AppleANS2DARTNVMeController"
  },
  {
    "IOClass": "AppleANS2NVMeController",
    "IOPropertyMatch": {
      "role": "ANS2"
    },
    "IOProviderClass": "RTBuddyService",
    "name": "AppleANS2NVMeController"
  },
  {
    "IOClass": "AppleANS3CGv2Controller",
    "IOPropertyMatch": {
      "role": "ANS2"
    },
    "IOProviderClass": "RTBuddyService",
    "name": "AppleANS3CGv2Controller"
  },
  {
    "IOClass": "AppleANS3NVMeController",
    "IOPropertyMatch": {
      "role": "ANS2"
    },
    "IOProviderClass": "RTBuddyService",
    "name": "AppleANS3NVMeController"
  },
  {
    "IOClass": "AppleEmbeddedNVMeController",
    "IOProviderClass": "IOPCIDevice",
    "name": "AppleEmbeddedNVMeController"
  },
  {
    "IOClass": "IONVMeController",
    "IOProbeScore": 100,
    "IOProviderClass": "IOPCIDevice",
    "name": "GenericNVMeSSD"
  },
  {
    "IOClass": "NVMeSEPNotifier",
    "IOProviderClass": "AppleSEPManager",
    "name": "NVMeSEPNotifier"
  }
]
```

## Dependencies

- `com.apple.driver.AppleA7IOP` >= `1.0.0`
- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleEmbeddedPCIE` >= `1.0.0`
- `com.apple.driver.AppleMobileFileIntegrity` >= `1.0.1`
- `com.apple.driver.AppleNANDConfigAccess` >= `1.0.0`
- `com.apple.driver.AppleSMC` >= `1.0.0`
- `com.apple.driver.IOSlaveProcessor` >= `1.0`
- `com.apple.driver.RTBuddy` >= `1.0.0`
- `com.apple.iokit.IOHIDFamily` >= `1.0`
- `com.apple.iokit.IOPCIFamily` >= `1.0.0`
- `com.apple.iokit.IOStorageFamily` >= `1.7.0`
- `com.apple.kec.corecrypto` >= `1.0`
- `com.apple.kpi.bsd` >= `9.0.0`
- `com.apple.kpi.iokit` >= `9.0.0`
- `com.apple.kpi.libkern` >= `9.0.0`
- `com.apple.kpi.mach` >= `9.0.0`
- `com.apple.kpi.private` >= `9.0.0`
- `com.apple.kpi.unsupported` >= `9.0.0`

## Windows implementation target

Preserve the existing synthetic NVMe bridge first; a native replacement requires Windows storage miniport and ANS protocol qualification.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `e45f8e9c7bfdd1c02ce73292db9b7151e9f3aae674eaa84eaa6c6b717525cc31`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
