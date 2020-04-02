import face_recognition
import cv2
import numpy as np


class ClientID:
	def __init__(self, camera=0):
		# Get a reference to webcam #0 (the default one)
		self.video_capture = cv2.VideoCapture(camera)
		# Initialize some variables
		self.face_locations = []
		self.face_encodings = []
		self.face_names = []
		self.process_this_frame = True

	def start(self):
		while True:
			try:
				# Grab a single frame of video
				ret, frame = self.video_capture.read()
				# Resize frame of video to 1/4 size for faster face recognition processing
				small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

				# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
				rgb_small_frame = small_frame[:, :, ::-1]

				# Only process every other frame of video to save time
				if self.process_this_frame:
					# Find all the faces and face encodings in the current frame of video
					face_locations = face_recognition.face_locations(rgb_small_frame)
					face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

				self.process_this_frame = not self.process_this_frame

					# Display the results
				for (top, right, bottom, left), name in self.face_locations:
					# Scale back up face locations since the frame we detected in was scaled to 1/4 size
					top *= 4
					right *= 4
					bottom *= 4
					left *= 4

					# Draw a box around the face
					cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

					# Draw a label with a name below the face
					# cv2.rectangle(frame, (left, bottom - 35),(right, bottom), (0, 0, 255), cv2.FILLED)
					# font = cv2.FONT_HERSHEY_DUPLEX
					# cv2.putText(frame, name, (left + 6, bottom - 6),font, 1.0, (255, 255, 255), 1)

					# Display the resulting image
					cv2.imshow('Video', frame)

					# Hit 'q' on the keyboard to quit!
					if cv2.waitKey(1) & 0xFF == ord('q'):
						break
			except Exception as e:
				print(f"Error during recognition: {e}")
			finally:
				self.stop()

	def stop(self):
		# Release handle to the webcam
		self.video_capture.release()
		cv2.destroyAllWindows()

video = ClientID()
