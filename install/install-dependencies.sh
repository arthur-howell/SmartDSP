#!/usr/bin/env bash
set -euo pipefail

echo "SmartDSP Dependency Installer"
echo "============================="

if [[ $EUID -eq 0 ]]; then
    echo "ERROR: Run this script as your normal SmartDSP user, not root."
    exit 1
fi

command -v sudo >/dev/null 2>&1 || {
    echo "ERROR: sudo is required."
    exit 1
}

command -v apt-get >/dev/null 2>&1 || {
    echo "ERROR: This installer currently supports Debian/Ubuntu systems."
    exit 1
}

echo
echo "Updating package metadata..."
sudo apt-get update

echo
echo "Installing core audio dependencies..."

sudo apt-get install -y \
    python3 \
    alsa-utils \
    pipewire \
    pipewire-audio \
    pipewire-jack \
    wireplumber \
    lv2-dev \
    lilv-utils \
    jalv \
    calf-plugins \
    ffmpeg \
    rsync

echo
echo "Checking optional telemetry packages..."

if ! command -v sensors >/dev/null 2>&1; then
    echo "Installing lm-sensors..."
    sudo apt-get install -y lm-sensors
fi

echo
echo "Checking Raspberry Pi telemetry..."

if [[ -r /proc/device-tree/model ]] &&
   grep -aq "Raspberry Pi" /proc/device-tree/model; then

    if command -v vcgencmd >/dev/null 2>&1; then
        echo "vcgencmd: available"
    else
        echo "WARNING: Raspberry Pi detected but vcgencmd is unavailable."
        echo "Temperature/throttling telemetry will be limited."
    fi
else
    echo "Non-Raspberry-Pi host: vcgencmd not required."
fi

echo
echo "========== DEPENDENCY CHECK =========="

required=(
    python3
    systemctl
    journalctl
    pw-jack
    pw-cli
    pw-link
    wpctl
    jalv
    lv2ls
    arecord
    aplay
    ffmpeg
    rsync
    tar
)

failed=0

for cmd in "${required[@]}"; do
    printf "%-14s " "$cmd"

    if path="$(command -v "$cmd" 2>/dev/null)"; then
        echo "$path"
    else
        echo "MISSING"
        failed=1
    fi
done

echo
printf "%-14s " "sensors"
command -v sensors 2>/dev/null || echo "OPTIONAL / NOT INSTALLED"

printf "%-14s " "vcgencmd"
command -v vcgencmd 2>/dev/null || echo "OPTIONAL / NOT INSTALLED"

echo

if (( failed )); then
    echo "ERROR: One or more required dependencies are unavailable."
    exit 1
fi

echo "PASS: required SmartDSP dependencies are available."
echo
echo "NOTE: CamillaDSP itself is installed separately."
