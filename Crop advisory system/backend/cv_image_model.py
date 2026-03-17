import base64
import io
import os
import pickle
from typing import Dict, List, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

try:
    from PIL import Image
except Exception:
    Image = None

class CropImageCVModel:
    def __init__(self, image_size: Tuple[int, int] = (96, 96), bins: int = 16):
        self.image_size = image_size
        self.bins = bins
        self.model = RandomForestClassifier(
            n_estimators=300,
            max_depth=18,
            random_state=42,
            class_weight="balanced",
        )
        self.labels: List[str] = []

    def _ensure_pillow(self):
        if Image is None:
            raise RuntimeError("Pillow is required for image processing. Install with: pip install pillow")

    def _preprocess(self, image: "Image.Image") -> np.ndarray:
        self._ensure_pillow()
        rgb = image.convert("RGB").resize(self.image_size)
        return np.asarray(rgb, dtype=np.float32) / 255.0

    def _extract_features_from_array(self, rgb_arr: np.ndarray) -> np.ndarray:
        feats: List[float] = []

        for c in range(3):
            channel = rgb_arr[:, :, c]
            feats.append(float(np.mean(channel)))
            feats.append(float(np.std(channel)))

        self._ensure_pillow()
        hsv_arr = np.asarray(Image.fromarray((rgb_arr * 255).astype(np.uint8)).convert("HSV"), dtype=np.float32) / 255.0
        for c in range(3):
            hist, _ = np.histogram(hsv_arr[:, :, c], bins=self.bins, range=(0.0, 1.0))
            hist = hist.astype(np.float32)
            hist /= (np.sum(hist) + 1e-8)
            feats.extend(hist.tolist())

        gray = np.mean(rgb_arr, axis=2)
        gx = np.diff(gray, axis=1)
        gy = np.diff(gray, axis=0)

        gmag = np.sqrt(gx[:-1, :].astype(np.float32) ** 2 + gy[:, :-1].astype(np.float32) ** 2)

        feats.append(float(np.mean(gmag)))
        feats.append(float(np.std(gmag)))
        feats.append(float(np.max(gmag)))

        return np.asarray(feats, dtype=np.float32)

    def extract_features_from_pil(self, image: "Image.Image") -> np.ndarray:
        rgb_arr = self._preprocess(image)
        return self._extract_features_from_array(rgb_arr)

    def extract_features_from_file(self, image_path: str) -> np.ndarray:
        self._ensure_pillow()
        with Image.open(image_path) as img:
            return self.extract_features_from_pil(img)

    def predict_from_base64(self, image_data_url: str) -> Dict[str, float]:
        self._ensure_pillow()
        if self.model is None or not self.labels:
            raise RuntimeError("CV model is not trained")

        encoded = image_data_url
        if "," in image_data_url:
            encoded = image_data_url.split(",", 1)[1]

        raw = base64.b64decode(encoded)
        with Image.open(io.BytesIO(raw)) as img:
            features = self.extract_features_from_pil(img).reshape(1, -1)

        pred_idx = int(self.model.predict(features)[0])
        confidence = float(np.max(self.model.predict_proba(features)[0]))
        return {"label": self.labels[pred_idx], "confidence": round(confidence * 100, 2)}

    def train_from_directory(self, dataset_dir: str, test_size: float = 0.2) -> Dict[str, float]:
        self._ensure_pillow()
        if not os.path.isdir(dataset_dir):
            raise ValueError(f"Dataset directory not found: {dataset_dir}")

        X: List[np.ndarray] = []
        y: List[int] = []
        class_names = sorted([d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))])
        if not class_names:
            raise ValueError("No class folders found in dataset directory")

        self.labels = class_names
        valid_ext = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

        for idx, class_name in enumerate(class_names):
            class_dir = os.path.join(dataset_dir, class_name)
            for name in os.listdir(class_dir):
                ext = os.path.splitext(name.lower())[1]
                if ext not in valid_ext:
                    continue
                path = os.path.join(class_dir, name)
                try:
                    X.append(self.extract_features_from_file(path))
                    y.append(idx)
                except Exception:
                    continue

        if len(X) < 20:
            raise ValueError("Not enough images to train. Add at least ~20 images.")

        X_arr = np.stack(X)
        y_arr = np.asarray(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X_arr, y_arr, test_size=test_size, random_state=42, stratify=y_arr
        )
        self.model.fit(X_train, y_train)
        acc = float(self.model.score(X_test, y_test))
        train_acc = float(self.model.score(X_train, y_train))
        return {
            "train_accuracy": round(train_acc, 4),
            "test_accuracy": round(acc, 4),
            "classes": len(class_names),
            "samples": len(X),
        }

    def save(self, path: str):
        payload = {
            "model": self.model,
            "labels": self.labels,
            "image_size": self.image_size,
            "bins": self.bins,
        }
        with open(path, "wb") as f:
            pickle.dump(payload, f)

    @classmethod
    def load(cls, path: str) -> "CropImageCVModel":
        with open(path, "rb") as f:
            payload = pickle.load(f)
        obj = cls(image_size=payload.get("image_size", (96, 96)), bins=payload.get("bins", 16))
        obj.model = payload["model"]
        obj.labels = payload["labels"]
        return obj