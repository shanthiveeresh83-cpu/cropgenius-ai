import os
import sys
import base64
from io import BytesIO
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cv_image_model import CropImageCVModel

model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crop_image_model.pkl")
model = CropImageCVModel.load(model_path)

print(f"Model loaded successfully!")
print(f"Labels: {model.labels}")

test_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_dataset", "rice", "rice_000.jpg")

with open(test_image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

    image_data_url = f"data:image/jpeg;base64,{image_data}"

try:
    result = model.predict_from_base64(image_data_url)
    print(f"\nPrediction result:")
    print(f"  Detected crop: {result['label']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"\nTest passed! The CV model is working correctly.")
except Exception as e:
    print(f"Error during prediction: {e}")
    import traceback
    traceback.print_exc()