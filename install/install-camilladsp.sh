#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CONFIG_DIR="${HOME}/.config/smrt-dsp"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

echo "SmartDSP CamillaDSP Installer"
echo "============================="

if ! command -v camilladsp >/dev/null 2>&1; then
    echo "ERROR: CamillaDSP is not installed or not in PATH."
    exit 1
fi

if ! command -v arecord >/dev/null 2>&1 ||
   ! command -v aplay >/dev/null 2>&1; then
    echo "ERROR: ALSA utilities are required."
    exit 1
fi

mkdir -p \
    "$CONFIG_DIR" \
    "$SYSTEMD_DIR"

echo "Installing reference CamillaDSP configuration..."

install -m 0644 \
    "$ROOT/config/camilladsp/reference-192k.yml" \
    "$CONFIG_DIR/camilladsp.yml"

echo "Installing systemd user service..."

install -m 0644 \
    "$ROOT/config/systemd/camilladsp.service" \
    "$SYSTEMD_DIR/camilladsp.service"

systemctl --user daemon-reload
systemctl --user enable camilladsp.service

echo
echo "CamillaDSP configuration installed."
echo
echo "Before starting the service, configure the audio endpoints:"
echo
echo "  ./install/configure-audio.sh"
echo
echo "Then start SmartDSP:"
echo
echo "  systemctl --user start camilladsp"
echo
echo "Check status with:"
echo
echo "  systemctl --user status camilladsp"
