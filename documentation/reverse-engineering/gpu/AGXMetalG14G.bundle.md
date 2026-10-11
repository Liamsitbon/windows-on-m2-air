# AGXMetalG14G.bundle

Bundle ID: `com.apple.AGXMetalG14G`; version `360.34.5`.

Executable in bundle: **False**. Entry in this boot collection: **False**. Available symbol names: **0**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[]
```

## Dependencies


## Windows implementation target

WDDM kernel display miniport plus Direct3D user-mode driver; GPU VA, queues, fences, TDR and residency must be reimplemented.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `2cfc7b07234bfbd9d15f855dfb906a4e220b26c5d88af7fa4cd0b7ee4f2cd0ab`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
