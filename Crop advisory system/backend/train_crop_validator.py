"""
Training script for Crop Image Validator

Dataset Structure Required:
training_data/
    crop_image/
        rice_001.jpg
        wheat_002.jpg
        maize_003.jpg
        cotton_004.jpg
        sugarcane_005.jpg
        ... (collect 500-1000 crop images)
    
    non_crop_image/
        aadhaar_001.jpg
        aadhaar_002.jpg
        resume_001.pdf.jpg
        resume_002.jpg
        face_001.jpg
        face_002.jpg
        document_001.jpg
        document_002.jpg
        signature_001.jpg
        id_card_001.jpg
        ... (collect 500-1000 non-crop images)

Usage:
    python train_crop_validator.py --dataset-dir training_data --epochs 15
"""

import os
import argparse
from crop_validator import train_crop_validator, TENSORFLOW_AVAILABLE


def main():
    if not TENSORFLOW_AVAILABLE:
        print("ERROR: TensorFlow is required for training")
        print("Install: pip install tensorflow")
        return
    
    parser = argparse.ArgumentParser(description='Train Crop Image Validator')
    parser.add_argument('--dataset-dir', type=str, required=True,
                        help='Path to training dataset directory')
    parser.add_argument('--output', type=str, default='crop_validator_model.h5',
                        help='Output model file path')
    parser.add_argument('--epochs', type=int, default=10,
                        help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for training')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset_dir):
        print(f"ERROR: Dataset directory not found: {args.dataset_dir}")
        print("\nExpected structure:")
        print("  training_data/")
        print("    crop_image/")
        print("      rice_001.jpg")
        print("      wheat_002.jpg")
        print("      ...")
        print("    non_crop_image/")
        print("      aadhaar_001.jpg")
        print("      resume_002.jpg")
        print("      face_003.jpg")
        print("      ...")
        return
    
    crop_dir = os.path.join(args.dataset_dir, 'crop_image')
    non_crop_dir = os.path.join(args.dataset_dir, 'non_crop_image')
    
    if not os.path.exists(crop_dir):
        print(f"ERROR: crop_image directory not found: {crop_dir}")
        return
    
    if not os.path.exists(non_crop_dir):
        print(f"ERROR: non_crop_image directory not found: {non_crop_dir}")
        return
    
    crop_count = len([f for f in os.listdir(crop_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
    non_crop_count = len([f for f in os.listdir(non_crop_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
    
    print(f"\nDataset Summary:")
    print(f"  Crop images: {crop_count}")
    print(f"  Non-crop images: {non_crop_count}")
    print(f"  Total: {crop_count + non_crop_count}")
    
    if crop_count < 50 or non_crop_count < 50:
        print("\nWARNING: Dataset too small. Recommended minimum: 100 images per class")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    print(f"\nStarting training...")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Output: {args.output}")
    
    model, history = train_crop_validator(
        train_dir=args.dataset_dir,
        model_save_path=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size
    )
    
    print("\n" + "="*50)
    print("Training completed successfully!")
    print(f"Model saved to: {args.output}")
    print("\nTo use the model, update app.py:")
    print(f"  validator = CropImageValidator('{args.output}')")


if __name__ == "__main__":
    main()
