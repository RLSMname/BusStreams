import threading
import time

from constants import TICK_INTERVAL


def prRed(s): print("\033[91m {}\033[00m".format(s))
def prGreen(s): print("\033[92m {}\033[00m".format(s))
def prCyan(s): print("\033[96m {}\033[00m".format(s))
def prYellow(s): print("\033[93m {}\033[00m".format(s))

class TickMonitor:
    def __init__(self, interval):
        self.interval = interval
        self.tick = 0
        self.running = False
        self.thread = None

    def _run(self):
        while self.running:
            time.sleep(self.interval)
            self.tick += 1
            prYellow(f"[Clock] {self.tick * self.interval}s passed")

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        prYellow("Starting clock...")
        self.thread.start()

    def stop(self):
        self.running = False