# cv-service/yolo_publisher.py
# YOLOv8 inference publisher (detection-only by default).
# Requirements: 'ultralytics' (pip), and PyTorch (follow PyTorch install for Windows).
# Usage examples:
#   python yolo_publisher.py --source 0
#   python yolo_publisher.py --source C:\path\to\video.mp4
#
# Note: For tracking IDs you can use model.track(...) if your ultralytics install supports trackers.
import argparse
import time
import requests
import os
from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str, default="0", help="0 for webcam or path to video/file")
parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLOv8 model (yolov8n.pt etc.)")
parser.add_argument("--api-url", type=str, default=os.getenv("API_URL", "http://localhost:8000/ingest"), help="Ingest API URL")
parser.add_argument("--conf", type=float, default=0.35, help="confidence threshold")
args = parser.parse_args()

source = args.source
if source == "0":
    source = 0  # webcam

print("[yolo_publisher] Loading model:", args.model)
model = YOLO(args.model)

print("[yolo_publisher] Starting inference on source:", source)
# stream=True yields results per frame
for result in model.predict(source=source, conf=args.conf, stream=True):
    # result is a Results object for a single frame
    vehicles = []
    try:
        if result.boxes is not None and len(result.boxes) > 0:
            # boxes.xyxy, boxes.conf, boxes.cls are available as tensors/arrays
            xyxy = result.boxes.xyxy.tolist()
            confs = result.boxes.conf.tolist()
            cls_ids = result.boxes.cls.tolist()
            for i, box in enumerate(xyxy):
                bbox = [int(box[0]), int(box[1]), int(box[2]), int(box[3])]
                vehicles.append({
                    "track_id": None,
                    "cls": str(int(cls_ids[i])),
                    "conf": float(confs[i]),
                    "bbox": bbox
                })
    except Exception as e:
        # fallback: try to iterate result.boxes
        try:
            for b in result.boxes:
                box = b.xyxy[0].tolist()
                vehicles.append({
                    "track_id": None,
                    "cls": str(int(b.cls)),
                    "conf": float(b.conf),
                    "bbox": [int(box[0]), int(box[1]), int(box[2]), int(box[3])]
                })
        except Exception:
            pass

    payload = {"camera_id": "cam_yolo", "ts": time.time(), "vehicles": vehicles}
    try:
        r = requests.post(args.api_url, json=payload, timeout=2.0)
        print("[yolo_publisher] sent", len(vehicles), "detections ->", r.status_code)
    except Exception as e:
        print("[yolo_publisher] error sending:", e)
