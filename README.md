#  Flooding-based UnderwaterAcoustic Communication Protocol (DFLOOD) Implementation for GNU Radio

Orthogonal frequency-division multiplexing (OFDM) transceiver.

# Copyright 2016 Carleton University.
# Authors: Ahmad Traboulsi & Michel Barbeau
# Version: May 17, 2016

## Installing 

`git clone https://github.com/michelbarbeau/gr-splash`

## Building


```
cd gr-splash

mkdir build

cd build 

cmake ../

make

sudo make install

sudo ldconfig

```

## Running

Example 1: In combination with DFLOOD (see: https://github.com/michelbarbeau/gr-dflood)

![DFLOOD Example](https://github.com/michelbarbeau/gr-splash/blob/master/node_DFLOOD.png)

To run within gnuradio-companion:

Open the flow graph  gr-splash/examples/node_DFLOOD.grc

To run outside gnuradio-companion (after generating the flow graph):

cd gr-splash/examples

python top_block.py

Example 2: In combination with LLSR (see: https://github.com/michelbarbeau/gr-dflood)

![LLSR Example](https://github.com/michelbarbeau/gr-splash/blob/master/node_LLSR.png)

To run within gnuradio-companion 

Open the flow graph  gr-splash/examples/node_LLSR.grc

To run outside gnuradio-companion (after generating the flow graph):

cd gr-splash/examples

python top_block.py
