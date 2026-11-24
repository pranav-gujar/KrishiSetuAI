"""
Captures a headless screenshot of the live KrishiSetu AI Command Center UI.
"""
import subprocess
import time
import urllib.request
import os

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PORT = 8772
SCREENSHOT_PATH = r"D:\Pranav\I Hack\krishisetu\docs\ui_preview.png"

proc = subprocess.Popen(
    ["python", "-m", "uvicorn", "app.main:app", "--port", str(PORT), "--host", "127.0.0.1"],
    cwd=r"D:\Pranav\I Hack\krishisetu",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

try:
    for _ in range(20):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/health", timeout=1) as resp:
                if resp.status == 200:
                    break
        except Exception:
            time.sleep(0.5)

    time.sleep(1.5)

    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size=1920,1080",
        f"--screenshot={SCREENSHOT_PATH}",
        f"http://127.0.0.1:{PORT}/",
    ]
    subprocess.run(cmd, check=True)
    print(f"Captured UI screenshot to {SCREENSHOT_PATH} ({os.path.getsize(SCREENSHOT_PATH) / 1024:.1f} KB)")
finally:
    proc.terminate()
    proc.wait(timeout=5)
