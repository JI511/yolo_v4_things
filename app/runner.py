import datetime
import os
import tensorflow as tf
import cv2
import numpy as np
from glob import glob
from models import Yolov4
import sys
sys.path.append("..")

model = Yolov4(weight_path='../yolov4.weights',
               class_name_path='../class_names/coco_classes.txt')
array, df = model.predict('../img/street.jpeg', random_color=True)

processed_name = datetime.datetime.now().microsecond
if not os.path.exists('../img_processed'):
    os.mkdir('../img_processed')
cv2.imwrite('../img_processed/%s.jpeg' % processed_name, array)
print(df)
