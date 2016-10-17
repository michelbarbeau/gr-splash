#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ----------------------------------------
# Frequency-Shift Keying (FSK) Transceiver
# ----------------------------------------
# Copyright 2016 Carleton University.
# Authors: Michel Barbeau & Ahmad Traboulsi
# Version: October 9, 2016
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

import numpy
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import pmt
from gnuradio.digital import modulation_utils,mod_pkts
import sys
import math

class XCEIVER(gr.hier_block2):

    def __init__(self,samp_rate=48000,tx_gain=1,rx_gain=1):
        gr.hier_block2.__init__(
           self, 
           "XCEIVER",
           # input signature
           gr.io_signaturev(2, 2, [gr.sizeof_int*1, gr.sizeof_char*1]),
	   # output signature
           gr.io_signaturev(2, 2, [gr.sizeof_int*1, gr.sizeof_char*1]))

        #######################################################################
        # Variables
	self.tx_gain = tx_gain
        self.transition = 1000
	# samples_per_symbol
        self.sps = 8
	self.sideband_tx = 500
        self.sideband_rx = 500
        self.samp_rate = samp_rate
        self.interpolation = 100 # w.r.t. transmitter
        self.decimation =  1 # w.r.t. transmitter
        self.carrier = 8000 # Hz
	# sensitivity is pi * modulation_index/samples_per_symbol
	self.sensitivity = (math.pi*0.6)/self.sps

        #######################################################################
        # Receiver
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.freq_xlating_fir_filter_R = \
	   filter.freq_xlating_fir_filter_ccc( \
	      1, \
	      (firdes.band_pass (0.5,self.samp_rate,self.carrier-self.sideband_rx, \
	        self.carrier+self.sideband_rx,self.transition)), \
	      self.carrier, \
	      self.samp_rate)
        self.rational_resampler_R_1 = filter.rational_resampler_ccc(
                interpolation=self.decimation,
                decimation=100,
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_R_2 = filter.rational_resampler_ccc(
                interpolation=self.decimation,
                decimation=self.interpolation/100,
                taps=None,
                fractional_bw=None,
        )
	# input is the complex modulated signal at baseband.
	# output is a stream of bits packed 1 bit per byte (the LSB)
        self.digital_gfsk_demod_0 = digital.gfsk_demod(
        	samples_per_symbol=self.sps,
        	sensitivity=self.sensitivity,
        	gain_mu=0.175,
        	mu=0.5,
        	omega_relative_limit=0.005,
        	freq_error=0.0,
        	verbose=False,
        	log=False,
        )        
        self.connect((self, 0), \
            (self.blocks_float_to_complex_0, 0))
	self.connect((self.blocks_float_to_complex_0, 0), \
	   (self.freq_xlating_fir_filter_R, 0))      
        self.connect((self.freq_xlating_fir_filter_R, 0),
	   (self.rational_resampler_R_1, 0)) 
        self.connect((self.rational_resampler_R_1, 0), \
	   (self.rational_resampler_R_2, 0))       
        self.connect((self.rational_resampler_R_2, 0), \
	   (self.digital_gfsk_demod_0, 0))
        self.connect((self.digital_gfsk_demod_0, 0), \
            (self, 1))
  
        #######################################################################
        # Transmitter 
        # Gaussian Frequency Shift Key (GFSK) modulator
        # input is a byte stream (unsigned char) and the
        # output is the complex modulated signal at baseband.
        self.digital_gfsk_mod = digital.gfsk_mod(
        	samples_per_symbol=self.sps,
        	sensitivity=self.sensitivity,
        	bt=0.35, # Gaussian filter bandwidth * symbol time
        	verbose=False,
        	log=False,
        )
        self.rational_resampler = filter.rational_resampler_ccc(
                # assuming sing at 48,000 samples/sec
                # yields (8 samples/symbol*1800)/48,000 samples/sec=3 symbols/sec
                interpolation=self.interpolation, 
                decimation=1,
                taps=None,
                fractional_bw=None,
        )
        self.freq_xlating_fir_filter = \
	   filter.freq_xlating_fir_filter_ccc( \
              1, \
	      (firdes.band_pass (0.5,self.samp_rate,self.carrier-self.sideband_tx, \
	         self.carrier+self.sideband_tx,self.transition)), \
	      -self.carrier, \
              self.samp_rate)
        self.blocks_complex_to_real = blocks.complex_to_real(1)
        self.blocks_multiply_const = blocks.multiply_const_vff((self.tx_gain,))
        self.blocks_throttle = blocks.throttle(gr.sizeof_gr_complex*1,self.samp_rate,True)
        # Connections
        self.connect((self, 1), \
	   (self.digital_gfsk_mod, 0))  
        self.connect((self.digital_gfsk_mod, 0), \
	   (self.rational_resampler, 0))
        self.connect((self.rational_resampler, 0), 
	   (self.freq_xlating_fir_filter, 0)) 
        self.connect((self.freq_xlating_fir_filter, 0), \
	   (self.blocks_throttle, 0))
        self.connect((self.blocks_throttle, 0), \
           (self.blocks_complex_to_real, 0))
        self.connect((self.blocks_complex_to_real, 0), \
	   (self.blocks_multiply_const, 0))    
        self.connect((self.blocks_multiply_const, 0), \
	   (self, 0))

    def get_transition(self):
        return self.transition

    def set_transition(self, transition):
        self.transition = transition
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.band_pass (0.5,self.samp_rate,10000-self.sideband,10000+self.sideband,self.transition)))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps

    def get_sideband_rx(self):
        return self.sideband_rx

    def set_sideband_rx(self, sideband_rx):
        self.sideband_rx = sideband_rx

    def get_sideband(self):
        return self.sideband

    def set_sideband(self, sideband):
        self.sideband = sideband
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.band_pass (0.5,self.samp_rate,10000-self.sideband,10000+self.sideband,self.transition)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.band_pass (0.5,self.samp_rate,10000-self.sideband,10000+self.sideband,self.transition)))

    def get_interpolation(self):
        return self.interpolation

    def set_interpolation(self, interpolation):
        self.interpolation = interpolation

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation

    def get_carrier(self):
        return self.carrier

    def set_carrier(self, carrier):
        self.carrier = carrier
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(-self.carrier)
