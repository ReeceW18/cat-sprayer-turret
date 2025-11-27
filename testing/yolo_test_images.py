"""
DISCLAIMER: This file is programmed almost entirely by github copilot and is buggy

reads jpgs from test_cats_dir and feeds them through each model in MODEL_PATHS
displays summary of detection quality and displays results in windows
"""
import cv2
import os
import numpy as np
import time
from pathlib import Path
from ultralytics import YOLO

# ===== CONFIGURATION =====
# Add multiple model paths here to compare them
MODEL_PATHS = [
    './models/11n_320p_halfprecision_ncnn_model',
    './models/11n_480p_halfprecision_ncnn_model',
    # './models/11n_640p_halfprecision_ncnn_model',
    './models/11s_320p_halfprecision_ncnn_model',
    # './models/11s_480p_halfprecision_ncnn_model',
    # './models/11s_640p_halfprecision_ncnn_model',
    # Add more model paths here, e.g.:
    # './models/another_model',
    'yolov8n.pt',
]
IMGSZ = 320  # Model input size
# =========================

# Load YOLO models
models = []
model_names = []
for model_path in MODEL_PATHS:
    try:
        model = YOLO(model_path)
        models.append(model)
        model_names.append(Path(model_path).name)
        print(f"Loaded model: {model_names[-1]}")
    except Exception as e:
        print(f"Failed to load model {model_path}: {e}")

if not models:
    print("No models loaded. Exiting.")
    exit(1)

def letterbox_image(img, target_size):
    """
    Apply letterboxing to image like YOLO does:
    - Scale the longest side to target_size while maintaining aspect ratio
    - Add gray bars to make it square
    """
    h, w = img.shape[:2]
    scale = target_size / max(h, w)
    new_h, new_w = int(h * scale), int(w * scale)
    
    resized = cv2.resize(img, (new_w, new_h))
    canvas = np.full((target_size, target_size, 3), 114, dtype=np.uint8)
    top = (target_size - new_h) // 2
    left = (target_size - new_w) // 2
    canvas[top:top + new_h, left:left + new_w] = resized
    return canvas

# Path to test images
test_cats_dir = Path(__file__).parent / 'test_cats'

# Get all jpg and jpeg images
image_extensions = ['*.JPG', '*.JPEG']
image_paths = []
for ext in image_extensions:
    image_paths.extend(test_cats_dir.glob(ext))

print(f"Found {len(image_paths)} images to process\n")
print(f"Processing all images with {len(models)} model(s)...\n")

# Process all images first to get summary for each model
all_model_results = []

for model_idx, model in enumerate(models):
    model_name = model_names[model_idx]
    print(f"\n{'='*60}")
    print(f"Processing with model: {model_name}")
    print('='*60)
    
    results_data = []
    durations_ms = []
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        
        if img is None:
            print(f"Failed to load {img_path.name}")
            continue

        print(f"Processing: {img_path.name}")
        
        # Run YOLO detection (measure time)
        start = time.perf_counter()
        results = model(img)
        end = time.perf_counter()
        durations_ms.append((end - start) * 1000.0)
        
        # Get the annotated image and apply letterboxing
        annotated_img = results[0].plot()
        letterboxed_img = letterbox_image(annotated_img, IMGSZ)
        
        # Check for cat detections (assuming 'cat' is in model names)
        cat_detections = []
        for detection in results[0].boxes:
            class_id = int(detection.cls)
            confidence = float(detection.conf)
            class_name = model.names[class_id]
            if 'cat' in class_name.lower():
                cat_detections.append(confidence)
        
        results_data.append({
            'path': img_path,
            'image': letterboxed_img,
            'cat_detections': cat_detections,
            'all_detections': results[0].boxes,
            'model_names': model.names
        })

    # Calculate and display summary for this model
    files_with_cats = sum(1 for r in results_data if len(r['cat_detections']) > 0)
    all_cat_confidences = [conf for r in results_data for conf in r['cat_detections']]
    avg_confidence = sum(all_cat_confidences) / len(all_cat_confidences) if all_cat_confidences else 0
    avg_time_ms = (sum(durations_ms) / len(durations_ms)) if durations_ms else 0.0

    print(f"\nSUMMARY - {model_name}")
    print("-" * 60)
    print(f"Total images processed: {len(results_data)}")
    print(f"Images with cat detected: {files_with_cats}")
    print(f"Average cat confidence: {avg_confidence:.2%}")
    print(f"Total cat detections: {len(all_cat_confidences)}")
    print(f"Average processing time: {avg_time_ms:.1f} ms/image")
    
    all_model_results.append({
        'model_name': model_name,
        'results_data': results_data,
        'summary': {
            'total': len(results_data),
            'with_cats': files_with_cats,
            'avg_confidence': avg_confidence,
            'total_detections': len(all_cat_confidences),
            'avg_time_ms': avg_time_ms
        }
    })

# Display overall summary
print("\n" + "="*60)
print("OVERALL DETECTION SUMMARY")
print("="*60)
for model_result in all_model_results:
    summary = model_result['summary']
    print(f"\n{model_result['model_name']}:")
    print(f"  Images with cat: {summary['with_cats']}/{summary['total']}")
    print(f"  Avg confidence: {summary['avg_confidence']:.2%}")
    print(f"  Total detections: {summary['total_detections']}")
    print(f"  Avg time: {summary['avg_time_ms']:.1f} ms/image")
print("="*60)
print(f"\nPress any key to cycle through images (press 'q' to quit)")
print(f"Images are displayed at {IMGSZ}x{IMGSZ} with letterboxing\n")

# Display images for each model, continuously cycling until 'q' is pressed
windows = {}
for model_result in all_model_results:
    model_name = model_result['model_name']
    window_name = f'YOLO Detection - {model_name} ({IMGSZ}x{IMGSZ})'
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(window_name, 50, 50)
    windows[model_name] = window_name

print(f"\n{'='*60}")
print("Viewing results (cycling). Press 'q' to quit.")
print('='*60)

quit_all = False
while not quit_all:
    for model_result in all_model_results:
        model_name = model_result['model_name']
        window_name = windows[model_name]
        results_data = model_result['results_data']

        for data in results_data:
            print(f"\nViewing ({model_name}): {data['path'].name}")
            cv2.imshow(window_name, data['image'])

            if data['all_detections']:
                for detection in data['all_detections']:
                    class_id = int(detection.cls)
                    confidence = float(detection.conf)
                    class_name = data['model_names'][class_id]
                    print(f"  Detected: {class_name} (confidence: {confidence:.2f})")
            else:
                print("  No detections")

            key = cv2.waitKey(0)
            if key == ord('q'):
                quit_all = True
                break
        if quit_all:
            break

for model_result in all_model_results:
    cv2.destroyWindow(f"YOLO Detection - {model_result['model_name']} ({IMGSZ}x{IMGSZ})")

cv2.destroyAllWindows()
print("\nViewing complete!")

'''
# Process all images first to get summary for each model
all_model_results = []

for model_idx, model in enumerate(models):
    model_name = model_names[model_idx]
    print(f"\n{'='*60}")
    print(f"Processing with model: {model_name}")
    print('='*60)
    
    results_data = []
    durations_ms = []
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        
        if img is None:
            print(f"Failed to load {img_path.name}")
            continue

        print(f"Processing: {img_path.name}")
        
        # Run YOLO detection (measure time)
        start = time.perf_counter()
        results = model(img, imgsz=IMGSZ, classes=[15])
        end = time.perf_counter()
        durations_ms.append((end - start) * 1000.0)
        
        # Get the annotated image and apply letterboxing
        annotated_img = results[0].plot()
        letterboxed_img = letterbox_image(annotated_img, IMGSZ)
        
        # Check for cat detections (assuming 'cat' is in model names)
        cat_detections = []
        for detection in results[0].boxes:
            class_id = int(detection.cls)
            confidence = float(detection.conf)
            class_name = model.names[class_id]
            if 'cat' in class_name.lower():
                cat_detections.append(confidence)
        
        results_data.append({
            'path': img_path,
            'image': letterboxed_img,
            'cat_detections': cat_detections,
            'all_detections': results[0].boxes,
            'model_names': model.names
        })

    # Calculate and display summary for this model
    files_with_cats = sum(1 for r in results_data if len(r['cat_detections']) > 0)
    all_cat_confidences = [conf for r in results_data for conf in r['cat_detections']]
    avg_confidence = sum(all_cat_confidences) / len(all_cat_confidences) if all_cat_confidences else 0

    avg_time_ms = (sum(durations_ms) / len(durations_ms)) if durations_ms else 0.0
    print(f"\nSUMMARY - {model_name}")
    print("-" * 60)
    print(f"Total images processed: {len(results_data)}")
    print(f"Images with cat detected: {files_with_cats}")
    print(f"Average cat confidence: {avg_confidence:.2%}")
    print(f"Total cat detections: {len(all_cat_confidences)}")
    print(f"Average processing time: {avg_time_ms:.1f} ms/image")
    
    all_model_results.append({
        'model_name': model_name,
        'results_data': results_data,
        'summary': {
            'total': len(results_data),
            'with_cats': files_with_cats,
            'avg_confidence': avg_confidence,
            'total_detections': len(all_cat_confidences),
            'avg_time_ms': avg_time_ms
        }
    })

# Display overall summary
print("\n" + "="*60)
print("OVERALL DETECTION SUMMARY")
print("="*60)
for model_result in all_model_results:
    summary = model_result['summary']
    print(f"\n{model_result['model_name']}:")
    print(f"  Images with cat: {summary['with_cats']}/{summary['total']}")
    print(f"  Avg confidence: {summary['avg_confidence']:.2%}")
    print(f"  Total detections: {summary['total_detections']}")
    print(f"  Avg time: {summary['avg_time_ms']:.1f} ms/image")
print("="*60)
print(f"\nPress any key to cycle through images (press 'q' to quit)")
print(f"Images are displayed at {IMGSZ}x{IMGSZ} with letterboxing\n")

# Display images for each model
for model_result in all_model_results:
    model_name = model_result['model_name']
    results_data = model_result['results_data']
    
    # Create a named window and position it
    window_name = f'YOLO Detection - {model_name} ({IMGSZ}x{IMGSZ})'
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(window_name, 50, 50)
    
    print(f"\n{'='*60}")
    print(f"Viewing results from: {model_name}")
    print('='*60)
    
    # Display each image
    for data in results_data:
        print(f"\nViewing: {data['path'].name}")
        
        # Update window title and show letterboxed image
        cv2.imshow(window_name, data['image'])
        
        # Print detection info for this image
        for detection in data['all_detections']:
            class_id = int(detection.cls)
            confidence = float(detection.conf)
            class_name = data['model_names'][class_id]
            print(f"  Detected: {class_name} (confidence: {confidence:.2f})")
        
        if not data['all_detections']:
            print("  No detections")
        
        # Wait for key press to continue to next image (press 'q' to quit)
        key = cv2.waitKey(0)
        if key == ord('q'):
            break
    
    cv2.destroyWindow(window_name)
    
    if key == ord('q'):
        break

cv2.destroyAllWindows()
print("\nViewing complete!")

'''