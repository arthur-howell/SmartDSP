# SmartDSP Signal Path

The current SmartDSP reference installation provides a high-resolution USB-to-USB digital processing path.

## Current Processing Format

The active reference configuration operates at:

- **Sample Rate:** 192,000 Hz
- **Sample Format:** S32_LE
- **Channels:** 2
- **Topology:** Stereo USB capture to USB playback

S32_LE describes the 32-bit sample container used by the Linux audio pipeline. It does not imply that the original source contains 32 bits of meaningful audio resolution.

## Reference Signal Chain

    Technics SL-1300
    Turntable
         |
         | Analog Phono
         v
    WiiM Ultra
    Phono Stage / Preamp / ADC
         |
         | USB Audio
         v
    Raspberry Pi 4
    SmartDSP
    192 kHz / S32_LE
         |
         | USB Audio
         v
    Topping D90
    DAC
         |
         | Balanced XLR
         v
    Fosi Audio V3 Mono x2
         |
         | Speaker Level
         v
    1977 Klipsch La Scala

## Analog-to-Digital Conversion

For vinyl playback, the original analog signal enters the WiiM Ultra through its phono input.

The WiiM performs:

    Phono Input
         |
         v
    Phono Preamplification
         |
         v
    Analog-to-Digital Conversion
         |
         v
    Digital Audio

From this point forward, the primary signal remains digital until it reaches the Topping D90.

## SmartDSP Processing

The WiiM Ultra sends digital audio over USB to the SmartDSP host.

Conceptually:

    USB Capture
         |
         v
    PipeWire / JACK
         |
         v
    SmartDSP Processing
         |
         +---- CamillaDSP
         |
         +---- Nonlinear Voicing
         |
         +---- Additional LV2 Processing
         |
         +---- Metering / Analysis
         |
         v
    USB Playback

The exact routing graph may vary depending upon the active SmartDSP configuration.

## Digital-to-Analog Conversion

After SmartDSP processing, the digital signal is sent over USB to the Topping D90.

The D90 performs the final digital-to-analog conversion for the main left and right channels.

    SmartDSP
         |
         | USB Digital
         v
    Topping D90
         |
         | Analog
         v
    Amplification

## Amplification

The reference system uses two Fosi Audio V3 Mono power amplifiers.

The Topping D90 feeds the amplifiers using balanced XLR connections.

Each monoblock drives one Klipsch La Scala loudspeaker.

## Loudspeakers

The reference loudspeakers are a pair of 1977 Klipsch La Scalas.

Their high sensitivity makes very small changes in noise, gain structure, nonlinear processing, and upstream electronics readily observable during SmartDSP development.

## Subwoofer Path

The current subwoofer is a BIC Acoustech Elite PL-300.

It is presently integrated at the WiiM Ultra rather than through SmartDSP.

    WiiM Ultra
         |
         | Subwoofer Output
         v
    BIC PL-300

This means the current SmartDSP USB processing path is responsible for the primary left and right channels while the WiiM manages the subwoofer path.

Bass management may be incorporated into SmartDSP in a future configuration.

## Current Reference Voicings

The most frequently used voicing profiles during current development are:

- **Triode**
- **Tube Buffer**

These profiles are used to introduce controlled nonlinear character into an otherwise very clean digital and Class-D signal chain.

## Hardware Independence

The equipment described above documents the system in which SmartDSP was developed.

It is not a required hardware configuration.

Conceptually, SmartDSP requires only:

    Compatible Digital Audio Source
                |
                v
        Linux SmartDSP Host
                |
                v
         Compatible DAC

The surrounding source equipment, DAC, amplification, loudspeakers, and subwoofer can be changed independently of SmartDSP.
