import glob
import os

import cv2
import face_recognition
import numpy as np


class FaceEngine:
    def __init__(self, debug=False):
        self.debug = debug
        self.percent_accuracy = 0
        self.debug = False

        ### NOTE: All images must have the following format to loaded and read properly:  'name.jpg' ####

        # Create arrays of known face encodings and their names
        self.known_face_encodings = []
        self.known_face_names = []

        # Load all images names into lists

        images = (os.listdir('images/'))
        imagesRGB = [face_recognition.load_image_file(file) for file in glob.glob('images/*.jpg')]

        # Add the known names as strings into an array & process their encodings
        for i in range(len(images)):
            self.known_face_names.append(images[i][:-4])
            sample_face_encoding = face_recognition.face_encodings(imagesRGB[i])[0]
            self.known_face_encodings.append(sample_face_encoding)

    def getFaces(self, frame):
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)

        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            ## Calculate the accuracy of the face detected (compared with the highest matched face)
            global percent_accuracy
            percent_accuracy = np.round((1 - face_distances[best_match_index]) * 100, 2)
            if matches[best_match_index] and percent_accuracy >= 50:
                name = self.known_face_names[best_match_index]

            face_names.append(name)  ## Label of the image being matched!

            ## Only print accuracy if it redetects a new person/unknown
            if (self.debug):
                print("Accuracy: " + str(self.percent_accuracy) + "% " + name)

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return face_names, frame
