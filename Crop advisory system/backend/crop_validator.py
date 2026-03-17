import os
import numpy as np
import cv2
from PIL import Image
import base64
from io import BytesIO

try:
    import tensorflow as tf
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.models import Model, load_model
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
    from tensorflow.keras.preprocessing.image import img_to_array
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("TensorFlow not available. Using fallback validation.")


class CropImageValidator:
    """Binary classifier to detect crop images vs non-crop images (documents, IDs, faces, etc.)"""
    
    def __init__(self, model_path=None):
        self.model = None
        self.img_size = (224, 224)
        
        if TENSORFLOW_AVAILABLE and model_path and os.path.exists(model_path):
            try:
                self.model = load_model(model_path)
                print(f"Loaded crop validator model from {model_path}")
            except Exception as e:
                print(f"Failed to load model: {e}")
                self.model = None
    
    def preprocess_image(self, image):
        """Preprocess image for CNN model"""
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        image = image.resize(self.img_size)
        img_array = img_to_array(image)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def validate_from_base64(self, base64_string):
        """Validate if image is a crop image from base64 string"""
        try:
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data)).convert('RGB')
            
            return self.validate_image(image)
        except Exception as e:
            return {'valid': False, 'error': f'Failed to decode image: {str(e)}'}
    
    def validate_image(self, image):
        """Main validation method combining CNN and heuristic checks"""
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        
        img_array = np.array(image)
        
        # Heuristic checks first (fast)
        heuristic_result = self._heuristic_validation(img_array)
        if not heuristic_result['valid']:
            return heuristic_result
        
        # CNN validation if model available
        if self.model and TENSORFLOW_AVAILABLE:
            cnn_result = self._cnn_validation(image)
            return cnn_result
        
        # If no CNN model, rely on heuristics
        return heuristic_result
    
    def _heuristic_validation(self, img_array):
        """Fast heuristic checks for obvious non-crop images"""
        height, width = img_array.shape[:2]
        
        # Check 1: Document detection (high edge density, white background)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (height * width)
        
        white_pixels = np.sum(gray > 240) / (height * width)
        
        if edge_density > 0.10 and white_pixels > 0.50:
            return {
                'valid': False,
                'reason': 'Document or ID card detected',
                'message': 'Invalid input: Please upload only crop or plant images.',
                'confidence': 0.95
            }
        
        # Check 2: Face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            return {
                'valid': False,
                'reason': 'Human face detected',
                'message': 'Invalid input: Please upload only crop or plant images.',
                'confidence': 0.98
            }
        
        # Check 3: Color analysis (crops should have green)
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        lower_green = np.array([25, 40, 40])
        upper_green = np.array([90, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        green_ratio = np.sum(green_mask > 0) / (height * width)
        
        avg_green = np.mean(img_array[:, :, 1])
        
        if green_ratio < 0.05 and avg_green < 50:
            return {
                'valid': False,
                'reason': 'No vegetation detected',
                'message': 'Invalid input: Please upload only crop or plant images.',
                'confidence': 0.75
            }
        
        return {'valid': True, 'confidence': 0.70}
    
    def _cnn_validation(self, image):
        """CNN-based validation using trained model"""
        try:
            img_array = self.preprocess_image(image)
            prediction = self.model.predict(img_array, verbose=0)[0][0]
            
            is_crop = prediction > 0.5
            confidence = prediction if is_crop else (1 - prediction)
            
            if is_crop:
                return {
                    'valid': True,
                    'confidence': float(confidence),
                    'method': 'CNN'
                }
            else:
                return {
                    'valid': False,
                    'reason': 'Non-crop image detected by CNN',
                    'message': 'Invalid input: Please upload only crop or plant images.',
                    'confidence': float(confidence),
                    'method': 'CNN'
                }
        except Exception as e:
            return {'valid': False, 'error': f'CNN validation failed: {str(e)}'}


def create_crop_validator_model(input_shape=(224, 224, 3)):
    """Create CNN model for crop vs non-crop classification"""
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow required to create model")
    
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    base_model.trainable = False
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs=base_model.input, outputs=x)
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def train_crop_validator(train_dir, model_save_path, epochs=10, batch_size=32):
    """
    Train crop validator model
    
    Expected directory structure:
    train_dir/
        crop_image/
            rice_001.jpg
            wheat_002.jpg
            ...
        non_crop_image/
            aadhaar_001.jpg
            resume_002.jpg
            face_003.jpg
            document_004.jpg
            ...
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow required for training")
    
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    
    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )
    
    train_generator = datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='binary',
        subset='training'
    )
    
    val_generator = datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='binary',
        subset='validation'
    )
    
    model = create_crop_validator_model()
    
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=epochs
    )
    
    model.save(model_save_path)
    print(f"Model saved to {model_save_path}")
    
    return model, history


if __name__ == "__main__":
    print("Crop Image Validator")
    print("=" * 50)
    
    validator = CropImageValidator()
    
    test_image_path = os.path.join(os.path.dirname(__file__), "image_dataset", "rice", "rice_000.jpg")
    
    if os.path.exists(test_image_path):
        result = validator.validate_image(test_image_path)
        print(f"\nTest validation result:")
        print(f"  Valid: {result['valid']}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
        if not result['valid']:
            print(f"  Reason: {result.get('reason', 'Unknown')}")
            print(f"  Message: {result.get('message', 'N/A')}")
