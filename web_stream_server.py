from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
import cv2
import threading
import time

app = FastAPI()
camera = None
streaming = False
lock = threading.Lock()

def generate_frames():
    global camera
    while streaming:
        with lock:
            if camera is None:
                break
            success, frame = camera.read()
            if not success:
                continue
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )
        time.sleep(0.03)

@app.get("/", response_class=HTMLResponse)
def main_page():
    return """
    <html>
        <head>
            <title>Live Stream Control</title>
        </head>
        <body>
            <h2>YOLOv5 Stream Demo</h2>
            <button onclick="fetch('/start-stream', {method: 'POST'}).then(() => location.reload())">Start Stream</button>
            <button onclick="fetch('/stop-stream', {method: 'POST'}).then(() => location.reload())">Stop Stream</button>
            <br><br>
            <img src="/video_feed" width="640" height="480"/>
        </body>
    </html>
    """

@app.post("/start-stream")
def start_stream():
    global camera, streaming
    if not streaming:
        camera = cv2.VideoCapture(0)
        streaming = True
    return JSONResponse(content={"status": "stream started"})

@app.post("/stop-stream")
def stop_stream():
    global camera, streaming
    if streaming:
        streaming = False
        with lock:
            if camera:
                camera.release()
                camera = None
    return JSONResponse(content={"status": "stream stopped"})

@app.get("/video_feed")
def video_feed():
    if not streaming or camera is None:
        return JSONResponse(status_code=400, content={"error": "Stream not active"})
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
