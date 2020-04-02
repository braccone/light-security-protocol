import face_recognition
from threading import Thread
import concurrent.futures
from multiprocessing import Process
import cv2
import time
import pickle
import zlib
import numpy as np


class VideoStreamWidget:
	def __init__(self, src=0):
		self.capture = cv2.VideoCapture(src)
		self.face_locations = []
		self.face_encodings = []
		self.threads = []

		# Start the thread to read frames from the video stream
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True
		self.thread.start()

	def update(self):
		# Read the next frame from the stream in a different thread
		while True:
			if self.capture.isOpened():
				(self.status, self.frame) = self.capture.read()
			time.sleep(.01)
	
	def recognizeFace(self):
		# Resize frame of video to 1/4 size for faster face recognition processing
		small_frame = cv2.resize(self.frame, (0, 0), fx=0.20, fy=0.20)
		# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
		rgb_small_frame = small_frame[:, :, ::-1]

		# Find all the faces and face encodings in the current frame of video
		self.face_locations = face_recognition.face_locations(rgb_small_frame)
		self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

		self.saveImage(self.face_encodings, self.face_locations, rgb_small_frame)

	def saveImage(self, face_encodings, face_locations, rgb_small_frame):
		if len(face_encodings) > 0:
			# print(face_encodings, len(face_encodings[0]))
			# print(type(face_locations), len(face_locations[0]))
			numpyTest = np.array(face_encodings)
			print(numpyTest, len(numpyTest))
			numpyBytes = numpyTest.tobytes()
			test = np.frombuffer(numpyBytes)
			print(f"-------------------> {test}")
			print(f"tipo: {numpyBytes} -- {len(numpyBytes)}")
			# pickledData = pickle.dumps(face_encodings)
			zipped = zlib.compress(numpyBytes)
			# print(len(pickledData))
			print(len(zipped))
			i = 0
			for (x, y, w, h) in face_locations:
				r = max(w, h) / 2
				centerx = x + w / 2
				centery = y + h / 2
				nx = int(centerx - r)
				ny = int(centery - r)
				nr = int(r * 2)

				faceimg = rgb_small_frame[ny:ny+nr, nx:nx+nr]
				lastimg = cv2.resize(faceimg, (32, 32))
				i += 1
				cv2.imwrite("image%d.jpg" % i, lastimg)

	def display_face(self, face_location):
		(top, right, bottom, left) = face_location

		# Scale back up face locations since the frame we detected in was scaled to 1/5 size
		top *= 5
		right *= 5
		bottom *= 5
		left *= 5

		# Draw a box around the face
		cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)

	def show_frame(self):
		self.recognizeFace()
		for face_location in self.face_locations:
			self.display_face(face_location)

		# Display frames in main program
		cv2.imshow('frame', self.frame)
		key = cv2.waitKey(1)
		if key == ord('q'):
			self.capture.release()
			cv2.destroyAllWindows()
			exit(1)

if __name__ == '__main__':
	video_stream_widget = VideoStreamWidget()
	while True:
		try:
			video_stream_widget.show_frame()
		except Exception as e:
			print(f"Errore: {e}")
			pass
