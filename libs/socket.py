import asyncio
import websockets
import json
import libs.logger
from threading import Thread
from libs.schedule import Schedule

class Socket(Thread):
    def __init__(self, stop_event):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.schedule = Schedule()
        self.logger = libs.logger.get_logger(__name__)

    def run(self):
        self.start_server = websockets.serve(self.socket_handler, 'localhost', 8765)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_server)
        self.loop.run_forever()

    def stop(self):
        self.loop.close()

    @asyncio.coroutine
    def socket_handler(self, websocket, path):
        while not self.stop_event.is_set():
            value = yield from websocket.recv()

            if path == "/mifare":
                self.logger.info("Asking for Mifare {}".format(value))
                response = self.schedule.requestMifare(value)
            else:
                self.logger.info("Asking for Student ID {}".format(value))
                response = self.schedule.requestStudent(value)

            serialized_response = json.dumps(response)
            yield from websocket.send(serialized_response)
