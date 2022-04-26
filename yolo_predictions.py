import datetime
import os
import tensorflow as tf
import cv2
import numpy as np
from glob import glob
from models import Yolov4
import sys
sys.path.append("")


class YoloPredictions(object):

    def __init__(self):
        self.model = Yolov4(weight_path='yolov4.weights', class_name_path='class_names/coco_classes.txt')

    def predict_and_save_image(self, image_data):
        """
        Performs a model prediction on the provided image and saves the predicted image with bounding boxes.

        :param image_data: Path to the image.
        :return Numpy array of the processed image.
        """
        print('\nProcessing: %s' % image_data)
        processed_time = datetime.datetime.now()
        image_name = os.path.split(image_data)[1]
        array, df = self.model.predict(image_data, random_color=True, plot_img=False)
        if not os.path.exists('./img_processed'):
            os.mkdir('./img_processed')
        # cv2.imwrite('./img_processed/processed_%s' % image_name, array)
        print(datetime.datetime.now() - processed_time)
        return array


if __name__ == '__main__':
    pass
