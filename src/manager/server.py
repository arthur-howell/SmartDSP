from pathlib import Path
#!/usr/bin/env python3

import json
import os
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import asyncio
import threading
import websockets

# SMRT_METER_BRIDGE
meter_latest = {}
meter_lock = threading.Lock()

async def meter_receiver():
    global meter_latest

    while True:
        try:
            async with websockets.connect("ws://127.0.0.1:8091") as ws:
                async for message in ws:
                    data = json.loads(message)
                    with meter_lock:
                        meter_latest = data
        except Exception:
            await asyncio.sleep(1)

def meter_thread():
    asyncio.run(meter_receiver())

threading.Thread(target=meter_thread, daemon=True).start()

from urllib.parse import urlparse
from urllib.request import Request, urlopen
import socket
import select
from system_telemetry import system_snapshot
from backup_manager import (
    save_local_state,
    local_state_info,
    create_backup_zip,
    restore_local_state,
    restore_backup_zip
)

BASE_DIR = str(Path(__file__).resolve().parent)
PRESET_CMD = str(Path.home() / ".local/bin/dsp-preset")
PRESET_STATE = str(Path.home() / ".config/smrt-dsp/current-preset")

VOICINGS_FILE = str(Path.home() / ".config/smrt-dsp/voicings.json")

def load_voicings():
    try:
        with open(VOICINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}

def valid_presets():
    return set(load_voicings().keys())

os.chdir(BASE_DIR)


def current_preset():
    try:
        with open(PRESET_STATE, "r", encoding="utf-8") as f:
            preset = f.read().strip().lower()

        if preset in valid_presets():
            return preset
    except OSError:
        pass

    return "unknown"



# SMRT visualizer static asset MIME mappings
import mimetypes

mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/wasm", ".wasm")

class ManagerHandler(SimpleHTTPRequestHandler):

    VISUALIZER_STATE = (
        str(Path.home() / ".config") + "/"
        "smrt-dsp/visualizer-state.json"
    )

    VALID_VISUALIZERS = {
        "Spectrum",
        "Gravity"
    }

    def send_json(self, data, status=200):
        payload = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Content-Length",
            str(len(payload))
        )
        self.send_header(
            "Cache-Control",
            "no-store"
        )
        self.end_headers()

        self.wfile.write(payload)

    def read_visualizer_state(self):
        with open(
            self.VISUALIZER_STATE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    def write_visualizer_state(self, state):
        target = Path(self.VISUALIZER_STATE)
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            json.dumps(state, indent=2) + "\n",
            encoding="utf-8"
        )

        temporary.replace(target)

    def proxy_gravity_websocket(self):
        """
        Tunnel the browser WebSocket to the Quantum Engine.
        Browser sees /gravity/ws on the Manager.
        Quantum remains local at 127.0.0.1:8092/ws.
        """

        upstream = None

        try:
            upstream = socket.create_connection(
                ("127.0.0.1", 8092),
                timeout=5
            )

            request_lines = [
                "GET /ws HTTP/1.1",
                "Host: 127.0.0.1:8092",
                "Upgrade: websocket",
                "Connection: Upgrade"
            ]

            for header in (
                "Sec-WebSocket-Key",
                "Sec-WebSocket-Version",
                "Sec-WebSocket-Protocol",
                "Sec-WebSocket-Extensions",
                "Origin"
            ):
                value = self.headers.get(header)

                if value:
                    request_lines.append(
                        f"{header}: {value}"
                    )

            request_lines.extend(["", ""])

            upstream.sendall(
                "\r\n".join(request_lines)
                .encode("latin-1")
            )

            response = b""

            while b"\r\n\r\n" not in response:
                chunk = upstream.recv(4096)

                if not chunk:
                    raise ConnectionError(
                        "Quantum WebSocket closed during handshake"
                    )

                response += chunk

            header, remainder = response.split(
                b"\r\n\r\n",
                1
            )

            if b" 101 " not in header.split(b"\r\n", 1)[0]:
                raise ConnectionError(
                    "Quantum WebSocket upgrade rejected: " +
                    header.split(
                        b"\r\n",
                        1
                    )[0].decode(
                        "latin-1",
                        errors="replace"
                    )
                )

            self.connection.sendall(
                header +
                b"\r\n\r\n" +
                remainder
            )

            self.connection.settimeout(None)
            upstream.settimeout(None)

            connections = [
                self.connection,
                upstream
            ]

            while True:
                readable, _, _ = select.select(
                    connections,
                    [],
                    [],
                    60
                )

                for source in readable:
                    data = source.recv(65536)

                    if not data:
                        return

                    destination = (
                        upstream
                        if source is self.connection
                        else self.connection
                    )

                    destination.sendall(data)

        except Exception as exc:
            print(
                "Gravity WebSocket proxy error:",
                exc,
                flush=True
            )

        finally:
            if upstream is not None:
                try:
                    upstream.close()
                except Exception:
                    pass

    def do_GET(self):
        path = urlparse(self.path).path

        # Quantum Gravity WebSocket proxy.
        if (
            path == "/gravity/ws"
            and self.headers.get(
                "Upgrade",
                ""
            ).lower() == "websocket"
        ):
            self.proxy_gravity_websocket()
            return

        # Quantum Gravity HTTP proxy.
        # Browser requests /gravity/* from the manager;
        # manager retrieves it locally from quantumd :8092.
        if path == "/gravity" or path.startswith("/gravity/"):

            upstream_path = path[len("/gravity"):]

            if not upstream_path:
                upstream_path = "/"

            try:
                request = Request(
                    "http://127.0.0.1:8092" + upstream_path,
                    headers={
                        "User-Agent": "SMRT-DSP-Manager"
                    }
                )

                with urlopen(
                    request,
                    timeout=5
                ) as response:

                    data = response.read()

                    self.send_response(
                        response.status
                    )

                    content_type = (
                        response.headers.get(
                            "Content-Type",
                            "application/octet-stream"
                        )
                    )

                    self.send_header(
                        "Content-Type",
                        content_type
                    )

                    self.send_header(
                        "Content-Length",
                        str(len(data))
                    )

                    self.send_header(
                        "Cache-Control",
                        "no-store"
                    )

                    self.end_headers()
                    self.wfile.write(data)

            except Exception as exc:

                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 502)

            return

        if path == "/api/voicings":
            self.send_json({
                "voicings": load_voicings(),
                "preset": current_preset()
            })
            return

        if path == "/api/voicing":
            self.send_json({
                "preset": current_preset()
            })
            return

        if path == "/api/now-playing":
            try:
                with open(
                    str(Path.home() / ".config") + "/"
                    "smrt-dsp/now-playing.json",
                    "r",
                    encoding="utf-8"
                ) as f:
                    self.send_json(json.load(f))

            except Exception as exc:
                self.send_json({
                    "state": "error",
                    "identified": False,
                    "error": str(exc)
                }, 500)

            return

        if path == "/api/system/backup/status":
            self.send_json(local_state_info())
            return

        if path == "/api/system/backup/download":
            try:
                backup = create_backup_zip()
                data = backup.read_bytes()

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "application/zip"
                )
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="{backup.name}"'
                )
                self.send_header(
                    "Content-Length",
                    str(len(data))
                )
                self.end_headers()
                self.wfile.write(data)

            except Exception as exc:
                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 500)

            return

        if path == "/api/system":
            try:
                self.send_json(system_snapshot())
            except Exception as exc:
                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 500)
            return

        if path == "/api/meters":
            with meter_lock:
                data = dict(meter_latest)

            self.send_json(data)
            return

        if path == "/api/visualizer-state":
            try:
                self.send_json(
                    self.read_visualizer_state()
                )

            except Exception as exc:
                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 500)

            return

        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/system/backup/restore-upload":
            temp_path = None

            try:
                content_type = self.headers.get(
                    "Content-Type", ""
                )

                if "application/zip" not in content_type:
                    raise ValueError(
                        "Upload must be a ZIP archive"
                    )

                length = int(
                    self.headers.get("Content-Length", "0")
                )

                max_size = 64 * 1024 * 1024

                if length <= 0:
                    raise ValueError("Empty backup upload")

                if length > max_size:
                    raise ValueError(
                        "Backup exceeds 64 MB limit"
                    )

                import tempfile

                with tempfile.NamedTemporaryFile(
                    prefix="smrt-upload-",
                    suffix=".zip",
                    delete=False
                ) as temp:
                    temp_path = temp.name

                    remaining = length

                    while remaining:
                        chunk = self.rfile.read(
                            min(1024 * 1024, remaining)
                        )

                        if not chunk:
                            raise ValueError(
                                "Incomplete backup upload"
                            )

                        temp.write(chunk)
                        remaining -= len(chunk)

                result = restore_backup_zip(temp_path)

                subprocess.run(
                    ["systemctl", "--user", "daemon-reload"],
                    check=False,
                    timeout=10
                )

                services = [
                    "pipewire.service",
                    "wireplumber.service",
                    "camilladsp.service",
                    "dsp-saturator.service",
                    "dsp-routing.service",
                    "smrt-dsp-meter.service",
                    "camillagui.service",
                    "wpwgraph-web.service",
                    "wpwgraph-reverb.service",
                    "wpwgraph-watch.service",
                ]

                restart = subprocess.run(
                    ["systemctl", "--user", "restart", *services],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30
                )

                self.send_json({
                    "success": restart.returncode == 0,
                    "restored_created":
                        result["restored"].get("created"),
                    "emergency_snapshot":
                        result["emergency_snapshot"],
                    "service_error":
                        restart.stderr.strip() or None
                }, 200 if restart.returncode == 0 else 500)

            except Exception as exc:
                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 400)

            finally:
                if temp_path:
                    try:
                        Path(temp_path).unlink(
                            missing_ok=True
                        )
                    except Exception:
                        pass

            return

        if path == "/api/system/backup/restore-local":
            try:
                result = restore_local_state()

                subprocess.run(
                    ["systemctl", "--user", "daemon-reload"],
                    check=False,
                    timeout=10
                )

                services = [
                    "pipewire.service",
                    "wireplumber.service",
                    "camilladsp.service",
                    "dsp-saturator.service",
                    "dsp-routing.service",
                    "smrt-dsp-meter.service",
                    "camillagui.service",
                    "wpwgraph-web.service",
                    "wpwgraph-reverb.service",
                    "wpwgraph-watch.service",
                ]

                restart = subprocess.run(
                    ["systemctl", "--user", "restart", *services],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30
                )

                self.send_json({
                    "success": restart.returncode == 0,
                    "restored_created":
                        result["restored"].get("created"),
                    "emergency_snapshot":
                        result["emergency_snapshot"],
                    "service_error":
                        restart.stderr.strip() or None
                }, 200 if restart.returncode == 0 else 500)

            except Exception as exc:
                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 500)

            return

        if path == "/api/system/backup/save":
            try:
                info = save_local_state()

                self.send_json({
                    "success": True,
                    "created": info.get("created")
                })

            except Exception as exc:
                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 500)

            return

        if path.startswith("/api/system/action/"):
            action = path.rsplit("/", 1)[-1]

            actions = {
                "restart-audio": [
                    ["systemctl", "--user", "restart",
                     "camilladsp.service",
                     "dsp-saturator.service",
                     "dsp-routing.service",
                     "smrt-dsp-meter.service"]
                ],
                "restart-pipewire": [
                    ["systemctl", "--user", "restart",
                     "pipewire.service",
                     "wireplumber.service"]
                ],
                "restart-web": [
                    ["systemctl", "--user", "restart",
                     "camillagui.service",
                     "wpwgraph-web.service",
                     "wpwgraph-reverb.service",
                     "wpwgraph-watch.service"]
                ]
            }

            if action not in actions:
                self.send_json({
                    "success": False,
                    "error": "Unknown system action"
                }, 404)
                return

            try:
                for command in actions[action]:
                    result = subprocess.run(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=20
                    )

                    if result.returncode != 0:
                        self.send_json({
                            "success": False,
                            "action": action,
                            "error":
                                result.stderr.strip()
                                or result.stdout.strip()
                        }, 500)
                        return

                self.send_json({
                    "success": True,
                    "action": action
                })

            except Exception as exc:
                self.send_json({
                    "success": False,
                    "action": action,
                    "error": str(exc)
                }, 500)

            return

        if path.startswith("/api/voicing/"):
            preset = path.rsplit("/", 1)[-1].lower()

            if preset not in valid_presets():
                self.send_json({
                    "success": False,
                    "error": "invalid preset"
                }, 400)
                return

            try:
                result = subprocess.run(
                    [PRESET_CMD, preset],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode != 0:
                    self.send_json({
                        "success": False,
                        "preset": current_preset(),
                        "error":
                            result.stderr.strip()
                            or result.stdout.strip()
                    }, 500)
                    return

                self.send_json({
                    "success": True,
                    "preset": current_preset()
                })

            except Exception as exc:
                self.send_json({
                    "success": False,
                    "preset": current_preset(),
                    "error": str(exc)
                }, 500)

            return

        if path == "/api/visualizer-state":

            try:
                length = int(
                    self.headers.get(
                        "Content-Length",
                        "0"
                    )
                )

                if length <= 0 or length > 65536:
                    self.send_json({
                        "success": False,
                        "error": "invalid content length"
                    }, 400)
                    return

                incoming = json.loads(
                    self.rfile.read(length)
                )

                if not isinstance(incoming, dict):
                    raise ValueError(
                        "JSON object required"
                    )

                state = self.read_visualizer_state()

                if "visualizer" in incoming:
                    visualizer = incoming["visualizer"]

                    if visualizer not in self.VALID_VISUALIZERS:
                        self.send_json({
                            "success": False,
                            "error": "invalid visualizer"
                        }, 400)
                        return

                    state["visualizer"] = visualizer

                if "enabled" in incoming:
                    state["enabled"] = bool(
                        incoming["enabled"]
                    )

                for key in (
                    "intensity",
                    "motion",
                    "sensitivity"
                ):
                    if key in incoming:
                        value = float(incoming[key])

                        if not 0.0 <= value <= 2.0:
                            raise ValueError(
                                f"{key} must be 0.0-2.0"
                            )

                        state[key] = value

                state["revision"] = (
                    int(state.get("revision", 0)) + 1
                )

                self.write_visualizer_state(state)

                self.send_json({
                    "success": True,
                    **state
                })

            except (
                ValueError,
                TypeError,
                json.JSONDecodeError
            ) as exc:
                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 400)

            except Exception as exc:
                self.send_json({
                    "success": False,
                    "error": str(exc)
                }, 500)

            return

        self.send_json({
            "success": False,
            "error": "not found"
        }, 404)


if __name__ == "__main__":
    server = ThreadingHTTPServer(
        ("0.0.0.0", 8090),
        ManagerHandler
    )

    print("SMRT DSP Manager listening on :8090")
    server.serve_forever()
