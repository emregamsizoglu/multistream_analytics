import cv2
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer
import threading
import numpy as np
from analytics.yolov5_annotator import YOLOv5Annotator
from utils_gstreamer.gstreamer_camera import GStreamerCamera

Gst.init(None)

class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        super(SensorFactory, self).__init__()
        self.detector = YOLOv5Annotator()

        pipeline = (
            "avfvideosrc device-index=0 ! "
            "videoconvert ! video/x-raw,format=BGR,width=640,height=480 ! "
            "appsink name=mysink"
        )
        self.camera = GStreamerCamera(pipeline)
        self.camera.start()

        self.launch_string = (
            'appsrc name=source is-live=true block=true format=time '
            'caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! '
            'videoconvert ! video/x-raw,format=I420,colorimetry=bt709 ! '
            'x264enc tune=zerolatency ! rtph264pay config-interval=1 name=pay0 pt=96'
        )

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        appsrc = rtsp_media.get_element().get_child_by_name("source")
        appsrc.set_property("format", Gst.Format.TIME)

        def push_data(_):
            ret, frame = self.camera.read()
            if not ret or frame is None:
                return False

            annotated = self.detector.annotate_frame(frame)
            data = annotated.tobytes()

            buf = Gst.Buffer.new_allocate(None, len(data), None)
            buf.fill(0, data)
            buf.duration = Gst.util_uint64_scale_int(1, Gst.SECOND, 30)

            timestamp = getattr(self, "timestamp", 0)
            buf.pts = buf.dts = int(timestamp)
            buf.offset = timestamp
            self.timestamp = timestamp + buf.duration

            retval = appsrc.emit("push-buffer", buf)
            return retval == Gst.FlowReturn.OK

        GLib.timeout_add(33, push_data, appsrc)

def start_rtsp_server(port=8554, mount_point="/video"):
    server = GstRtspServer.RTSPServer()
    server.props.service = str(port)
    factory = SensorFactory()
    factory.set_shared(True)
    mount_points = server.get_mount_points()
    mount_points.add_factory(mount_point, factory)
    server.attach(None)
    print(f"🎥 RTSP stream started at rtsp://127.0.0.1:{port}{mount_point}")
    loop = GLib.MainLoop()
    loop.run()
