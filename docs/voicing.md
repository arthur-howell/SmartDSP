# SmartDSP Nonlinear Voicing

SmartDSP includes a real-time nonlinear voicing system designed to alter the harmonic and transfer-function characteristics of an audio signal without replacing the physical DAC, preamplifier, or power amplifier.

This is fundamentally different from conventional equalization.

## Linear EQ vs. Nonlinear Voicing

Conventional EQ changes the amplitude of frequencies already present in the signal.

Nonlinear processing can generate additional harmonic content and modify the relationship between input and output amplitude.

Conceptually:

    Linear Processing

    Input
      |
      v
     EQ
      |
      v
    Same frequencies
    Different amplitudes


    Nonlinear Processing

    Input
      |
      v
    Transfer Function
      |
      v
    Modified waveform
      |
      +-- Harmonic generation
      +-- Saturation
      +-- Peak shaping
      +-- Symmetry / asymmetry
      +-- Dynamic nonlinear behavior

SmartDSP uses these characteristics as a controllable form of system voicing.

## Current Implementation

The current voicing engine uses the Calf Saturator LV2 plugin hosted by `jalv`.

Control is performed independently from the real-time audio stream.

    SmartDSP UI
         |
         v
    Preset Selection
         |
         v
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
         |
         v
    Audio Pipeline

This architecture allows voicing changes without restarting the primary DSP pipeline.

## Preset State

Each SmartDSP preset defines the processing parameters required for that voicing.

When a new preset is selected, the control system establishes the complete parameter state rather than depending upon values left behind by the previously selected preset.

This prevents unintended state leakage between voicings.

## Voicing Philosophy

The goal of SmartDSP voicing is not exact circuit simulation.

A physical amplifier, transformer, tube stage, tape machine, or preamplifier contains complex electrical behavior that cannot be completely represented by a simple saturation model.

Instead, SmartDSP profiles explore characteristic nonlinear behavior associated with broad equipment families and design philosophies.

A profile named:

    300B SET

should therefore be interpreted as:

    "A nonlinear voicing inspired by characteristics associated
     with a 300B single-ended triode amplifier."

It should NOT be interpreted as:

    "A circuit-accurate simulation of a specific 300B amplifier."

The same principle applies to equipment-inspired profiles.

## Profile Families

SmartDSP currently organizes voicings into several conceptual groups.

### Reference

Profiles intended to preserve an essentially transparent presentation.

Examples:

- Reference
- Subtle
- Modern Reference

These are useful as baselines when evaluating more aggressive nonlinear profiles.

### Solid-State

Profiles inspired by broad solid-state amplifier behavior.

Examples:

- Class-A
- Vintage Class-AB
- MOSFET Class-A
- Bipolar Class-A
- High-Bias Class-AB
- Class-D + Weight

These profiles explore different combinations of harmonic structure, drive, saturation, and transfer behavior.

### Tube

General tube-oriented profiles include:

- Triode
- Vintage Tube
- Modern Tube
- Tube Preamp
- Tube Buffer

These range from subtle buffer-like processing to more obvious nonlinear coloration.

### Single-Ended Triode

SET-inspired profiles include:

- 300B SET
- 45 SET
- 2A3 SET
- 211 SET
- 845 SET

These profiles explore nonlinear behavior commonly associated with single-ended tube amplification.

### Push-Pull Tube

Push-pull-inspired profiles include:

- EL84 Push-Pull
- EL34 Push-Pull
- 6L6GC Push-Pull
- 5881 Push-Pull
- KT66 Push-Pull
- KT88 Push-Pull
- 6550 Push-Pull

### Ultralinear

Current ultralinear-inspired profiles include:

- EL34 Ultralinear
- KT88 Ultralinear

### Equipment / Design Inspired

SmartDSP also contains profiles inspired by broader equipment or amplifier design concepts.

Examples include:

- GAS Inspired
- Big Iron
- Unity-Coupled Inspired
- Minimalist Class-A Inspired

These profiles are intentionally described as "inspired" rather than hardware emulations.

### Creative

Some voicings are designed around a desired listening characteristic rather than an amplifier topology.

Examples include:

- Warm
- Velvet
- Liquid
- Analog
- Studio Console
- Transformer
- Tape Light
- Tape Hot
- Late Night
- Horn Tamer
- Presence
- Maximum Funk

These profiles provide a more explicitly creative use of the nonlinear engine.

## Reference and Bypass

A nonlinear processing system requires a known baseline.

SmartDSP therefore includes reference-oriented settings that allow the user to compare processed and minimally processed playback.

When evaluating a profile, users should compare it against the reference state at matched playback level.

Small level differences can otherwise be mistaken for differences in sound quality.

## Current Development Preferences

In the reference SmartDSP system, the current preferred profiles are:

### Triode

Triode is currently one of the primary listening profiles.

It is used when additional harmonic character and dimensionality are desired without substantially changing the basic tonal balance of the system.

### Tube Buffer

Tube Buffer is used when a smaller nonlinear contribution is desired.

The objective is subtle harmonic modification rather than an obvious effect.

These preferences are subjective and are documented only to establish the development reference used while building SmartDSP.

## Reference Playback System

Current voicing development is performed using:

    SmartDSP
       |
       v
    Topping D90
       |
       | Balanced XLR
       v
    Fosi Audio V3 Mono x2
       |
       v
    1977 Klipsch La Scala

The combination provides a clean downstream signal path and highly sensitive loudspeakers, making relatively small processing changes readily apparent.

## Future Development

The voicing system is intended to evolve independently of the rest of SmartDSP.

Potential future work includes:

- Additional nonlinear engines
- More sophisticated waveshaping
- Independent harmonic controls
- Additional LV2 plugins
- Profile comparison tools
- User-created profiles
- Profile import/export
- Level-matched A/B testing
- Measurement-assisted profile development
- More sophisticated equipment-inspired models

The architecture intentionally separates preset definitions from the underlying processing engine so additional implementations can be introduced without redesigning the entire SmartDSP platform.
