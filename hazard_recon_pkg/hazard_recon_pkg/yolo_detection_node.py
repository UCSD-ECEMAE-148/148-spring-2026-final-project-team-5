#!/usr/bin/env python3
"""
ROS2 node: YOLO detection using OAK-D camera.
Publishes detected triangle class to /hazard_detected as a String.
Also streams annotated frames via MJPEG at http://<PI_IP>:8080
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from ultralytics import YOLO
import depthai as dai
import cv2
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

MODEL_PATH  = "/home/projects/final_ws/src/148-spring-2026-final-project-team-5/hazard_recon_pkg/triangle_ncnn_model/"
CONF_THRESH = 0.65
STREAM_PORT = 8080
LABELS      = ["blue triangle", "green triangle", "red trangle"]

COLORS = {
    "blue triangle":  (255, 100, 0),
    "green triangle": (0, 200, 0),
    "red trangle":    (0, 0, 220),
}

# Aspect ratio guard
MIN_ASPECT = 0.5
MAX_ASPECT = 2.0

# Shared frame for MJPEG stream
latest_frame = None
frame_lock = threading.Lock()


class MJPEGHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress access logs

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """
            <html>
            <head>
                <title>Hazard Recon - YOLO Stream</title>
                <style>
                    body { background: #111; color: #eee; font-family: sans-serif;
                           display: flex; flex-direction: column;
                           align-items: center; padding: 20px; }
                    img  { border: 2px solid #444; max-width: 100%; }
                    h2   { margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <h2>Hazard Recon - Live YOLO Feed</h2>
                <img src="/stream" />
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type",
                             "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()
            try:
                while True:
                    with frame_lock:
                        frame = latest_frame
                    if frame is None:
                        continue
                    _, jpg = cv2.imencode(".jpg", frame,
                                         [cv2.IMWRITE_JPEG_QUALITY, 80])
                    data = jpg.tobytes()
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(data)}\r\n\r\n".encode())
                    self.wfile.write(data)
                    self.wfile.write(b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                pass


def start_mjpeg_server():
    server = HTTPServer(("0.0.0.0", STREAM_PORT), MJPEGHandler)
    server.serve_forever()


class YoloDetectionNode(Node):
    def __init__(self):
        super().__init__('yolo_detection_node')
        self.pub = self.create_publisher(String, '/hazard_detected', 10)

        # Start MJPEG server in background
        t = threading.Thread(target=start_mjpeg_server, daemon=True)
        t.start()
        self.get_logger().info(f'Stream server started — open http://<PI_IP>:{STREAM_PORT}')

        self.get_logger().info('Loading NCNN model...')
        self.model = YOLO(MODEL_PATH, task='detect')
        self.get_logger().info('Model loaded. Starting OAK-D pipeline...')
        self._run_pipeline()

    def _run_pipeline(self):
        global latest_frame
        device = dai.Device()
        with dai.Pipeline(device) as pipeline:
            cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
            q = cam.requestOutput(
                size=(640, 640),
                type=dai.ImgFrame.Type.BGR888p,
                fps=15
            ).createOutputQueue()

            pipeline.start()
            self.get_logger().info('Pipeline running.')

            while rclpy.ok() and pipeline.isRunning():
                frame_msg = q.tryGet()
                if frame_msg is None:
                    continue

                frame = frame_msg.getCvFrame()
                results = self.model(frame, conf=CONF_THRESH, verbose=False)

                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        conf   = float(box.conf[0])
                        label  = LABELS[cls_id] if cls_id < len(LABELS) else 'unknown'
                        color  = COLORS.get(label, (255, 255, 255))

                        # Aspect ratio filter
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        w, h = x2 - x1, y2 - y1
                        aspect = w / h if h > 0 else 0
                        if aspect < MIN_ASPECT or aspect > MAX_ASPECT:
                            continue

                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, f"{label} {conf:.2f}",
                                    (x1, y1 - 8),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                        self.get_logger().info(f'Detected: {label} ({conf:.2f})')
                        msg = String()
                        msg.data = label
                        self.pub.publish(msg)

                # Push annotated frame to stream
                with frame_lock:
                    latest_frame = frame.copy()


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
