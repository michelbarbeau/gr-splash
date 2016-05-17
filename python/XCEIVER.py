#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# --------------------------------------------------------------
# Orthogonal frequency-division multiplexing (OFDM) transceiver.
# -------------------------------------------------------------- 
# Copyright 2016 Carleton University.
# Authors: Ahmad Traboulsi & Michel Barbeau
# Version: May 176, 2016
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

class XCEIVER(gr.hier_block2):

    def __init__(self,samp_rate=48000,tx_gain=1,rx_gain=1):
        gr.hier_block2.__init__(
            self, "XCEIVER",
           gr.io_signature(1, 1, gr.sizeof_char),
           gr.io_signature(1, 1, gr.sizeof_char))

        # message input interface from upper layer protocol
        #self.message_port_register_hier_in(pmt.intern('in'))
        # message output interface to upper layer protocol 
        #self.message_port_register_hier_out(pmt.intern('out'))

        ##################################################
        # Variables
        ##################################################
        self.transistion = transistion = 1000
        self.sync_word2 = sync_word2 = [0j, 0j, 0j, 0j, 0j, 0j, (-1+0j), (-1+0j), (-1+0j), (-1+0j), (1+0j), (1+0j), (-1+0j), (-1+0j), (-1+0j), (1+0j), (-1+0j), (1+0j), (1+0j), (1 +0j), (1+0j), (1+0j), (-1+0j), (-1+0j), (-1+0j), (-1+0j), (-1+0j), (1+0j), (-1+0j), (-1+0j), (1+0j), (-1+0j), 0j, (1+0j), (-1+0j), (1+0j), (1+0j), (1+0j), (-1+0j), (1+0j), (1+0j), (1+0j), (-1+0j), (1+0j), (1+0j), (1+0j), (1+0j), (-1+0j), (1+0j), (-1+0j), (-1+0j), (-1+0j), (1+0j), (-1+0j), (1+0j), (-1+0j), (-1+0j), (-1+0j), (-1+0j), 0j, 0j, 0j, 0j, 0j]
        self.sync_word1 = sync_word1 = [0., 0., 0., 0., 0., 0., 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., -1.41421356, 0., -1.41421356, 0., -1.41421356, 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., -1.41421356, 0., -1.41421356, 0., -1.41421356, 0., -1.41421356, 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., 1.41421356, 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., 1.41421356, 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., 1.41421356, 0., 1.41421356, 0., 0., 0., 0., 0., 0.]
        self.sideband_rx = sideband_rx = 4000
        self.sideband = sideband = 4000
        self.samp_rate = samp_rate
        self.tx_gain=1
        self.rx_gain=1
        self.pilot_symbols = pilot_symbols = ((1, 1, 1, -1,),)
        self.pilot_carriers = pilot_carriers = ((-21, -7, 7, 21,),)
        self.packet_length_tag_key = packet_length_tag_key = "packet_len"
        self.packet_len = packet_len = 8
        self.occupied_carriers = occupied_carriers = (range(-26, -21) + range(-20, -7) + range(-6, 0) + range(1, 7) + range(8, 21) + range(22, 27),)
        self.length_tag_key = length_tag_key = "packet_len"
        self.fft_len = fft_len = 64

        ########
        # Blocks
        ########
        # Receiver
        self.audio_source_0 = audio.source(48000, "", True)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((self.rx_gain, ))
        self.blocks_packed_to_unpacked_xx_0 = blocks.packed_to_unpacked_bb(1, gr.GR_MSB_FIRST)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.freq_xlating_fir_filter_xxx_0_0 = \
            filter.freq_xlating_fir_filter_ccc(1, (filter.firdes.low_pass(1, self.samp_rate, \
            sideband_rx,1000)), 5000, self.samp_rate)
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=220,
                taps=None,
                fractional_bw=None,
        )
        self.digital_ofdm_rx_0 = digital.ofdm_rx(
        	  fft_len=fft_len, cp_len=fft_len/4,
        	  frame_length_tag_key='frame_'+"length",
        	  packet_length_tag_key="length",
        	  occupied_carriers=occupied_carriers,
        	  pilot_carriers=pilot_carriers,
        	  pilot_symbols=pilot_symbols,
        	  sync_word1=sync_word1,
        	  sync_word2=sync_word2,
        	  bps_header=1,
        	  bps_payload=2,
        	  debug_log=False,
        	  scramble_bits=False
        	 )
        # Transmitter 
        self.blocks_unpacked_to_packed_xx_1 = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.blocks_stream_to_tagged_stream_0 = \
            blocks.stream_to_tagged_stream(gr.sizeof_char, 1, packet_len, packet_length_tag_key)
        self.digital_ofdm_tx_0 = digital.ofdm_tx(
        	  fft_len=fft_len, cp_len=fft_len/4,
        	  packet_length_tag_key=packet_length_tag_key,
        	  occupied_carriers=occupied_carriers,
        	  pilot_carriers=pilot_carriers,
        	  pilot_symbols=pilot_symbols,
        	  sync_word1=sync_word1,
        	  sync_word2=sync_word2,
        	  bps_header=1,
        	  bps_payload=2,
        	  rolloff=0,
        	  debug_log=True,
        	  scramble_bits=False
        	 )
        self.blocks_tag_gate_0 = blocks.tag_gate(gr.sizeof_gr_complex * 1, False)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=220,
                decimation=1,
                taps=None,
                fractional_bw=None,
        )
        self.freq_xlating_fir_filter_xxx_0 = \
            filter.freq_xlating_fir_filter_ccc(1, \
            (firdes.band_pass (0.5,self.samp_rate,10000-sideband,10000+sideband,transistion)),\
            -5000, self.samp_rate)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)        
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_vff((self.tx_gain, ))
        self.audio_sink_0 = audio.sink(48000, "", True)

        #############
        # Connections
        #############
        # Transmitter 
        self.connect((self, 0), \
            (self.blocks_unpacked_to_packed_xx_1, 0))           
        self.connect((self.blocks_unpacked_to_packed_xx_1, 0), \
           (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), \
            (self.digital_ofdm_tx_0, 0))
        self.connect((self.digital_ofdm_tx_0, 0), \
             (self.blocks_tag_gate_0, 0))
        self.connect((self.blocks_tag_gate_0, 0), 
            (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), \
            (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), \
            (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), \
            (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), \
            (self.audio_sink_0, 0))
        # Receiver
        self.connect((self.audio_source_0, 0), \
            (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), \
            (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), \
            (self.freq_xlating_fir_filter_xxx_0_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_0, 0), \
            (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.digital_ofdm_rx_0, 0))
        self.connect((self.digital_ofdm_rx_0, 0), \
            (self.blocks_packed_to_unpacked_xx_0, 0))
        self.connect((self.blocks_packed_to_unpacked_xx_0, 0), \
            (self, 0))

    def get_transistion(self):
        return self.transistion

    def set_transistion(self, transistion):
        self.transistion = transistion
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.band_pass (0.5,self.samp_rate,10000-self.sideband,10000+self.sideband,self.transistion)))

    def get_sync_word2(self):
        return self.sync_word2

    def set_sync_word2(self, sync_word2):
        self.sync_word2 = sync_word2

    def get_sync_word1(self):
        return self.sync_word1

    def set_sync_word1(self, sync_word1):
        self.sync_word1 = sync_word1

    def get_sideband_rx(self):
        return self.sideband_rx

    def set_sideband_rx(self, sideband_rx):
        self.sideband_rx = sideband_rx
        self.freq_xlating_fir_filter_xxx_0_0.set_taps((filter.firdes.low_pass(1, self.samp_rate, self.sideband_rx,1000)))

    def get_sideband(self):
        return self.sideband

    def set_sideband(self, sideband):
        self.sideband = sideband
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.band_pass (0.5,self.samp_rate,10000-self.sideband,10000+self.sideband,self.transistion)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.band_pass (0.5,self.samp_rate,10000-self.sideband,10000+self.sideband,self.transistion)))
        self.freq_xlating_fir_filter_xxx_0_0.set_taps((filter.firdes.low_pass(1, self.samp_rate, self.sideband_rx,1000)))

    def get_pilot_symbols(self):
        return self.pilot_symbols

    def set_pilot_symbols(self, pilot_symbols):
        self.pilot_symbols = pilot_symbols

    def get_pilot_carriers(self):
        return self.pilot_carriers

    def set_pilot_carriers(self, pilot_carriers):
        self.pilot_carriers = pilot_carriers

    def get_packet_length_tag_key(self):
        return self.packet_length_tag_key

    def set_packet_length_tag_key(self, packet_length_tag_key):
        self.packet_length_tag_key = packet_length_tag_key

    def get_packet_len(self):
        return self.packet_len

    def set_packet_len(self, packet_len):
        self.packet_len = packet_len

    def get_occupied_carriers(self):
        return self.occupied_carriers

    def set_occupied_carriers(self, occupied_carriers):
        self.occupied_carriers = occupied_carriers

    def get_length_tag_key(self):
        return self.length_tag_key

    def set_length_tag_key(self, length_tag_key):
        self.length_tag_key = length_tag_key

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len

