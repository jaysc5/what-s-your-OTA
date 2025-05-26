import os
import signal
import requests
import sys

REPO = "jaysc5/OTA-Software-Update"
PID_FILE = "state/pid.txt"
CURRENT_FILE = "state/current.txt"

def get_latest_tag():
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    r = requests.get(url)
    return r.json()["tag_name"] if r.ok else None

def read_pid():
    if not os.path.exists(PID_FILE):
        return None
    with open(PID_FILE) as f:
        content = f.read().strip()
        if content.isdigit():
            pid = int(content)
            try:
                os.kill(pid, 0)  # Check process exists
                return pid
            except ProcessLookupError:
                print(f"[watcher] PID {pid} does not exist.")
    return None

def read_current_tag():
    if not os.path.exists(CURRENT_FILE):
        return None
    with open(CURRENT_FILE) as f:
        return f.read().strip()

def send_signal(pid):
    os.kill(pid, signal.SIGUSR1)
    print(f"[watcher] Sent SIGUSR1 to PID {pid}")

if __name__ == "__main__":
    pid = read_pid()
    if not pid:
        print("[watcher] No valid PID found. GUI not running?")
        sys.exit(1)

    current = read_current_tag()
    latest = get_latest_tag()

    if latest and current and latest != current:
        print(f"[watcher] Update available! current={current}, latest={latest}")
        send_signal(pid)
    else:
        print("[watcher] No update.")
