import React, { useState } from 'react';
import axios from 'axios';
import './AdvancedDashboard.css';
function AdvancedDashboard() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('prediction');
  const handleAutoAnalysis = async () => {
    setLoading(true);
    setError('');
    setResults(null);
    const token = localStorage.getItem('token');
    try {
      const response = await axios.post(
        'http://localhost:5000
        {}, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = response.data;
      const transformedResults = {
        recommended_crop: data.recommended_crop,
        confidence: data.confidence,
        features: data.features,
        data_sources: data.data_sources,
        location: data.location,
        mode: data.mode,
        soil_health: {
          health_class: getHealthClass(data.features),
          health_score: calculateHealthScore(data.features),
          component_scores: {
            nitrogen: Math.min(100, (data.features.N / 100) * 100),
            phosphorus: Math.min(100, (data.features.P / 60) * 100),
            potassium: Math.min(100, (data.features.K / 60) * 100),
            ph: Math.min(100, ((data.features.ph - 5.5) / (8.0 - 5.5)) * 100)
          },
          recommendations: [
            `Maintain current ${data.recommended_crop} cultivation practices`,
            `Monitor soil nutrients regularly for optimal yield`,
            `Consider organic matter addition for soil health`
          ]
        },
        fertilizer_recommendations: getFertilizerRecommendations(data.features)
      };
      setResults(transformedResults);
    } catch (error) {
      console.error('Error:', error);
      setError(error.response?.data?.error || 'Failed to get automatic analysis. Please try again.');
    }
    setLoading(false);
  };
  const getHealthClass = (features) => {
    const avgNutrient = (features.N + features.P + features.K) / 3;
    if (avgNutrient > 60) return 'Excellent';
    if (avgNutrient > 40) return 'Good';
    if (avgNutrient > 25) return 'Fair';
    return 'Poor';
  };
  const calculateHealthScore = (features) => {
    const nScore = Math.min(100, (features.N / 100) * 100);
    const pScore = Math.min(100, (features.P / 60) * 100);
    const kScore = Math.min(100, (features.K / 60) * 100);
    const phScore = Math.min(100, ((features.ph - 5.5) / (8.0 - 5.5)) * 100);
    return Math.round((nScore + pScore + kScore + phScore) / 4);
  };
  const getFertilizerRecommendations = (features) => {
    const recommendations = [];
    if (features.N < 50) {
      recommendations.push({
        nutrient: 'N',
        fertilizer: 'Urea',
        quantity: '50-75 kg/hectare'
      });
    }
    if (features.P < 30) {
      recommendations.push({
        nutrient: 'P',
        fertilizer: 'DAP (Diammonium Phosphate)',
        quantity: '100-125 kg/hectare'
      });
    }
    if (features.K < 40) {
      recommendations.push({
        nutrient: 'K',
        fertilizer: 'MOP (Muriate of Potash)',
        quantity: '60-80 kg/hectare'
      });
    }
    if (recommendations.length === 0) {
      recommendations.push({
        nutrient: 'Balanced',
        fertilizer: 'NPK 10:26:26',
        quantity: '150-200 kg/hectare'
      });
    }
    return recommendations;
  };
  const getSourceLabel = (source) => {
    const labels = {
      'dataset': 'Dataset',
      'iot_sensor': 'IoT Sensor',
      'ml_estimator': 'ML Model',
      'weather_api': 'Weather API',
      'api': 'Weather API',
      'default': 'Default',
      'fallback': 'Fallback'
    };
    return labels[source] || source;
  };
  return (
    <div className="advanced-dashboard">
      <header className="dashboard-hero">
        <h1>🌾 Smart Agriculture Platform</h1>
        <p>AI-Powered Automatic Crop Advisory System</p>
      </header>
      <div className="dashboard-tabs">
        <button className={activeTab === 'prediction' ? 'active' : ''} onClick={() => setActiveTab('prediction')}>
          🔮 Auto Prediction
        </button>
        <button className={activeTab === 'soil' ? 'active' : ''} onClick={() => setActiveTab('soil')}>
          🌍 Soil Analysis
        </button>
        <button className={activeTab === 'fertilizer' ? 'active' : ''} onClick={() => setActiveTab('fertilizer')}>
          🧪 Fertilizer
        </button>
        <button className={activeTab === 'weather' ? 'active' : ''} onClick={() => setActiveTab('weather')}>
          ☁️ Weather Data
        </button>
      </div>
      <div className="dashboard-content">
        <div className="input-section">
          <h2>🤖 Automatic Farm Analysis</h2>
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <p style={{ marginBottom: '20px', color: '#666' }}>
              ✨ <strong>Fully Automatic:</strong> No manual input required!<br/>
              🌐 System automatically collects weather data and simulates IoT sensors
            </p>
            {error && (
              <div style={{ 
                color: 'red', 
                marginBottom: '15px',
                padding: '10px',
                background: '#ffe6e6',
                borderRadius: '5px',
                border: '1px solid #ffcccc'
              }}>
                {error}
              </div>
            )}
            <button 
              onClick={handleAutoAnalysis} 
              className="analyze-btn" 
              disabled={loading}
              style={{
                backgroundColor: loading ? '#ccc' : '#27ae60',
                cursor: loading ? 'not-allowed' : 'pointer',
                padding: '15px 30px',
                fontSize: '18px'
              }}
            >
              {loading ? '⏳ Auto-Analyzing Farm...' : '🚀 Start Automatic Analysis'}
            </button>
          </div>
        </div>
        {results && (
          <div className="results-section">
            <div className="result-card crop-prediction">
              <h3>🌾 Recommended Crop</h3>
              <div className="crop-result">
                <span className="crop-name">{results.recommended_crop}</span>
                {results.confidence && (
                  <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                    Confidence: {results.confidence}%
                  </div>
                )}
              </div>
              <div style={{ fontSize: '12px', color: '#999', marginTop: '10px' }}>
                Mode: {results.mode} | All data auto-collected
              </div>
            </div>
            {}
            <div className="result-card data-sources">
              <h3>📊 Auto-Collected Data</h3>
              <div className="data-grid">
                <div className="data-item">
                  <span className="data-label">🌡️ Temperature:</span>
                  <span className="data-value">{results.features.temperature}°C</span>
                  <small>({getSourceLabel(results.data_sources.temperature)})</small>
                </div>
                <div className="data-item">
                  <span className="data-label">💧 Humidity:</span>
                  <span className="data-value">{results.features.humidity}%</span>
                  <small>({getSourceLabel(results.data_sources.humidity)})</small>
                </div>
                <div className="data-item">
                  <span className="data-label">🌧️ Rainfall:</span>
                  <span className="data-value">{results.features.rainfall}mm</span>
                  <small>({getSourceLabel(results.data_sources.rainfall)})</small>
                </div>
                <div className="data-item">
                  <span className="data-label">🧪 Nitrogen:</span>
                  <span className="data-value">{results.features.N}</span>
                  <small>({getSourceLabel(results.data_sources.N)})</small>
                </div>
                <div className="data-item">
                  <span className="data-label">🧪 Phosphorus:</span>
                  <span className="data-value">{results.features.P}</span>
                  <small>({getSourceLabel(results.data_sources.P)})</small>
                </div>
                <div className="data-item">
                  <span className="data-label">🧪 Potassium:</span>
                  <span className="data-value">{results.features.K}</span>
                  <small>({getSourceLabel(results.data_sources.K)})</small>
                </div>
                <div className="data-item">
                  <span className="data-label">⚖️ pH Level:</span>
                  <span className="data-value">{results.features.ph}</span>
                  <small>({getSourceLabel(results.data_sources.ph)})</small>
                </div>
              </div>
              {results.location && (
                <div style={{ marginTop: '10px', padding: '8px', background: '#e8f5e9', borderRadius: '4px' }}>
                  <strong>📍 Location:</strong> {results.location.city || 'Default'}
                </div>
              )}
            </div>
            <div className="result-card soil-health">
              <h3>🌍 Soil Health Analysis</h3>
              <div className="health-score">
                <div className={`score-badge ${results.soil_health.health_class.toLowerCase()}`}>
                  {results.soil_health.health_class}
                </div>
                <div className="score-value">{results.soil_health.health_score}/100</div>
              </div>
              <div className="component-scores">
                <div className="score-item">
                  <span>Nitrogen</span>
                  <div className="progress-bar">
                    <div className="progress" style={{width: `${results.soil_health.component_scores.nitrogen}%`}}></div>
                  </div>
                </div>
                <div className="score-item">
                  <span>Phosphorus</span>
                  <div className="progress-bar">
                    <div className="progress" style={{width: `${results.soil_health.component_scores.phosphorus}%`}}></div>
                  </div>
                </div>
                <div className="score-item">
                  <span>Potassium</span>
                  <div className="progress-bar">
                    <div className="progress" style={{width: `${results.soil_health.component_scores.potassium}%`}}></div>
                  </div>
                </div>
                <div className="score-item">
                  <span>pH Level</span>
                  <div className="progress-bar">
                    <div className="progress" style={{width: `${results.soil_health.component_scores.ph}%`}}></div>
                  </div>
                </div>
              </div>
            </div>
            <div className="result-card fertilizer-rec">
              <h3>🧪 Fertilizer Recommendations</h3>
              {results.fertilizer_recommendations.map((rec, idx) => (
                <div key={idx} className="fertilizer-item">
                  <div className="nutrient-badge">{rec.nutrient}</div>
                  <div className="fertilizer-details">
                    <strong>{rec.fertilizer}</strong>
                    <span>{rec.quantity}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="result-card recommendations">
              <h3>💡 AI Recommendations</h3>
              <ul>
                {results.soil_health.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
export default AdvancedDashboard;