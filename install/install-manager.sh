#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

INSTALL_DIR="${HOME}/.local/share/smartdsp/manager"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

echo "SmartDSP Manager Installer"
echo "=========================="

command -v python3 >/dev/null 2>&1 || {
    echo "ERROR: python3 is required."
    exit 1
}

mkdir -p \
    "$INSTALL_DIR" \
    "$SYSTEMD_DIR" \
    "${HOME}/.config/smrt-dsp"

echo "Installing Manager..."

cp -a "$ROOT/src/manager/." "$INSTALL_DIR/"

find "$INSTALL_DIR" -type d -name '__pycache__' \
    -prune -exec rm -rf {} +

echo "Installing systemd service..."

install -m 0644 \
    "$ROOT/config/systemd/smartdsp-manager.service" \
    "$SYSTEMD_DIR/smartdsp-manager.service"

systemctl --user daemon-reload
systemctl --user enable smartdsp-manager.service

echo
echo "SmartDSP Manager installed."
echo
echo "Start with:"
echo "  systemctl --user start smartdsp-manager"
echo
echo "Status:"
echo "  systemctl --user status smartdsp-manager"
