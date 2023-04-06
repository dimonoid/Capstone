from json import detect_encoding
from flask import Flask, render_template, Response, flash
import cv2
import face_recognition
import numpy as np

import pickle
import urllib
import requests

from os import walk


# Get a reference to webcam #0 (the default one)
# app = Flask(__name__)
# camera = cv2.VideoCapture(cv2.CAP_V4L2)


def fit():
    # # Load a sample picture and learn how to recognize it.
    # ahmad = face_recognition.load_image_file("images/Ahmad.jpg")
    # ahmad_face_encoding = face_recognition.face_encodings(ahmad)[0]
    #
    # # Load a second sample picture and learn how to recognize it.
    # mohamad = face_recognition.load_image_file("images/Mohamad.jpg")
    # mohamad_face_encoding = face_recognition.face_encodings(mohamad)[0]
    #
    # # Load a second sample picture and learn how to recognize it.
    # humza = face_recognition.load_image_file("images/Humza.jpg")
    # humza_face_encoding = face_recognition.face_encodings(humza)[0]
    #
    # # Create arrays of known face encodings and their names
    # known_face_encodings = [
    #     ahmad_face_encoding,
    #     mohamad_face_encoding,
    #     humza_face_encoding
    # ]
    # known_face_names = [
    #     "Ahmad",
    #     "Mohamad",
    #     "Humza"
    # ]

    encodings = []
    for (dirpath, dirnames, filenames) in walk("test/"):
        for filename in filenames:
            encodings.append(Face(filename, face_recognition.load_image_file(dirpath + filename)))

    # a = pickle.dumps(known_face_encodings)

    return encodings


def save_random_faces(n=10, folder='test'):
    """Downloads fake face to file"""
    d = set()
    for i in range(n):

        while 1:
            img_data = requests.get("https://thispersondoesnotexist.com/image",
                                    headers={'Cache-Control': 'no-cache'}).content
            if img_data not in d:
                break

        d.add(img_data)
        print(i, img_data.__hash__())

        with open('./' + folder + '/face_image_' + str(i) + '.jpg', 'wb') as handler:
            handler.write(img_data)


class Face:
    def __init__(self, name, encodings):
        self.encodings = encodings
        self.name = name


if __name__ == '__main__':
    # for i in range(10):
    #    save_random_face(i, 'test')

    # save_random_faces(100)

    print(fit())

    # face_recognition.
