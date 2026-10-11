# AppleDCPDPTXProxy.kext

Bundle ID: `com.apple.driver.AppleDCPDPTXProxy`; version `1.0.0`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **885**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleDCPDPTXRemoteHDCPAuthSessionProxy",
    "IOPropertyMatch": {
      "EPICName": "dcpdptx-hdcp-auth-session"
    },
    "IOProviderClass": "AFKEndpointInterface",
    "name": "AppleDCPDPTXRemoteHDCPAuthSessionProxy"
  },
  {
    "IOClass": "AppleDCPDPTXRemoteHDCPInterfaceProxy",
    "IOPropertyMatch": {
      "EPICName": "dcpdptx-hdcp-interface"
    },
    "IOProviderClass": "AFKEndpointInterface",
    "name": "AppleDCPDPTXRemoteHDCPInterfaceProxy"
  },
  {
    "IOClass": "AppleDCPDPTXRemotePortProxy",
    "IOPropertyMatch": {
      "EPICName": "dcpdptx-port-epic"
    },
    "IOProviderClass": "AFKEndpointInterface",
    "name": "AppleDCPDPTXRemotePortProxy"
  },
  {
    "IOClass": "AppleDCPLPDPTXPortProxy",
    "IOPropertyMatch": {
      "EPICName": "dcp-lpdptx-port-epic"
    },
    "IOProviderClass": "AFKEndpointInterface",
    "name": "AppleDCPLPDPTXPortProxy"
  }
]
```

## Dependencies

- `com.apple.driver.AppleDCP` >= `1.0`
- `com.apple.driver.AppleFirmwareKit` >= `1.0.0`
- `com.apple.driver.DCPAVFamilyProxy` >= `1.0.0`
- `com.apple.driver.DCPDPFamilyProxy` >= `1.0.0`
- `com.apple.iokit.IOAVFamily` >= `1.0`
- `com.apple.iokit.IOAccessoryManager` >= `1.0`
- `com.apple.iokit.IODisplayPortFamily` >= `1.0`
- `com.apple.iokit.IOHDCPFamily` >= `1.0`
- `com.apple.iokit.IOPortFamily` >= `1.0`
- `com.apple.kpi.iokit` >= `19.0`
- `com.apple.kpi.libkern` >= `19.0`
- `com.apple.kpi.mach` >= `19.0`

## Windows implementation target

DCP firmware protocol plus WDDM VidPn/present/scanout ownership; rendering and scanout require separate qualification.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `34683de8f206e7d93beaaebd9760366041ba6b4c2b291c2a0733f8bbe6375539`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
