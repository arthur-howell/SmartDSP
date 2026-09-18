# SmartDSP Dependencies

SmartDSP combines several Linux audio projects into a unified digital signal-processing platform.

## Core Audio Components

### PipeWire

PipeWire provides the underlying Linux audio graph and device management.

SmartDSP uses PipeWire for communication between audio devices and processing components.

### JACK Compatibility

PipeWire's JACK compatibility layer allows JACK-oriented applications to participate in the PipeWire audio graph.

SmartDSP uses `pw-jack` when launching compatible processing components.

### CamillaDSP

CamillaDSP provides the primary high-resolution DSP engine.

It handles the principal digital processing pipeline, including filtering and routing.

Project:

https://github.com/HEnquist/camilladsp

### LV2

LV2 provides the plugin architecture used by SmartDSP's nonlinear processing system.

### jalv

`jalv` is the command-line LV2 host currently used by the SmartDSP voicing engine.

SmartDSP launches the nonlinear processor through:

    PipeWire
        |
        v
      pw-jack
        |
        v
       jalv
        |
        v
    LV2 Plugin

### Calf Studio Gear

The current nonlinear voicing implementation uses the Calf Saturator LV2 plugin:

    http://calf.sourceforge.net/plugins/Saturator

The plugin is hosted by `jalv` and controlled at runtime through a Unix FIFO.

## Python

SmartDSP utilities require Python 3.

The current `dsp-preset` utility uses Python standard-library components including:

- json
- pathlib
- subprocess
- sys

## systemd

SmartDSP uses systemd user services for persistent processing components.

The nonlinear voicing engine currently uses:

    ~/.config/systemd/user/dsp-saturator.service

This service creates the control FIFO and launches the LV2 processing engine.

## Optional Tools

### WPWGraph

WPWGraph provides graphical inspection and manipulation of the PipeWire graph.

It is useful for:

- Troubleshooting
- Experimental routing
- Alternate USB sources
- Alternate USB destinations
- Additional processing stages
- Manual graph inspection

WPWGraph is not required for normal preset operation.

### lv2ls

`lv2ls` can be used to enumerate installed LV2 plugins.

The SmartDSP voicing installer uses it when available to verify that the required Calf Saturator plugin exists.

## Current Reference Platform

The development/reference installation currently uses:

    Raspberry Pi 4
    Linux
    PipeWire / JACK
    CamillaDSP
    192 kHz
    S32_LE
    Stereo USB Input
    Stereo USB Output

The project is intended to become increasingly hardware-independent as installation automation develops.
