

import threading
import sys
if sys.version_info[0] < 3:
    import Queue as queue
else:
    import queue

import numpy as np
import audioop

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

            rms = audioop.rms(data, 2)
            rms_db = 20 * np.log10(rms)

            pp = 20 * np.log10(audioop.avgpp(data, 2))

            x = np.fromstring(data, dtype='int16')

            nfft = x.shape[0]
            resolution = self.fs / nfft

            X = np.fft.rfft(x)

            self.on_data(20 * np.log10(np.abs(X)))

            base = self.ff / resolution
            F1 = np.abs(X[base])
            Fh = 0

            harmonic = 2 * base
            while harmonic < (nfft / 2):
                Fh += np.abs(X[harmonic])
                harmonic += base

            thd = Fh / F1
            print('RMS: {} dB, THD: {}, Peak: {} dB'.format(rms_db, thd, pp))

            super(THD, self).put(data)


def main():
    import time
    import datetime
    from voice_engine.source import Source
    from voice_engine.channel_picker import ChannelPicker
    from voice_engine.file_sink import FileSink

    src = Source(channels=2, rate=48000, frames_size=48000)
    chx = ChannelPicker(channels=src.channels, pick=0)
    thd = THD(1000, src.rate)

    filename = '2.94dB1KHz.' + datetime.datetime.now().strftime("%Y%m%d.%H:%M:%S") + '.wav'

    sink = FileSink(filename, channels=src.channels, rate=src.rate)

    src.link(sink)
    src.pipeline(chx, thd)

    src.pipeline_start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    src.pipeline_stop()


if __name__ == '__main__':
    main()
