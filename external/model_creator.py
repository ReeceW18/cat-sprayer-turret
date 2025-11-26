import shutil
from ultralytics import YOLO
import os

# settings
source_model = "yolov8n.pt"
output_name = "8n_320"
image_size = 320

# create new model
model = YOLO(source_model)
export_path = model.export(format="ncnn", imgsz=image_size)

# move model to final location
final_path = "models/" + output_name + "_ncnn_model/" # NOTE must have _ncnn_model suffix for yolo to recognize the model

if not os.path.exists(final_path):
    os.makedirs(final_path)
shutil.move(export_path, final_path)

print(f"model exported to {final_path}/{export_path}")