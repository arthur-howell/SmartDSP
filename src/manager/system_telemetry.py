import os
import re
import time
import shutil
import subprocess
from pathlib import Path


HOME = Path.home()


def run(cmd, timeout=2):
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=timeout,
            check=False,
        )
        return p.stdout.strip()
    except Exception:
        return ""


def read(path, default=""):
    try:
        return Path(path).read_text().strip().replace("\x00", "")
    except Exception:
        return default


def service_state(name, user=True):
    cmd = ["systemctl"]
    if user:
        cmd.append("--user")
    cmd += ["is-active", name]

    value = run(cmd)

    if value == "active":
        return "active"
    if value == "inactive":
        return "inactive"
    if value == "failed":
        return "failed"

    return value or "unknown"


def oneshot_state(name):
    # Oneshot services normally become inactive after successful completion.
    result = run([
        "systemctl", "--user", "show", name,
        "--property=Result",
        "--value"
    ])
    return "complete" if result == "success" else (result or "unknown")


def vcgencmd(*args):
    if not shutil.which("vcgencmd"):
        return ""
    return run(["vcgencmd", *args])


def parse_number(text, pattern):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def throttle_info():
    raw = vcgencmd("get_throttled")
    try:
        value = int(raw.split("=")[1], 16)
    except Exception:
        value = 0

    return {
        "raw": raw or "unavailable",
        "value": value,

        "undervoltage_now": bool(value & (1 << 0)),
        "frequency_capped_now": bool(value & (1 << 1)),
        "throttled_now": bool(value & (1 << 2)),
        "soft_temp_limit_now": bool(value & (1 << 3)),

        "undervoltage_occurred": bool(value & (1 << 16)),
        "frequency_cap_occurred": bool(value & (1 << 17)),
        "throttling_occurred": bool(value & (1 << 18)),
        "soft_temp_limit_occurred": bool(value & (1 << 19)),
    }


def memory_info():
    mem = {}
    for line in read("/proc/meminfo").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        try:
            mem[key] = int(value.strip().split()[0]) * 1024
        except Exception:
            pass

    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", 0)

    return {
        "total_bytes": total,
        "used_bytes": max(0, total - available),
        "available_bytes": available,
    }


def uptime_info():
    try:
        seconds = float(read("/proc/uptime").split()[0])
    except Exception:
        seconds = 0

    return {
        "seconds": int(seconds),
        "human": (
            f"{int(seconds // 86400)}d "
            f"{int((seconds % 86400) // 3600)}h "
            f"{int((seconds % 3600) // 60)}m"
        )
    }


def usb_info():
    raw = run(["lsusb"])

    devices = []
    for line in raw.splitlines():
        if line:
            devices.append(line)

    audio_cards = run(["aplay", "-l"])
    capture_cards = run(["arecord", "-l"])

    return {
        "devices": devices,
        "playback": audio_cards,
        "capture": capture_cards,

        # These become true automatically once hardware appears.
        "d90_detected": bool(
            re.search(r"Topping|D90", raw + "\n" + audio_cards, re.I)
        ),
        "wiim_detected": bool(
            re.search(r"WiiM", raw + "\n" + capture_cards, re.I)
        ),
    }


def pipewire_info():
    rate = None
    quantum = None

    status = run(["pw-metadata", "-n", "settings"])

    m = re.search(r"clock\.rate.*?value:'?(\d+)", status)
    if m:
        rate = int(m.group(1))

    m = re.search(r"clock\.quantum.*?value:'?(\d+)", status)
    if m:
        quantum = int(m.group(1))

    # Known configured values are still useful if metadata presentation
    # changes between PipeWire releases.
    if rate is None:
        rate = 192000
    if quantum is None:
        quantum = 1024

    return {
        "pipewire": service_state("pipewire.service"),
        "wireplumber": service_state("wireplumber.service"),
        "rate": rate,
        "quantum": quantum,
    }


def preset():
    return read(
        HOME / ".config/smrt-dsp/current-preset",
        "unknown"
    )


def system_snapshot():
    temp_raw = vcgencmd("measure_temp")
    arm_clock = vcgencmd("measure_clock", "arm")
    core_clock = vcgencmd("measure_clock", "core")
    volts = vcgencmd("measure_volts", "core")

    load = read("/proc/loadavg").split()

    return {
        "timestamp": time.time(),

        "pi": {
            "model": read(
                "/proc/device-tree/model",
                "Raspberry Pi"
            ),
            "temperature_c": parse_number(
                temp_raw, r"=([\d.]+)"
            ),
            "cpu_mhz": (
                parse_number(arm_clock, r"=(\d+)") or 0
            ) / 1_000_000,
            "core_mhz": (
                parse_number(core_clock, r"=(\d+)") or 0
            ) / 1_000_000,
            "core_voltage": parse_number(
                volts, r"=([\d.]+)"
            ),
            "throttle": throttle_info(),
            "uptime": uptime_info(),
            "memory": memory_info(),
            "load": [
                float(x) for x in load[:3]
            ] if len(load) >= 3 else [0, 0, 0],
            "kernel": run(["uname", "-srmo"]),
        },

        "audio": {
            "pipewire": pipewire_info(),
            "camilladsp": service_state(
                "camilladsp.service"
            ),
            "saturator": service_state(
                "dsp-saturator.service"
            ),
            "routing": service_state(
                "dsp-routing.service"
            ),
            "meter": service_state(
                "smrt-dsp-meter.service"
            ),
            "preset": preset(),
        },

        "usb": usb_info(),

        "services": {
            "camilladsp": service_state(
                "camilladsp.service"
            ),
            "dsp_saturator": service_state(
                "dsp-saturator.service"
            ),
            "dsp_routing": service_state(
                "dsp-routing.service"
            ),
            "dsp_meter": service_state(
                "smrt-dsp-meter.service"
            ),
            "preset_restore": oneshot_state(
                "dsp-preset-restore.service"
            ),
            "wpwgraph_web": service_state(
                "wpwgraph-web.service"
            ),
            "wpwgraph_reverb": service_state(
                "wpwgraph-reverb.service"
            ),
            "wpwgraph_watch": service_state(
                "wpwgraph-watch.service"
            ),
            "manager": service_state(
                "smrt-dsp-manager.service"
            ),
            "pipewire": service_state(
                "pipewire.service"
            ),
            "wireplumber": service_state(
                "wireplumber.service"
            ),
        }
    }
