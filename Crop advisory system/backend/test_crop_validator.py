"""
Test script to demonstrate crop validator behavior
Creates synthetic test images to show rejection of non-crop images
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

def create_test_images():
    """Create synthetic test images"""
    test_dir = "test_validation_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # 1. Create a document-like image (white background with text)
    doc_img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(doc_img)
    
    # Draw text lines to simulate document
    for i in range(20):
        y = 50 + i * 40
        draw.rectangle([50, y, 750, y+20], fill='black')
    
    doc_img.save(os.path.join(test_dir, "document.jpg"))
    print("Created: document.jpg (should be REJECTED)")
    
    # 2. Create an ID card-like image
    id_card = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(id_card)
    draw.rectangle([50, 50, 550, 350], outline='black', width=3)
    draw.rectangle([100, 100, 200, 200], fill='gray')  # Photo placeholder
    for i in range(5):
        y = 120 + i * 30
        draw.rectangle([220, y, 500, y+15], fill='black')
    id_card.save(os.path.join(test_dir, "id_card.jpg"))
    print("Created: id_card.jpg (should be REJECTED)")
    
    # 3. Create a green crop-like image
    crop_img = np.zeros((400, 400, 3), dtype=np.uint8)
    crop_img[:, :, 1] = 150  # Green channel
    crop_img[:, :, 0] = 50   # Red channel
    crop_img[:, :, 2] = 50   # Blue channel
    
    # Add some texture
    for _ in range(1000):
        x, y = np.random.randint(0, 400, 2)
        crop_img[y:y+10, x:x+10] = [30, 180, 30]
    
    crop_pil = Image.fromarray(crop_img)
    crop_pil.save(os.path.join(test_dir, "crop_green.jpg"))
    print("Created: crop_green.jpg (should be ACCEPTED)")
    
    # 4. Create a signature-like image
    sig_img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(sig_img)
    # Draw wavy line to simulate signature
    points = [(50 + i*5, 100 + 30*np.sin(i*0.2)) for i in range(60)]
    draw.line(points, fill='blue', width=3)
    sig_img.save(os.path.join(test_dir, "signature.jpg"))
    print("Created: signature.jpg (should be REJECTED)")
    
    print(f"\nTest images created in: {test_dir}/")
    return test_dir


def test_validator():
    """Test the validator with synthetic images"""
    from crop_validator import CropImageValidator
    
    test_dir = create_test_images()
    validator = CropImageValidator()
    
    print("\n" + "="*60)
    print("TESTING CROP IMAGE VALIDATOR")
    print("="*60)
    
    test_files = [
        ("document.jpg", False),
        ("id_card.jpg", False),
        ("signature.jpg", False),
        ("crop_green.jpg", True),
    ]
    
    for filename, expected_valid in test_files:
        filepath = os.path.join(test_dir, filename)
        result = validator.validate_image(filepath)
        
        status = "PASS" if result['valid'] == expected_valid else "FAIL"
        
        print(f"\n{status} | {filename}")
        print(f"  Expected: {'ACCEPT' if expected_valid else 'REJECT'}")
        print(f"  Result: {'ACCEPTED' if result['valid'] else 'REJECTED'}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
        if not result['valid']:
            print(f"  Reason: {result.get('reason', 'N/A')}")
            print(f"  Message: {result.get('message', 'N/A')}")
    
    # Test with actual crop image if available
    rice_path = os.path.join(os.path.dirname(__file__), "image_dataset", "rice", "rice_000.jpg")
    if os.path.exists(rice_path):
        print(f"\n{'='*60}")
        print("Testing with REAL crop image (rice)")
        print("="*60)
        result = validator.validate_image(rice_path)
        print(f"  Result: {'ACCEPTED' if result['valid'] else 'REJECTED'}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
        if not result['valid']:
            print(f"  Reason: {result.get('reason', 'N/A')}")


if __name__ == "__main__":
    test_validator()
