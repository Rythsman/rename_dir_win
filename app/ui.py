"""PySimpleGUI UI for the directory prefix renamer.

UI features:
- Input folder path with a folder browser.
- Checkbox to include root-level files.
- Start button to run in a background thread.
- Realtime log output to a multiline text box.
"""

from __future__ import annotations

import queue
import threading
import time
from pathlib import Path
from typing import Optional

import PySimpleGUI as sg

from .renamer import rename_files_in_tree


def _worker(
    root: Path,
    include_root_files: bool,
    log_queue: "queue.Queue[str]",
) -> None:
    """Background worker that performs the renaming and logs progress."""

    def _log(msg: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        log_queue.put(f"[{timestamp}] {msg}")

    start_ts = time.time()
    _log(f"Start processing: {root}")
    try:
        total = rename_files_in_tree(root, include_root_files=include_root_files, log=_log)
        elapsed = time.time() - start_ts
        _log(f"SUCCESS: Renamed {total} files in {elapsed:.2f}s")
    except Exception as exc:  # pylint: disable=broad-except
        elapsed = time.time() - start_ts
        _log(f"FAILED after {elapsed:.2f}s with error: {exc}")
    finally:
        # Signal completion with a sentinel
        log_queue.put("__DONE__")


def run_app() -> None:
    """Launch the PySimpleGUI application."""
    sg.theme("SystemDefault")

    layout = [
        [
            sg.Text("Root Folder", size=(12, 1)),
            sg.Input(key="-FOLDER-", enable_events=True, expand_x=True),
            sg.FolderBrowse(target="-FOLDER-")
        ],
        [
            sg.Checkbox("Include root files", key="-INCLUDE_ROOT-", default=False),
            sg.Push(),
            sg.Button("Start", key="-START-", bind_return_key=True),
        ],
        [
            sg.Multiline(
                key="-LOG-",
                size=(100, 25),
                autoscroll=True,
                disabled=True,
                expand_x=True,
                expand_y=True,
                font=("Consolas", 10),
            )
        ],
    ]

    window = sg.Window("Dir Prefix Renamer", layout, resizable=True)

    log_queue: "queue.Queue[str]" = queue.Queue()
    worker: Optional[threading.Thread] = None
    running = False

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break

        # Pump logs to the UI
        while True:
            try:
                msg = log_queue.get_nowait()
            except queue.Empty:
                break
            if msg == "__DONE__":
                running = False
                window["-START-"].update(disabled=False, text="Start")
                continue
            window["-LOG-"].update(value=(msg + "\n"), append=True)

        if event == "-START-":
            if running:
                continue
            folder_str = str(values.get("-FOLDER-", "")).strip()
            include_root = bool(values.get("-INCLUDE_ROOT-", False))
            if not folder_str:
                sg.popup_error("Please select a root folder.")
                continue
            root = Path(folder_str)
            if not root.exists() or not root.is_dir():
                sg.popup_error("Selected path is not a directory.")
                continue

            window["-LOG-"].update("")
            window["-START-"].update(disabled=True, text="Running...")
            running = True
            worker = threading.Thread(
                target=_worker,
                args=(root, include_root, log_queue),
                daemon=True,
            )
            worker.start()

    window.close()


