from picamera import PiCamera
from time import sleep, strftime
from secrets import COGNITIVE_SERVICES_KEY, PERSON_GROUP_ID, SCREEN_ID, FIREBASE_CONFIG

import cv2
import numpy as np
import os
import cognitive_face as CF
import pyrebase

# Setup some constants
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 288
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FACE_DETECTOR_PATH = "{base_path}/cascades/haarcascade_frontalface_default.xml".format(
        base_path=BASE_PATH)

# Initialize Cognitive Services
CF.Key.set(COGNITIVE_SERVICES_KEY)

# Initialize Firebase
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
db = firebase.database()

# Create a new cascade classifier and image buffer
face_cascade = cv2.CascadeClassifier(FACE_DETECTOR_PATH)
image_buffer = np.empty((IMAGE_HEIGHT * IMAGE_WIDTH * 3), dtype=np.uint8)

# Instantiate the camera and change settings
camera = PiCamera()
camera.resolution = (IMAGE_WIDTH, IMAGE_HEIGHT)
camera.framerate = 24

# Warmup the camera
sleep(2)

print("Starting face detection, press Ctrl+C to exit")

running = True

while running:
        try:
                print("---> Attempting face detection")
                camera.capture(image_buffer, 'rgb')
                image = image_buffer.reshape((IMAGE_HEIGHT, IMAGE_WIDTH, 3))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                print("Running face classifier")
                rects = face_cascade.detectMultiScale(image, scaleFactor=1.5, minNeighbors=5,
                        minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)

                if len(rects) > 0:
                        print("Faces detected!")
                else:
                        print("No faces detected")

                i = 0
                for (x, y, width, height) in rects:
                        print("Processing detection")
                        cropped = image[y:y+height, x:x+width]
                        impath = "{base_path}/detections/{imagename} ({no}).jpg".format(
                                base_path=BASE_PATH, imagename=strftime("%c"), no=i)
                        cv2.imwrite(impath, cropped)

                        print("Using CF to obtain a faceId")
                        detections = CF.face.detect(impath)

                        if len(detections) > 0:
                                print("Attemtping to identify face")
                                faceId = detections[0]["faceId"]
                                faces = CF.face.identify([faceId], PERSON_GROUP_ID)

                                if len(faces) > 0:
                                        candidates = faces[0]["candidates"]
                                        if len(candidates) > 0:
                                                personId = candidates[0]["personId"]

                                                print("Recognized person, writing to Firebase")
                                                db.child("screens").child(SCREEN_ID).child("personId").set(personId)
                                        else:
                                                print("CF couldn't identify the face")
                        else:
                                print("CF didn't detect a face")

                        i+=1

                print("Finishing loop run")
                sleep(1)
        except (KeyboardInterrupt, SystemExit):
                running = False
                print("Exiting...")
