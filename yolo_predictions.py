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

    def predict_and_save_image(self, image_data):
        """
        Performs a model prediction on the provided image and saves the predicted image with bounding boxes.

        :param image_data: Path to the image.
        :return Numpy array of the processed image.
        """
        start_time = time.time()
        array, df = self.model.predict(image_data, random_color=True, plot_img=False)
        processing_time = time.time() - start_time
        self._prediction_sum += processing_time
        self.total_predictions += 1
        if self.average_predict_time is None:
            self.average_predict_time = processing_time
        else:
            self.average_predict_time = round(self._prediction_sum / self.total_predictions, 4)
        print('Avg prediction time: %s' % self.average_predict_time)

        return array


if __name__ == '__main__':
    pass
