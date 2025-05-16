import cv2
from analytics.yolov5_annotator import YOLOv5Annotator

def main():
    detector = YOLOv5Annotator()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera could not be opened.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break


        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        annotated = detector.annotate_frame(frame)

        cv2.imshow("YOLO Annotated - OpenCV Preview", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
