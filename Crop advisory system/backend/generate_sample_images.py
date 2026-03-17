import os
import numpy as np
from PIL import Image, ImageDraw

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
    print("PIL not available. Creating placeholder dataset structure.")

CROP_TYPES = ["rice", "wheat", "maize", "cotton", "sugarcane"]

def generate_crop_image(crop_type, size=(96, 96), seed=None):
    if not PIL_AVAILABLE:
        return None

    if seed is not None:
        np.random.seed(seed)

    colors = {
        "rice": (34, 139, 34),      # Green (paddy)
        "wheat": (218, 165, 32),     # Golden yellow
        "maize": (154, 205, 50),    # Yellow-green
        "cotton": (245, 245, 220),   # White/beige
        "sugarcane": (85, 107, 47)   # Dark olive green
    }

    base_color = colors.get(crop_type, (100, 150, 50))

    img = Image.new("RGB", size, base_color)
    draw = ImageDraw.Draw(img)

    pixels = img.load()
    for i in range(size[0]):
        for j in range(size[1]):

            noise = np.random.randint(-30, 30)
            r = max(0, min(255, base_color[0] + noise))
            g = max(0, min(255, base_color[1] + noise))
            b = max(0, min(255, base_color[2] + noise))
            pixels[i, j] = (r, g, b)

    if crop_type == "rice":

        for y in range(10, size[1], 15):
            draw.line([(0, y), (size[0], y)], fill=(50, 120, 50), width=2)
    elif crop_type == "wheat":

        for _ in range(20):
            x, y = np.random.randint(0, size[0]), np.random.randint(0, size[1])
            draw.ellipse([x, y, x+5, y+10], fill=(200, 180, 50))
    elif crop_type == "maize":

        for _ in range(15):
            x, y = np.random.randint(5, size[0]-5), np.random.randint(5, size[1]-5)
            draw.ellipse([x, y, x+8, y+8], fill=(200, 200, 80))
    elif crop_type == "cotton":

        for _ in range(10):
            x, y = np.random.randint(5, size[0]-5), np.random.randint(5, size[1]-5)
            draw.ellipse([x, y, x+12, y+12], fill=(255, 255, 255))
    elif crop_type == "sugarcane":

        for x in range(10, size[0], 20):
            draw.line([(x, 0), (x+3, size[1])], fill=(70, 90, 40), width=3)

    return img

def create_sample_dataset(base_dir, images_per_class=30):
    dataset_dir = os.path.join(base_dir, "image_dataset")

    print(f"Creating sample dataset at: {dataset_dir}")
    print(f"Generating {images_per_class} images per crop type...")

    if not PIL_AVAILABLE:
        print("Error: PIL is required to generate images.")
        print("Please install Pillow: pip install pillow")
        return False

    for crop in CROP_TYPES:
        crop_dir = os.path.join(dataset_dir, crop)
        os.makedirs(crop_dir, exist_ok=True)
        print(f"Created directory: {crop_dir}")

    for crop in CROP_TYPES:
        crop_dir = os.path.join(dataset_dir, crop)
        print(f"Generating {crop} images...")

        for i in range(images_per_class):

            seed = hash(f"{crop}_{i}") % (2**32)
            img = generate_crop_image(crop, size=(96, 96), seed=seed)

            if img:

                img_path = os.path.join(crop_dir, f"{crop}_{i:03d}.jpg")
                img.save(img_path, "JPEG", quality=85)

        print(f"  Generated {images_per_class} images for {crop}")

    print(f"\nDataset created successfully!")
    print(f"Total images: {len(CROP_TYPES) * images_per_class}")
    print(f"Location: {dataset_dir}")
    return True

if __name__ == "__main__":

    backend_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 50)
    print("Crop Image Dataset Generator")
    print("=" * 50)

    success = create_sample_dataset(backend_dir, images_per_class=30)

    if success:
        print("\n" + "=" * 50)
        print("Next steps:")
        print("=" * 50)
        print(f"1. Run: python train_cv_model.py --dataset-dir {os.path.join(backend_dir, 'image_dataset')}")
        print("2. This will create: crop_image_model.pkl")
        print("3. Restart the backend to use the image upload feature")
    else:
        print("\nFailed to create dataset. Please install required packages.")