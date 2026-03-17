import os
import numpy as np
from PIL import Image
import io
import base64

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    from tensorflow.keras.applications import MobileNetV2, ResNet50
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

class CropDiseaseClassifier:

    def __init__(self, model_type='mobilenet'):
        self.model_type = model_type
        self.model = None
        self.class_names = [
            'healthy', 'bacterial_blight', 'brown_spot', 'leaf_blast',
            'tungro', 'bacterial_leaf_streak', 'sheath_blight'
        ]
        self.img_size = (224, 224)

    def build_model(self, num_classes=7):

        if self.model_type == 'mobilenet':

            base_model = MobileNetV2(
                input_shape=(*self.img_size, 3),
                include_top=False,
                weights='imagenet'
            )
            base_model.trainable = False

            model = models.Sequential([
                base_model,
                layers.GlobalAveragePooling2D(),
                layers.Dense(256, activation='relu'),
                layers.Dropout(0.5),
                layers.Dense(num_classes, activation='softmax')
            ])

        elif self.model_type == 'resnet':

            base_model = ResNet50(
                input_shape=(*self.img_size, 3),
                include_top=False,
                weights='imagenet'
            )
            base_model.trainable = False

            model = models.Sequential([
                base_model,
                layers.GlobalAveragePooling2D(),
                layers.Dense(512, activation='relu'),
                layers.Dropout(0.5),
                layers.Dense(256, activation='relu'),
                layers.Dropout(0.3),
                layers.Dense(num_classes, activation='softmax')
            ])

        else:

            model = models.Sequential([
                layers.Conv2D(32, (3, 3), activation='relu', input_shape=(*self.img_size, 3)),
                layers.MaxPooling2D((2, 2)),
                layers.Conv2D(64, (3, 3), activation='relu'),
                layers.MaxPooling2D((2, 2)),
                layers.Conv2D(128, (3, 3), activation='relu'),
                layers.MaxPooling2D((2, 2)),
                layers.Conv2D(128, (3, 3), activation='relu'),
                layers.MaxPooling2D((2, 2)),
                layers.Flatten(),
                layers.Dense(512, activation='relu'),
                layers.Dropout(0.5),
                layers.Dense(num_classes, activation='softmax')
            ])

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        self.model = model
        return model

    def train(self, train_dir, val_dir, epochs=20, batch_size=32):

        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        val_datagen = ImageDataGenerator(rescale=1./255)

        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='categorical'
        )

        val_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='categorical'
        )

        callbacks = [
            keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
            keras.callbacks.ModelCheckpoint('best_model.h5', save_best_only=True)
        ]

        history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=val_generator,
            callbacks=callbacks
        )

        return history

    def predict_from_base64(self, base64_image):
        try:

            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]

            img_data = base64.b64decode(base64_image)
            img = Image.open(io.BytesIO(img_data))

            img = img.convert('RGB')
            img = img.resize(self.img_size)
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            predictions = self.model.predict(img_array, verbose=0)
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx] * 100)

            disease = self.class_names[class_idx]

            treatment = self._get_treatment(disease)

            return {
                'disease': disease,
                'confidence': confidence,
                'severity': self._get_severity(disease),
                'treatment': treatment['treatment'],
                'prevention': treatment['prevention'],
                'all_predictions': {
                    self.class_names[i]: float(predictions[0][i] * 100)
                    for i in range(len(self.class_names))
                }
            }

        except Exception as e:
            return {'error': str(e)}

    def _get_severity(self, disease):
        severity_map = {
            'healthy': 'None',
            'bacterial_blight': 'High',
            'brown_spot': 'Medium',
            'leaf_blast': 'High',
            'tungro': 'Critical',
            'bacterial_leaf_streak': 'Medium',
            'sheath_blight': 'High'
        }
        return severity_map.get(disease, 'Unknown')

    def _get_treatment(self, disease):
        treatments = {
            'healthy': {
                'treatment': 'No treatment needed. Continue regular care.',
                'prevention': 'Maintain proper nutrition and watering schedule.'
            },
            'bacterial_blight': {
                'treatment': 'Apply copper-based bactericide. Remove infected leaves.',
                'prevention': 'Use resistant varieties. Avoid overhead irrigation.'
            },
            'brown_spot': {
                'treatment': 'Apply fungicide (Mancozeb). Improve drainage.',
                'prevention': 'Balanced fertilization. Avoid water stress.'
            },
            'leaf_blast': {
                'treatment': 'Apply Tricyclazole or Carbendazim fungicide.',
                'prevention': 'Use resistant varieties. Avoid excessive nitrogen.'
            },
            'tungro': {
                'treatment': 'No cure. Remove infected plants immediately.',
                'prevention': 'Control green leafhopper vectors. Use resistant varieties.'
            },
            'bacterial_leaf_streak': {
                'treatment': 'Apply copper bactericide. Remove infected parts.',
                'prevention': 'Use clean seeds. Avoid field flooding.'
            },
            'sheath_blight': {
                'treatment': 'Apply Validamycin or Hexaconazole fungicide.',
                'prevention': 'Proper spacing. Avoid excessive nitrogen.'
            }
        }
        return treatments.get(disease, {
            'treatment': 'Consult agricultural expert.',
            'prevention': 'Follow good agricultural practices.'
        })

    def save(self, path):
        self.model.save(path)

    def load(self, path):
        self.model = keras.models.load_model(path)

def train_disease_model(dataset_dir, model_type='mobilenet'):

    if not TF_AVAILABLE:
        print("TensorFlow not available. Install: pip install tensorflow")
        return

    print(f"Training {model_type} model...")

    classifier = CropDiseaseClassifier(model_type=model_type)
    classifier.build_model(num_classes=7)

    train_dir = os.path.join(dataset_dir, 'train')
    val_dir = os.path.join(dataset_dir, 'val')

    history = classifier.train(train_dir, val_dir, epochs=20, batch_size=32)

    classifier.save('crop_disease_model.h5')
    print("Model saved: crop_disease_model.h5")

    return classifier, history

if __name__ == '__main__':

    # train_disease_model('path/to/dataset', model_type='mobilenet')
    pass