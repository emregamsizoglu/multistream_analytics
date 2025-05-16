import sys
import os
import cv2
import torch


FILE = os.path.dirname(os.path.abspath(__file__))
YOLO_DIR = os.path.join(FILE, '..', 'yolov5')
sys.path.append(YOLO_DIR)

class YOLOv5Annotator:
    def __init__(self, model_name='yolov5s'):

        self.model = torch.hub.load('ultralytics/yolov5', model_name, pretrained=True)
        self.model.eval()

    def annotate_frame(self, frame):

        results = self.model(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        return results.render()[0]
