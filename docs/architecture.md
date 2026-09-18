# SmartDSP Architecture

SmartDSP is structured as cooperating Linux audio services rather than a single monolithic application.

The design separates the real-time audio path from management, telemetry, visualization, and user-interface functions.

## Architecture

    ┌─────────────────────────────────────────────┐
    │              SMARTDSP CONTROL PLANE         │
    │                                             │
    │              SmartDSP Manager               │
    │                     │                       │
    │       ┌─────────────┼─────────────┐         │
    │       │             │             │         │
    │   Telemetry      Presets      Service       │
    │                                Control      │
    └───────┼─────────────┼─────────────┼─────────┘
            │             │             │
            └─────────────┼─────────────┘
                          │
                          v
    ┌─────────────────────────────────────────────┐
    │               AUDIO CONTROL LAYER           │
    │                                             │
    │             PipeWire / JACK                 │
    │                    │                        │
    │        ┌───────────┴───────────┐            │
    │        │                       │            │
    │   CamillaDSP              LV2 Plugins       │
    │                                │            │
    │                               jalv          │
    └────────┬───────────────────────┬────────────┘
             │                       │
             └───────────┬───────────┘
                         │
                         v
    ┌─────────────────────────────────────────────┐
    │                  AUDIO PLANE                │
    │                                             │
    │ USB Capture -> DSP -> Voicing -> USB Output│
    └─────────────────────────────────────────────┘

## Primary Components

### CamillaDSP

CamillaDSP provides the primary high-resolution digital signal-processing engine.

The current reference installation operates at:

- 192,000 Hz sample rate
- S32_LE sample format
- 2 channels

### PipeWire / JACK

PipeWire provides the Linux audio graph.

JACK compatibility allows SmartDSP to integrate software designed around the JACK audio model while retaining PipeWire as the underlying audio infrastructure.

WPWGraph can be used to inspect or modify non-standard routing.

### Nonlinear Voicing Engine

SmartDSP provides a selectable nonlinear processing stage.

The current implementation uses:

    voicings.json
          |
          v
      dsp-preset
          |
          v
      Control FIFO
          |
          v
         jalv
          |
          v
    Calf Saturator LV2
          |
          v
    PipeWire / JACK

Preset changes establish the complete parameter state required by the selected profile.

### SmartDSP Manager

The Manager provides the browser-based control plane.

Its responsibilities include:

- DSP status
- System telemetry
- Voicing control
- Meter integration
- Service management
- Backup and restore
- System information
- Visualization integration

### SmartDSP Meter

The meter subsystem provides real-time audio telemetry for the management interface.

Metering operates independently from the primary browser interface.

### Visualization

SmartDSP contains experimental audio-reactive visualization systems.

The visualization subsystem is intentionally separate from the real-time DSP path so visualization load cannot become a requirement for audio processing.

### Quantum Engine

The Quantum Engine is an experimental physics-based visualization project.

Frequency-domain information is mapped into simulated objects whose behavior can be influenced by calculated physical forces.

This component remains experimental.

## Design Principles

SmartDSP is being developed around several principles:

1. Preserve a high-resolution digital signal path.
2. Keep the primary audio engine independent from the web interface.
3. Avoid requiring proprietary audio hardware.
4. Permit flexible USB-to-USB audio processing.
5. Make DSP configuration reproducible.
6. Allow nonlinear voicing without replacing the physical amplifier.
7. Expose useful system and audio telemetry.
8. Keep experimental visualization outside the critical audio path.
9. Allow the DSP host to be upgraded without redesigning the surrounding audio system.
10. Treat the surrounding source, DAC, amplifier, and loudspeakers as independent components.

## Reference Data Flow

    WiiM Ultra
    USB Audio
        |
        v
    Raspberry Pi 4
        |
        +--> PipeWire / JACK
        |
        +--> CamillaDSP
        |
        +--> Nonlinear Voicing
        |
        +--> Metering
        |
        +--> Telemetry
        |
        +--> Visualization
        |
        v
    USB Audio
        |
        v
    Topping D90

The management and visualization layers observe or control the system but are not intended to become dependencies for continued audio playback.
