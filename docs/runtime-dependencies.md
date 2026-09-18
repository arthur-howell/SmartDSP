# SmartDSP Runtime Dependencies

SmartDSP uses a combination of Linux audio infrastructure, command-line
utilities, and Python.

## Required

### Core

- Python 3
- systemd
- ALSA utilities
- CamillaDSP

### Audio Infrastructure

- PipeWire
- PipeWire JACK compatibility
- WirePlumber

### Voicing Engine

- LV2
- Lilv utilities
- jalv
- Calf Studio Gear plugins

The current nonlinear voicing engine uses the Calf Saturator LV2 plugin.

### Utilities

- FFmpeg
- rsync
- tar

## Optional Telemetry

### lm-sensors

Provides additional hardware temperature and sensor information where
supported.

SmartDSP remains functional without it.

### vcgencmd

Used on Raspberry Pi systems for:

- SoC temperature
- throttling state
- undervoltage state
- frequency limiting

It is not required on non-Raspberry-Pi systems.

## CamillaDSP

CamillaDSP is deliberately not installed automatically by the generic
APT dependency installer.

SmartDSP currently targets CamillaDSP 4.x.

The installed binary must be available as:

    camilladsp

or installed at the platform-appropriate executable location.

## Installation

Install distribution-provided dependencies with:

    ./install/install-dependencies.sh

Then configure the audio endpoints:

    ./install/configure-audio.sh

Install the CamillaDSP configuration:

    ./install/install-camilladsp.sh

Install the voicing subsystem:

    ./install/install-voicing.sh

Install the Manager:

    ./install/install-manager.sh
