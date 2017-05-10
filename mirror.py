from libs.detector import Detector
from libs.rfid import Rfid
from libs.socket import Socket
from threading import Event

import signal

stop_event = Event()

detect = Detector(stop_event)
detect.start()

rfid = Rfid(stop_event)
rfid.start()

socket = Socket(stop_event)
socket.start()

def signal_handler(signal, frame):
    stop_event.set()
    socket.stop()

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to stop')
signal.pause()
