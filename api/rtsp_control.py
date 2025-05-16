import sys
import os
import threading
import subprocess

stream_thread = None
stream_process = None

def start_rtsp_stream():
    global stream_thread, stream_process

    if stream_thread and stream_thread.is_alive():
        return "RTSP stream already running."

    def run():
        global stream_process

        python_path = os.path.join(os.getcwd(), "venv", "bin", "python")
        script_path = os.path.abspath("rtsp_test.py")

        env = os.environ.copy()
        env["PATH"] = os.path.join(os.getcwd(), "venv", "bin") + ":" + env["PATH"]

        print(">>> Forcing Python:", python_path)
        stream_process = subprocess.Popen([python_path, script_path], env=env)

    stream_thread = threading.Thread(target=run)
    stream_thread.start()
    return "RTSP stream started."

def stop_rtsp_stream():
    global stream_process
    if stream_process:
        stream_process.terminate()
        stream_process = None
        return "RTSP stream stopped."
    return "RTSP stream is not running."
