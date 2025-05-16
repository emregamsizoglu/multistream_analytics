from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import cv2
import time
from utils_gstreamer.gstreamer_camera import GStreamerCamera
from analytics.yolov5_annotator import YOLOv5Annotator

app = FastAPI()


pipeline = (
    "avfvideosrc device-index=0 ! "
    "videoconvert ! video/x-raw,format=BGR,width=640,height=480 ! "
    "appsink name=mysink"
)
camera = GStreamerCamera(pipeline)
camera.start()

detector = YOLOv5Annotator()


@app.get("/video_feed")
def video_feed():
    def generate():
        print("[INFO] Starting MJPEG stream")
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                print("[WARN] No frame")
                time.sleep(0.01)
                continue

            annotated = detector.annotate_frame(frame)
            ret2, jpeg = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not ret2:
                print("[WARN] JPEG encode failed")
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
            )
            time.sleep(0.03)

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>YOLOv5 Live Stream</title>
        </head>
        <body>
            <h2>YOLOv5 Live Stream</h2>
            <img src="/video_feed" width="640" height="480"/>
        </body>
    </html>
    """
