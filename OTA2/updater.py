import os
import requests
import zipfile
import shutil
import signal
import subprocess
import time

REPO = "jaysc5/OTA-Software-Update"  #Replace with your GitHub repository
PID_FILE = "state/pid.txt"
CURRENT_FILE = "state/current.txt"
APP_DIR = "app"
BACKUP_DIR = "backup"
TMP_ZIP = "latest_release.zip"

def get_latest_release():
    url = f"https://api.github.com/repos/{REPO}/tags"
    r = requests.get(url)
    if r.ok:
        data = r.json()
        if data:
            tag_name = data[0]['name']  # 가장 최근 태그
            zip_url = f"https://github.com/{REPO}/archive/refs/tags/{tag_name}.zip"
            print(f"[OTA] GitHub latest tag: {tag_name}")
            return tag_name, zip_url
    return None, None


def read_current_tag():
    if not os.path.exists(CURRENT_FILE):
        return None
    with open(CURRENT_FILE) as f:
        return f.read().strip()

def write_current_tag(tag):
    os.makedirs("state", exist_ok=True)
    with open(CURRENT_FILE, "w") as f:
        f.write(tag)

def read_pid():
    if not os.path.exists(PID_FILE):
        return None
    with open(PID_FILE) as f:
        return int(f.read().strip())

def download_and_extract(zip_url):
    print("[OTA] Downloading latest release...")
    r = requests.get(zip_url)
    with open(TMP_ZIP, "wb") as f:
        f.write(r.content)

    print("[OTA] Extracting zip...")
    with zipfile.ZipFile(TMP_ZIP, 'r') as zip_ref:
        zip_ref.extractall("temp_update")

    os.remove(TMP_ZIP)

def replace_app_code():
    print("[OTA] Backing up old app/...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(APP_DIR, exist_ok=True)

    # Backup current contents of app/
    for item in os.listdir(APP_DIR):
        src = os.path.join(APP_DIR, item)
        dst = os.path.join(BACKUP_DIR, item)
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, dst)

    # Install new code from inside temp_update
    print("[OTA] Installing new app...")
    temp_root = "temp_update"
    contents = os.listdir(temp_root)
    if len(contents) != 1 or not os.path.isdir(os.path.join(temp_root, contents[0])):
        raise RuntimeError("[OTA] Invalid zip structure: expected one root folder in temp_update/")

    extracted_root = os.path.join(temp_root, contents[0])
    for item in os.listdir(extracted_root):
        src = os.path.join(extracted_root, item)
        dst = os.path.join(APP_DIR, item)
        shutil.move(src, dst)

    shutil.rmtree(temp_root)
    print("[OTA] App updated to latest version.")

def send_signal(pid):
    try:
        os.kill(pid, signal.SIGUSR1)
        print(f"[OTA] Sent SIGUSR1 to PID {pid}")
    except ProcessLookupError:
        print(f"[OTA] PID {pid} is not running")

def launch_app_and_kill_old(pid):
    main_py = os.path.join(APP_DIR, "mainwindow.py")
    if os.path.exists(main_py):
        print(f"[OTA] Launching {main_py}")
        proc = subprocess.Popen(["python3", main_py])

        time.sleep(2)

        if pid and proc.poll() is None:
            try:
                os.kill(pid, signal.SIGTERM)  # signal.SIGKILL
                print(f"[OTA] Killed old process with PID {pid}")
            except ProcessLookupError:
                print(f"[OTA] Old PID {pid} not found. Might have exited already.")
    else:
        print(f"[OTA] {main_py} not found. Skipping execution.")


if __name__ == "__main__":
    latest_tag, zip_url = get_latest_release()
    current_tag = read_current_tag()

    if latest_tag and latest_tag != current_tag:
        print(f"[OTA] New version found: {latest_tag}")
        download_and_extract(zip_url)
        replace_app_code()
        write_current_tag(latest_tag)

        pid = read_pid()
        launch_app_and_kill_old(pid)
    else:
        print("[OTA] No update or already up to date.")
