import io
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path


HOME = Path.home()

STATE_ROOT = HOME / ".local/state/smrt-dsp"
LOCAL_STATE = STATE_ROOT / "known-good"

BACKUP_ROOT = HOME / ".local/share/smrt-dsp/backups"

FORMAT_NAME = "SMRT-DSP-BACKUP"
FORMAT_VERSION = 1


# source, archive-relative destination
BACKUP_ITEMS = [
    (HOME / "camilladsp",                    Path("home/camilladsp")),
    (HOME / ".config/smrt-dsp",              Path("home/.config/smrt-dsp")),
    (HOME / ".config/pipewire",               Path("home/.config/pipewire")),
    (HOME / ".config/systemd/user",           Path("home/.config/systemd/user")),
    (HOME / ".local/bin/dsp-preset",          Path("home/.local/bin/dsp-preset")),
    (HOME / ".local/bin/dsp-routing",         Path("home/.local/bin/dsp-routing")),
    (HOME / "smrt-dsp-manager",               Path("home/smrt-dsp-manager")),
    (HOME / "smrt-dsp-meter",                 Path("home/smrt-dsp-meter")),
    (HOME / "smrt-dsp-visualizer",            Path("home/smrt-dsp-visualizer")),
    (HOME / "wpwgraph/.env",                  Path("home/wpwgraph/.env")),
]


EXCLUDES = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".cache",
}


def command_output(command):
    try:
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
            check=False
        ).stdout.strip()
    except Exception:
        return ""


def manifest():
    model = ""
    try:
        model = Path("/proc/device-tree/model").read_text().replace("\0", "").strip()
    except Exception:
        pass

    return {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "created": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "model": model,
        "kernel": command_output(["uname", "-srmo"]),
        "camilladsp": command_output(
            ["/usr/local/bin/camilladsp", "--version"]
        ),
    }


def excluded(path):
    return any(part in EXCLUDES for part in path.parts)


def copy_item(source, destination):
    if not source.exists():
        return

    if source.is_dir():
        for item in source.rglob("*"):
            rel = item.relative_to(source)

            if excluded(rel):
                continue

            target = destination / rel

            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)

            elif item.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)

    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def create_tree(destination):
    destination.mkdir(parents=True, exist_ok=True)

    for source, relative in BACKUP_ITEMS:
        copy_item(source, destination / relative)

    (destination / "manifest.json").write_text(
        json.dumps(manifest(), indent=2)
    )


def save_local_state():
    STATE_ROOT.mkdir(parents=True, exist_ok=True)

    temp = STATE_ROOT / "known-good.new"

    if temp.exists():
        shutil.rmtree(temp)

    create_tree(temp)

    previous = STATE_ROOT / "known-good.previous"

    if previous.exists():
        shutil.rmtree(previous)

    if LOCAL_STATE.exists():
        LOCAL_STATE.rename(previous)

    temp.rename(LOCAL_STATE)

    return manifest()


def local_state_info():
    manifest_file = LOCAL_STATE / "manifest.json"

    if not manifest_file.exists():
        return {
            "exists": False,
            "created": None
        }

    try:
        data = json.loads(manifest_file.read_text())
        return {
            "exists": True,
            "created": data.get("created")
        }
    except Exception:
        return {
            "exists": True,
            "created": None
        }


def create_backup_zip():
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"smrt-dsp-backup-{stamp}.zip"
    output = BACKUP_ROOT / filename

    with tempfile.TemporaryDirectory(
        prefix="smrt-dsp-backup-"
    ) as td:
        root = Path(td) / "SMRT-DSP"
        create_tree(root)

        with zipfile.ZipFile(
            output,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6
        ) as archive:

            for item in root.rglob("*"):
                if item.is_file():
                    archive.write(
                        item,
                        Path("SMRT-DSP") /
                        item.relative_to(root)
                    )

    return output


def validate_backup(path):
    with zipfile.ZipFile(path, "r") as archive:
        names = set(archive.namelist())

        manifest_name = "SMRT-DSP/manifest.json"

        if manifest_name not in names:
            raise ValueError(
                "Not a SMRT DSP backup: manifest missing"
            )

        data = json.loads(
            archive.read(manifest_name).decode("utf-8")
        )

        if data.get("format") != FORMAT_NAME:
            raise ValueError("Invalid backup format")

        if data.get("version") != FORMAT_VERSION:
            raise ValueError(
                f"Unsupported backup version: "
                f"{data.get('version')}"
            )

        # Block path traversal.
        for name in names:
            p = Path(name)

            if p.is_absolute() or ".." in p.parts:
                raise ValueError(
                    "Unsafe path detected in backup"
                )

        return data


def validate_tree(root):
    manifest_file = root / "manifest.json"

    if not manifest_file.exists():
        raise ValueError("SMRT DSP manifest missing")

    data = json.loads(manifest_file.read_text())

    if data.get("format") != FORMAT_NAME:
        raise ValueError("Invalid SMRT DSP state")

    if data.get("version") != FORMAT_VERSION:
        raise ValueError(
            f"Unsupported state version: {data.get('version')}"
        )

    return data


def restore_tree(root):
    validate_tree(root)

    # Map archive paths back to live locations.
    restore_items = [
        (root / "home/camilladsp",
         HOME / "camilladsp"),

        (root / "home/.config/smrt-dsp",
         HOME / ".config/smrt-dsp"),

        (root / "home/.config/pipewire",
         HOME / ".config/pipewire"),

        (root / "home/.config/systemd/user",
         HOME / ".config/systemd/user"),

        (root / "home/.local/bin/dsp-preset",
         HOME / ".local/bin/dsp-preset"),

        (root / "home/.local/bin/dsp-routing",
         HOME / ".local/bin/dsp-routing"),

        (root / "home/smrt-dsp-manager",
         HOME / "smrt-dsp-manager"),

        (root / "home/smrt-dsp-meter",
         HOME / "smrt-dsp-meter"),

        (root / "home/smrt-dsp-visualizer",
         HOME / "smrt-dsp-visualizer"),

        (root / "home/wpwgraph/.env",
         HOME / "wpwgraph/.env"),
    ]

    for source, destination in restore_items:
        if not source.exists():
            continue

        if source.is_dir():
            destination.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True
            )

        else:
            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )
            shutil.copy2(source, destination)


def create_emergency_snapshot():
    STATE_ROOT.mkdir(parents=True, exist_ok=True)

    emergency = (
        STATE_ROOT /
        f"pre-restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )

    create_tree(emergency)

    return emergency


def restore_local_state():
    if not LOCAL_STATE.exists():
        raise ValueError("No local state has been saved")

    info = validate_tree(LOCAL_STATE)

    emergency = create_emergency_snapshot()

    restore_tree(LOCAL_STATE)

    return {
        "restored": info,
        "emergency_snapshot": str(emergency)
    }


def restore_backup_zip(path):
    path = Path(path)

    # Validate the archive completely before extracting anything.
    info = validate_backup(path)

    emergency = create_emergency_snapshot()

    with tempfile.TemporaryDirectory(
        prefix="smrt-dsp-restore-"
    ) as td:
        td = Path(td)

        with zipfile.ZipFile(path, "r") as archive:
            # validate_backup already checked traversal,
            # but keep extraction rooted in our private temp directory.
            archive.extractall(td)

        root = td / "SMRT-DSP"

        if not root.is_dir():
            raise ValueError(
                "SMRT-DSP root directory missing"
            )

        validate_tree(root)
        restore_tree(root)

    return {
        "restored": info,
        "emergency_snapshot": str(emergency)
    }
