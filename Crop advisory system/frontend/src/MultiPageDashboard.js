import React, { useState } from 'react';
import './MultiPageDashboard.css';
function MultiPageDashboard() {
  const [currentPage, setCurrentPage] = useState('home');
  const [formData, setFormData] = useState({
    N: '', P: '', K: '', temperature: '', humidity: '', ph: '', rainfall: ''
  });
  const [results, setResults] = useState(null);
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  const handleAnalyze = async () => {
    const requiredFields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
    for (const field of requiredFields) {
      if (!formData[field] || formData[field] === '') {
        alert(`Please fill in all fields. ${field} is missing.`);
        return;
      }
    }
    try {
      const response = await fetch('http://localhost:5000
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      setResults(data);
      setCurrentPage('results');
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Error: Could not complete analysis. Please check if the backend is running.\n' + error.message);
    }
  };
  const renderPage = () => {
    switch(currentPage) {
      case 'home':
        return <HomePage onNext={() => setCurrentPage('input')} />;
      case 'input':
        return <InputPage formData={formData} onChange={handleChange} onAnalyze={handleAnalyze} onBack={() => setCurrentPage('home')} />;
      case 'results':
        return <ResultsPage results={results} onBack={() => setCurrentPage('input')} onHome={() => setCurrentPage('home')} />;
      default:
        return <HomePage onNext={() => setCurrentPage('input')} />;
    }
  };
  return (
    <div className="multi-page-dashboard">
      {renderPage()}
    </div>
  );
}
function HomePage({ onNext }) {
  return (
    <div className="page home-page">
      <div className="hero-content">
        <h1>🌾 Smart Agriculture Platform</h1>
        <p>AI-Powered Crop Advisory System</p>
        <div className="features">
          <div className="feature-card">
            <span className="icon">🔮</span>
            <h3>Crop Prediction</h3>
            <p>Get AI-based crop recommendations</p>
          </div>
          <div className="feature-card">
            <span className="icon">🌍</span>
            <h3>Soil Analysis</h3>
            <p>Comprehensive soil health assessment</p>
          </div>
          <div className="feature-card">
            <span className="icon">🧪</span>
            <h3>Fertilizer Guide</h3>
            <p>Personalized fertilizer recommendations</p>
          </div>
        </div>
        <button className="btn-large" onClick={onNext}>Get Started →</button>
      </div>
    </div>
  );
}
function InputPage({ formData, onChange, onAnalyze, onBack }) {
  return (
    <div className="page input-page">
      <div className="page-header">
        <button className="btn-back" onClick={onBack}>← Back</button>
        <h2>📊 Enter Farm Parameters</h2>
      </div>
      <div className="input-container">
        <div className="input-grid">
          <div className="input-group">
            <label>Nitrogen (N)</label>
            <input type="number" name="N" value={formData.N} onChange={onChange} required />
          </div>
          <div className="input-group">
            <label>Phosphorus (P)</label>
            <input type="number" name="P" value={formData.P} onChange={onChange} required />
          </div>
          <div className="input-group">
            <label>Potassium (K)</label>
            <input type="number" name="K" value={formData.K} onChange={onChange} required />
          </div>
          <div className="input-group">
            <label>Temperature (°C)</label>
            <input type="number" name="temperature" value={formData.temperature} onChange={onChange} required />
          </div>
          <div className="input-group">
            <label>Humidity (%)</label>
            <input type="number" name="humidity" value={formData.humidity} onChange={onChange} required />
          </div>
          <div className="input-group">
            <label>pH Level</label>
            <input type="number" step="0.1" name="ph" value={formData.ph} onChange={onChange} required />
          </div>
          <div className="input-group">
            <label>Rainfall (mm)</label>
            <input type="number" name="rainfall" value={formData.rainfall} onChange={onChange} required />
          </div>
        </div>
        <button className="btn-large" onClick={onAnalyze}>Analyze Farm →</button>
      </div>
    </div>
  );
}
function ResultsPage({ results, onBack, onHome }) {
  if (!results) return null;
  return (
    <div className="page results-page">
      <div className="page-header">
        <button className="btn-back" onClick={onBack}>← Back</button>
        <h2>📈 Comprehensive Farm Analysis</h2>
        <button className="btn-home" onClick={onHome}>🏠 Home</button>
      </div>
      <div className="results-grid">
        {}
        <div className="result-card featured">
          <h3>🌾 Recommended Crop</h3>
          <div className="crop-display">{results.recommended_crop}</div>
          {results.yield_prediction && (
            <div className="yield-info">
              <span>📊 Expected Yield: {results.yield_prediction.estimated_yield} {results.yield_prediction.unit}</span>
            </div>
          )}
        </div>
        {}
        <div className="result-card">
          <h3>🌍 Soil Health</h3>
          <div className={`health-badge ${results.soil_health.health_class.toLowerCase()}`}>
            {results.soil_health.health_class}
          </div>
          <div className="score">{results.soil_health.health_score}/100</div>
          <div className="scores-list">
            <div className="score-item">
              <span>Nitrogen</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.nitrogen}%`}}></div>
              </div>
            </div>
            <div className="score-item">
              <span>Phosphorus</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.phosphorus}%`}}></div>
              </div>
            </div>
            <div className="score-item">
              <span>Potassium</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.potassium}%`}}></div>
              </div>
            </div>
            {results.soil_health.component_scores.ph && (
              <div className="score-item">
                <span>pH Level</span>
                <div className="bar">
                  <div className="fill" style={{width: `${results.soil_health.component_scores.ph}%`}}></div>
                </div>
              </div>
            )}
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
        {}
        {results.price_analysis && (
          <div className="result-card">
            <h3>💰 Market Analysis</h3>
            <div className="price-info">
              <div className="price-row">
                <span>Current Price:</span>
                <strong>₹{results.price_analysis.current_price}/quintal</strong>
              </div>
              <div className="price-row">
                <span>Trend:</span>
                <span className={`trend ${results.price_analysis.trend.toLowerCase()}`}>
                  {results.price_analysis.trend}
                </span>
              </div>
              <div className="price-row">
                <span>Change:</span>
                <span>{results.price_analysis.change_percentage > 0 ? '+' : ''}{results.price_analysis.change_percentage}%</span>
              </div>
            </div>
            {results.price_analysis.future_prices && results.price_analysis.future_prices.length > 0 && (
              <div className="future-prices">
                <h4>📈 Next 5 Days Forecast</h4>
                <div className="price-chart">
                  {results.price_analysis.future_prices.map((price, idx) => (
                    <div key={idx} className="price-bar-container">
                      <div className="price-bar" style={{height: `${(price / results.price_analysis.current_price) * 100}%`}}></div>
                      <span>Day {idx+1}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <p className="market-rec">{results.price_analysis.recommendation}</p>
          </div>
        )}
        {}
        {results.crop_specific && (
          <div className="result-card">
            <h3>🎯 Crop-Specific Plan</h3>
            <div className="crop-specific">
              <p><strong>For {results.recommended_crop}:</strong></p>
              {results.crop_specific.deficit && (
                <div className="deficit-info">
                  <p>Nutrient Deficits to address:</p>
                  <ul>
                    {results.crop_specific.deficit.N > 0 && <li>Nitrogen: {results.crop_specific.deficit.N} kg/hectare</li>}
                    {results.crop_specific.deficit.P > 0 && <li>Phosphorus: {results.crop_specific.deficit.P} kg/hectare</li>}
                    {results.crop_specific.deficit.K > 0 && <li>Potassium: {results.crop_specific.deficit.K} kg/hectare</li>}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
        {}
        <div className="result-card full-width">
          <h3>💡 Overall Recommendations</h3>
          <ul className="overall-rec">
            {results.overall_recommendations && results.overall_recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
            {results.soil_health.recommendations && results.soil_health.recommendations.slice(0, 2).map((rec, idx) => (
              <li key={`rec-${idx}`}>{rec}</li>
            ))}
          </ul>
        </div>
        {}
        <div className="result-card timestamp">
          <p>Analysis completed: {results.analysis_timestamp}</p>
        </div>
      </div>
    </div>
  );
}
export default MultiPageDashboard;