import os
import cv2

yolo_config = {
    # Basic
    'img_size': (416, 416, 3),
    'anchors': [12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401],
    'strides': [8, 16, 32],
    'xyscale': [1.2, 1.1, 1.05],

    # Training
    'iou_loss_thresh': 0.5,
    'batch_size': 8,
    'num_gpu': 1,  # 2,

    # Inference
    'max_boxes': 100,
    'iou_threshold': 0.413,
    'score_threshold': 0.3,
}

display_config = {
    "info_text_color": (0, 211, 0),
    "font": cv2.FONT_HERSHEY_PLAIN,
    "font_size": 1.0,
    "thickness": 1
}

VIDEO_SAVE_DIRECTORY = os.path.abspath(__file__)
