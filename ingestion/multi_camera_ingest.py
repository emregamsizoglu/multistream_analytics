import cv2
import threading

def capture_stream(camera_id, window_name):
    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print(f"Camera {camera_id} could not be opened.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(window_name)

def start_multi_camera(cameras):
    threads = []
    for i, cam_id in enumerate(cameras):
        thread = threading.Thread(target=capture_stream, args=(cam_id, f'Camera {i}'))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()
