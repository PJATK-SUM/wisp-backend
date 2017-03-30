from picamera import PiCamera
from time import sleep, strftime

import cv2
import numpy as np
import os

# Setup some constants
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 288
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FACE_DETECTOR_PATH = "{base_path}/cascades/haarcascade_frontalface_default.xml".format(
	base_path=BASE_PATH)

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
		camera.capture(image_buffer, 'rgb')
		image = image_buffer.reshape((IMAGE_HEIGHT, IMAGE_WIDTH, 3))
		image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		rects = face_cascade.detectMultiScale(image, scaleFactor=1.5, minNeighbors=5,
			minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)

		if len(rects) > 0:
			print("Faces detected!")
		else:
			print("No faces detected")

		i = 0
		for (x, y, width, height) in rects:
			cropped = image[y:y+height, x:x+width]
			cv2.imwrite("{base_path}/detections/{imagename} ({no}).jpg".format(
				base_path=BASE_PATH, imagename=strftime("%c"), no=i), cropped)
			i+=1

		sleep(1)
	except (KeyboardInterrupt, SystemExit):
		running = False
		print("Exiting...")
