from picamera import PiCamera
from time import strftime
from secrets import COGNITIVE_SERVICES_KEY, PERSON_GROUP_ID, SCREEN_ID, FIREBASE_CONFIG
from threading import Thread

import cv2
import numpy as np
import os
import cognitive_face as CF
import pyrebase

# Setup some constants
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 288
TRACKING_THRESHOLD_X = IMAGE_WIDTH / 6
TRACKING_THRESHOLD_Y = IMAGE_HEIGHT / 6
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FACE_DETECTOR_PATH = "{base_path}/cascades/haarcascade_frontalface_alt.xml".format(
        base_path=BASE_PATH)

class Detector(Thread):
    def __init__(self, stop_event):
        Thread.__init__(self)

        self.stop_event = stop_event

        # Initialize Cognitive Services
        CF.Key.set(COGNITIVE_SERVICES_KEY)

        # Initialize Firebase
        firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        self.db = firebase.database()

        # Create a new cascade classifier and image buffer
        self.face_cascade = cv2.CascadeClassifier(FACE_DETECTOR_PATH)
        self.image_buffer = np.empty((IMAGE_HEIGHT * IMAGE_WIDTH * 3), dtype=np.uint8)

        # Instantiate the camera and change settings
        self.camera = PiCamera()
        self.camera.resolution = (IMAGE_WIDTH, IMAGE_HEIGHT)
        self.camera.framerate = 24

        self.captured_image = None
        self.detections = []
        self.last_center_x = None
        self.last_center_y = None

    def run(self):
        # Warmup the camera
        self.stop_event.wait(2)

        while(not self.stop_event.is_set()):
            print("Attempting face detection")
            self.detect()
            self.process()

            print("Finishing loop run")
            self.stop_event.wait(1)

    def detect(self):
        self.camera.capture(self.image_buffer, 'rgb')
        self.captured_image = self.image_buffer.reshape((IMAGE_HEIGHT, IMAGE_WIDTH, 3))
        self.captured_image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2GRAY)

        print("Running face classifier")
        self.detections = self.face_cascade.detectMultiScale(self.captured_image, scaleFactor=1.5, minNeighbors=5,
            minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)

    def process(self):
        print("Processing results")

        if self.no_detections():
            print("No faces detected")
            self.clear_last_center()
            self.clear_person()
            return

        x, y, width, height = self.detections[0]

        if self.is_previous_face(x, y, width, height):
            print("Face already detected")
            return

        print("Possible new face - attempting identification")

        self.set_identifying(True)
        self.identify()
        self.set_identifying(False)

    def no_detections(self):
        return len(self.detections) == 0

    def clear_person(self):
        self.db.child("screens").child(SCREEN_ID).child("personId").remove()

    def set_person(self, person_id):
        self.db.child("screens").child(SCREEN_ID).child("personId").set(person_id)

    def clear_last_center(self):
        self.last_center_x = None
        self.last_center_y = None

    def is_previous_face(self, x, y, width, height):
        center_x = x + width / 2
        center_y = y + height / 2

        if self.last_center_x == None or self.last_center_y == None:
            center_delta_x = IMAGE_WIDTH
            center_delta_y = IMAGE_HEIGHT
        else:
            center_delta_x = abs(self.last_center_x - center_x)
            center_delta_y = abs(self.last_center_y - center_y)

        self.last_center_x = center_x
        self.last_center_y = center_y

        return center_delta_x < TRACKING_THRESHOLD_X and center_delta_y < TRACKING_THRESHOLD_Y

    def set_identifying(self, value):
        self.db.child("screens").child(SCREEN_ID).child("identifying").set(value)

    def identify(self):
        cropped = self.captured_image[y:y+height, x:x+width]
        impath = "{base_path}/detections/{imagename}.jpg".format(
            base_path=BASE_PATH, imagename=strftime("%c"))
        cv2.imwrite(impath, cropped)

        print("Using CF to obtain a faceId")
        detections = CF.face.detect(impath)

        if len(detections) == 0:
            print("CF didn't detect a face")
            self.clear_person()
            return

        print("Attemtping to identify face")
        faceId = detections[0]["faceId"]
        faces = CF.face.identify([faceId], PERSON_GROUP_ID)

        if len(faces) == 0:
            return

        candidates = faces[0]["candidates"]

        if len(candidates) == 0:
            print("CF couldn't identify the face")
            self.clear_person()

        print("Recognized person, writing to Firebase")
        person_id = candidates[0]["personId"]
        self.set_person(person_id)