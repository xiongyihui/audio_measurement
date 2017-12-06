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
    # xin = wave.open('sweep.wav', 'rb')
    yout = wave.open('sweep-out-02.wav', 'rb')

    # x = xin.readframes(xin.getnframes())
    y = yout.readframes(yout.getnframes())

    # xin.close()
    yout.close()

    y = np.fromstring(y, dtype='int16')
    y -= int(np.sum(y) / y.shape[0])

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

    # match filter
    k = np.exp(t*R/T)
    f = x[::-1] / k

    h = sig.fftconvolve(y, f, mode='full')

    freq, H = dbfft(h, fs)
    
    plt.figure()
    plt.plot(h)
    plt.figure()
    plt.semilogx(freq, H)
    plt.show()