#!/usr/bin/env python

from __future__ import division
import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt
import wave


def dbfft(x, fs, win=None):
    N = len(x)  # Length of input sequence

    if win is None:
        win = np.ones(x.shape)
    if len(x) != len(win):
            raise ValueError('Signal and window must be of the same length')
    x = x * win

    # Calculate real FFT and frequency vector
    sp = np.fft.rfft(x)
    freq = np.arange((N / 2) + 1) / (float(N) / fs)

    # Scale the magnitude of FFT by window and factor of 2,
    # because we are using half of FFT spectrum.
    s_mag = np.abs(sp) * 2 / np.sum(win)

    # Convert to dBFS
    ref = s_mag.max()
    s_dbfs = 20 * np.log10(s_mag/ref)

    return freq, s_dbfs

if __name__ == "__main__":
    # Sweep Parameters
    f1 = 20
    f2 = 10000
    T = 3
    fs = 48000
    t = np.arange(0, T*fs)/fs
    R = np.log(f2/f1)

    # ESS generation
    x = np.sin((2*np.pi*f1*T/R)*(np.exp(t*R/T)-1)) * (1 << 15)
    x = x.astype('int16')
    # Inverse filter
    k = np.exp(t*R/T)
    f = x[::-1]/k
    # Impulse response
    # ir = sig.fftconvolve(x, f, mode='same')

    # # Get spectra of all signals
    # freq, Xdb = dbfft(x, fs)
    # freq, Fdb = dbfft(f, fs)
    # freq, IRdb = dbfft(ir, fs)

    # plt.figure()
    # plt.subplot(3,1,1)
    # plt.grid()
    # plt.plot(t, x)
    # plt.title('ESS')
    # plt.subplot(3,1,2)
    # plt.grid()
    # plt.plot(t, f)
    # plt.title('Inverse filter')
    # plt.subplot(3,1,3)
    # plt.grid()
    # plt.plot(t, ir)
    # plt.title('Impulse response')

    # plt.figure()
    # plt.grid()
    # plt.semilogx(freq, Xdb, label='ESS')
    # plt.semilogx(freq, Fdb, label='Inverse filter')
    # plt.semilogx(freq, IRdb, label='IR')
    # plt.title('Spectrum')
    # plt.xlabel('Frequency [Hz]')
    # plt.ylabel('Amplitude [dBFS]')
    # plt.legend()

    # plt.show()

    writer = wave.open('sweep.wav', 'wb')
    writer.setnchannels(1) # 1 channel, mono
    writer.setsampwidth(2) # 16bit
    writer.setframerate(fs) # sample rate
    writer.writeframes(x.tostring())
    