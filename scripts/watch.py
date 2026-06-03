#!/usr/bin/env python3

import subprocess
import sys
import time
from pathlib import Path


DEFAULT_PATHS = [Path("scripts")]
DEFAULT_COMMAND = ["make", "preprocess", "render"]
POLL_INTERVAL_SECONDS = 0.5


def take_snapshot(paths):
    snapshot = {}
    for root in paths:
        root = Path(root)
        if root.is_file():
            snapshot[str(root)] = root.stat().st_mtime_ns
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                snapshot[str(path)] = path.stat().st_mtime_ns
    return snapshot


def detect_changes(previous, current):
    return previous != current


def run_command(command):
    return subprocess.run(command).returncode


def watch(paths=None, command=None, poll_interval=POLL_INTERVAL_SECONDS):
    watch_paths = [Path(path) for path in (paths or DEFAULT_PATHS)]
    build_command = command or DEFAULT_COMMAND

    print(f"Watching: {', '.join(str(path) for path in watch_paths)}", flush=True)
    print(f"Running on change: {' '.join(build_command)}", flush=True)

    previous = take_snapshot(watch_paths)
    while True:
        time.sleep(poll_interval)
        current = take_snapshot(watch_paths)
        if not detect_changes(previous, current):
            continue

        previous = current
        print("Change detected, rebuilding...", flush=True)
        exit_code = run_command(build_command)
        if exit_code != 0:
            print(f"Build failed with exit code {exit_code}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    watch()
