import datetime
import os
import time
from models import Yolov4
import sys
sys.path.append("")


class YoloPredictions(object):

    def __init__(self):
        if not os.path.exists('./img_processed'):
            os.mkdir('./img_processed')
        self.model = Yolov4(weight_path='yolov4.weights', class_name_path='class_names/coco_classes.txt')
        self.total_predictions = 0
        self._prediction_sum = 0
        self.average_predict_time = None

    def predict_image(self, image):
        start_time = time.time()
        if isinstance(image, str):
            array, df = self.model.predict(image, random_color=True, plot_img=False)
        else:
            array, df = self.model.predict_img(image, random_color=True, plot_img=False, return_output=True)
        processing_time = time.time() - start_time
        self._prediction_sum += processing_time
        self.total_predictions += 1
        self.average_predict_time = round(self._prediction_sum / self.total_predictions, 2)

        if self.total_predictions % 20 == 0:
            print(self.average_predict_time)

        return array


if __name__ == '__main__':
    pass
