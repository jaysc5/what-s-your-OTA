import os
import signal
from PySide6.QtCore import QTimer

PID_FILE = "pid.txt"

def setup_signal_handling(widget, callback_on_signal):
    print("[OTA] setup_signal_handling() 호출됨")
    os.makedirs("state", exist_ok=True)
    pid = os.getpid()
    with open("state/pid.txt", "w") as f:
        f.write(str(pid))
    print(f"[MainWindow] PID {pid} saved to state/pid.txt. Waiting for SIGUSR1...")


    def handle_signal(signum, frame):
        if signum == signal.SIGUSR1:
            print("[MainWindow] OTA 시그널 수신됨")
            callback_on_signal()

    signal.signal(signal.SIGUSR1, handle_signal)

    timer = QTimer(widget)
    timer.timeout.connect(lambda: None)
    timer.start(100)
