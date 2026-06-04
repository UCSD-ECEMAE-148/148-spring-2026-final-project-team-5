#!/usr/bin/env python3
"""
Standalone YOLO + OAK-D test — no ROS2.
Loads NCNN model and runs inference on OAK-D camera feed.
Press 'q' to quit.

Usage:
    python3 yolo_test.py
"""

from ultralytics import YOLO
import depthai as dai
import cv2

MODEL_PATH  = "/home/projects/final_ws/src/148-spring-2026-final-project-team-5/hazard_recon_pkg/triangle_ncnn_model/"
CONF_THRESH = 0.5

LABELS = ["blue triangle", "green triangle", "red trangle"]  # must match model exactly

# Label colors (BGR)
COLORS = {
    "blue triangle":  (255, 100, 0),
    "green triangle": (0, 200, 0),
    "red trangle":    (0, 0, 220),
}

def main():
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
        print("[INFO] Running — press 'q' to quit")

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
                    print(f"[DETECT] {label} ({conf:.2f})")

            cv2.imshow("Hazard Recon - YOLO Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    print("[INFO] Done.")

if __name__ == "__main__":
    main()
