import datetime
import os
import tensorflow as tf
import cv2
import numpy as np
from glob import glob
from models import Yolov4
import sys
sys.path.append("..")


def predict_and_save_image(image_path):
    """
    Performs a model prediction on the provided image and saves the predicted image with bounding boxes.

    :param image_path: Path to the image to process.
    :return The time taken to perform and save the prediction.
    """
    print('\nProcessing: %s' % image_path)
    processed_time = datetime.datetime.now()
    image_name = os.path.split(image_path)[1].split('.')[0]
    array, df = model.predict(image_path, random_color=True)
    if not os.path.exists('../img_processed'):
        os.mkdir('../img_processed')
    cv2.imwrite('../img_processed/%s_%s.jpeg' % (image_name, processed_time.microsecond), array)
    # print(df)
    return datetime.datetime.now() - processed_time


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    model = Yolov4(weight_path='../yolov4.weights',
                   class_name_path='../class_names/coco_classes.txt')
    yolo_time = datetime.datetime.now()
    print('yolo init complete in: %s' % (yolo_time - start_time))

    print(predict_and_save_image('../img/street.jpeg'))
    print(predict_and_save_image('../img/test6.jpg'))
    print(predict_and_save_image('../img/test2.jpg'))
    print(predict_and_save_image('../img/test3.jpg'))
    print(predict_and_save_image('../img/test.jpg'))
    print(predict_and_save_image('../img/test.jpg'))
    print(predict_and_save_image('../img/test.jpg'))
    print(predict_and_save_image('../img/test.jpg'))
    print(predict_and_save_image('../img/test.jpg'))

    print('\ntotal time: %s' % (datetime.datetime.now() - start_time))
