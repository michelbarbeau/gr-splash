#  Continuous-Phase Frequency-Shift Keying (CPFSK) Transceiver, Packet/Encoder Decoder and Forward Error Correction (FEC) in GNU Radio.

The project includes the following contributions (see gr-splash/docs):

Margarita Otochkina, Forward Error Correction in Underwater Acoustic Sensor Networks, Bachelor of Computer Science Honours Project, School of Computer Science, Carleton University, December 2016.

Ahmad, Traboulsi, Software-Defined Underwater Acoustic Modems for Arctic-Like Environements, Master of Computer Science, Thesis, School of Computer Science, Carleton University, September 2016.


# Copyright 2017 Carleton University.
# Authors: Michel Barbeau, Margarita Otochkina & Ahmad Traboulsi
# Version: March 4, 2017

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

Open the flow graph  gr-splash/examples/node_0_DFLOOD.grc

To run outside gnuradio-companion (after generating the flow graph):

cd gr-splash/examples

python top_block.py

Example 2: In combination with LLSR (see: https://github.com/michelbarbeau/gr-llsr)

![LLSR Example](https://github.com/michelbarbeau/gr-splash/blob/master/node_LLSR.png)

To run within gnuradio-companion 

Open the flow graph  gr-splash/examples/node_0_LLSR.grc

To run outside gnuradio-companion (after generating the flow graph):

cd gr-splash/examples

python top_block.py

## Experimental Work

Experimental work is in progress. Watch the following water bucket demo of gr-spalsh and gr-dflood (produced by Derek Aubin).

[![Derek Aubin Demo](https://i1.ytimg.com/vi/6tYkVLcpsKY/hqdefault.jpg)](https://youtu.be/6tYkVLcpsKY)

Outdoor experimental work is planned for this summer. Stay tuned!

