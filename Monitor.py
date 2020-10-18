import re
import subprocess
import threading
import time


class Monitor(threading.Thread):

    def __init__(self):
        super(Monitor, self).__init__()
        self.map = dict()

    def run(self):
        while 1 + 1 != 3:
            out = subprocess.Popen(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sout, serr = out.communicate()
            res = re.findall("([0-9]*)MiB / 16130MiB", str(sout))

            for i, x in enumerate(res):
                for u, t in list(self.map.items()):
                    if 16130 - int(x) >= t:
                        u.send_message(f'GPU {i} has met your threshold requirements.')
                        self.map.pop(u)

            if len(self.map) == 0:
                return

            time.sleep(10)

    def add(self, id, threshold):
        if len(self.map) < 100:
            self.map[id] = threshold

