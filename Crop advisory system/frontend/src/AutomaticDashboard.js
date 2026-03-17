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
    const cropImages = {
      'rice': 'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=400&q=80',
      'wheat': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&q=80',
      'maize': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400&q=80',
      'corn': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400&q=80',
      'cotton': 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400&q=80',
      'sugarcane': 'https://images.unsplash.com/photo-1583484963886-cfe2bff2945f?w=400&q=80',
      'chickpea': 'https://images.unsplash.com/photo-1589927986089-35812388d1f4?w=400&q=80',
      'kidneybeans': 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400&q=80',
      'pigeonpeas': 'https://images.unsplash.com/photo-1589927986089-35812388d1f4?w=400&q=80',
      'mothbeans': 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400&q=80',
      'mungbean': 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400&q=80',
      'blackgram': 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400&q=80',
      'lentil': 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400&q=80',
      'pomegranate': 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400&q=80',
      'banana': 'https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400&q=80',
      'mango': 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=400&q=80',
      'grapes': 'https://images.unsplash.com/photo-1599819177626-c0d3b3a5e5b1?w=400&q=80',
      'watermelon': 'https://images.unsplash.com/photo-1587049352846-4a222e784210?w=400&q=80',
      'muskmelon': 'https://images.unsplash.com/photo-1621583832199-d1f1c8f46c1d?w=400&q=80',
      'apple': 'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&q=80',
      'orange': 'https://images.unsplash.com/photo-1547514701-42782101795e?w=400&q=80',
      'papaya': 'https://images.unsplash.com/photo-1617112848923-cc2234396a8d?w=400&q=80',
      'coconut': 'https://images.unsplash.com/photo-1589606663923-283bbd309229?w=400&q=80',
      'jute': 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400&q=80',
      'coffee': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&q=80'
    };
    return cropImages[cropName.toLowerCase()] || 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&q=80';
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
            </div>
            <div className="source-item">
              <span className="source-label">💧 Humidity:</span>
              <span className="source-value">{results.features.humidity}%</span>
            </div>
            <div className="source-item">
              <span className="source-label">🌧️ Rainfall:</span>
              <span className="source-value">{results.features.rainfall}mm</span>
            </div>
          </div>
          {results.location && (
            <div style={{ marginTop: '10px', padding: '10px', background: 'linear-gradient(135deg, rgba(139, 195, 74, 0.2), rgba(104, 159, 56, 0.2))', borderRadius: '8px', border: '2px solid rgba(139, 195, 74, 0.4)', boxShadow: '0 0 15px rgba(139, 195, 74, 0.3)' }}>
              <strong style={{ color: '#8bc34a', textShadow: '0 0 10px rgba(139, 195, 74, 0.5)' }}>📍 Location:</strong> <span style={{ color: '#fff', fontWeight: '600' }}>{results.location.city || results.location.district || results.location.state || 'Unknown'}, {results.location.state || 'India'}</span>
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
            </div>
            <div className="score-item">
              <span>Phosphorus ({results.features.P})</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.phosphorus}%`}}></div>
              </div>
            </div>
            <div className="score-item">
              <span>Potassium ({results.features.K})</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.potassium}%`}}></div>
              </div>
            </div>
            <div className="score-item">
              <span>pH Level ({results.features.ph})</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.ph}%`}}></div>
              </div>
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

        {}
        <div className="result-card">
          <h3>🧪 Fertilizer Recommendations</h3>
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

        {/* Market Price Analysis Section */}
        {results.price_analysis && (
          <div className="result-card market-price-card full-width">
            <h3>💰 Market Price Analysis</h3>
            <div className="price-content">
              <div className="price-info">
                <div className="price-item">
                  <span className="price-label">Crop</span>
                  <span className="price-value crop-name">{results.recommended_crop.toUpperCase()}</span>
                </div>
                <div className="price-item">
                  <span className="price-label">Current Price</span>
                  <span className="price-value">₹{results.price_analysis.current_price}/quintal</span>
                </div>
                <div className="price-item">
                  <span className="price-label">Predicted Price</span>
                  <span className="price-value predicted">
                    ₹{results.price_analysis.future_prices && results.price_analysis.future_prices[0] 
                      ? results.price_analysis.future_prices[0].toFixed(0) 
                      : results.price_analysis.current_price}/quintal
                  </span>
                </div>
                <div className="price-item">
                  <span className="price-label">Price Trend</span>
                  <span className={`price-trend ${results.price_analysis.trend.toLowerCase()}`}>
                    {results.price_analysis.trend === 'Rising' ? '📈' : results.price_analysis.trend === 'Falling' ? '📉' : '➡️'}
                    {results.price_analysis.trend} ({results.price_analysis.change_percentage > 0 ? '+' : ''}{results.price_analysis.change_percentage}%)
                  </span>
                </div>
              </div>
              <div className="price-chart">
                <div className="chart-title">7-Day Price Forecast</div>
                <svg className="line-chart" viewBox="0 0 300 150" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="priceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" style={{stopColor: results.price_analysis.trend === 'Rising' ? '#4ade80' : results.price_analysis.trend === 'Falling' ? '#f87171' : '#fbbf24', stopOpacity: 0.3}} />
                      <stop offset="100%" style={{stopColor: results.price_analysis.trend === 'Rising' ? '#4ade80' : results.price_analysis.trend === 'Falling' ? '#f87171' : '#fbbf24', stopOpacity: 0}} />
                    </linearGradient>
                  </defs>
                  {results.price_analysis.future_prices && results.price_analysis.future_prices.length > 0 && (() => {
                    const prices = [results.price_analysis.current_price, ...results.price_analysis.future_prices.slice(0, 6)];
                    const maxPrice = Math.max(...prices);
                    const minPrice = Math.min(...prices);
                    const range = maxPrice - minPrice || 1;
                    const points = prices.map((price, i) => {
                      const x = (i / (prices.length - 1)) * 300;
                      const y = 150 - ((price - minPrice) / range) * 130 - 10;
                      return `${x},${y}`;
                    }).join(' ');
                    const areaPoints = `0,150 ${points} 300,150`;
                    return (
                      <>
                        <polyline points={areaPoints} fill="url(#priceGradient)" />
                        <polyline points={points} fill="none" stroke={results.price_analysis.trend === 'Rising' ? '#22c55e' : results.price_analysis.trend === 'Falling' ? '#ef4444' : '#f59e0b'} strokeWidth="3" />
                        {prices.map((price, i) => {
                          const x = (i / (prices.length - 1)) * 300;
                          const y = 150 - ((price - minPrice) / range) * 130 - 10;
                          return <circle key={i} cx={x} cy={y} r="4" fill={results.price_analysis.trend === 'Rising' ? '#22c55e' : results.price_analysis.trend === 'Falling' ? '#ef4444' : '#f59e0b'} />;
                        })}
                      </>
                    );
                  })()}
                </svg>
                <div className="chart-labels">
                  <span>Today</span>
                  <span>Day 3</span>
                  <span>Day 7</span>
                </div>
              </div>
            </div>
            <div className="price-recommendation">
              <strong>💡 Recommendation:</strong> {results.price_analysis.recommendation}
            </div>
          </div>
        )}

        {/* Timestamp */}
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