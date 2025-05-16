import cv2
import threading
from analytics.yolov5_annotator import YOLOv5Annotator

def camera_worker(cam_id, window_name):
    cap = cv2.VideoCapture(cam_id)
    if not cap.isOpened():
        print(f"[!] Camera {cam_id} could not be opened.")
        return

    detector = YOLOv5Annotator()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = detector.annotate_frame(frame)
        cv2.imshow(window_name, result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(window_name)

def start_multi_yolo_stream(camera_ids):
    threads = []
    for i, cam_id in enumerate(camera_ids):
        t = threading.Thread(target=camera_worker, args=(cam_id, f"Camera {i}"))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":

    start_multi_yolo_stream([0])
