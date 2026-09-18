# SmartDSP Manager

SmartDSP Manager is the web-based control and observability interface for SmartDSP.

It provides a unified interface for the DSP system rather than requiring direct interaction with each underlying service.

## Components

The Manager consists of:

- `server.py` — Manager HTTP/API backend
- `index.html` — primary SmartDSP interface
- `backup_manager.py` — backup and restore support
- `system_telemetry.py` — host and DSP telemetry
- `quantum-horizon.html` — physics-based audio visualizer
- `vendor/` — locally hosted frontend dependencies

## Interface

The Manager provides access to the major SmartDSP subsystems:

- Overview
- CamillaDSP
- Audio routing
- Voicing
- Signal meters
- Now Playing
- Visualizer
- System management
- Backup and restore

## Architecture

The Manager is a control and observability layer.

It is intentionally separate from the real-time audio path:

    Audio Plane
    ===========
    USB Input
        |
    CamillaDSP
        |
    DSP / Voicing
        |
    USB DAC


    Management Plane
    ================
    SmartDSP Manager
        |
        +-- CamillaDSP control
        +-- Voicing presets
        +-- Telemetry
        +-- Routing tools
        +-- Visualizer
        +-- Service management
        +-- Backup / restore

Failure of the Manager should not interrupt the primary audio path.

## Installation

Install the Manager with:

    ./install/install-manager.sh

The installer places the application under:

    ~/.local/share/smartdsp/manager

and installs the user service:

    ~/.config/systemd/user/smartdsp-manager.service

Start it with:

    systemctl --user start smartdsp-manager

Enable it at login with:

    systemctl --user enable smartdsp-manager

Check status with:

    systemctl --user status smartdsp-manager

## Voicing Integration

The Manager expects the SmartDSP voicing utility at:

    ~/.local/bin/dsp-preset

and the voicing library at:

    ~/.config/smrt-dsp/voicings.json

The current preset state is stored at:

    ~/.config/smrt-dsp/current-preset

## CamillaDSP

CamillaDSP remains the primary DSP engine.

The Manager provides access to the CamillaDSP interface but does not replace CamillaDSP or participate directly in the real-time audio stream.

## Visualizer

The included Quantum Horizon visualizer is an experimental audio-reactive visualization based on physics-inspired motion.

Visualization is deliberately treated as a secondary workload.

It must never be allowed to block or introduce latency into the audio-processing path.

## Now Playing

Audio identification / Now Playing functionality is experimental.

Development currently exists separately from the stable SmartDSP Manager because audio identification must remain completely isolated from the real-time audio path.

## Portability

Repository versions of the Manager do not contain the original development host's username, home-directory path, or private IP addresses.

User-specific paths are derived at runtime using the current user's home directory.

## Design Principle

SmartDSP separates real-time audio processing from management and optional workloads.

The fundamental rule is:

> Nothing in the management, visualization, identification, or observability planes should be capable of blocking the audio plane.
