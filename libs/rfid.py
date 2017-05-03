# Contributed by Mateusz Knop (https://github.com/Persiasty)

import struct
import time
from pirc522 import RFID

class Rfid():
    def __init__(self):
        self.isRunning = True
        self.rdr = RFID()  # initialize rfid reader

    def scan(self, callback):
        if __debug__:
            print("Starting")
        while self.isRunning:
            (error, data) = self.rdr.request()

            #if not error and __debug__:
            #   print("\nDetected: " + format(data, "02x"))

            (error, uid) = self.rdr.anticoll()
            if not error:
                mifareUID = Rfid.mifareDataToInt(uid)
                callback(mifareUID)
                if __debug__:
                    print("Mifare: %d" % (mifareUID))
            time.sleep(1)

    def close(self):
        self.isRunning = False
        self.rdr.cleanup()

    @staticmethod
    def mifareDataToInt(data):
        return struct.unpack("I", bytearray(data[:4]))[0]
