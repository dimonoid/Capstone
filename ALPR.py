import re

import cv2
import imutils
import matplotlib.pyplot as plt
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

garbage_words_list = ['ontario', 'to', 'discover', 'mar']


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
    if cnt is not None:
        new_image = cv2.drawContours(mask, [cnt], 0, 255, -1)
        new_image = cv2.bitwise_and(frame, frame, mask=mask)

        (x, y) = np.where(mask == 255)  # crop out masked image
        (x1, y1) = (np.min(x), np.min(y))
        (x2, y2) = (np.max(x), np.max(y))
        crop = gray[x1:x2 + 1, y1:y2 + 1]

        text = pytesseract.image_to_string(crop)
        text = re.sub('[\W_]+', '', text)
        for exception in garbage_words_list:
            text = text.replace(exception, '')

        print("License plate number is: ", text)
        return text
    else:
        return None


np.random.seed(42)

classes_path = './input/yolo-weights-for-licence-plate-detector/classes.names'
weights_path = './input/yolo-weights-for-licence-plate-detector/lapi.weights'
configuration_path = './input/yolo-weights-for-licence-plate-detector/darknet-yolov3.cfg'

with open(classes_path) as f:
    labels = [line.strip() for line in f]

colours = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')

probability_minimum = 0.5
threshold = 0.3

network = cv2.dnn.readNetFromDarknet(configuration_path, weights_path)
layers_names_all = network.getLayerNames()
# layers_names_output = [layers_names_all[i[0]-1] for i in network.getUnconnectedOutLayers()]  # uncomment when using CUDA
layers_names_output = [layers_names_all[i - 1] for i in network.getUnconnectedOutLayers()]  # when using CPU


def display_image(image_to_show):
    plt.rcParams['figure.figsize'] = (10.0, 10.0)
    plt.imshow(cv2.cvtColor(image_to_show, cv2.COLOR_BGR2RGB))
    plt.show()


def rotate_image(image, angle):
    image_rotated = imutils.rotate_bound(image, angle)
    return image_rotated


def readLP2(image_input, angle=0):
    blob = cv2.dnn.blobFromImage(image_input, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    blob_to_show = blob[0, :, :, :].transpose(1, 2, 0)

    display_image(blob_to_show)

    network.setInput(blob)
    output_from_network = network.forward(layers_names_output)

    bounding_boxes = []
    confidences = []
    class_numbers = []
    h, w = image_input.shape[:2]

    for result in output_from_network:
        for detection in result:
            scores = detection[5:]
            class_current = np.argmax(scores)
            confidence_current = scores[class_current]
            if confidence_current > probability_minimum:
                box_current = detection[0:4] * np.array([w, h, w, h])
                x_center, y_center, box_width, box_height = box_current.astype('int')
                x_min = int(x_center - (box_width / 2))
                y_min = int(y_center - (box_height / 2))
                bounding_boxes.append([x_min, y_min, int(box_width), int(box_height)])
                confidences.append(float(confidence_current))
                class_numbers.append(class_current)

    results = cv2.dnn.NMSBoxes(bounding_boxes, confidences, probability_minimum, threshold)

    image_input_copy = image_input.copy()

    if len(results) > 0:
        for i in results.flatten():
            x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
            box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]
            colour_box_current = [int(j) for j in colours[class_numbers[i]]]
            cv2.rectangle(image_input, (x_min, y_min), (x_min + box_width, y_min + box_height),
                          colour_box_current, 5)
            text_box_current = '{}: {:.4f}'.format(labels[int(class_numbers[i])], confidences[i])
            cv2.putText(image_input, text_box_current, (x_min, y_min - 7), cv2.FONT_HERSHEY_SIMPLEX,
                        1.5, colour_box_current, 5)

    else:
        print('No license plate detected')
        return []

    display_image(image_input)

    crop = cv2.cvtColor(image_input_copy[(y_min):(y_min + box_height), (x_min):(x_min + box_width)], cv2.COLOR_BGR2RGB)

    display_image(crop)

    list_of_possible_plates = []

    for anngle_trial in range(-angle, angle + 1, 1):
        crop_rotated = rotate_image(crop, anngle_trial)
        text = pytesseract.image_to_string(crop_rotated, lang='eng', config='--psm 7')
        text = re.sub(r'[\W_]+', '', text)
        for exception in garbage_words_list:
            text = text.replace(exception, '')

        if len(text) > 0:
            list_of_possible_plates.append(text)
        print(anngle_trial, text)

    return list_of_possible_plates


if __name__ == '__main__':
    ret = readLP2(cv2.imread('./input/labeled-licence-plates-dataset/dataset/train/145.jpg'), 5)
    print(ret)
