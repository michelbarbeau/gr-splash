#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Mon Nov 14 22:14:27 2016
##################################################

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import fec
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import dflood
import pmt
import splash


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.rate = rate = 2
        self.polys = polys = [109, 79]
        self.k = k = 7
        self.samp_rate = samp_rate = 48000
        
        
        self.enc_cc = enc_cc = fec.cc_encoder_make(8000, k, rate, (polys), 0, fec.CC_TERMINATED, False)
            
        
        
        self.dec_cc = dec_cc = fec.cc_decoder.make(8000, k, rate, (polys), 0, -1, fec.CC_TERMINATED, False)
            

        ##################################################
        # Blocks
        ##################################################
        self.splash_packet_encoder_0 = splash.packet_encoder(
                  samples_per_symbol=8,
                  bits_per_symbol=1,
                  preamble="",
                  access_code="",
                  pad_for_usrp=False,
        	  payload_length=9
                )
          
        self.splash_packet_decoder_0 = splash.packet_decoder(
                  access_code="",
                  threshold=-1
                )
          
        self.splash_XCEIVER_0 = splash.XCEIVER()
        self.digital_map_bb_0 = digital.map_bb(([-1,1]))
        self.dflood_dflood_0 = dflood.dflood(
          2, 0, 30, False, False, 
          5, 65, 2, 120, 50, 2, True, None
          )
        self.blocks_tagged_stream_to_pdu_1 = blocks.tagged_stream_to_pdu(blocks.float_t, "packet_len")
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(8, 1, "packet_len", True, gr.GR_MSB_FIRST)
        self.blocks_random_pdu_0_0 = blocks.random_pdu(1, 5, chr(0xFF), 1)
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, "packet_len")
        self.blocks_message_strobe_2 = blocks.message_strobe(pmt.intern("TEST"), 10000)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern("TEST"), 10000)
        self.blocks_message_debug_0 = blocks.message_debug()
        self.blocks_char_to_float_0_1 = blocks.char_to_float(1, 1)
        self.audio_source_0 = audio.source(48000, "", True)
        self.audio_sink_0 = audio.sink(48000, "", True)
        self.analog_probe_avg_mag_sqrd_x_0 = analog.probe_avg_mag_sqrd_c(-70, 1)
        self.Async_Ecnoder = fec.async_encoder(enc_cc, True, False, False, 1500)
        self.Async_Decoder = fec.async_decoder(dec_cc, True, False, 1500)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.Async_Decoder, 'out'), (self.dflood_dflood_0, 'from_radio'))    
        self.msg_connect((self.Async_Ecnoder, 'out'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))    
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.blocks_random_pdu_0_0, 'generate'))    
        self.msg_connect((self.blocks_message_strobe_2, 'strobe'), (self.dflood_dflood_0, 'ctrl_in'))    
        self.msg_connect((self.blocks_random_pdu_0_0, 'pdus'), (self.dflood_dflood_0, 'from_app'))    
        self.msg_connect((self.blocks_tagged_stream_to_pdu_1, 'pdus'), (self.Async_Decoder, 'in'))    
        self.msg_connect((self.dflood_dflood_0, 'to_radio'), (self.Async_Ecnoder, 'in'))    
        self.msg_connect((self.dflood_dflood_0, 'to_app'), (self.blocks_message_debug_0, 'print_pdu'))    
        self.connect((self.audio_source_0, 0), (self.splash_XCEIVER_0, 0))    
        self.connect((self.blocks_char_to_float_0_1, 0), (self.blocks_tagged_stream_to_pdu_1, 0))    
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.splash_packet_encoder_0, 0))    
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.digital_map_bb_0, 0))    
        self.connect((self.digital_map_bb_0, 0), (self.blocks_char_to_float_0_1, 0))    
        self.connect((self.splash_XCEIVER_0, 2), (self.analog_probe_avg_mag_sqrd_x_0, 0))    
        self.connect((self.splash_XCEIVER_0, 0), (self.audio_sink_0, 0))    
        self.connect((self.splash_XCEIVER_0, 1), (self.splash_packet_decoder_0, 0))    
        self.connect((self.splash_packet_decoder_0, 0), (self.blocks_repack_bits_bb_0, 0))    
        self.connect((self.splash_packet_encoder_0, 0), (self.splash_XCEIVER_0, 1))    

    def get_rate(self):
        return self.rate

    def set_rate(self, rate):
        self.rate = rate

    def get_polys(self):
        return self.polys

    def set_polys(self, polys):
        self.polys = polys

    def get_k(self):
        return self.k

    def set_k(self, k):
        self.k = k

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_enc_cc(self):
        return self.enc_cc

    def set_enc_cc(self, enc_cc):
        self.enc_cc = enc_cc

    def get_dec_cc(self):
        return self.dec_cc

    def set_dec_cc(self, dec_cc):
        self.dec_cc = dec_cc


def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
