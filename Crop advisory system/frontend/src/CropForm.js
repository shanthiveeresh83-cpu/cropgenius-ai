import React, { useState } from "react";
import axios from "axios";
import { useLanguage } from "./LanguageContext";
import LocationDetector from "./LocationDetector";
import LocationSearch from "./LocationSearch";
import "./styles.css";
function CropForm() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const { t } = useLanguage();
  const handleAutoPredict = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    const token = localStorage.getItem("token");
    try {
      const response = await axios.post(
        "http://localhost:5000
        {},  
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResult(response.data);
    } catch (err) {
      console.error("Prediction error:", err);
      if (err.response?.data?.action_required === 'enable_location') {
        setError(
          "📍 Location not detected. Please enable location access below to get personalized recommendations for your area."
        );
      } else {
        setError(err.response?.data?.error || "Failed to get prediction. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };
  const getSourceLabel = (source) => {
    const labels = {
      'dataset': 'From Dataset',
      'iot_sensor': 'Simulated IoT Sensor',
      'ml_estimator': 'ML Estimated',
      'weather_api': 'Weather API',
      'default': 'Default Value',
      'api': 'Weather API'
    };
    return labels[source] || source;
  };
  return (
    <div className="container">
      <h2>🌾 Smart Crop Advisory</h2>
      {}
      <LocationDetector onLocationDetected={(loc) => console.log('Location set:', loc)} />
      {}
      <LocationSearch />
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Click the button below to get an automatic crop recommendation based on your location's weather conditions and simulated soil data.
      </p>
      <button 
        onClick={handleAutoPredict} 
        disabled={loading}
        style={{
          padding: '15px 30px',
          fontSize: '18px',
          backgroundColor: loading ? '#ccc' : '#27ae60',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: loading ? 'not-allowed' : 'pointer',
          width: '100%',
          marginBottom: '20px'
        }}
      >
        {loading ? '🤔 Analyzing...' : '🤖 Get Automatic Recommendation'}
      </button>
      {error && (
        <div className="error-message" style={{ color: 'red', marginBottom: '15px' }}>
          {error}
        </div>
      )}
      {result && (
        <div className="result-card">
          <h3>🌱 Recommended Crop</h3>
          <h2 style={{ color: "#27ae60", fontSize: '32px', margin: '10px 0' }}>
            {result.recommended_crop}
          </h2>
          {result.confidence && (
            <p style={{ color: '#666' }}>
              Confidence: <strong>{result.confidence}%</strong>
            </p>
          )}
          <div style={{ marginTop: '20px', textAlign: 'left' }}>
            <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
              📊 Environmental Parameters Used:
            </h4>
            <div className="features-grid" style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '15px',
              marginTop: '15px'
            }}>
              <div className="feature-item" style={{ 
                background: '#f8f9fa', 
                padding: '12px', 
                borderRadius: '8px',
                borderLeft: '3px solid #3498db'
              }}>
                <strong>Nitrogen (N)</strong>
                <div style={{ fontSize: '20px', color: '#2c3e50' }}>{result.features.N}</div>
                <small style={{ color: '#7f8c8d' }}>{getSourceLabel(result.data_sources.N)}</small>
              </div>
              <div className="feature-item" style={{ 
                background: '#f8f9fa', 
                padding: '12px', 
                borderRadius: '8px',
                borderLeft: '3px solid #9b59b6'
              }}>
                <strong>Phosphorus (P)</strong>
                <div style={{ fontSize: '20px', color: '#2c3e50' }}>{result.features.P}</div>
                <small style={{ color: '#7f8c8d' }}>{getSourceLabel(result.data_sources.P)}</small>
              </div>
              <div className="feature-item" style={{ 
                background: '#f8f9fa', 
                padding: '12px', 
                borderRadius: '8px',
                borderLeft: '3px solid #e67e22'
              }}>
                <strong>Potassium (K)</strong>
                <div style={{ fontSize: '20px', color: '#2c3e50' }}>{result.features.K}</div>
                <small style={{ color: '#7f8c8d' }}>{getSourceLabel(result.data_sources.K)}</small>
              </div>
              <div className="feature-item" style={{ 
                background: '#f8f9fa', 
                padding: '12px', 
                borderRadius: '8px',
                borderLeft: '3px solid #e74c3c'
              }}>
                <strong>Temperature</strong>
                <div style={{ fontSize: '20px', color: '#2c3e50' }}>{result.features.temperature}°C</div>
                <small style={{ color: '#7f8c8d' }}>{getSourceLabel(result.data_sources.temperature)}</small>
              </div>
              <div className="feature-item" style={{ 
                background: '#f8f9fa', 
                padding: '12px', 
                borderRadius: '8px',
                borderLeft: '3px solid #1abc9c'
              }}>
                <strong>Humidity</strong>
                <div style={{ fontSize: '20px', color: '#2c3e50' }}>{result.features.humidity}%</div>
                <small style={{ color: '#7f8c8d' }}>{getSourceLabel(result.data_sources.humidity)}</small>
              </div>
              <div className="feature-item" style={{ 
                background: '#f8f9fa', 
                padding: '12px', 
                borderRadius: '8px',
                borderLeft: '3px solid #34495e'
              }}>
                <strong>Soil pH</strong>
                <div style={{ fontSize: '20px', color: '#2c3e50' }}>{result.features.ph}</div>
                <small style={{ color: '#7f8c8d' }}>{getSourceLabel(result.data_sources.ph)}</small>
              </div>
              <div className="feature-item" style={{ 
                background: '#f8f9fa', 
                padding: '12px', 
                borderRadius: '8px',
                borderLeft: '3px solid #3498db'
              }}>
                <strong>Rainfall</strong>
                <div style={{ fontSize: '20px', color: '#2c3e50' }}>{result.features.rainfall} mm</div>
                <small style={{ color: '#7f8c8d' }}>{getSourceLabel(result.data_sources.rainfall)}</small>
              </div>
            </div>
            {result.location && (
              <div style={{ marginTop: '15px', padding: '10px', background: '#e8f5e9', borderRadius: '5px' }}>
                <strong>📍 Location:</strong> {result.location.city || 'Unknown'}
              </div>
            )}
            <div style={{ marginTop: '10px', fontSize: '12px', color: '#999' }}>
              Mode: {result.mode} | Prediction stored: {result.prediction_stored ? '✓ Yes' : '✗ No'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
export default CropForm;