import face_recognition
from threading import Thread
import concurrent.futures
from multiprocessing import Process
import cv2
import time
import pickle
import zlib


class VideoStreamWidget:
	def __init__(self, src=0):
		self.capture = cv2.VideoCapture(src)
		self.face_locations = []
		self.face_encodings = []
		self.threads = []

		# Start the thread to read frames from the video stream
		# with concurrent.futures.ThreadPoolExecutor() as executor:
		# 	f1 = executor.submit(self.update)
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True
		self.thread.start()

	def update(self):
		# Read the next frame from the stream in a different thread
		while True:
			if self.capture.isOpened():
				(self.status, self.frame) = self.capture.read()
				# Resize frame of video to 1/4 size for faster face recognition processing
				small_frame = cv2.resize(self.frame, (0, 0), fx=0.20, fy=0.20)
				# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
				rgb_small_frame = small_frame[:, :, ::-1]

				# Find all the faces and face encodings in the current frame of video
				self.face_locations = face_recognition.face_locations(rgb_small_frame)
				self.face_encodings = face_recognition.face_encodings(
				    rgb_small_frame, self.face_locations)

				if len(self.face_locations) > 0:
					print(self.face_encodings, len(self.face_encodings[0]))
					print(self.face_locations, len(self.face_locations[0]))
					pickledData = pickle.dumps(self.face_encodings)
					zipped = zlib.compress(pickledData)
					print(len(pickledData))
					print(len(zipped))
					i = 0
					for (x, y, w, h) in self.face_locations:
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
					# data = pickle.loads(pickledData)
					# print(data)
					break

			time.sleep(.01)
	def display_face(self, top, right, bottom, left):
		# (top, right, bottom, left) = face_location

		# Scale back up face locations since the frame we detected in was scaled to 1/5 size
		top *= 5
		right *= 5
		bottom *= 5
		left *= 5

		# Draw a box around the face
		cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)

	def show_frame(self):
		for face_location in self.face_locations:
			t = Thread(target=self.display_face,args=(face_location))
			t.start()
			self.threads.append(t)
			# self.display_face(face_location)
		# Display frames in main program
		# for thread in self.threads:
		# 	thread.join()
		cv2.imshow('frame', self.frame)
		key = cv2.waitKey(1)
		if key == ord('q') or len(self.face_locations) > 0:
			self.capture.release()
			cv2.destroyAllWindows()
			exit(1)

if __name__ == '__main__':
	video_stream_widget = VideoStreamWidget()
	while True:
		try:
			video_stream_widget.show_frame()
		except AttributeError:
			pass
