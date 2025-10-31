# pt100reader
Code to use a Raspberry Pico 2 as a PT100 multiplexer.

# Basic Information:

The Pico 2 has 26 GPIO pins.

![pico2](./pico2pinout.jpg)

The output of the OpAmp must connect to pin 26, 27, or 28. These pins expose the Pico's ADC.
The remaining pins are for the (DE)MUX select pins.

# User's Guide:

# Guide for the unfortunate undergrad/grad who has to modify this software:

First, you must 
   ``git clone [repo]``
   

Features to implement:
- Configuration File with Pins to choose/disable
- Configuration GUI with Pinout of Pico
- Real time graph
- Save data locally
- Save data on dedicated database (Lab Pi)

Features implemented:
