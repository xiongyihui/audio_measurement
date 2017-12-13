#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Measure impluse response, frequency response and total harmonic distortion

code based on https://github.com/maqifrnswa/scimpy/blob/master/scimpy/speakertest.py
'''

import time
import logging
import pyaudio
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt


class SpeakerTestEngine():
    """Class that will control signal I/O during speaker testing"""

    def __init__(self):
        self.counter = 0
        self.pyaudio_instance = pyaudio.PyAudio()

        self.input_device_index = self.pyaudio_instance.get_default_input_device_info()[
            'index']
        self.output_device_index = self.pyaudio_instance.get_default_output_device_info()[
            'index']

    def run(self,
            f1=20,
            f2=20000,
            fs=44100,
            duration=0.3):

        framesize = 0

        def cb_stream_processing(in_data, frame_count, time_info, status):
            """PyAudio callback to fill output buffer and handle input
            buffer"""
            input_data.append(in_data)
            global message
            if status != 0:
                message = "error"
            data_out = data[self.counter * 2:(self.counter + frame_count) * 2]
            self.counter = self.counter + frame_count
            return(data_out, pyaudio.paContinue)

        np_type = np.int16

        # data = scipy.signal.chirp(t=np.arange(0, duration, 1./fs),
        #                           f0=10,
        #                           t1=duration,
        #                           f1=22050,
        #                           method='log',
        #                           phi=-90)*((2**(8*width))/2.-1)

        # Sweep Parameters
        f1 = 20
        f2 = 20000
        T = duration
        t = np.arange(0, T * fs) / fs
        R = np.log(f2 / f1)

        # ESS generation
        x = np.sin((2 * np.pi * f1 * T / R) *
                   (np.exp(t * R / T) - 1)) * (2**15 - 1)
        x = x.astype('int16')

        # match filter
        k = np.exp(t * R / T)
        f = x[::-1] / k

        data = x

        data = np.concatenate((np.zeros(int(duration * .1 * fs)),
                               data,
                               np.zeros(int(duration * .9 * fs))))

        data_filter = np.concatenate((np.zeros(int(duration * .1 * fs)),
                                      f,
                                      np.zeros(int(duration * 0.9 * fs))))

        data = data.astype(dtype=np_type, copy=False)

        # make it stereo
        data = np.array(
            [data, np.zeros(len(data), dtype=np_type)]).transpose().flatten()

        # use as a list of byte objects for speed, then convert
        # actually faster than byte array
        input_data = []

        self.counter = 0
        self.stream = self.pyaudio_instance.open(format=pyaudio.paInt16,
                                                 channels=2,
                                                 rate=fs,
                                                 output=True,
                                                 input=True,
                                                 input_device_index=self.input_device_index,
                                                 output_device_index=self.output_device_index,
                                                 stream_callback=cb_stream_processing,
                                                 frames_per_buffer=framesize)

        while self.stream.is_active():
            time.sleep(0.2)

        # Close the open _channel(s)_...
        self.stream.close()

        print len(input_data[0]), len(input_data[1])

        input_data = np.fromstring(b''.join(input_data), dtype=np.int16)
        input_data = input_data[:len(data)]

        # two channels
        input_data = np.reshape(input_data, (int(len(input_data) / 2), 2))
        input_data_fft0 = np.fft.rfft(input_data[:, 0])
        input_data_fft1 = np.fft.rfft(input_data[:, 1])

        data = np.reshape(data, (int(len(data) / 2), 2))

        print data.shape, input_data.shape

        # data_filter = np.concatenate((data_filter,
        #                               np.zeros(input_data.shape[0] - data_filter.shape[0])))

        data_filter_fft = np.fft.rfft(data_filter)

        imp_data0 = input_data_fft0 * data_filter_fft
        imp_data1 = input_data_fft1 * data_filter_fft

        ir0 = np.fft.irfft(imp_data0)
        ir1 = np.fft.irfft(imp_data1)

        return [ir0, ir1]


duration = 0.3
f1 = 20
f2 = 20000.0
fs = 44100


test_engine = SpeakerTestEngine()
impulse_response = test_engine.run(f1=f1, f2=f2, fs=fs, duration=duration)

t1 = np.argmax(np.abs(impulse_response[0]))

harmonic = []
for i in range(2, 10):
    x = t1 - duration * fs * np.log(i) / np.log(f2 / f1)
    harmonic.append(x)


fr = 10 * np.log10(np.abs(np.fft.rfft(impulse_response[0][t1 - 300:t1 + 600])))
freq = np.fft.rfftfreq(900, d=1. / fs)

plt.figure()
plt.subplot(2, 1, 1)
# plt.grid()
plt.plot(impulse_response[0])
plt.title('ch0')
for t in harmonic:
    plt.axvline(x=t, linestyle=':')

plt.subplot(2, 1, 2)
plt.grid()
plt.plot(impulse_response[1])
plt.title('ch1')


plt.figure()
plt.grid()
plt.semilogx(freq, fr, label='Frequency Response')
plt.title('Frequency Response')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [dB]')
plt.legend()
plt.show()
