

import threading
import sys
if sys.version_info[0] < 3:
    import Queue as queue
else:
    import queue

import numpy as np
import audioop

from voice_engine.element import Element
from voice_engine.source import Source
from voice_engine.file_sink import FileSink
from voice_engine.channel_picker import ChannelPicker


class RMS(Element):
    def __init__(self):
        super(RMS, self).__init__()

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

            print('RMS: {} dB'.format(rms_db))

            # x = np.fromstring(data, dtype='int16')

            super(RMS, self).put(data)


def main():
    import time
    import datetime

    src = Source(rate=48000, channels=2, frames_size=4800)
    chx = ChannelPicker(channels=src.channels, pick=0)
    rms = RMS()

    filename = '1.quiet.' + datetime.datetime.now().strftime("%Y%m%d.%H:%M:%S") + '.wav'

    sink = FileSink(filename, channels=src.channels, rate=src.rate)

    src.pipeline(chx, rms)

    src.link(sink)

    src.pipeline_start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    src.pipeline_stop()


if __name__ == '__main__':
    main()
