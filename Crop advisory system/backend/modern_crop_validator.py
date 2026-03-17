"""
Modern Crop Image Validator
Rejects non-crop images like Aadhaar cards, human photos, documents, etc.
"""
import base64
import io
import numpy as np
from PIL import Image

class CropImageValidator:
    """Validates if uploaded image is a crop/plant image"""
    
    def __init__(self):
        self.valid_categories = ['plant', 'crop', 'leaf', 'agriculture', 'vegetation']
        self.invalid_patterns = ['face', 'person', 'document', 'text', 'card', 'signature']
    
    def validate_from_base64(self, base64_image):
        """
        Validate if image is a crop/plant image
        
        Returns:
            dict: {'valid': bool, 'reason': str, 'confidence': float, 'message': str}
        """
        try:
            # Decode image
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            
            img_data = base64.b64decode(base64_image)
            img = Image.open(io.BytesIO(img_data))
            img = img.convert('RGB')
            
            # Basic image analysis
            img_array = np.array(img)
            
            # Check 1: Color analysis (crops are typically green)
            green_score = self._analyze_green_content(img_array)
            
            # Check 2: Texture analysis (crops have organic textures)
            texture_score = self._analyze_texture(img_array)
            
            # Check 3: Edge detection (documents have sharp edges)
            edge_score = self._analyze_edges(img_array)
            
            # Check 4: Text detection (documents have text)
            text_score = self._detect_text_regions(img_array)
            
            # Calculate overall crop probability
            crop_probability = (
                green_score * 0.4 +
                texture_score * 0.3 +
                (1 - edge_score) * 0.2 +
                (1 - text_score) * 0.1
            )
            
            # Decision threshold
            if crop_probability > 0.4:
                return {
                    'valid': True,
                    'reason': 'Valid crop/plant image detected',
                    'confidence': crop_probability,
                    'message': 'Image validated successfully'
                }
            else:
                # Determine rejection reason
                if text_score > 0.6:
                    reason = 'Document or text detected'
                elif edge_score > 0.7:
                    reason = 'Document-like sharp edges detected'
                elif green_score < 0.2:
                    reason = 'No vegetation detected'
                else:
                    reason = 'Non-crop image detected'
                
                return {
                    'valid': False,
                    'reason': reason,
                    'confidence': 1 - crop_probability,
                    'message': '⚠️ Invalid input: Please upload only crop or plant images. Documents, photos, and non-agricultural images are not accepted.'
                }
        
        except Exception as e:
            return {
                'valid': False,
                'reason': f'Image processing error: {str(e)}',
                'confidence': 0,
                'message': 'Unable to process image. Please upload a valid crop image.'
            }
    
    def _analyze_green_content(self, img_array):
        """Analyze green color content (crops are typically green)"""
        # Convert to HSV for better color detection
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # Green detection: G > R and G > B
        green_pixels = np.sum((g > r) & (g > b) & (g > 100))
        total_pixels = img_array.shape[0] * img_array.shape[1]
        
        green_ratio = green_pixels / total_pixels
        return min(1.0, green_ratio * 3)  # Scale up
    
    def _analyze_texture(self, img_array):
        """Analyze texture complexity (organic vs artificial)"""
        # Calculate standard deviation in small patches
        gray = np.mean(img_array, axis=2)
        
        # Divide into patches and calculate variance
        patch_size = 20
        h, w = gray.shape
        variances = []
        
        for i in range(0, h - patch_size, patch_size):
            for j in range(0, w - patch_size, patch_size):
                patch = gray[i:i+patch_size, j:j+patch_size]
                variances.append(np.var(patch))
        
        # Organic textures have moderate variance
        avg_variance = np.mean(variances)
        texture_score = min(1.0, avg_variance / 1000)
        
        return texture_score
    
    def _analyze_edges(self, img_array):
        """Detect sharp edges (documents have many sharp edges)"""
        gray = np.mean(img_array, axis=2)
        
        # Simple edge detection using gradient
        grad_x = np.abs(np.diff(gray, axis=1))
        grad_y = np.abs(np.diff(gray, axis=0))
        
        # Count strong edges
        strong_edges_x = np.sum(grad_x > 50)
        strong_edges_y = np.sum(grad_y > 50)
        total_edges = strong_edges_x + strong_edges_y
        
        total_pixels = gray.shape[0] * gray.shape[1]
        edge_ratio = total_edges / total_pixels
        
        return min(1.0, edge_ratio * 10)
    
    def _detect_text_regions(self, img_array):
        """Detect text-like regions (documents have text)"""
        gray = np.mean(img_array, axis=2)
        
        # Text regions have high contrast and regular patterns
        # Check for horizontal lines (common in text)
        horizontal_variance = np.var(gray, axis=1)
        
        # High variance in horizontal direction suggests text
        text_score = min(1.0, np.mean(horizontal_variance) / 2000)
        
        return text_score

def get_validator():
    """Get validator instance"""
    return CropImageValidator()
