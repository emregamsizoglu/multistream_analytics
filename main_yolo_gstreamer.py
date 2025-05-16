import cv2
from analytics.yolov5_annotator import YOLOv5Annotator
from utils_gstreamer.gstreamer_camera import GStreamerCamera


def main():
    pipeline = (
        "avfvideosrc device-index=0 ! "
        "videoconvert ! video/x-raw,format=BGR,width=640,height=480 ! "
        "appsink name=mysink"
    )

    cam = GStreamerCamera(pipeline)
    cam.start()

    detector = YOLOv5Annotator()

    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        annotated = detector.annotate_frame(frame)
        cv2.imshow("GStreamer YOLO", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
