"""
This program exports models to specific formats and settings

Usage:
    Set parameters under settings comment to desired values and then run program. 
    This program is specifically designed to export ncnn models which are better 
    for use on arm based processors. 
    image_size: the size the image will be converted to before being processed
    source_model: the original yolo model, yolo + v8 or 11 + n, s, m, l, or x
        (n or s recommended for pi)
    output_name: the beginning of the folder name the model is exported to
    half_precision: whether the model uses half precision floating point or not
"""
import os
import shutil

from ultralytics import YOLO

# settings
source_model = "yolo11s.pt"
output_name = "11s_320p_halfprecision"
image_size = 320
half_precision = True
models_path = "models/"

model_format = "ncnn"
model = YOLO(source_model)
export_path = model.export(format=model_format, imgsz=image_size, half=half_precision)

final_path = models_path + output_name + "_ncnn_model/" # NOTE must have _ncnn_model suffix for yolo to recognize the model

if not os.path.exists(models_path):
    os.makedirs(models_path)
shutil.move(export_path, final_path)

print(f"model exported to {final_path}")