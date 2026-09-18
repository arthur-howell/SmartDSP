#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CONFIG_DIR="${HOME}/.config/smrt-dsp"
BIN_DIR="${HOME}/.local/bin"
RUN_DIR="${HOME}/.local/run"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

echo "SmartDSP Voicing Engine Installer"
echo "================================="

# Verify required commands
for cmd in python3 systemctl pw-jack jalv; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "ERROR: Required command not found: $cmd"
        exit 1
    fi
done

# Verify Calf Saturator LV2 exists
if command -v lv2ls >/dev/null 2>&1; then
    if ! lv2ls | grep -q 'http://calf.sourceforge.net/plugins/Saturator'; then
        echo "ERROR: Calf Saturator LV2 plugin not found."
        exit 1
    fi
else
    echo "WARNING: lv2ls unavailable; skipping LV2 plugin verification."
fi

echo "Creating SmartDSP directories..."

mkdir -p \
    "$CONFIG_DIR" \
    "$BIN_DIR" \
    "$RUN_DIR" \
    "$SYSTEMD_DIR"

echo "Installing voicing library..."

install -m 0644 \
    "$ROOT/voicing/config/voicings.json" \
    "$CONFIG_DIR/voicings.json"

echo "Installing dsp-preset..."

install -m 0755 \
    "$ROOT/voicing/bin/dsp-preset" \
    "$BIN_DIR/dsp-preset"

echo "Installing systemd service..."

install -m 0644 \
    "$ROOT/config/systemd/dsp-saturator.service" \
    "$SYSTEMD_DIR/dsp-saturator.service"

echo "Reloading user systemd..."

systemctl --user daemon-reload

echo "Enabling DSP saturator..."

systemctl --user enable dsp-saturator.service

echo "Starting DSP saturator..."

systemctl --user restart dsp-saturator.service

sleep 1

if systemctl --user is-active --quiet dsp-saturator.service; then
    echo "DSP saturator: ACTIVE"
else
    echo "ERROR: dsp-saturator.service failed to start."
    systemctl --user status dsp-saturator.service --no-pager || true
    exit 1
fi

echo
echo "Installed successfully."
echo
echo "Available voicings:"
"$BIN_DIR/dsp-preset" list

echo
echo "Current status:"
"$BIN_DIR/dsp-preset" status
