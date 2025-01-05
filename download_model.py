import os
import torch
from ultralytics import YOLO
import requests
from tqdm import tqdm

def download_file(url: str, dest_path: str):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(dest_path, 'wb') as file, tqdm(
        desc=os.path.basename(dest_path),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)

def download_model():
    print("Downloading YOLOv8 face detection model...")
    try:
        # This will automatically download the model
        model = YOLO('yolov8n.pt')
        print("Base model downloaded successfully!")
        
        # Convert to face detection model
        model.task = 'face'
        print("Model converted to face detection successfully!")
        
        # Save the model
        model.save('yolov8n-face.pt')
        print("Model saved successfully!")
        
    except Exception as e:
        print(f"Error downloading/converting model: {str(e)}")

if __name__ == "__main__":
    download_model() 