import datetime

import boto3
import cv2
from flask import jsonify, send_from_directory
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

import ALPR
import FaceEngine
from dbFunc import *
from dbFunctions import find_lp_owner

# import RPi.GPIO as GPIO # Uncomment when running on the pi

# Initialize app
app = Flask(__name__, static_url_path='', )

# Code needed for image uploading
app.config['SECRET_KEY'] = 'capstone123'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

sns_client = boto3.client(
    'sns',
    region_name='ca-central-1',
    aws_access_key_id='',
    aws_secret_access_key=''
)


class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, 'Only images are allowed.'),
            FileRequired('File field should not be empty.')
        ]
    )
    submit = SubmitField('Upload')


face_engine = FaceEngine.FaceEngine()

currentName = "-"
percent_accuracy = "-"
display_lpResult = "-"
display_oResult = "-"
display_iResult = "-"
display_cResult = "-"

running = False


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


class Timer:
    def __init__(self, N):
        self.start_time = self.time_last = datetime.datetime.now()
        self.N = N

    def print(self, text):
        time_now = datetime.datetime.now()
        print(N, text, (time_now - self.time_last))
        self.time_last = time_now

    def print_total(self):
        return str(datetime.datetime.now() - self.start_time)


N = 0

timer_frame_to_frame = Timer(N=0)  # to measure overall FPS without accounting for delays


def gen_frames(debug=False, filename=None):
    global running
    global currentName
    global N
    global timer_frame_to_frame
    """Generates facial predictions either from camera or local files"""
    print('gen_frames 1 started')
    if running:
        return None
    else:
        running = True

    if not debug:
        camera = cv2.VideoCapture(0)

    while True:
        try:
            if debug:
                frame = cv2.imread(filename)
                success = True
            else:
                success, frame = camera.read()

            if success:
                print('gen_frames next frame', N, 'processing...')
                timer = Timer(N=N)  # for each frame, to measure time in pipeline
                N += 1

                # use pipe and filter
                # print current time
                print(1, datetime.datetime.now().strftime("%H:%M:%S.%f"))

                # diminishing returns!,
                # (0, 1) is fastest but too low accuracy,
                # (10, 2) is optimal with lower accuracy,
                # (10, 1) is optimal with higher accuracy,
                # (45, 1) is too slow with the highest accuracy

                list_of_possible_plates, frame = ALPR.readLP2(frame, 10, 2, timer)
                print(list_of_possible_plates)
                print(2, datetime.datetime.now().strftime("%H:%M:%S.%f"))

                face_names, frame = face_engine.getFaces(frame)
                print(face_names)
                print(3, datetime.datetime.now().strftime("%H:%M:%S.%f"))

                currentName = face_names[0] if len(face_names) > 0 else "Unknown"

                # frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # optimization

                cv2.putText(frame,
                            timer_frame_to_frame.print_total(), (0, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255),
                            5)  # FPS
                timer_frame_to_frame = Timer(N=0)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame_ret = buffer.tobytes()

                print(4, datetime.datetime.now().strftime("%H:%M:%S.%f"))

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_ret + b'\r\n')
            else:
                running = False
                break
        except Exception as e:
            print(e)
            running = False
            break


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lpPage', methods=['GET', 'POST'])
def lpPage():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('get_file', filename=filename)
        global display_lpResult
        display_lpResult = ALPR.readLP(filename)  # Deprecated

        # Initialize database connection
        con = sqlite3.Connection('Database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # dbQuery = None if the plate isn't in the database
        dbQuery = find_lp_owner(display_lpResult, cur)
        print(dbQuery)
        print(type(dbQuery))
        global display_oResult
        global display_iResult
        global display_cResult
        if dbQuery is None:
            display_oResult = "Not Found"
            display_iResult = "Not Found"
            display_cResult = "Not Found"
        else:
            display_oResult = dbQuery['Owner']
            display_iResult = dbQuery['Info']
            display_cResult = dbQuery['Colour']
            # if(display_cResult == "red"):
            #        t = Thread(target=buzz_for_5_seconds)
            #        t.start()

        # Close connection to database
        con.close()

        print("Uploaded file: " + filename)  # Variable 'filename' stores the name of the image selected, e.g. im4.png
    else:
        file_url = None
    return render_template('lpPage.html',
                           form=form,
                           file_url=file_url,
                           display_lpResult=display_lpResult,
                           display_oResult=display_oResult,
                           display_iResult=display_iResult,
                           display_cResult=display_cResult,
                           my_string=display_cResult)


@app.route('/fPage', methods=['GET', 'POST'])
def fPage():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('fPage.html',
                           displayName=currentName,
                           displayAccuracy=str(percent_accuracy) + " %")


@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


@app.route("/currentName")
def updateCurrentName():
    print('name')
    return f"{currentName}"


@app.route("/displayAccuracy")
def updateAccuracy():
    print('acc')
    return str(percent_accuracy) + "%"


@app.route('/markers')
def get_markers_data():
    conn = sqlite3.connect('Database.db')
    c = conn.cursor()
    c.execute('SELECT latitude, longitude, name, date, time, threat FROM Markers')
    data = c.fetchall()
    conn.close()
    markers = []
    for item in data:
        markers.append({
            'lat': item[0],
            'lng': item[1],
            'name': item[2],
            'date': item[3],
            'time': item[4],
            'threat': item[5]
        })
    return jsonify(markers)


@app.route('/insert_marker', methods=['POST'])
def insert_marker():
    data = request.get_json()
    name = data['name']
    latitude = data['latitude']
    longitude = data['longitude']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date, time = timestamp.split(' ')
    threat = data['threat']

    print(threat)

    conn = sqlite3.connect('Database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Markers WHERE name=?", (name,))
    existing_marker = c.fetchone()

    if existing_marker is None:
        c.execute("INSERT INTO Markers (name, latitude, longitude, date, time, threat) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, latitude, longitude, date, time, threat))
        conn.commit()
        response = {'status': 'success', 'date': date, 'time': time}
    else:
        response = {'status': 'error', 'message': 'Marker with this name already exists'}

    conn.close()

    return jsonify(response)


@app.route('/send-text', methods=['POST'])
def send_text():
    data = request.get_json()
    phone_number = data['phone_number']
    name = data['name']
    latitude = data['latitude']
    longitude = data['longitude']
    date = data['date']
    time = data['time']
    threat = data['threat']
    message = f'Alert: {name} is detected! Location: ({latitude}, {longitude}) Date: {date} Time: {time} Threat: {threat}'
    response = sns_client.publish(
        PhoneNumber=phone_number,
        Message=message
    )
    return jsonify({'message': 'Text message sent!'})


@app.route('/criminals')
def get_criminals_data():
    conn = sqlite3.connect('Database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Criminals')
    data = c.fetchall()
    conn.close()
    criminals = []
    for item in data:
        criminals.append({
            'Name': item[0],
            'Crime': item[1],
            'Color': item[2]
        })
    return jsonify(criminals)


@app.route('/alarm.mp3')
def play_alarm():
    return send_from_directory(app.static_folder, 'alarm.mp3')


def test1():
    """All results are unknown means very low false positives, what is good result"""
    for i in range(100):
        gen = gen_frames(debug=True, filename="test/face_image_" + str(i) + ".jpg")

        print(i)
        gen.__next__()

        gen.close()


def test2():
    """Shows only recognizable faces"""
    for i in ("Ahmad", "Humza", "Leonardo", "Mohamad",):
        gen = gen_frames(debug=True, filename="images/" + i + ".jpg")

        print(i)
        gen.__next__()

        gen.close()


# def buzz_for_5_seconds():
#     BuzzerPin = 4

#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(BuzzerPin, GPIO.OUT)
#     GPIO.setwarnings(False)

#     global Buzz
#     Buzz = GPIO.PWM(BuzzerPin, 440)
#     Buzz.start(50)
#     A4=440
#     song = [A4]
#     beat = [1]

#     for i in range(0, int(5 / 0.13)):
#         Buzz.ChangeFrequency(song[0])
#         time.sleep(beat[0]*0.13)

#     Buzz.stop()
#     GPIO.cleanup()


if __name__ == '__main__':
    # test1()
    # test2()
    app.run(host='0.0.0.0', debug=True, threaded=True, ssl_context='adhoc')
