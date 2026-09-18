# SmartDSP

SmartDSP is a Linux-based high-resolution audio DSP platform designed to sit between a digital audio source and DAC.

It combines:

- CamillaDSP
- PipeWire / JACK audio routing
- Nonlinear transfer-function voicing
- LV2 processing
- Real-time metering
- System telemetry
- Audio visualization
- Web-based management
- Backup and restore
- Service management

The current reference implementation runs on a Raspberry Pi 4 and processes stereo audio at **192 kHz using S32_LE**.

SmartDSP began as a way to add flexible DSP processing to a reference audio system without replacing the existing DAC, amplifier, or source components.

It has since developed into a complete Linux audio processing appliance.

## Signal Architecture

    Digital Audio Source
            |
            v
       USB Capture
            |
            v
        SmartDSP
            |
            +-- CamillaDSP
            +-- Nonlinear Voicing
            +-- LV2 Processing
            +-- Metering
            +-- Visualization
            +-- System Management
            |
            v
        USB Audio
            |
            v
           DAC
            |
            v
        Amplifier
            |
            v
         Speakers

## Nonlinear Voicing

SmartDSP includes a selectable nonlinear voicing system.

Unlike conventional EQ, nonlinear processing modifies the transfer function of the signal and can introduce controlled harmonic structure, saturation, asymmetry, peak behavior, and other nonlinear characteristics.

Current profiles include amplifier-, tube-, transformer-, tape-, console-, and topology-inspired voicings.

Examples include:

- Triode
- Tube Buffer
- Tube Preamp
- 300B SET
- 2A3 SET
- 45 SET
- EL34 Push-Pull
- KT88 Push-Pull
- Class-A
- MOSFET Class-A
- High-Bias Class-AB
- Transformer
- Tape
- Studio Console
- Modern Reference

These profiles are transfer-function approximations intended to explore characteristic nonlinear behavior. They should not be interpreted as circuit-level emulations of specific hardware.

## Reference System

SmartDSP is currently developed and evaluated using:

| Function | Equipment |
|---|---|
| Turntable | Technics SL-1300 |
| Phono / Preamp / ADC | WiiM Ultra |
| SmartDSP Host | Raspberry Pi 4 |
| USB DAC | Topping D90 |
| Amplifiers | Fosi Audio V3 Mono x2 |
| Speakers | 1977 Klipsch La Scala |
| Subwoofer | BIC Acoustech Elite PL-300 |

### Main Signal Path

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
    Klipsch La Scala

The BIC PL-300 subwoofer is currently integrated through the WiiM Ultra rather than the SmartDSP processing path.

## Current Voicing Preference

The author's current preferred profiles are:

- **Triode**
- **Tube Buffer**

They provide subtle nonlinear character to an otherwise extremely clean digital and Class-D playback chain.

> The reference system is an example implementation, not required SmartDSP hardware.

## Project Status

SmartDSP is operational in the author's reference audio system.

The public release is currently **Experimental / Development** while installation automation, documentation, hardware abstraction, and packaging are completed.

## License

License selection is pending before the first tagged release.

## Acknowledgements

SmartDSP builds upon open-source projects including CamillaDSP, PipeWire, JACK-compatible tooling, jalv, LV2, and Calf Studio Gear.

Those projects retain their respective copyrights and licenses.
