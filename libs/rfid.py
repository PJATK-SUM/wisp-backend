# Contributed by Mateusz Knop (https://github.com/Persiasty)

import pyrebase
import struct
import time
import libs.logger
from pirc522 import RFID
from secrets import SCREEN_ID, FIREBASE_CONFIG
from threading import Thread

class Rfid(Thread):
    def __init__(self, stop_event):
        Thread.__init__(self)

        firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        self.db = firebase.database()
        self.stop_event = stop_event
        self.logger = libs.logger.get_logger(__name__)
        self.rdr = RFID()

    def run(self):
        self.logger.info("Starting RFID scanner")
        while(not self.stop_event.is_set()):
            (error, data) = self.rdr.request()
            if not error:
                (error, uid) = self.rdr.anticoll()
                if not error:
                    mifareUID = Rfid.mifareDataToInt(uid)
                    self.db.child("screens").child(SCREEN_ID).child("mifare").set(mifareUID)
                    self.db.child("screens").child(SCREEN_ID).child("identification").set("mifare")
                    self.logger.info("Mifare: %d" % (mifareUID))
            self.stop_event.wait(1)
        self.rdr.cleanup()

    @staticmethod
    def mifareDataToInt(data):
        return struct.unpack("I", bytearray(data[:4]))[0]
