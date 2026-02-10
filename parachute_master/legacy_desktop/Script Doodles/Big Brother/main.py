#!/usr/bin/env python3
"""
Big Brother — Multi-Bot Launcher (folders -> main.py)

Behavior:
- Define an expandable list of relative folder paths (under the current working directory).
- For each folder, find `main.py` and start it in its own working directory.
- Run each bot in parallel; stream prefixed stdout/stderr to this console.
- Gracefully stop all children on Ctrl+C.
- No CLI flags required; edit TARGET_DIRS to add/remove bots.

Default targets (customize as needed):
    - ibd_staffing_bot
    - to_staffing_bot
"""

from __future__ import annotations
import os
import sys
import time
import threading
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# -------------------------------------------------------------------
# Configure your bot folders here (relative to current working dir):
# -------------------------------------------------------------------
TARGET_DIRS: List[str] = [
    "ibd_staffing_bot",
    "to_staffing_bot",
]

PYTHON = sys.executable or "python"
ENV = os.environ.copy()
ENV["PYTHONUNBUFFERED"] = "1"  # ensure child output is flushed promptly


class BotProcess:
    def __init__(self, name: str, workdir: Path, cmd: List[str]) -> None:
        self.name = name
        self.workdir = workdir
        self.cmd = cmd
        self.proc: Optional[subprocess.Popen] = None
        self._threads: List[threading.Thread] = []

    def start(self):
        self.proc = subprocess.Popen(
            self.cmd,
            cwd=str(self.workdir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=ENV,
        )
        t_out = threading.Thread(target=self._stream, args=(self.proc.stdout, False), daemon=True)
        t_err = threading.Thread(target=self._stream, args=(self.proc.stderr, True), daemon=True)
        t_out.start()
        t_err.start()
        self._threads.extend([t_out, t_err])
        print(f"[launcher] started '{self.name}' pid={self.proc.pid} in {self.workdir}")

    def _stream(self, pipe, is_err: bool):
        if pipe is None:
            return
        prefix = f"[{self.name}] "
        try:
            for line in pipe:
                msg = line.rstrip("\n")
                if is_err:
                    sys.stderr.write(prefix + msg + "\n")
                else:
                    sys.stdout.write(prefix + msg + "\n")
        except Exception as e:
            sys.stderr.write(f"[launcher] stream error for {self.name}: {e}\n")

    def terminate(self, timeout: float = 5.0):
        if self.proc is None:
            return
        if self.proc.poll() is None:
            try:
                self.proc.terminate()
            except Exception:
                pass
            try:
                self.proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                try:
                    self.proc.kill()
                except Exception:
                    pass

    def is_running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def returncode(self) -> Optional[int]:
        return None if self.proc is None else self.proc.returncode


def discover_targets(base: Path, folders: List[str]) -> Dict[str, Path]:
    found: Dict[str, Path] = {}
    for folder in folders:
        p = (base / folder).resolve()
        if not p.exists() or not p.is_dir():
            print(f"[launcher] skip: {folder} (not found or not a directory)")
            continue
        main = p / "main.py"
        if not main.exists():
            print(f"[launcher] skip: {folder} (main.py not found)")
            continue
        found[folder] = p
    return found


def launch_all(targets: Dict[str, Path]) -> List[BotProcess]:
    bots: List[BotProcess] = []
    for name, path in targets.items():
        cmd = [PYTHON, "main.py"]
        bot = BotProcess(name=name, workdir=path, cmd=cmd)
        try:
            bot.start()
            bots.append(bot)
        except Exception as e:
            print(f"[launcher] failed to start {name}: {e}")
    return bots


def main():
    base = Path.cwd()
    print(f"[launcher] base dir: {base}")
    targets = discover_targets(base, TARGET_DIRS)
    if not targets:
        print("[launcher] no valid targets found. Edit TARGET_DIRS to add folders.")
        sys.exit(1)

    bots = launch_all(targets)

    try:
        while True:
            alive = [b for b in bots if b.is_running()]
            if not alive:
                print("[launcher] all bots have exited.")
                break
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[launcher] Ctrl+C received. Stopping children...")
        for b in bots:
            b.terminate()
        print("[launcher] shutdown complete.")


if __name__ == "__main__":
    main()
