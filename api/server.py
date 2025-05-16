from api.rtsp_control import start_rtsp_stream, stop_rtsp_stream
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading
import cv2
from analytics.yolov5_annotator import YOLOv5Annotator

app = FastAPI()
active_streams = {}

class CameraRequest(BaseModel):
    camera_id: int

def stream_worker(camera_id: int):
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"[!] Camera {camera_id} could not be opened.")
        return

    detector = YOLOv5Annotator()
    window_name = f"Camera {camera_id}"

    while active_streams.get(camera_id, False):
        ret, frame = cap.read()
        if not ret:
            break

        result = detector.annotate_frame(frame)
        cv2.imshow(window_name, result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(window_name)
    active_streams[camera_id] = False

@app.get("/status")
def get_status():
    return {"active_cameras": [k for k, v in active_streams.items() if v]}

@app.post("/start")
def start_camera(req: CameraRequest):
    camera_id = req.camera_id
    if active_streams.get(camera_id, False):
        raise HTTPException(status_code=400, detail="Camera already running.")

    active_streams[camera_id] = True
    thread = threading.Thread(target=stream_worker, args=(camera_id,))
    thread.start()
    return {"message": f"Camera {camera_id} started."}

@app.post("/stop")
def stop_camera(req: CameraRequest):
    camera_id = req.camera_id
    if not active_streams.get(camera_id, False):
        raise HTTPException(status_code=400, detail="Camera not running.")

    active_streams[camera_id] = False
    return {"message": f"Camera {camera_id} stopping..."}

@app.post("/start-stream")
def start_stream():
    return {"message": start_rtsp_stream()}

@app.post("/stop-stream")
def stop_stream():
    return {"message": stop_rtsp_stream()}
