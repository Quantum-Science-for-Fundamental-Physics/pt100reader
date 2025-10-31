# pt100reader
Code to use a Raspberry Pico 2 as a PT100 multiplexer.

# Basic Information:

The Pico 2 has 26 GPIO pins.

![pico2](./pico2pinout.jpg)

The output of the OpAmp must connect to pin 26, 27, or 28. These pins expose the Pico's ADC.
The remaining pins are for the (DE)MUX select pins.

# User's Guide:

# Guide for the unfortunate undergrad/grad who has to modify this software:

## Setup:

If you know what you're doing, you can ignore this section.

To setup the programming environement, youu must clone the repo, create a python virtual environment, and install the required packages. This code was written in ``Python 3.11.7``.
Then, install the required addons in VSCode.

### Detailed instructions on these steps:

Run the command to clone the repo:

   ``git clone [repo]``.

First, make sure you're running ``Python 3.11.7``. If you don't have it on your system, you will need to install it. Then create the virtual environement,

   ``python3.11.7 -m venv pt100``.

Second, you need to install packages. This is done with

   ``pip install -r requirements.txt``.

Third, you should install VSCode and install the ``MicroPico`` addon.




Features to implement:
- Configuration File with Pins to choose/disable
- Configuration GUI with Pinout of Pico
- Real time graph
- Save data locally
- Save data on dedicated database (Lab Pi)

Features implemented:
