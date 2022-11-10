from json import detect_encoding
from flask import Flask, render_template, Response, flash
import cv2
import face_recognition
import numpy as np

# Get a reference to webcam #0 (the default one)
app = Flask(__name__)
#camera = cv2.VideoCapture(cv2.CAP_V4L2)

# Load a sample picture and learn how to recognize it.
ahmad0 = face_recognition.load_image_file("images/ahmad0.jpg")
ahmad0_face_encoding = face_recognition.face_encodings(ahmad0)[0]

# Load a sample picture and learn how to recognize it.
ahmad1 = face_recognition.load_image_file("images/ahmad1.jpg")
ahmad1_face_encoding = face_recognition.face_encodings(ahmad1)[0]

# Load a second sample picture and learn how to recognize it.
ahmad2 = face_recognition.load_image_file("images/ahmad2.jpg")
ahmad2_face_encoding = face_recognition.face_encodings(ahmad2)[0]


# Create arrays of known face encodings and their names
known_face_encodings = [
    ahmad0_face_encoding,
    ahmad1_face_encoding,
    ahmad2_face_encoding
]
known_face_names = [
    "ahmad0",
    "ahmad1",
    "ahmad2"
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

def gen_frames():
    camera = cv2.VideoCapture(0)

    while True:       
        success, frame = camera.read()
        if not success:
            break
        else:
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
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)  ## Label of the image being matched!
                print(name)
                log_person(name)
            

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

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def log_person(name):
    return name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True) 