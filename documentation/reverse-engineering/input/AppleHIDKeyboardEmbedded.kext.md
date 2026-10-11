# AppleHIDKeyboardEmbedded.kext

Bundle ID: `com.apple.driver.AppleHIDKeyboardEmbedded`; version `1.2.0a3`.

Executable in bundle: **False**. Entry in this boot collection: **False**. Available symbol names: **0**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleEmbeddedKeyboard",
    "IOProviderClass": "IOHIDInterface",
    "name": "iAP B62 ANSI Map"
  },
  {
    "IOClass": "AppleEmbeddedKeyboard",
    "IOProviderClass": "IOHIDInterface",
    "name": "iAP B62 ISO Map"
  },
  {
    "IOClass": "AppleEmbeddedKeyboard",
    "IOProviderClass": "IOHIDInterface",
    "name": "iAP B62 JIS Map"
  }
]
```

## Dependencies

- `com.apple.iokit.IOHIDFamily` >= `1.4`
- `com.apple.kpi.iokit` >= `10.0.0d2`
- `com.apple.kpi.libkern` >= `10.0.0d2`

## Windows implementation target

KMDF DockChannel/RTKit transport plus VHF keyboard and Precision Touchpad HID reports; no J313 SPI reuse.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `5a4bd8e0671187e5b806a4ab92f7b953c42873aa235b9b0bdc68a36812384608`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
