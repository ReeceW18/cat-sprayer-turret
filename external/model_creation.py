import shutil
from ultralytics import YOLO

source_model = "yolov8n.pt"

model = YOLO(source_model)

export_path = model.export(format="ncnn", imgsz=320)

final_path = "models/"
shutil.move(export_path, final_path)

print(f"model exported to {final_path}/{export_path}")