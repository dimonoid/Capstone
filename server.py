from json import detect_encoding
from flask import Flask, render_template, Response, flash
import cv2
import face_recognition
import numpy as np

import pickle
import urllib
import requests


# Get a reference to webcam #0 (the default one)
# app = Flask(__name__)
# camera = cv2.VideoCapture(cv2.CAP_V4L2)


def fit():
    # Load a sample picture and learn how to recognize it.
    ahmad = face_recognition.load_image_file("images/Ahmad.jpg")
    ahmad_face_encoding = face_recognition.face_encodings(ahmad)[0]

    # Load a second sample picture and learn how to recognize it.
    mohamad = face_recognition.load_image_file("images/Mohamad.jpg")
    mohamad_face_encoding = face_recognition.face_encodings(mohamad)[0]

    # Load a second sample picture and learn how to recognize it.
    humza = face_recognition.load_image_file("images/Humza.jpg")
    humza_face_encoding = face_recognition.face_encodings(humza)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        ahmad_face_encoding,
        mohamad_face_encoding,
        humza_face_encoding
    ]
    known_face_names = [
        "Ahmad",
        "Mohamad",
        "Humza"
    ]

    a = pickle.dumps(known_face_encodings)

    print(a)


def save_random_face(i, folder):
    img_data = requests.get("https://thispersondoesnotexist.com/image").content
    with open('./' + folder + '/face_image_' + str(i) + '.jpg', 'wb') as handler:
        handler.write(img_data)


class Face:
    def __init__(self, encodings, name):
        self.encodings = encodings
        self.name = name


if __name__ == '__main__':
    fit()
    # for i in range(10):
    #    save_random_face(i, 'test')
