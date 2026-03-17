import React, { useState } from 'react';
import axios from 'axios';
import './CropImageAnalysis.css';

function CropImageAnalysis() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
      setResult(null);
      setError('');
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const reader = new FileReader();
    reader.onloadend = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://localhost:5000/api/analyze-crop',
          { image: reader.result },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        setResult(response.data);
      } catch (err) {
        console.error('Full error:', err);
        console.error('Response data:', err.response?.data);
        const errorMsg = err.response?.data?.error || err.message || 'Failed to analyze image';
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };
    reader.readAsDataURL(selectedImage);
  };

  return (
    <div className="crop-image-analysis">
      <h2>🌾 Crop Image Analysis</h2>
      
      <div className="upload-section">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          id="crop-image-input"
          style={{ display: 'none' }}
        />
        <label htmlFor="crop-image-input" className="upload-btn">
          📷 Select Crop Image
        </label>
      </div>

      {imagePreview && (
        <div className="preview-section">
          <img src={imagePreview} alt="Preview" className="image-preview" />
          <button onClick={analyzeImage} disabled={loading} className="analyze-btn">
            {loading ? '🔍 Analyzing...' : '🔬 Analyze Crop'}
          </button>
        </div>
      )}

      {error && (
        <div className="error-box">
          ❌ {error}
        </div>
      )}

      {result && (
        <div className="result-section">
          <h3>✅ Analysis Results</h3>
          <div className="result-card">
            <p><strong>Detected Crop:</strong> {result.detected_crop}</p>
            <p><strong>Confidence:</strong> {result.confidence}%</p>
            <p><strong>Fertilizer:</strong> {result.fertilizer}</p>
            <p><strong>Irrigation:</strong> {result.irrigation}</p>
            <p><strong>Season:</strong> {result.season}</p>
            <p><strong>Advice:</strong> {result.advice}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default CropImageAnalysis;
