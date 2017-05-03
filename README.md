# Wisp Backend

This is the Python backend for Wisp - the personal assistant at [PJAIT](http://www.pja.edu.pl/en/).
Its main task is to detect people approaching it, either by face, using beacons or by RFID.

## Prerequisites

* Python 3

## Installation

```bash
# Install Python packages from requirements.txt
pip install -r requirements.txt

# Set the boot SPI boot config on Raspberry Pi
echo "dtparam=spi=on" >> /boot/config.txt
echo "dtoverlay=spi-bcm2708" >> /boot/config.txt
```
