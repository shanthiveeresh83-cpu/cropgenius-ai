import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cv_image_model import CropImageCVModel

dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_dataset")

print(f"Dataset directory: {dataset_dir}")
print(f"Directory exists: {os.path.isdir(dataset_dir)}")

class_names = sorted([d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))])
print(f"Class folders: {class_names}")

from PIL import Image
import numpy as np

for class_name in class_names[:1]:
    class_dir = os.path.join(dataset_dir, class_name)
    files = os.listdir(class_dir)[:3]
    print(f"\nTesting images from {class_name}:")
    for f in files:
        path = os.path.join(class_dir, f)
        print(f"  - {f}")
        try:
            with Image.open(path) as img:
                print(f"    Opened: {img.size}, mode: {img.mode}")

                model = CropImageCVModel()
                features = model.extract_features_from_pil(img)
                print(f"    Features shape: {features.shape}")
        except Exception as e:
            print(f"    Error: {e}")

print("\n\nTrying to train the model...")
model = CropImageCVModel()
try:
    metrics = model.train_from_directory(dataset_dir)
    print(f"Training successful!")
    print(f"Metrics: {metrics}")

    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crop_image_model.pkl")
    model.save(model_path)
    print(f"Model saved to: {model_path}")
except Exception as e:
    print(f"Training failed: {e}")
    import traceback
    traceback.print_exc()