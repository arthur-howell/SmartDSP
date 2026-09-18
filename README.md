# SmartDSP

**A high-resolution, software-defined audio processor for nonlinear voicing, filtering, routing, metering, visualization, and system management.**

SmartDSP is a Linux-based USB-to-USB digital audio processing platform built around CamillaDSP, PipeWire/JACK-compatible tooling, LV2 processing, and a custom web management interface.

The reference implementation runs at **192 kHz / 32-bit** on a Raspberry Pi 4 between a digital source/ADC and an external USB DAC.

> **Project status:** Experimental / Development. SmartDSP is operational in the reference system while installation automation, hardware abstraction, and packaging continue to mature.

## Features

- 192 kHz / 32-bit digital processing
- CamillaDSP filtering and signal processing
- 44 nonlinear voicing profiles
- LV2 plugin hosting
- USB-to-USB processing
- ALSA hardware abstraction
- PipeWire/JACK routing
- Real-time metering
- System telemetry
- Backup and restore
- Service management
- Custom web management interface
- Physics-based visualization
- Experimental audio identification

## Architecture

SmartDSP separates the real-time audio plane from management and optional workloads.

```text
Analog / Digital Source
        |
        v
   ADC / USB Audio
        |
        v
+--------------------+
|      SmartDSP      |
|                    |
|    CamillaDSP      |
|         +          |
|      Filtering     |
|         +          |
|       Voicing      |
|         +          |
|    LV2 Processing  |
+--------------------+
        |
        v
      USB DAC
        |
        v
    Amplifier
        |
        v
     Speakers
```

The management plane operates alongside the audio path:

```text
SmartDSP Manager
       |
       +-- CamillaDSP control
       +-- Voicing presets
       +-- System telemetry
       +-- Routing
       +-- Signal meters
       +-- Visualization
       +-- Backup / restore
       +-- Service management
```

**Nothing in the management, visualization, identification, or observability planes should be capable of blocking the audio plane.**

See [Architecture](docs/architecture.md) and [Signal Path](docs/signal-path.md).

## Nonlinear Voicing

SmartDSP includes a selectable nonlinear transfer-function voicing engine. Rather than conventional EQ alone, voicing can alter:

- Harmonic structure
- Saturation
- Transfer-curve shape
- Asymmetry
- Peak behavior
- Soft clipping
- Dynamic character

The current library contains **44 profiles**, including Triode, Tube Buffer, Tube Preamp, 300B SET, 2A3 SET, 45 SET, EL34 Push-Pull, KT88 Push-Pull, Class-A, MOSFET Class-A, High-Bias Class-AB, Transformer, Tape, Studio Console, and Modern Reference.

These are **transfer-function approximations**, not circuit-level simulations or claims of exact hardware emulation.

See [Voicing](docs/voicing.md).

## SmartDSP Manager

The custom browser-based Manager provides:

- Overview and system telemetry
- CamillaDSP control
- Routing
- Voicing selection
- Signal meters
- Backup and restore
- Service management
- Visualizer
- Experimental Now Playing interface

The Manager is outside the real-time audio path. Its failure should not interrupt playback.

See [SmartDSP Manager](docs/manager.md).

## Reference System

| Function | Equipment |
|---|---|
| Turntable | Technics SL-1300 |
| Phono / Preamp / ADC | WiiM Ultra |
| SmartDSP Host | Raspberry Pi 4 |
| USB DAC | Topping D90 |
| Amplification | Fosi Audio V3 Mono x2 |
| Loudspeakers | 1977 Klipsch La Scala |
| Subwoofer | BIC Acoustech Elite PL-300 |

### Reference Signal Chain

```text
Technics SL-1300
       |
       v
   WiiM Ultra
Phono / Preamp / ADC
       |
      USB
       |
       v
    SmartDSP
 Raspberry Pi 4
192 kHz / S32_LE
       |
      USB
       |
       v
  Topping D90
       |
 Balanced XLR
       |
       v
Fosi V3 Mono x2
       |
       v
1977 Klipsch La Scala
```

The BIC PL-300 subwoofer is currently integrated at the WiiM Ultra.

The reference system is an example implementation. **SmartDSP does not require this hardware.**

See [Reference System](docs/reference-system.md).

## Reference DSP Configuration

The portable CamillaDSP reference configuration operates at:

```text
Sample Rate:       192000 Hz
Processing Format: S32_LE
Channels:          2
Chunk Size:        1024
```

Hardware-specific ALSA endpoints are abstracted as:

```text
SMARTDSP_CAPTURE
SMARTDSP_PLAYBACK
```

and mapped during installation.

## Installation

Clone the repository and run:

```bash
./install.sh
```

The guided installer handles:

1. Runtime dependencies
2. ALSA capture/playback endpoints
3. CamillaDSP configuration
4. Nonlinear voicing
5. SmartDSP Manager

Verify the resulting installation with:

```bash
./install/verify-installation.sh
```

Individual components can also be installed separately from `install/`.

See [Runtime Dependencies](docs/runtime-dependencies.md) and [Dependencies](docs/dependencies.md).

## Repository Layout

```text
SmartDSP/
├── config/
│   ├── alsa/
│   ├── camilladsp/
│   └── systemd/
├── docs/
├── install/
├── src/
│   └── manager/
├── voicing/
│   ├── bin/
│   └── config/
├── install.sh
└── README.md
```

## Experimental: Audio Identification

Audio identification is being developed separately from the stable audio path.

The current prototype successfully detects:

```text
SILENCE
   |
audio begins
   v
CAPTURE REQUEST
   |
   v
PLAYING
   |
sustained silence
   v
REARM
```

Detection uses CamillaDSP's live capture telemetry. PCM acquisition and recognition remain experimental because the current reference UAC2 capture architecture exposes a single hardware capture substream.

This work remains isolated until identification can operate without compromising the primary audio path.

## Design Philosophy

SmartDSP is built around a simple idea:

**The purpose of an audio system is to listen to music.**

SmartDSP concentrates experimentation where meaningful system changes can be made:

- DSP
- Transfer-function behavior
- Analog output stages
- Amplification
- Loudspeakers
- Room interaction
- System voicing

The goal is not to maximize specifications for their own sake.

The goal is to build a system that can be **measured, understood, changed, and enjoyed.**

## Documentation

- [Architecture](docs/architecture.md)
- [Signal Path](docs/signal-path.md)
- [Nonlinear Voicing](docs/voicing.md)
- [SmartDSP Manager](docs/manager.md)
- [Reference System](docs/reference-system.md)
- [Runtime Dependencies](docs/runtime-dependencies.md)
- [Dependencies](docs/dependencies.md)

## Built With

SmartDSP builds upon open-source projects including CamillaDSP, PipeWire, JACK-compatible Linux audio tooling, LV2, jalv, and Calf Studio Gear.

These projects retain their respective copyrights and licenses.

## License

License selection is pending before the first tagged release.
