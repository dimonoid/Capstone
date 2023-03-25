import re
from collections import deque

import cv2
import imutils
import numpy as np
import pytesseract

from dbFunc import plate_detected


def readLP(frame):
    # pytesseract.pytesseract.tesseract_cmd= r'C:\Program Files\Tesseract-OCR\tesseract'
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # gray image
    noise_reduction = cv2.bilateralFilter(gray, 13, 15, 15)  # apply filters for noise reduction
    edged = cv2.Canny(noise_reduction, 30, 200)  # detect edges

    points = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # approximate contours
    contours = imutils.grab_contours(points)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]  # find top 10 contours

    # loop top 10 contours to find license plate
    cnt = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            cnt = approx
            break

    mask = np.zeros(gray.shape, np.uint8)  # mask image
    new_image = cv2.drawContours(mask, [cnt], 0, 255, -1)
    new_image = cv2.bitwise_and(frame, frame, mask=mask)

    (x, y) = np.where(mask == 255)  # crop out masked image
    (x1, y1) = (np.min(x), np.min(y))
    (x2, y2) = (np.max(x), np.max(y))
    crop = gray[x1:x2 + 1, y1:y2 + 1]

    text = pytesseract.image_to_string(crop)
    text = re.sub('[\W_]+', '', text)

    print("License plate number is: ", text)

    d = deque(plate_detected(text))

    return text
