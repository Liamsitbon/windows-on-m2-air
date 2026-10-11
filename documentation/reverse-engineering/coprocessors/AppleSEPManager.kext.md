# AppleSEPManager.kext

Bundle ID: `com.apple.driver.AppleSEPManager`; version `1.0.1`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **2643**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleSEPManager",
    "IONameMatch": "iop-nub,sep",
    "IOProviderClass": "AppleA7IOPNub",
    "name": "A7IOPNub"
  },
  {
    "IOClass": "AppleSEPARTRequestsService",
    "IONameMatch": "sep-endpoint,artr",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "ARTRequestsDevice"
  },
  {
    "IOClass": "AppleSEPARTService",
    "IOProviderClass": "AppleSEPManager",
    "name": "ARTService"
  },
  {
    "IOClass": "AppleSEPARTStorageService",
    "IONameMatch": "sep-endpoint,arts",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "ARTStorageDevice"
  },
  {
    "IOClass": "AppleSEPDebugService",
    "IONameMatch": "sep-endpoint,debu",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "DebugDevice"
  },
  {
    "IOClass": "AppleSEPHiloService",
    "IONameMatch": "sep-endpoint,hilo",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "HiloDevice"
  },
  {
    "IOClass": "AppleSEPIntelIOP",
    "IONameMatch": "SEPM",
    "IOProviderClass": "IOPCIDevice",
    "name": "IntelIOP"
  },
  {
    "IOClass": "AppleSEPManager",
    "IONameMatch": "iop-nub,sep",
    "IOProviderClass": "AppleSEPIntelIOPNub",
    "name": "IntelIOPNub"
  },
  {
    "IOClass": "AppleSEPLoggerService",
    "IONameMatch": "sep-endpoint,log",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "LoggingDevice"
  },
  {
    "IOClass": "AppleSEPPairing",
    "IONameMatch": "sep-endpoint,pair",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "PairingDevice"
  },
  {
    "IOClass": "AppleSEPTestingService",
    "IONameMatch": "sep-endpoint,unit",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "TestingDevice"
  },
  {
    "IOClass": "AppleSEPXARTService",
    "IONameMatch": "sep-endpoint,xarm",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "xARTMasterDevice"
  },
  {
    "IOClass": "AppleSEPXARTService",
    "IONameMatch": "sep-endpoint,xars",
    "IOProviderClass": "AppleSEPDeviceService",
    "name": "xARTSlaveDevice"
  }
]
```

## Dependencies

- `com.apple.driver.AppleA7IOP` >= `1.0.1`
- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.IODARTFamily` >= `1.0.0`
- `com.apple.driver.IOSlaveProcessor` >= `1.0.0`
- `com.apple.kec.corecrypto` >= `1.0`
- `com.apple.kpi.bsd` >= `8.0`
- `com.apple.kpi.iokit` >= `8.0`
- `com.apple.kpi.libkern` >= `8.0`
- `com.apple.kpi.mach` >= `8.0`
- `com.apple.kpi.private` >= `8.0`
- `com.apple.kpi.unsupported` >= `8.0`

## Windows implementation target

Bounded RTKit mailbox transport with firmware ABI qualification; SEP authentication is optional and unimplemented.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `7d41d9fca4a4f9ba21f90a245cef066b660401b4443dc7a204d577cc2edfb047`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
