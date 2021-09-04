A small project to display data to my e-ink display connected to my Raspberry Pi 3.

Goal: Display the weather, a simple chart and possibly today's calendar events on the display.

E-Paper Waveshare instructions: https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT

# Hardware

- Waveshare 7.5" e-ink display 
- Raspberry Pi 3

# Python 3 Libraries

`sudo apt-get update`
`sudo apt-get install python3-pip`
`sudo apt-get install python3-pil`
`sudo apt-get install python3-numpy`
`sudo pip3 install RPi.GPIO`
`sudo pip3 install spidev`

# Usage

Start display
`python3 client.py`
