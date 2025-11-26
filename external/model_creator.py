import shutil
from ultralytics import YOLO
import os

# settings
source_model = "yolo11s.pt"
output_name = "11s_320p_halfprecision"
image_size = 320

# create new model
model = YOLO(source_model)
export_path = model.export(format="ncnn", imgsz=image_size, half=True)

# move model to final location
models_path = "models/"
final_path = models_path + output_name + "_ncnn_model/" # NOTE must have _ncnn_model suffix for yolo to recognize the model

if not os.path.exists(models_path):
    os.makedirs(models_path)
shutil.move(export_path, final_path)

print(f"model exported to {final_path}")