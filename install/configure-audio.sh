#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$ROOT/config/alsa/smartdsp.conf.template"
OUTPUT="${HOME}/.asoundrc"

echo "SmartDSP Audio Configuration"
echo "============================"
echo
echo "Available CAPTURE devices:"
echo
arecord -l
echo
read -rp "ALSA capture CARD identifier: " CAPTURE_CARD

echo
echo "Available PLAYBACK devices:"
echo
aplay -l
echo
read -rp "ALSA playback CARD identifier: " PLAYBACK_CARD

[[ "$CAPTURE_CARD" =~ ^[A-Za-z0-9_-]+$ ]] || {
    echo "ERROR: Invalid capture card identifier."
    exit 1
}

[[ "$PLAYBACK_CARD" =~ ^[A-Za-z0-9_-]+$ ]] || {
    echo "ERROR: Invalid playback card identifier."
    exit 1
}

if [[ -f "$OUTPUT" ]]; then
    BACKUP="${OUTPUT}.smartdsp-backup-$(date +%Y%m%d-%H%M%S)"
    cp -a "$OUTPUT" "$BACKUP"
    echo
    echo "Existing .asoundrc backed up to:"
    echo "  $BACKUP"
fi

sed \
    -e "s/SMARTDSP_CAPTURE_CARD/${CAPTURE_CARD}/g" \
    -e "s/SMARTDSP_PLAYBACK_CARD/${PLAYBACK_CARD}/g" \
    "$TEMPLATE" > "$OUTPUT"

echo
echo "Configured:"
echo "  SMARTDSP_CAPTURE  -> hw:CARD=${CAPTURE_CARD},DEV=0"
echo "  SMARTDSP_PLAYBACK -> hw:CARD=${PLAYBACK_CARD},DEV=0"

echo
echo "ALSA definitions:"
aplay -L | grep -E 'SMARTDSP_CAPTURE|SMARTDSP_PLAYBACK' || true
arecord -L | grep -E 'SMARTDSP_CAPTURE|SMARTDSP_PLAYBACK' || true
