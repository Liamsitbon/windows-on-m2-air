# AppleAOPAudio.kext

Bundle ID: `com.apple.driver.AppleAOPAudio`; version `600.1`.

Executable in bundle: **False**. Entry in this boot collection: **True**. Available symbol names: **1958**.

A collection entry proves packaging, not that the driver attached or its hardware protocol was decoded.

## Observed IOKit matching

```json
[
  {
    "IOClass": "AppleAOPAudioAmpManagerDevice",
    "IONameMatch": [
      "audio-amp"
    ],
    "IOProbeScore": 1000,
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioAmpManagerDevice"
  },
  {
    "IOClass": "AppleAOPAudioButtonHapticDevice",
    "IONameMatch": [
      "audio-aop-bhap",
      "audio-bhap"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioButtonHapticDevice"
  },
  {
    "IOClass": "AppleAOPAudioButtonOutputDevice",
    "IONameMatch": [
      "audio-aop-buttonout",
      "audio-buttonout"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioButtonOutput"
  },
  {
    "IOClass": "AppleAOPAudioClientManager",
    "IONameMatch": [
      "audio-hp",
      "audio-aop-ldcm",
      "audio-aop-hawking",
      "audio-leap-internal-loopback",
      "audio-leap-mca-loopback",
      "audio-aop-speaker-manager",
      "audio-aud-mca-baseband",
      "audio-aud-mca-loopback",
      "audio-aop-mca2-pmgr",
      "audio-aop-mca3-pmgr",
      "audio-aop-mca4-pmgr",
      "audio-aop-mca5-pmgr"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioClientManager"
  },
  {
    "IOClass": "AppleAOPAudioController",
    "IONameMatch": [
      "aop-audio"
    ],
    "IOProviderClass": "AppleSPUAppInterface",
    "name": "AppleAOPAudioController"
  },
  {
    "IOClass": "AppleAOPAudioDevice",
    "IONameMatch": [
      "audio-aop-edt-config"
    ],
    "IOProbeScore": 1000,
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioDevice"
  },
  {
    "IOClass": "AppleAOPAudioDeviceProvider",
    "IOPropertyMatch": {
      "compatible": "aop-audio-control"
    },
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioDeviceProvider"
  },
  {
    "IOClass": "AppleAOPAudioFWdtAssetManagerDevice",
    "IONameMatch": [
      "audio-fwdt-asset-mgr"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioFWdtAssetManagerDevice"
  },
  {
    "IOClass": "AppleAOPAudioHallDevice",
    "IONameMatch": [
      "audio-hall",
      "audio-aop-hall"
    ],
    "IOProviderClass": "IOService",
    "name": "AppleAOPAudioHallDevice"
  },
  {
    "IOClass": "AppleAOPAudioDeviceProvider",
    "IOPropertyMatch": {
      "compatible": "aop-audio-haptic"
    },
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioHapticControlDevice"
  },
  {
    "IOClass": "AppleAOPAudioDeviceProvider",
    "IOPropertyMatch": {
      "compatible": "aop-audio-hpdbg"
    },
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioHapticDebugControlDevice"
  },
  {
    "IOClass": "AppleAOPAudioHapticLEAP",
    "IONameMatch": [
      "audio-aop-haptic-leap",
      "audio-haptic-leap"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioHapticLEAP"
  },
  {
    "IOClass": "AppleAOPAudioLEAP",
    "IONameMatch": [
      "audio-aop-leap",
      "audio-leap"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioLEAP"
  },
  {
    "IOClass": "AppleAOPAudioLEAPClientManager",
    "IONameMatch": [
      "audio-aop-hapticmgr",
      "audio-hapticmgr"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioLEAPClientManager"
  },
  {
    "IOClass": "AppleAOPAudioLPMicInDevice",
    "IONameMatch": [
      "audio-lp-mic-in",
      "audio-aop-lp-mic-in"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioLPMicInDevice"
  },
  {
    "IOClass": "AppleAOPAudioMCA2Device",
    "IONameMatch": [
      "audio-mca0",
      "audio-mca1"
    ],
    "IOProbeScore": 1000,
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioMCA2Device "
  },
  {
    "IOClass": "AppleAOPAudioPCMAssetManagerDevice",
    "IONameMatch": [
      "audio-aop-pcmaudiomgr",
      "audio-pcmaudiomgr",
      "audio-hw-pcm-audiomgr"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioPCMAssetManagerDevice"
  },
  {
    "IOClass": "AppleAOPAudioPDM2Device",
    "IONameMatch": [
      "audio-aop-pdm2",
      "audio-pdm2"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioPDM2Device"
  },
  {
    "IOClass": "AppleAOPAudioSpeakerClientManager",
    "IONameMatch": [
      "audio-aop-spkrmgr",
      "audio-spkrmgr"
    ],
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioSpeakerClientManager"
  },
  {
    "IOClass": "AppleAOPAudioDeviceProvider",
    "IOPropertyMatch": {
      "compatible": "aop-audio-speaker"
    },
    "IOProviderClass": "AppleAOPAudioDeviceNode",
    "name": "AppleAOPAudioSpeakerControlDevice"
  }
]
```

## Dependencies

- `com.apple.driver.AppleARMPlatform` >= `1.0.0`
- `com.apple.driver.AppleEmbeddedAudioLibs` >= `1.0`
- `com.apple.driver.AppleSPU` >= `1.0.0`
- `com.apple.iokit.IOAudio2Family` >= `1.0`
- `com.apple.kpi.bsd` >= `9.0.0`
- `com.apple.kpi.iokit` >= `9.0.0`
- `com.apple.kpi.libkern` >= `9.0.0`
- `com.apple.kpi.mach` >= `9.0.0`
- `com.apple.kpi.private` >= `9.0.0`
- `com.apple.kpi.unsupported` >= `9.0.0`

## Windows implementation target

Windows audio driver plus AOP/codec/amp protocol, DMA and measured speaker protection.

## Next reverse-engineering evidence

1. Resolve the matched IORegistry service to its live ADT resources.
2. Use the local symbol/address index to locate start/stop, interrupt, mailbox and DMA handlers in a disassembler.
3. Recover message layouts, lengths, ordering, error paths and firmware version checks; distinguish observed fields from hypotheses.
4. Verify sequencing against Asahi/m1n1 primary implementations and a bounded hardware trace.
5. Implement the hardware protocol behind Windows driver APIs and validate recovery before expanding functionality.

Metadata SHA-256: `a372cc696b90bb1929c88c32fbf867d9f104d5bfb3da2feeb3763ebb356d2540`.

Raw bundles, complete symbols and kernel collections are stored under `.local/kext-research/`, excluded from Git.
