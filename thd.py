

import threading
import sys
if sys.version_info[0] < 3:
    import Queue as queue
else:
    import queue

import numpy as np

from voice_engine.source import Source
from voice_engine.element import Element


class THD(Element):
    def __init__(self, ff, fs):
        """
        ff: fundamental frequency
        fs: sampling rate
        """
        super(THD, self).__init__()

        self.ff = ff
        self.fs = fs

        self.queue = queue.Queue()
        self.done = True

    def put(self, data):
        self.queue.put(data)

    def start(self):
        self.done = False
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.done = True

    def on_data(self, data):
        pass

    def run(self):
        while not self.done:
            data = self.queue.get()
            x = np.fromstring(data, dtype='int16')

            nfft = x.shape[0]
            resolution = self.fs / nfft

            X = np.fft.rfft(x)

            self.on_data(np.abs(X))

            base = self.ff / resolution
            F1 = np.abs(X[base])
            Fh = 0

            harmonic = 2 * base
            while harmonic <= (nfft / 2):
                Fh += np.abs(X[harmonic])
                harmonic += base

            thd = 10 * np.log10(Fh / F1)
            print(thd)

            super(THD, self).put(data)


def main():
    import time
    from voice_engine.source import Source

    src = Source(rate=48000, frames_size=48000)
    thd = THD(1000, src.rate)

    src.pipeline(thd)

    src.pipeline_start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    src.pipeline_stop()


if __name__ == '__main__':
    main()
