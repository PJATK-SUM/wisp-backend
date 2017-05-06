from libs.detector import Detector
from threading import Event

import signal
import sys

stop_event = Event()
detect = Detector(stop_event)
detect.start()

def signal_handler(signal, frame):
    stop_event.set()

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to stop')
signal.pause()