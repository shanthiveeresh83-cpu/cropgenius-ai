"""
Nutrient Estimator Service - ML Models to Estimate N and P Values

This service provides:
- Training models to predict Nitrogen (N) and Phosphorus (P) from soil/region data
- Loading pre-trained models for inference
- Fallback to dataset-based estimation when models are unavailable

Usage:
    estimator = NutrientEstimator()
    
    # Load or train model
    estimator.load_model('nutrient_model.pkl')  # or train with estimator.train_model()
    
    # Estimate N and P values
    n, p = estimator.estimate_nutrients(
        soil_type='clay',
        region='punjab',
        crop='wheat',
        ph=7.0,
        rainfall=80
    )
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple, List
import pickle

import numpy as np

# Lazy import for pandas - will be imported only when needed
pd = None
PANDAS_AVAILABLE = False

# Try to import sklearn, required for ML models
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("sklearn not available, using fallback estimation")


def _ensure_pandas():
    """Lazy import pandas when needed."""
    global pd, PANDAS_AVAILABLE
    if not PANDAS_AVAILABLE:
        try:
            import pandas as pd_module
            pd = pd_module
            PANDAS_AVAILABLE = True
        except ImportError:
            logging.warning("pandas not available, using fallback estimation only")
            PANDAS_AVAILABLE = False
    return PANDAS_AVAILABLE


# Default nutrient values based on soil type and crop
# These are used as fallback when ML model is unavailable
SOIL_TYPE_NUTRIENTS = {
    'clay': {'N': 60, 'P': 35, 'K': 45},
    'sandy': {'N': 30, 'P': 20, 'K': 25},
    'loam': {'N': 50, 'P': 30, 'K': 40},
    'silt': {'N': 55, 'P': 32, 'K': 42},
    'peaty': {'N': 70, 'P': 40, 'K': 50},
    'chalky': {'N': 25, 'P': 15, 'K': 20},
}

CROP_NUTRIENT_REQUIRMENTS = {
    'rice': {'N_mult': 1.4, 'P_mult': 1.2},
    'wheat': {'N_mult': 1.0, 'P_mult': 1.0},
    'maize': {'N_mult': 1.2, 'P_mult': 1.3},
    'cotton': {'N_mult': 1.3, 'P_mult': 1.1},
    'sugarcane': {'N_mult': 1.5, 'P_mult': 1.0},
    'potato': {'N_mult': 1.1, 'P_mult': 1.4},
    'onion': {'N_mult': 0.9, 'P_mult': 1.2},
    'tomato': {'N_mult': 1.0, 'P_mult': 1.3},
}

REGION_MODIFIERS = {
    'punjab': {'N': 1.2, 'P': 1.1, 'K': 1.0},
    'haryana': {'N': 1.1, 'P': 1.0, 'K': 1.1},
    'uttar_pradesh': {'N': 1.0, 'P': 1.0, 'K': 1.0},
    'maharashtra': {'N': 0.9, 'P': 1.1, 'K': 1.2},
    'karnataka': {'N': 0.85, 'P': 1.0, 'K': 1.1},
    'tamil_nadu': {'N': 1.0, 'P': 1.2, 'K': 0.9},
    'west_bengal': {'N': 1.1, 'P': 1.0, 'K': 1.0},
    'gujarat': {'N': 0.9, 'P': 0.9, 'K': 1.3},
    'madhya_pradesh': {'N': 1.0, 'P': 1.0, 'K': 1.0},
    'andhra_pradesh': {'N': 1.0, 'P': 1.1, 'K': 0.9},
}


class NutrientEstimator:
    """
    Service for estimating Nitrogen (N) and Phosphorus (P) values.
    
    Uses:
    - ML models (Random Forest Regressor) when available
    - Dataset-based fallback estimation
    - Rule-based adjustments for soil type, region, and crop
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize NutrientEstimator.
        
        Args:
            model_path: Path to pre-trained model file. If None, uses default path.
        """
        self.model_path = model_path or os.getenv("NUTRIENT_MODEL_PATH", "nutrient_model.pkl")
        self.model = None
        self.is_loaded = False
        
        # Enable/disable features
        self.enable_fallback = os.getenv("ENABLE_AUTO_NUTRIENT_ESTIMATION", "True").lower() == "true"
        
        # Try to load pre-trained model
        self._try_load_model()
        
        logger.info(f"NutrientEstimator initialized. Model loaded: {self.is_loaded}")
    
    def _try_load_model(self) -> bool:
        """Try to load pre-trained model from file."""
        if not os.path.exists(self.model_path):
            logger.info(f"Model file not found: {self.model_path}")
            return False
        
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.is_loaded = True
            logger.info(f"Successfully loaded nutrient model from: {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False
    
    def load_model(self, model_path: str) -> bool:
        """
        Load a pre-trained model from file.
        
        Args:
            model_path: Path to model file
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return False
        
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.is_loaded = True
            self.model_path = model_path
            logger.info(f"Successfully loaded model from: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False
    
    def train_model(self, data_path: str = "crop_data.csv", save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Train ML models to predict N and P values.
        
        Args:
            data_path: Path to training data CSV
            save_path: Path to save trained model (optional)
            
        Returns:
            Dictionary with training metrics
        """
        if not SKLEARN_AVAILABLE:
            raise NutrientEstimatorError("sklearn not available, cannot train model")
        
        if not _ensure_pandas():
            raise NutrientEstimatorError("pandas not available, cannot train model")
        
        # Load training data
        if not os.path.exists(data_path):
            raise NutrientEstimatorError(f"Training data not found: {data_path}")
        
        df = pd.read_csv(data_path)
        
        # Create feature matrix
        feature_cols = ['K', 'temperature', 'humidity', 'ph', 'rainfall']
        
        X = df[feature_cols].values
        y_n = df['N'].values
        y_p = df['P'].values
        
        # Split data
        X_train, X_test, y_n_train, y_n_test = train_test_split(
            X, y_n, test_size=0.2, random_state=42
        )
        _, _, y_p_train, y_p_test = train_test_split(
            X, y_p, test_size=0.2, random_state=42
        )
        
        # Train N model
        n_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        n_model.fit(X_train, y_n_train)
        n_pred = n_model.predict(X_test)
        n_rmse = np.sqrt(mean_squared_error(y_n_test, n_pred))
        n_r2 = r2_score(y_n_test, n_pred)
        
        # Train P model
        p_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        p_model.fit(X_train, y_p_train)
        p_pred = p_model.predict(X_test)
        p_rmse = np.sqrt(mean_squared_error(y_p_test, p_pred))
        p_r2 = r2_score(y_p_test, p_pred)
        
        # Combine models
        self.model = {
            'n_model': n_model,
            'p_model': p_model,
            'feature_cols': feature_cols
        }
        
        # Save model
        save_path = save_path or self.model_path
        try:
            with open(save_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to: {save_path}")
        except Exception as e:
            logger.warning(f"Failed to save model: {str(e)}")
        
        self.is_loaded = True
        
        return {
            'n_model': {'rmse': n_rmse, 'r2': n_r2},
            'p_model': {'rmse': p_rmse, 'r2': p_r2}
        }
    
    def _estimate_fallback(self, 
                          soil_type: Optional[str] = None,
                          region: Optional[str] = None,
                          crop: Optional[str] = None,
                          ph: float = 7.0,
                          rainfall: float = 100.0) -> Tuple[float, float]:
        """
        Fallback estimation using rule-based approach.
        
        Args:
            soil_type: Type of soil (clay, sandy, loam, etc.)
            region: Geographic region
            crop: Target crop
            ph: Soil pH value
            rainfall: Rainfall in mm
            
        Returns:
            Tuple of (N, P) estimated values
        """
        # Get base values from soil type
        soil_type = (soil_type or 'loam').lower()
        base_n = SOIL_TYPE_NUTRIENTS.get(soil_type, SOIL_TYPE_NUTRIENTS['loam'])['N']
        base_p = SOIL_TYPE_NUTRIENTS.get(soil_type, SOIL_TYPE_NUTRIENTS['loam'])['P']
        
        # Apply crop modifier
        if crop:
            crop = crop.lower()
            crop_mod = CROP_NUTRIENT_REQUIRMENTS.get(crop, {'N_mult': 1.0, 'P_mult': 1.0})
            base_n *= crop_mod['N_mult']
            base_p *= crop_mod['P_mult']
        
        # Apply region modifier
        if region:
            region = region.lower().replace(' ', '_')
            region_mod = REGION_MODIFIERS.get(region, {'N': 1.0, 'P': 1.0, 'K': 1.0})
            base_n *= region_mod['N']
            base_p *= region_mod['P']
        
        # Adjust for pH (optimal range 6.0-7.0)
        if ph < 6.0:
            # Acidic soil - N and P less available
            base_n *= 0.9
            base_p *= 0.8
        elif ph > 7.5:
            # Alkaline soil - P less available
            base_p *= 0.85
        
        # Adjust for rainfall
        if rainfall > 200:
            # High rainfall - nutrients leached
            base_n *= 0.85
            base_p *= 0.90
        elif rainfall < 50:
            # Low rainfall - nutrients less available
            base_p *= 0.95
        
        return round(base_n, 2), round(base_p, 2)
    
    def estimate_nutrients(self,
                          soil_type: Optional[str] = None,
                          region: Optional[str] = None,
                          crop: Optional[str] = None,
                          ph: float = 7.0,
                          rainfall: float = 100.0,
                          temperature: float = 25.0,
                          humidity: float = 70.0,
                          k: float = 40.0) -> Tuple[float, float]:
        """
        Estimate Nitrogen (N) and Phosphorus (P) values.
        
        Args:
            soil_type: Type of soil (clay, sandy, loam, etc.)
            region: Geographic region/state
            crop: Target crop for prediction
            ph: Soil pH value
            rainfall: Rainfall in mm
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            k: Potassium value (optional, for ML model)
            
        Returns:
            Tuple of (N, P) estimated values
            
        Example:
            >>> estimator = NutrientEstimator()
            >>> n, p = estimator.estimate_nutrients(
            ...     soil_type='clay',
            ...     region='punjab',
            ...     crop='wheat',
            ...     ph=7.0,
            ...     rainfall=80
            ... )
            >>> print(f"N: {n}, P: {p}")
        """
        # If ML model is loaded, use it
        if self.is_loaded and self.model is not None:
            try:
                # Create feature vector
                features = np.array([[k, temperature, humidity, ph, rainfall]])
                
                n_pred = self.model['n_model'].predict(features)[0]
                p_pred = self.model['p_model'].predict(features)[0]
                
                # Apply reasonable bounds
                n_pred = max(10, min(150, n_pred))
                p_pred = max(10, min(100, p_pred))
                
                logger.info(f"ML estimation: N={n_pred:.2f}, P={p_pred:.2f}")
                return round(n_pred, 2), round(p_pred, 2)
                
            except Exception as e:
                logger.warning(f"ML estimation failed: {str(e)}, using fallback")
        
        # Use fallback estimation
        if self.enable_fallback:
            logger.info("Using fallback nutrient estimation")
            return self._estimate_fallback(soil_type, region, crop, ph, rainfall)
        else:
            raise NutrientEstimatorError(
                "Nutrient estimation unavailable. Either load a model or enable fallback."
            )
    
    def estimate_from_crop_data(self, 
                                crop_data: Dict[str, Any]) -> Tuple[float, float]:
        """
        Estimate N and P values from a crop data dictionary.
        
        Args:
            crop_data: Dictionary with keys like:
                - soil_type, region, crop, ph, rainfall, temperature, humidity, k
                
        Returns:
            Tuple of (N, P) estimated values
        """
        return self.estimate_nutrients(
            soil_type=crop_data.get('soil_type'),
            region=crop_data.get('region'),
            crop=crop_data.get('crop'),
            ph=float(crop_data.get('ph', 7.0)),
            rainfall=float(crop_data.get('rainfall', 100.0)),
            temperature=float(crop_data.get('temperature', 25.0)),
            humidity=float(crop_data.get('humidity', 70.0)),
            k=float(crop_data.get('K', crop_data.get('k', 40.0)))
        )


class NutrientEstimatorError(Exception):
    """Custom exception for NutrientEstimator errors."""
    pass


# Convenience function for quick usage
def estimate_nutrients(location: Dict[str, Any], crop: Optional[str] = None) -> Tuple[float, float]:
    """
    Quick function to estimate nutrients.
    
    Args:
        location: Location dictionary with soil_type, region, etc.
        crop: Target crop
        
    Returns:
        Tuple of (N, P) estimated values
    """
    estimator = NutrientEstimator()
    return estimator.estimate_nutrients(
        soil_type=location.get('soil_type'),
        region=location.get('region'),
        crop=crop,
        ph=location.get('ph', 7.0),
        rainfall=location.get('rainfall', 100.0)
    )


# Example usage and testing
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize estimator
    estimator = NutrientEstimator()
    
    # Try to train model if not loaded
    if not estimator.is_loaded:
        print("Training new nutrient estimation model...")
        try:
            metrics = estimator.train_model('crop_data.csv')
            print(f"Training complete! Metrics: {metrics}")
        except NutrientEstimatorError as e:
            print(f"Training failed: {e}")
    
    # Test estimation
    print("\n=== Test 1: Estimate with soil type and region ===")
    n, p = estimator.estimate_nutrients(
        soil_type='clay',
        region='punjab',
        crop='wheat',
        ph=7.0,
        rainfall=80
    )
    print(f"Nitrogen (N): {n}")
    print(f"Phosphorus (P): {p}")
    
    print("\n=== Test 2: Estimate with crop only ===")
    n, p = estimator.estimate_nutrients(
        crop='rice',
        ph=6.5,
        rainfall=200
    )
    print(f"Nitrogen (N): {n}")
    print(f"Phosphorus (P): {p}")
    
    print("\n=== Test 3: From dictionary ===")
    data = {
        'soil_type': 'loam',
        'region': 'maharashtra',
        'crop': 'cotton',
        'ph': 7.2,
        'rainfall': 100
    }
    n, p = estimator.estimate_from_crop_data(data)
    print(f"Nitrogen (N): {n}")
    print(f"Phosphorus (P): {p}")
