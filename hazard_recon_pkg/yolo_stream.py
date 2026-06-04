#!/usr/bin/env python3
"""
Standalone YOLO + OAK-D test — no ROS2.
Loads NCNN model and runs inference on OAK-D camera feed.
Streams annotated frames via MJPEG at http://<PI_IP>:8080

Usage:
    python3 yolo_test.py
Then open http://<PI_IP>:8080 in a browser on the same network.
Press Ctrl+C to quit.
"""

from ultralytics import YOLO
import depthai as dai
import cv2
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

MODEL_PATH  = "/home/projects/final_ws/src/148-spring-2026-final-project-team-5/hazard_recon_pkg/triangle_ncnn_model/"
CONF_THRESH = 0.5
STREAM_PORT = 8080

LABELS = ["blue triangle", "green triangle", "red trangle"]  # must match model exactly

COLORS = {
    "blue triangle":  (255, 100, 0),
    "green triangle": (0, 200, 0),
    "red trangle":    (0, 0, 220),
}

# Shared frame state
latest_frame = None
frame_lock = threading.Lock()


class MJPEGHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress access logs

    def do_GET(self):
        if self.path == "/":
            # Serve a simple HTML page with the stream embedded
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
                    _, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    data = jpg.tobytes()
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(data)}\r\n\r\n".encode())
                    self.wfile.write(data)
                    self.wfile.write(b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                pass  # client disconnected
        else:
            self.send_response(404)
            self.end_headers()


def start_server():
    server = HTTPServer(("0.0.0.0", STREAM_PORT), MJPEGHandler)
    server.serve_forever()


def main():
    # Start MJPEG server in background thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    print(f"[INFO] Stream server started — open http://<PI_IP>:{STREAM_PORT} in a browser")

    print("[INFO] Loading NCNN model...")
    model = YOLO(MODEL_PATH, task="detect")
    print("[INFO] Model loaded!")

    print("[INFO] Starting OAK-D pipeline...")
    device = dai.Device()
    with dai.Pipeline(device) as pipeline:
        cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
        q = cam.requestOutput(
            size=(640, 640),
            type=dai.ImgFrame.Type.BGR888p,
            fps=15
        ).createOutputQueue()

        pipeline.start()
        print("[INFO] Running — press Ctrl+C to quit")

        while pipeline.isRunning():
            frame_msg = q.tryGet()
            if frame_msg is None:
                continue

            frame = frame_msg.getCvFrame()

            # Run YOLO inference
            results = model(frame, conf=CONF_THRESH, verbose=False)

            # Draw detections
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf   = float(box.conf[0])
                    label  = LABELS[cls_id] if cls_id < len(LABELS) else "unknown"
                    color  = COLORS.get(label, (255, 255, 255))

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{label} {conf:.2f}",
                                (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    print(f"[DETECT] {label} ({conf:.2f}) @ [{x1},{y1},{x2},{y2}]")

            # Push annotated frame to stream
            with frame_lock:
                global latest_frame
                latest_frame = frame.copy()


if __name__ == "__main__":
    main()
