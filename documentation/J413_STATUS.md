# J413 development checkpoint — 2026-10-11

The base is the clean GitHub fork at
`1a247525175fce61484e75e0915adc452475a0c2`. No Gemini source modifications were
imported. Root-tracked overlays and patch files preserve reproducibility without
pointing gitlinks at unpublished submodule commits.

| Component | Software evidence | Hardware evidence |
| --- | --- | --- |
| J413 Mu firmware overlay | CLANGPDB DEBUG build completed; 97 EFI images verified | No J413 firmware launch |
| CPU / virtual GIC description | Eight enabled GICC entries, 4E+4P MPIDRs and efficiency classes; 64-bit GICR address | No Windows CPU startup |
| Framebuffer contract | 2560×1664, stride 10240, allocation `0x1040000` | No Windows scanout |
| AIC2 USB1 routing | Physical IRQ 1112 → virtual INTID 857; incoming/EOI/capacity host tests | No Windows USB/DART qualification |
| DockChannel FIFO | Original portable bounded core and fake-register tests | No live FIFO access or HID publication |
| RTKit management | MIT source adaptation from official Asahi; version/endpoint/power plans and Windows ARM64 COFF compilation | No live coprocessor negotiation |
| DockChannel HID framing | MIT source adaptation; packet/checksum/bounds tests under ASan/UBSan; Windows ARM64 COFF compilation | No keyboard/trackpad enumeration |
| GPU / DCP | G14G and DCP bundle inventory and interface mapping | No M2 GPU command or accelerated frame |
| Power, audio, WLAN, SEP | Bundle matching/dependency inventory | No Windows driver qualification |

## Primary evidence and ownership

`investigation/j413-macos-resources.json` contains a whitelisted read-only ADT
capture from Mac14,2/T8112. ADT `reg` values are preserved as raw parent-relative
pairs; version 2 also resolves physical pairs through every ancestor's ranges.
Missing, ambiguous or incomplete mappings remain explicitly unresolved, and
inactive zero/zero placeholders have no physical address. This inventory grants
no MMIO access or DMA ownership.
The live USB1 IRQ is 1112, outside the guest GIC's 0..1019 namespace. The IRQ
patch keeps these namespaces separate and reverses the mapping for EOI. USB0
remains outside that static guest route. UART0 uses the observed AIC IRQ 739,
confirmed by the live ADT and T8112 DTS; the M1 value 1097 is removed.

Inspected [Asahi T8112 DTS](https://github.com/AsahiLinux/linux/blob/asahi/arch/arm64/boot/dts/apple/t8112.dtsi),
[J413 DTS](https://github.com/AsahiLinux/linux/blob/asahi/arch/arm64/boot/dts/apple/t8112-j413.dts),
DockChannel, pinned m1n1 `aic.c`, `hv.c`, `vgic.c`, `hv_irq_routes.c`, `kboot.c`,
and pinned Mu ACPI/platform libraries. m1n1 already recognizes T8112/AIC2 and
provides virtual GIC regions at `0xf00000000`, `0xf10000000`, `0xf20000000`.
The M2 input transport is DockChannel/RTKit, so the J413 overlay omits the M1
`APPL0001` SPI device instead of pretending it can drive M2 input.

The hypervisor must establish physical resources, DMA/DART ownership and guest
mappings before ACPI can safely expose devices. Mu publishes guest topology and
firmware services. Windows drivers own runtime queues, interrupts, power and
recovery within those established resources. Unmeasured M1 PMU IRQs are omitted.
The existing T810X memory and platform libraries are still shared: this is a
firmware build target, not proof that their full M2 launch assumptions hold.

## Reproduce the software checkpoint

Pinned submodules remain:

- m1n1: `9cd80ac652ac404e92ae279deeaec8c629d7d184`
- Mu: `8b4dc4b4e3ff8606d0af36163acf9de79b7b4737`

```sh
git submodule update --init --recursive
python3 tools/j413_platform.py
python3 tools/j413_platform.py --stage-m1n1
python3 -m unittest discover -s tests
make -C m1n1_windows host-tests CC=clang
scripts/build-j413-firmware.sh
```

The script stages only new Mu platform paths, rejects different local files or
tracked-file overwrites, builds DEBUG firmware using the pinned dependencies,
and records a board-specific manifest with the overlay source hash. On macOS it
uses the native ARM64 Docker build environment. Mu requires Python 3.10–3.12.
The manifest utility defaults to J313 for existing callers; J413 must be explicit
and is refused for a release profile until hardware qualification exists.

Output: `dist/j413/firmware-debug/J413_EFI.fd`, 30,965,760 bytes, SHA-256:

`12409354b231ab22dd3d2c80982d8eb2da8ebcc1a16fdf75e13cbe1983f6098c`

Overlay SHA-256:
`f129ef244f49ccdfe93d6a33d4ab753dc6f9dc76841e7e47b1ed24fa7f818973`

The compiled MADT was inspected directly: UIDs 0..7, MPIDRs 0..3 and
`0x10100`..`0x10103`, efficiency classes 0/1, GICR base `0xf10000000`, length
`0x100000`. Its raw compiler output has an unset ACPI checksum; the ACPI install
path supplies runtime checksums. This inspection does not verify installed ACPI.

## GPU source checkpoint

The real upstream M1 GPU implementation is separate from main:

- root [GPU checkpoint ca71f54](https://github.com/paulsmir/windows-on-m1/commit/ca71f549820ea9b7c6c4e89eac9b3afd283dc175)
- m1n1 [c52b159](https://github.com/paulsmir/m1n1_windows/commit/c52b1593c665e474cbf0343f547aaa6c84064f9d)
- Mu [0dac687](https://github.com/paulsmir/apple_silicon_platforms_mu/commit/0dac68712f3bc520d46f88af84a430cfb916dfc4)

It contains a WDDM KMD and Mesa-based D3D10 UMD, with an explicit G13G admission
check in `drivers/apple-agx/windows/one-shot/agx_kmt_native_bridge.c` and G13
package identification. Changing that check to accept G14G would not port
firmware layouts, UAT, queues, synchronization, cache/DART ownership or DCP.
The exact source was inspected in a separate local checkout; it has not been
merged or labelled M2-compatible. [Kext research](reverse-engineering/README.md)
is an additional source of evidence for those contracts.

## Next hardware checkpoint and recovery

The inherited firmware/ADT/boot-argument/ramdisk reservations in
`config/j413-guest-layout.json` are internally checked guest reservations, not
measured safe live M2 placement. A launch must first translate live ADT resources,
validate all physical reservations and establish a reversible log/recovery path.
Only the target Air is available; the upstream assisted workflow assumes a
second host and cannot be adopted as-is. A board-specific autonomous UEFI experiment is now compiled;
[build and recovery boundaries](J413_BOOT_EXPERIMENT.md) describe its runtime
gates and exact unlaunched artifact. It is not a hardware-qualified Windows
boot image.

No partition, boot policy, ESP or running hardware state was changed. macOS is
the current recovery state. Do not install this component as a complete boot
image. The next experiment must record its exact artifact and recovery path in
`investigation/EXPERIMENTS.md`; first seek an observable UEFI checkpoint, then
qualify Windows/CPU/timer/storage before DMA, GPU or additional peripherals.

External installer preparation: [observed SSD and boot boundaries](J413_EXTERNAL_SETUP.md).

Official Asahi source adaptations and measured resources:
[portable protocol components](ASAHI_PORTS.md).

The current J413 boot experiment is physical/debug-off with `M1N1_NO_PROXY` in
both stages (EXP-20261011-J413-013). It excludes takeover and interactive proxy
fallback; failed startup stops visibly. The earlier UART candidate is superseded.
See J413_BOOT_EXPERIMENT.md for the current hash and existing ESP install command.
No new physical UEFI or Windows success is claimed.
