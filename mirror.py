from libs.detector import Detector
from threading import Event

import signal
import sys

stop_event = Event()
detect = Detector(stop_event)

def signal_handler(signal, frame):
    stop_event.set()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to stop')
signal.pause()