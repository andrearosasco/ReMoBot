import subprocess

class Allocator():
    '''This class exists to avoid having 305 MiB of GPU memory
    permanently allocated to Numba. When the thread running this class is destroyed
    that memory should be available again'''

    def __init__(self):
        super(Allocator, self).__init__()
        self.memory = dict()

    def add(self, user, size, gpu):
        proc = subprocess.Popen(['python', './reserve.py', gpu, size])
        self.memory[user] = proc.pid

    def remove(self, user):
        subprocess.Popen(['kill', str(self.memory[user]), '-9'])
        del self.memory[user]
