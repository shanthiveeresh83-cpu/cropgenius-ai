import React, { useState } from 'react';
import LocationDetector from './LocationDetector';
import { DownloadReportButton } from './DownloadReportButton';
import './MultiPageDashboard.css';
function AutomaticDashboard() {
  const [currentPage, setCurrentPage] = useState('home');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const handleAutoAnalyze = async () => {
    setLoading(true);
    setError('');
    setResults(null);
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:5000/api/comprehensive-analysis', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({})  
      });
      const data = await response.json();
      if (!response.ok) {
        if (data.error === 'Location not set' || data.action_required === 'enable_location') {
          setError('⚠️ Location Required: Please enable location detection first.\n\nGo to the Crop Prediction page and click "Detect My Location" to save your location.');
        } else {
          setError(`Error: ${data.error || data.message || `Server error: ${response.status} ${response.statusText}`}`);
        }
        setLoading(false);
        return;
      }
      const transformedResults = {
        recommended_crop: data.recommended_crop,
        confidence: data.confidence,
        features: data.features,
        data_sources: data.data_sources,
        location: data.location,
        mode: data.mode,
        analysis_timestamp: new Date().toLocaleString(),
        price_analysis: data.price_analysis || null,
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
            `Monitor soil nutrients regularly for optimal yield`
          ]
        },
        weather_suitability: getWeatherSuitability(data.features),
        fertilizer_recommendations: getFertilizerRecommendations(data.features),
        overall_recommendations: [
          `${data.recommended_crop} is well-suited for current conditions`,
          `Continue monitoring environmental parameters`,
          `Consider crop rotation for long-term soil health`
        ]
      };
      setResults(transformedResults);
      setCurrentPage('results');
    } catch (error) {
      console.error('Analysis error:', error);
      setError('Error: Could not complete analysis. Please check if the backend is running.\n' + error.message);
    } finally {
      setLoading(false);
    }
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
  const getWeatherSuitability = (features) => {
    if (features.temperature >= 20 && features.temperature <= 30 && 
        features.humidity >= 60 && features.humidity <= 80) {
      return 'Excellent';
    }
    if (features.temperature >= 15 && features.temperature <= 35) {
      return 'Good';
    }
    return 'Fair';
  };
  const getCropImage = (cropName) => {
    const colors = {
      'rice': '#8BC34A', 'wheat': '#FFC107', 'maize': '#FF9800', 'cotton': '#E0E0E0',
      'sugarcane': '#4CAF50', 'chickpea': '#795548', 'kidneybeans': '#D32F2F',
      'pigeonpeas': '#CDDC39', 'mothbeans': '#8D6E63', 'mungbean': '#689F38',
      'blackgram': '#424242', 'lentil': '#FF5722', 'pomegranate': '#E91E63',
      'banana': '#FFEB3B', 'mango': '#FFC107', 'grapes': '#9C27B0',
      'watermelon': '#F44336', 'muskmelon': '#FFE082', 'apple': '#F44336',
      'orange': '#FF9800', 'papaya': '#FF6F00', 'coconut': '#795548',
      'jute': '#8BC34A', 'coffee': '#5D4037', 'corn': '#FDD835',
      'tea': '#4CAF50', 'tobacco': '#8D6E63', 'groundnut': '#BCAAA4',
      'peanut': '#D7CCC8', 'soybean': '#AED581', 'sunflower': '#FFEB3B',
      'mustard': '#FDD835', 'barley': '#F9A825', 'millets': '#FBC02D'
    };
    const color = colors[cropName.toLowerCase()] || '#9E9E9E';
    return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect width='400' height='300' fill='${color}'/%3E%3Ctext x='50%25' y='50%25' font-size='32' fill='white' text-anchor='middle' dy='.3em' font-family='Arial'%3E${cropName.toUpperCase()}%3C/text%3E%3C/svg%3E`;
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
        fertilizer: 'DAP',
        quantity: '100-125 kg/hectare'
      });
    }
    if (features.K < 40) {
      recommendations.push({
        nutrient: 'K',
        fertilizer: 'MOP',
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
  const renderPage = () => {
    switch(currentPage) {
      case 'home':
        return <HomePage onNext={handleAutoAnalyze} loading={loading} error={error} />;
      case 'results':
        return <ResultsPage results={results} onBack={() => setCurrentPage('home')} onHome={() => setCurrentPage('home')} getCropImage={getCropImage} />;
      default:
        return <HomePage onNext={handleAutoAnalyze} loading={loading} error={error} />;
    }
  };
  return (
    <div className="multi-page-dashboard">
      {renderPage()}
    </div>
  );
}
function HomePage({ onNext, loading, error }) {
  return (
    <div className="page home-page">
      <div className="hero-content">
        <h1>🌾 Smart Agriculture Platform</h1>
        <p>AI-Powered Automatic Crop Advisory System</p>
        {}
        <div style={{ marginBottom: '20px' }}>
          <LocationDetector onLocationDetected={(loc) => console.log('Location saved:', loc)} />
        </div>
        <div className="features">
          <div className="feature-card">
            <span className="icon">🤖</span>
            <h3>Automatic Analysis</h3>
            <p>No manual input required - AI collects all data</p>
          </div>
          <div className="feature-card">
            <span className="icon">🌍</span>
            <h3>Real-time Data</h3>
            <p>Live weather and simulated soil sensors</p>
          </div>
          <div className="feature-card">
            <span className="icon">🎯</span>
            <h3>Smart Recommendations</h3>
            <p>Personalized crop and fertilizer advice</p>
          </div>
        </div>
        {error && (
          <div className="error-message" style={{ 
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
          className="btn-large" 
          onClick={onNext}
          disabled={loading}
          style={{
            backgroundColor: loading ? '#ccc' : '#27ae60',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? '🤔 Analyzing Farm Conditions...' : '🚀 Start Automatic Analysis'}
        </button>
        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          <p>✨ <strong>Fully Automatic:</strong> No need to enter soil or weather data</p>
          <p>🌐 System automatically fetches weather and simulates IoT sensors</p>
          <p>📍 <strong>Note:</strong> Enable location above for personalized recommendations</p>
        </div>
      </div>
    </div>
  );
}
function ResultsPage({ results, onBack, onHome, getCropImage }) {
  if (!results) return null;
  return (
    <div className="page results-page">
      <div className="page-header">
        <button className="btn-back" onClick={onBack}>← Back</button>
        <h2>📈 Automatic Farm Analysis Results</h2>
        <button className="btn-home" onClick={onHome}>🏠 Home</button>
      </div>
      
      <DownloadReportButton results={results} />
      
      <div className="results-grid">
        {}
        <div className="result-card featured">
          <h3>🌾 Recommended Crop</h3>
          <div className="crop-image-container" style={{ marginBottom: '15px', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 15px rgba(0,0,0,0.2)' }}>
            <img 
              src={getCropImage(results.recommended_crop)} 
              alt={results.recommended_crop}
              style={{ width: '100%', height: '200px', objectFit: 'cover' }}
              onError={(e) => { e.target.style.display = 'none'; }}
            />
          </div>
          <div className="crop-display">{results.recommended_crop}</div>
          {results.confidence && (
            <div className="yield-info">
              <span>🎯 Confidence: {results.confidence}%</span>
            </div>
          )}
          <div className="mode-info" style={{ fontSize: '12px', color: '#666', marginTop: '10px' }}>
            Mode: {results.mode} | Auto-collected data
          </div>
        </div>
        {}
        <div className="result-card">
          <h3>📊 Data Collection</h3>
          <div className="data-sources">
            <div className="source-item">
              <span className="source-label">🌡️ Temperature:</span>
              <span className="source-value">{results.features.temperature}°C</span>
              <small className="source-type">({getSourceLabel(results.data_sources.temperature)})</small>
            </div>
            <div className="source-item">
              <span className="source-label">💧 Humidity:</span>
              <span className="source-value">{results.features.humidity}%</span>
              <small className="source-type">({getSourceLabel(results.data_sources.humidity)})</small>
            </div>
            <div className="source-item">
              <span className="source-label">🌧️ Rainfall:</span>
              <span className="source-value">{results.features.rainfall}mm</span>
              <small className="source-type">({getSourceLabel(results.data_sources.rainfall)})</small>
            </div>
          </div>
          {results.location && (
            <div style={{ marginTop: '10px', padding: '10px', background: 'linear-gradient(135deg, rgba(139, 195, 74, 0.2), rgba(104, 159, 56, 0.2))', borderRadius: '8px', border: '2px solid rgba(139, 195, 74, 0.4)', boxShadow: '0 0 15px rgba(139, 195, 74, 0.3)' }}>
              <strong style={{ color: '#8bc34a', textShadow: '0 0 10px rgba(139, 195, 74, 0.5)' }}>📍 Location:</strong> <span style={{ color: '#fff', fontWeight: '600' }}>{results.location.city || 'Default'}</span>
            </div>
          )}
        </div>
        {}
        <div className="result-card">
          <h3>🌍 Soil Analysis</h3>
          <div className={`health-badge ${results.soil_health.health_class.toLowerCase()}`}>
            {results.soil_health.health_class}
          </div>
          <div className="score">{results.soil_health.health_score}/100</div>
          <div className="scores-list">
            <div className="score-item">
              <span>Nitrogen ({results.features.N})</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.nitrogen}%`}}></div>
              </div>
              <small>({getSourceLabel(results.data_sources.N)})</small>
            </div>
            <div className="score-item">
              <span>Phosphorus ({results.features.P})</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.phosphorus}%`}}></div>
              </div>
              <small>({getSourceLabel(results.data_sources.P)})</small>
            </div>
            <div className="score-item">
              <span>Potassium ({results.features.K})</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.potassium}%`}}></div>
              </div>
              <small>({getSourceLabel(results.data_sources.K)})</small>
            </div>
            <div className="score-item">
              <span>pH Level ({results.features.ph})</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.ph}%`}}></div>
              </div>
              <small>({getSourceLabel(results.data_sources.ph)})</small>
            </div>
          </div>
        </div>
        {}
        <div className="result-card">
          <h3>🌤️ Weather Suitability</h3>
          <div className={`suitability-badge ${results.weather_suitability?.toLowerCase() || 'good'}`}>
            {results.weather_suitability || 'Good'}
          </div>
          <p className="suitability-text">
            {results.weather_suitability === 'Excellent' && 'Perfect weather conditions for this crop!'}
            {results.weather_suitability === 'Good' && 'Good weather conditions for cultivation'}
            {results.weather_suitability === 'Fair' && 'Weather is moderate, consider adjustments'}
            {results.weather_suitability === 'Poor' && 'Weather conditions may affect crop yield'}
          </p>
        </div>
        `{}
        <div className="result-card">
          <h3>🧪 FertilizerPRICEANALYSISHERE Recommendations</h3>
          {results.fertilizer_recommendations && results.fertilizer_recommendations.map((rec, idx) => (
            <div key={idx} className="fert-item">
              <span className="badge">{rec.nutrient}</span>
              <div>
                <strong>{rec.fertilizer}</strong>
                <p>{rec.quantity}</p>
              </div>
            </div>
          ))}
        </div>
        {}
        <div className="result-card full-width">
          <h3>💡 AI Recommendations</h3>
          <ul className="overall-rec">
            {results.overall_recommendations && results.overall_recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
        {}
        <div className="result-card timestamp">
          <p>🤖 Automatic analysis completed: {results.analysis_timestamp}</p>
          <p style={{ fontSize: '12px', color: '#666' }}>
            All data collected automatically - no manual input required
          </p>
        </div>
      </div>
    </div>
  );
}
function getSourceLabel(source) {
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
}
export default AutomaticDashboard;
