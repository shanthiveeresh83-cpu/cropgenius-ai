import argparse
import os

from cv_image_model import CropImageCVModel

def main():
    parser = argparse.ArgumentParser(description="Train crop image CV model from folder dataset")
    parser.add_argument(
        "--dataset-dir",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_dataset"),
        help="Dataset path with class subfolders, e.g. image_dataset/rice/*.jpg",
    )
    parser.add_argument(
        "--model-path",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "crop_image_model.pkl"),
        help="Output model path",
    )
    args = parser.parse_args()

    model = CropImageCVModel()
    metrics = model.train_from_directory(args.dataset_dir)
    model.save(args.model_path)

    print("CV model trained and saved.")
    print(f"Dataset: {args.dataset_dir}")
    print(f"Model: {args.model_path}")
    print(f"Samples: {metrics['samples']}")
    print(f"Classes: {metrics['classes']}")
    print(f"Train accuracy: {metrics['train_accuracy']}")
    print(f"Test accuracy: {metrics['test_accuracy']}")

if __name__ == "__main__":
    main()