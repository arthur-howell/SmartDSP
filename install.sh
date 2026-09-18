#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo
echo "========================================"
echo "             SmartDSP Setup"
echo "========================================"
echo
echo "This installer configures the SmartDSP"
echo "high-resolution audio processing system."
echo
echo "Installation stages:"
echo
echo "  1. Runtime dependencies"
echo "  2. ALSA audio endpoints"
echo "  3. CamillaDSP configuration"
echo "  4. Nonlinear voicing engine"
echo "  5. SmartDSP Manager"
echo

if [[ $EUID -eq 0 ]]; then
    echo "ERROR: Run SmartDSP as your normal user, not root."
    exit 1
fi

run_stage() {
    local name="$1"
    local script="$2"

    echo
    echo "========================================"
    echo "$name"
    echo "========================================"
    echo

    if [[ ! -x "$script" ]]; then
        echo "ERROR: Missing installer:"
        echo "  $script"
        exit 1
    fi

    "$script"
}

ask() {
    local prompt="$1"

    while true; do
        read -rp "$prompt [Y/n]: " answer
        answer="${answer:-Y}"

        case "$answer" in
            [Yy]|[Yy][Ee][Ss])
                return 0
                ;;
            [Nn]|[Nn][Oo])
                return 1
                ;;
            *)
                echo "Please answer yes or no."
                ;;
        esac
    done
}

echo "SmartDSP repository:"
echo "  $ROOT"
echo

if ask "Install/verify system dependencies?"; then
    run_stage \
        "Stage 1/5 - Dependencies" \
        "$ROOT/install/install-dependencies.sh"
else
    echo "Skipping dependency installation."
fi

if ask "Configure ALSA capture and playback endpoints?"; then
    run_stage \
        "Stage 2/5 - Audio Endpoints" \
        "$ROOT/install/configure-audio.sh"
else
    echo "Skipping ALSA configuration."
fi

if ask "Install the CamillaDSP SmartDSP configuration?"; then
    run_stage \
        "Stage 3/5 - CamillaDSP" \
        "$ROOT/install/install-camilladsp.sh"
else
    echo "Skipping CamillaDSP configuration."
fi

if ask "Install the nonlinear voicing engine?"; then
    run_stage \
        "Stage 4/5 - Voicing Engine" \
        "$ROOT/install/install-voicing.sh"
else
    echo "Skipping voicing engine."
fi

if ask "Install the SmartDSP Manager?"; then
    run_stage \
        "Stage 5/5 - SmartDSP Manager" \
        "$ROOT/install/install-manager.sh"
else
    echo "Skipping SmartDSP Manager."
fi

echo
echo "========================================"
echo "          Installation Complete"
echo "========================================"
echo
echo "Installed services can be inspected with:"
echo
echo "  systemctl --user status camilladsp"
echo "  systemctl --user status dsp-saturator"
echo "  systemctl --user status smartdsp-manager"
echo
echo "SmartDSP configuration:"
echo "  ~/.config/smrt-dsp/"
echo
echo "Manager installation:"
echo "  ~/.local/share/smartdsp/manager/"
echo
echo "Voicing utility:"
echo "  ~/.local/bin/dsp-preset"
echo
