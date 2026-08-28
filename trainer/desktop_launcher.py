"""
Knowledge Trainer — Desktop App Wrapper.

Launches the FastAPI server in the background, opens a dedicated standalone
desktop window (Chromium/Edge App Mode), and cleanly terminates the server
when the user closes the window.
"""
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
PYTHON_EXE = r"C:\Users\Admin\miniconda3\envs\cszero\python.exe"
PORT = 8010
URL = f"http://127.0.0.1:{PORT}/"
STATE_URL = f"http://127.0.0.1:{PORT}/api/state"


def is_server_ready() -> bool:
    try:
        with urllib.request.urlopen(STATE_URL, timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False


def find_browser_app_executable() -> str | None:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def main():
    # 1. Start FastAPI server silently in background
    CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
    server_proc = subprocess.Popen(
        [PYTHON_EXE, "-m", "uvicorn", "trainer.app:app", "--port", str(PORT)],
        cwd=str(PROJECT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW,
    )

    # 2. Wait until server responds
    for _ in range(40):
        if is_server_ready():
            break
        time.sleep(0.15)

    # 3. Launch dedicated standalone desktop window
    browser_exe = find_browser_app_executable()
    temp_profile = os.path.join(
        os.environ.get("TEMP", "."), "knowledge_trainer_app_profile"
    )

    try:
        if browser_exe:
            # Opens in App Mode (borderless, standalone window, no URL bar)
            # This call BLOCKS until the user closes the window.
            subprocess.run(
                [
                    browser_exe,
                    f"--app={URL}",
                    f"--user-data-dir={temp_profile}",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--window-size=1100,850",
                ],
                check=False,
            )
        else:
            import webbrowser
            webbrowser.open(URL)
            # If no app mode browser found, wait on server
            server_proc.wait()
    finally:
        # 4. Clean shutdown when the user closes the app window
        try:
            server_proc.terminate()
            server_proc.wait(timeout=2)
        except Exception:
            server_proc.kill()


if __name__ == "__main__":
    main()
