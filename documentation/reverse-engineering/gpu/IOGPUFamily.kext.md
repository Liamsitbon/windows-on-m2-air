# IOGPUFamily.kext

Bundle ID: `com.apple.iokit.IOGPUFamily`; version `162.11`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **3759**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[]
```

## Dependencies

- `com.apple.driver.AppleMobileFileIntegrity` >= `1.0.1`
- `com.apple.iokit.IOGraphicsFamily` >= `1.0.0b1`
- `com.apple.iokit.IOPCIFamily` >= `1.0.0b1`
- `com.apple.iokit.IOReportFamily` >= `1.0`
- `com.apple.iokit.IOSurface` >= `87.0`
- `com.apple.kpi.bsd` >= `9.0.0b1`
- `com.apple.kpi.iokit` >= `9.0.0b1`
- `com.apple.kpi.libkern` >= `9.0.0b1`
- `com.apple.kpi.mach` >= `9.0.0b1`
- `com.apple.kpi.private` >= `10.0.0d3`
- `com.apple.kpi.unsupported` >= `9.0.0b1`

## Windows implementation target

WDDM kernel display miniport plus Direct3D user-mode driver; GPU VA, queues, fences, TDR and residency must be reimplemented.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `1094c63ec9bf2299582719d9662b6f31c479b78064f4785c6ba83509a1049926`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
