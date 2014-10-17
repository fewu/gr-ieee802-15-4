#! /usr/bin python

import css_mod
import css_constants
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
	print "Generate IEEE 802.15.4 compliant CSS baseband signal"
	m = css_mod.modulator(slow_rate=False, phy_packetsize_bytes=14, nframes=4, chirp_number=4)
	[payload,baseband] = m.modulate_random()	
	print "len baseband signal:", len(baseband)

	print "samples in one..."
	print "-> subchirp: ", css_constants.n_sub
	print "-> average chirp sequence:", css_constants.n_chirp
	nsamp_frame = len(baseband)/m.nframes
	print "-> frame: ", nsamp_frame
	nsamp_payload = m.phy_packetsize_bytes*css_constants.n_chirp
	nsamp_header = nsamp_frame - nsamp_payload
	print "-> frame header: ", nsamp_header
	print "-> frame payload: ", nsamp_payload

	f, axarr = plt.subplots(4)
	for i in range(4):
		axarr[i].plot(m.possible_chirp_sequences[i].real,label='real')
		axarr[i].plot(m.possible_chirp_sequences[i].imag,label='imag')
		axarr[i].legend()
	f.suptitle("Real and imaginary part of the 4 chirp sequences windows with the raised cosine")

	# plot PSD and frequency mask
	s = abs(np.fft.fftshift(np.fft.fft(baseband)))**2
	freq = np.linspace(-css_constants.bb_samp_rate/2, css_constants.bb_samp_rate/2-1/css_constants.bb_samp_rate, len(s))
	mask = np.zeros(len(s))
	for i in range(len(mask)):
		if abs(freq[i]) > 22e6:
			mask[i] = 1e-5
		if abs(freq[i]) > 11e6:
			mask[i] = 1e-3
		if abs(freq[i]) <= 11e6:
			mask[i] = 1
	f, axarr = plt.subplots(3,1)
	s_norm = s/max(s)
	axarr[0].plot(freq, 10*np.log10(s_norm))
	axarr[0].plot(freq, 10*np.log10(mask), 'r')
	axarr[0].set_title("Complex baseband spectrum and frequency mask")
	axarr[0].set_ylabel("|S| [dB]")
	axarr[0].set_xlabel("Hz")
	axarr[0].set_ylim([-50,0])
	axarr[0].set_xlim([freq[0], freq[-1]])

	# plot time signal magnitude
	t = np.linspace(0,1,css_constants.bb_samp_rate+1)
	t = t[:len(s)]
	axarr[1].plot(abs(baseband[:len(t)]))
	axarr[1].set_title("Complex baseband magnitude")
	axarr[1].set_xlabel("n")
	axarr[1].set_ylabel("|s(n)|")

	# plot real part of time signal
	axarr[2].plot(baseband[:len(t)].real, label='real')
	axarr[2].plot(baseband[:len(t)].imag, label='imag')
	axarr[2].legend()
	axarr[2].set_title("Real and imaginary part of time signal using chirp sequence #"+str(m.chirp_number))
	for i in range(len(t)/nsamp_frame):
		axarr[2].axvline(x=nsamp_frame*i, linewidth=4, color='r')

	# plot auto-/crosscorrelation of chirp sequences
	ccf = []
	for i in range(4):
		for k in range(4):
			tmp = abs(np.correlate(m.possible_chirp_sequences[i], m.possible_chirp_sequences[k], mode='same'))
			ccf.append(tmp)

	f, axarr = plt.subplots(4,4)
	for i in range(4):
		for k in range(4):
			titlestring = "("+str(i+1)+","+str(k+1)+")"
			axarr[i,k].plot(ccf[i*4+k], label=titlestring)
			axarr[i,k].legend()
	f.suptitle("Cross correlation of chirp sequence pairs (no time gaps)")

	# # plot correlation of chirp sequences and transmit signal with raised cosine filter
	# f, axarr = plt.subplots(6)
	# axarr[0].plot(m.rcfilt, label="RC filter")
	# axarr[0].legend()
	# axarr[0].set_ylim([0,1.2])
	# for i in range(1,5):
	# 	titlestring = str(i)
	# 	axarr[i].plot(abs(np.correlate(m.rcfilt, m.possible_chirp_sequences[i-1], mode='full')), label=titlestring)
	# 	axarr[i].legend()
	# titlestring = "tx w/ rc filter"
	# axarr[5].plot(abs(np.correlate(m.rcfilt, baseband[:len(t)], mode='full')), label=titlestring)
	# axarr[5].legend()
	# f.suptitle("Correlation of raised cosine filter with chirp sequences and transmit signal")

	# plot correlation of chirp sequences with transmit signal
	f, axarr = plt.subplots(4)
	for i in range(4):
		titlestring = "chirp seq #"+str(i+1)
		axarr[i].plot(abs(np.correlate(baseband, m.possible_chirp_sequences[i], mode='full')), label=titlestring)
		axarr[i].legend()
		axarr[i].set_xlim([0,nsamp_frame*m.nframes])
		for k in range(m.nframes):
			axarr[i].axvline(x=nsamp_frame*k, linewidth=4, color='r')
	f.suptitle("Correlation of chirp sequences with transmit signal carrying chirp seq #"+ str(m.chirp_number))

	# plot correlation of subchirps with transmit signal
	f, axarr = plt.subplots(4,2)
	sc = []
	for i in range(4):
		sc.append(m.chirp_seq[i*css_constants.n_sub:(i+1)*css_constants.n_sub])
	for i in range(4):
		titlestring = "subchirp #" + str(i+1)
		axarr[i,0].plot(abs(np.correlate(baseband, sc[i])),label=titlestring)
		axarr[i,0].legend()
		axarr[i,0].set_xlim([0,4*css_constants.n_chirp])
		axarr[i,1].plot(sc[i].real,label='real')
		axarr[i,1].plot(sc[i].imag,label='imag')
		axarr[i,1].legend()
	f.suptitle("Correlation of subchirps with transmit signal")
	
	plt.show()







