#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# --------------
# Packet Decoder
# --------------
# Copyright 2016 Carleton University.
# Authors: Michel Barbeau
# Version: October 17, 2016
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
# 

from gnuradio import gr, digital
from gnuradio import blocks
from gnuradio.digital import packet_utils
import gnuradio.gr.gr_threading as _threading
import sys
import pmt

##payload length in bytes
DEFAULT_PAYLOAD_LEN = 512

##how many messages in a queue
DEFAULT_MSGQ_LIMIT = 2

##threshold for unmaking packets
DEFAULT_THRESHOLD = 12

##################################################
## Packet Decoder
##################################################
class _packet_decoder_thread(_threading.Thread):

    def __init__(self, msgq, callback):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self._msgq = msgq
        self.callback = callback
        self.keep_running = True
        self.start()

    def run(self):
        while self.keep_running:
            msg = self._msgq.delete_head()
            ok, payload = packet_utils.unmake_packet(msg.to_string(), int(msg.arg1()))
            if self.callback:
                self.callback(ok, payload)

class packet_decoder_sink(gr.hier_block2):
    """
    Hierarchical block for wrapping packet-based demodulators.
    """

    def __init__(self, access_code='', threshold=-1, callback=None):
        """
        packet_demod constructor.

        Args:
            access_code: AKA sync vector
            threshold: detect access_code with up to threshold bits wrong (0 -> use default)
            callback: a function of args: ok, payload
        """
        #access code
        if not access_code: #get access code
            access_code = packet_utils.default_access_code
        if not packet_utils.is_1_0_string(access_code):
            raise ValueError, "Invalid access_code %r. Must be string of 1's and 0's" % (access_code,)
        self._access_code = access_code
        #threshold
        if threshold < 0: threshold = DEFAULT_THRESHOLD
        self._threshold = threshold
        #blocks
        msgq = gr.msg_queue(DEFAULT_MSGQ_LIMIT) #holds packets from the PHY
        correlator = digital.correlate_access_code_bb(self._access_code, self._threshold)
        framer_sink = digital.framer_sink_1(msgq)
        #initialize hier2
        gr.hier_block2.__init__(
            self,
            "packet_decoder",
            gr.io_signature(1, 1, gr.sizeof_char), # Input signature
            gr.io_signature(0, 0, 0) # Output signature
        )
        #connect
        self.connect(self, correlator, framer_sink)
        #start thread
        _packet_decoder_thread(msgq, callback)

##################################################
## Packet Demod for OFDM Demod and Packet Decoder
##################################################
class packet_decoder(gr.hier_block2):
    """
    Hierarchical block for wrapping packet sink block.
    """

    def __init__(self, access_code='', threshold=-1):

	packet_sink=packet_decoder_sink(access_code, threshold, lambda ok, payload: self.recv_pkt(ok, payload))

	self._item_size_out = gr.sizeof_char
	
        #initialize hier2
        gr.hier_block2.__init__(
            self,
            "ofdm_mod",
            gr.io_signature(1, 1, packet_sink.input_signature().sizeof_stream_item(0)), # Input signature
            gr.io_signature(1, 1, self._item_size_out) # Output signature
        )
        #create blocks
        #msg_source = blocks.message_source(self._item_size_out, DEFAULT_MSGQ_LIMIT)
        #self._msgq_out = msg_source.msgq()
        # create message queue
	self._msgq_out = gr.msg_queue(DEFAULT_MSGQ_LIMIT)
        # map message queue to tagged stream block
        msg_source=blocks.message_source(self._item_size_out, self._msgq_out, "packet_len")
        #connect
        self.connect(self, packet_sink)
        self.connect(msg_source, self)
        if packet_sink.output_signature().sizeof_stream_item(0):
            self.connect(packet_sink,
                         blocks.null_sink(packet_sink.output_signature().sizeof_stream_item(0)))

    def recv_pkt(self, ok, payload):
        msg = gr.message_from_string(payload, 0, self._item_size_out,
                                     len(payload)/self._item_size_out)
        if ok: self._msgq_out.insert_tail(msg)

