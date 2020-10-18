import numpy as np
import sys
from numba import cuda
import signal

if __name__ == '__main__':
    gpu = int(sys.argv[1])
    size = int(sys.argv[2])

    cuda.select_device(gpu)
    t = cuda.device_array((size * 2, 2 ** 8, 2 ** 8), dtype=np.float)
    signal.pause()

