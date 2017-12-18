"""
Record audio from a 6+1 mic array, and then search the keyword "snowboy".
After finding the keyword, Direction Of Arrival (DOA) is estimated.

The hardware is respeaker 6+1 usb mic array:
    https://www.seeedstudio.com/ReSpeaker-Mic-Array-Far-field-w--7-PDM-Microphones--p-2719.html
"""


import time
from voice_engine.source import Source
from voice_engine.channel_picker import ChannelPicker
from voice_engine.kws import KWS
from voice_engine.file_sink import FileSink
import datetime


def main():
    src = Source(rate=16000, channels=8)
    ch1 = ChannelPicker(channels=8, pick=1)
    kws = KWS()

    filename = '4.kws.' + datetime.datetime.now().strftime("%Y%m%d.%H:%M:%S") + '.wav'

    sink = FileSink(filename, channels=src.channels, rate=src.rate)

    src.link(sink)
    src.pipeline(ch1, kws)

    def on_detected(keyword):
        print('detected {}'.format(keyword))

    kws.set_callback(on_detected)

    src.recursive_start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    src.recursive_stop()


if __name__ == '__main__':
    main()
