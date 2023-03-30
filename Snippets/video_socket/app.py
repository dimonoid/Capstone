import base64
import io
from io import StringIO

from PIL import Image

import cv2
import imutils
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


def readb64(base64_string):
    idx = base64_string.find('base64,')
    base64_string = base64_string.split(',')[1]
    # base64_string = base64_string[idx + 7:]

    sbuf = io.BytesIO()

    sbuf.write(base64.b64decode(base64_string, ' /'))
    pimg = Image.open(sbuf)

    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@socketio.on('image')
def image(data_image):
    print("Frame received")

    global fps, cnt, prev_recv_time, fps_array
    # recv_time = time.time()
    # text = 'FPS: ' + str(fps)
    frame = (readb64(data_image))

    # frame = changeLipstick(frame, [255, 0, 0])
    # frame = ps.putBText(frame, text, text_offset_x=20, text_offset_y=30, vspace=20, hspace=10, font_scale=1.0,
    #                    background_RGB=(10, 20, 222), text_RGB=(255, 255, 255))
    imgencode = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])[1]

    # base64 encode
    stringData = base64.b64encode(imgencode).decode('utf-8')
    b64_src = 'data:image/jpeg;base64,'
    stringData = b64_src + stringData

    # emit the frame back
    emit('response_back', stringData)

    # fps = 1 / (recv_time - prev_recv_time)
    # fps_array.append(fps)
    # fps = round(moving_average(np.array(fps_array)), 1)
    # prev_recv_time = recv_time
    ## print(fps_array)
    # cnt += 1
    # if cnt == 30:
    #    fps_array = [fps]
    #    cnt = 0

    # sbuf = StringIO()
    # sbuf.write(data_image)


#
## decode and convert into image
# b = io.BytesIO(base64.b64decode(data_image))
# pimg = Image.open(b)
#
### converting RGB to BGR, as opencv standards
# frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
#
## Process the image frame
# frame = imutils.resize(frame, width=700)
# frame = cv2.flip(frame, 1)
# imgencode = cv2.imencode('.jpg', frame)[1]
#
## base64 encode
# stringData = base64.b64encode(imgencode).decode('utf-8')
# b64_src = 'data:image/jpg;base64,'
# stringData = b64_src + stringData
#
## emit the frame back
# emit('response_back', stringData)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True, ssl_context='adhoc')
