import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modern_crop_validator import get_validator

validator = get_validator()

# Test with signature image
signature_path = os.path.join(os.path.dirname(__file__), "signature.jpeg")

if os.path.exists(signature_path):
    print(f"Testing signature image: {signature_path}")
    result = validator.validate_image(signature_path)
    
    print(f"\nValidation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Method: {result.get('method', 'N/A')}")
    print(f"  Confidence: {result.get('confidence', 'N/A')}")
    
    if not result['valid']:
        print(f"  Reason: {result.get('reason', 'Unknown')}")
        print(f"  Message: {result.get('message', 'N/A')}")
        print("\n✓ SUCCESS: Signature correctly rejected!")
    else:
        print("\n✗ FAILED: Signature was not rejected!")
else:
    print(f"Signature file not found at: {signature_path}")

# Test with real crop image
rice_path = os.path.join(os.path.dirname(__file__), "image_dataset", "rice", "rice_000.jpg")
if os.path.exists(rice_path):
    print(f"\n\nTesting crop image: {rice_path}")
    result = validator.validate_image(rice_path)
    
    print(f"\nValidation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Method: {result.get('method', 'N/A')}")
    print(f"  Confidence: {result.get('confidence', 'N/A')}")
    
    if result['valid']:
        print("\n✓ SUCCESS: Crop image correctly accepted!")
    else:
        print(f"\n✗ FAILED: Crop image was rejected!")
        print(f"  Reason: {result.get('reason', 'Unknown')}")
