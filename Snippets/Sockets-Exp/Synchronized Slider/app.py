from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

values = {
    'slider1': 25,
    'slider2': 0,
}


@app.route('/')
def index():
    return render_template('index.html', **values)


@socketio.on('connect')
def test_connect():
    print('Client connected')
    emit('after connect', {'data': 'Lets dance'})


@socketio.on('Slider value changed')
def value_changed(message):
    print(message)
    # values[message['who']] = message['data']
    # emit('update value', message, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True, ssl_context='adhoc')
