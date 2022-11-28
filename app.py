from json import detect_encoding
from flask import Flask, render_template, Response, flash
import cv2
import glob
import face_recognition
import numpy as np
import os
from flask import request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3

from sqlalchemy.sql import func

# Get a reference to webcam #0 (the default one)
app = Flask(__name__, static_url_path='', )

#set path to database and initialize
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'Databse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

currentName = ""
percent_accuracy = None

### NOTE: All images must have the following format to loaded and read properly:  'name.jpg' ####

# Create arrays of known face encodings and their names
known_face_names = list()
known_face_encodings = list()

# Load all images names into lists 

images = (os.listdir('images/'))
imagesRGB = [face_recognition.load_image_file(file) for file in glob.glob('images/*.jpg')]

# Add the known names as strings into an array & process their encodings
for i in range(len(images)):
    known_face_names.append(images[i][:-4])
    sample_face_encoding = face_recognition.face_encodings(imagesRGB[i])[0]
    known_face_encodings.append(sample_face_encoding)

process_this_frame = True



def gen_frames():
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []

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

                ## Calculate the accuracy of the face detected (compared with the highest matched face)
                global percent_accuracy
                percent_accuracy = np.round((1-face_distances[best_match_index]) * 100 , 2)
                if matches[best_match_index] and percent_accuracy >= 50:
                    name = known_face_names[best_match_index]

                face_names.append(name)  ## Label of the image being matched!

                ## Only print accuracy if it redetects a new person/unknown
                global currentName
                if(name != currentName):
                    print("Accuracy: " + str(percent_accuracy) + " %")

                currentName = name
            
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


def log_person():
    return currentName

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lpPage', methods=['GET', 'POST'])
def lpPage():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('lpPage.html')

@app.route('/fPage', methods=['GET', 'POST'])
def fPage():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('fPage.html', displayName = currentName, displayAccuracy = str(percent_accuracy) + " %")

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True) 

#class to declare a license plate    
class Plate(db.Model):
    id=db.Column(db.String(7), nullable = False, unique=True)
    name=db.Column(db.String(100), nullable=False)
    info=db.Column(db.String(500), nullable=False)
    
    def __repr__(self):
        return f'<Plate {self.id}>'        

#compare string detected from license plate to plate table in database
def plate_detected(str):
    conn = sqlite3.connect('Database.db')
    cur=conn.cursor()
    cur.execute("SELECT * FROM LicensePlate WHERE one=?", (columnchosen,))

    records = cur.fetchall()
    for row in records:
		if(row[0] == str):
			print("License Plate Number: ", row[0])
			print("Owner: ", row[1])
			print("Infractions: ", row[2])
			print("/n")
        
    cur.close()

#add License Plate to database
def add_plate(LicensePlate, Owner, Info):
	try:
		con = sql.connect('Database.db')
		c = con.cursor()
		c.execute("INSERT INTO LicensePlate (LicensePlate, Owner, Info) VALUES (%s, %s, %s)" %(LicensePlate, Owner, Info))
		con.commit()
	except:
		print("Error adding plate to db")

#add Face to database
def add_face(Name, Crime):
	try:
		con=sql.connect('Database.db')
		c=con.cursor()
		c.execute("INSERT INTO Criminals (Name, Crime) VALUES (%b, %s, %s)" %(Name, Crime))
		con.commit()
	except:
		print("Error adding face to db")

#compare string of person's name to database
def compare_face(str):
	conn = sqlite3.connect('Database.db')
	cur=conn.cursor()
	cur.execute("SELECT * FROM Criminals WHERE one=?", (columnchosen,))
	
	records = curr.fetchall()
	for row in records:
		if(row[0] == str):
			print("Name: ", row[0])
			print("Crimes: ", row[1]
			print("/n")
		
	cur.close()


