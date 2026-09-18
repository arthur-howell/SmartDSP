# SmartDSP Reference System

The primary SmartDSP development and listening system is a high-resolution USB-to-USB digital processing chain.

## Signal Chain

    Technics SL-1300
          |
          v
      WiiM Ultra
    Phono / ADC / Preamp
          |
          | USB
          v
      SmartDSP
    Raspberry Pi 4
    192 kHz / S32_LE
          |
          | USB
          v
     Topping D90
          |
          | Balanced XLR
          v
    Fosi Audio V3 Mono x2
          |
          v
    1977 Klipsch La Scala

The BIC PL-300 subwoofer is currently integrated through the WiiM Ultra.

## Digital Processing

The reference CamillaDSP engine operates at:

    Sample rate: 192000 Hz
    Format:      S32_LE
    Channels:    2
    Chunk size:  1024

The production system uses direct ALSA capture and playback.

## Reference Filters

### Anti-Clip

Soft limiting protects against processing overshoot.

### Infrasonic / Subsonic

    High-pass: 42 Hz
    Q:         0.8

Configured around the low-frequency behavior of the reference Klipsch La Scala system.

### Squawker Correction

    Frequency: 4500 Hz
    Gain:      -0.8 dB
    Q:          1.5

Provides a mild correction to the reference system's midrange response.

### High-Frequency Rolloff

    Frequency: 16000 Hz
    Gain:      -1.5 dB
    Q:          0.61

Provides a gentle upper-frequency rolloff.

### Processing Headroom

    Gain: -6 dB

Six decibels of digital headroom are reserved for DSP processing and nonlinear voicing.

## Voicing

Current preferred SmartDSP voicing profiles on the reference system are:

- Triode
- Tube Buffer

Voicing uses controlled nonlinear transfer functions rather than conventional frequency-response EQ alone.

## Hardware Independence

The public `reference-192k.yml` configuration intentionally uses:

    SMARTDSP_CAPTURE
    SMARTDSP_PLAYBACK

instead of the device names from the development system.

These endpoints should be mapped to the appropriate ALSA devices during installation.

## Design Objective

SmartDSP is intended to provide a high-resolution, controllable DSP environment without requiring exotic digital hardware.

The reference system demonstrates the project using commercially available source, conversion, amplification, and loudspeaker hardware while concentrating experimentation in the DSP layer.
