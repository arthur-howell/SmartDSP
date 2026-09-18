#!/usr/bin/env python3

import enum
import json
import signal
import sys
import time
from pathlib import Path

from camilladsp import CamillaClient


class State(enum.Enum):
    SILENT = "silent"
    CAPTURE = "capture"
    IDENTIFY = "identify"
    PLAYING = "playing"


class AudioIdentifier:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = json.loads(self.config_path.read_text())

        self.host = self.config.get("camilladsp_host", "127.0.0.1")
        self.port = int(self.config.get("camilladsp_port", 1234))

        self.threshold = float(
            self.config.get("silence_threshold_dbfs", -100.0)
        )

        self.silence_seconds = float(
            self.config.get("silence_seconds", 3.0)
        )

        self.poll_seconds = float(
            self.config.get("poll_seconds", 0.25)
        )

        self.state = State.SILENT
        self.silence_started = None
        self.running = True

        self.client = CamillaClient(self.host, self.port)

    def log(self, msg):
        print(
            time.strftime("%Y-%m-%d %H:%M:%S"),
            f"[{self.state.value.upper()}]",
            msg,
            flush=True,
        )

    def connect(self):
        self.client.connect()

        # Flush previous level windows.
        self.client.levels.capture_peak_since_last()
        self.client.levels.capture_rms_since_last()

        self.log(
            f"Connected to CamillaDSP at {self.host}:{self.port}"
        )

    def read_levels(self):
        peak = self.client.levels.capture_peak_since_last()
        rms = self.client.levels.capture_rms_since_last()

        return peak, rms

    def audio_present(self, rms):
        return any(level > self.threshold for level in rms)

    def trigger_capture(self):
        #
        # The actual 5-second audio extraction worker goes here next.
        #
        self.state = State.CAPTURE
        self.log("Audio transition detected -- capture requested")

    def process(self, rms):
        now = time.monotonic()
        active = self.audio_present(rms)

        if self.state == State.SILENT:

            if active:
                self.trigger_capture()
                return

        elif self.state == State.CAPTURE:
            #
            # Temporary behavior until capture backend is attached.
            #
            self.state = State.PLAYING
            self.log("Capture backend pending -- entering PLAYING")
            return

        elif self.state == State.IDENTIFY:
            return

        elif self.state == State.PLAYING:

            if active:
                self.silence_started = None
                return

            if self.silence_started is None:
                self.silence_started = now
                self.log("Silence candidate")
                return

            elapsed = now - self.silence_started

            if elapsed >= self.silence_seconds:
                self.state = State.SILENT
                self.silence_started = None
                self.log("Sustained silence -- identification rearmed")

    def run(self):
        self.connect()

        self.log(
            f"Detector running: threshold={self.threshold:.1f} dBFS, "
            f"silence={self.silence_seconds:.1f}s"
        )

        try:
            while self.running:
                time.sleep(self.poll_seconds)

                peak, rms = self.read_levels()

                self.process(rms)

        finally:
            try:
                self.client.disconnect()
            except Exception:
                pass

    def stop(self, *_):
        self.running = False


def main():
    root = Path(__file__).resolve().parents[2]

    config = (
        root /
        "config/audio-identification/config.json"
    )

    engine = AudioIdentifier(config)

    signal.signal(signal.SIGINT, engine.stop)
    signal.signal(signal.SIGTERM, engine.stop)

    engine.run()


if __name__ == "__main__":
    main()
