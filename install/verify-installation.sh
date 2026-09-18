#!/usr/bin/env bash
set -u

FAIL=0
WARN=0

pass() {
    printf "PASS  %s\n" "$1"
}

fail() {
    printf "FAIL  %s\n" "$1"
    FAIL=$((FAIL + 1))
}

warn() {
    printf "WARN  %s\n" "$1"
    WARN=$((WARN + 1))
}

echo "SmartDSP Installation Verification"
echo "=================================="
echo

echo "--- Commands ---"

for cmd in python3 camilladsp arecord aplay systemctl; do
    if command -v "$cmd" >/dev/null 2>&1; then
        pass "$cmd"
    else
        fail "$cmd"
    fi
done

for cmd in pw-jack jalv lv2ls ffmpeg rsync; do
    if command -v "$cmd" >/dev/null 2>&1; then
        pass "$cmd"
    else
        warn "$cmd"
    fi
done

echo
echo "--- ALSA ---"

if arecord -L 2>/dev/null | grep -q '^SMARTDSP_CAPTURE$'; then
    pass "SMARTDSP_CAPTURE"
else
    fail "SMARTDSP_CAPTURE"
fi

if aplay -L 2>/dev/null | grep -q '^SMARTDSP_PLAYBACK$'; then
    pass "SMARTDSP_PLAYBACK"
else
    fail "SMARTDSP_PLAYBACK"
fi

echo
echo "--- Configuration ---"

[[ -f "$HOME/.config/smrt-dsp/camilladsp.yml" ]] \
    && pass "CamillaDSP configuration" \
    || fail "CamillaDSP configuration"

[[ -f "$HOME/.config/smrt-dsp/voicings.json" ]] \
    && pass "Voicing library" \
    || warn "Voicing library"

[[ -x "$HOME/.local/bin/dsp-preset" ]] \
    && pass "dsp-preset" \
    || warn "dsp-preset"

[[ -f "$HOME/.local/share/smartdsp/manager/server.py" ]] \
    && pass "SmartDSP Manager" \
    || warn "SmartDSP Manager"

echo
echo "--- Services ---"

for service in \
    camilladsp.service \
    dsp-saturator.service \
    smartdsp-manager.service
do
    if systemctl --user list-unit-files "$service" \
        --no-legend 2>/dev/null | grep -q "$service"; then
        pass "$service installed"
    else
        warn "$service not installed"
    fi
done

echo
echo "=================================="
echo "Failures: $FAIL"
echo "Warnings: $WARN"

if (( FAIL > 0 )); then
    exit 1
fi

echo "SmartDSP core verification passed."
exit 0
