import React, { useState } from 'react';
import { useLanguage } from '../LanguageContext';
import './MultiPageDashboard.css';
function MultiPageDashboard() {
  const [currentPage, setCurrentPage] = useState('home');
  const [formData, setFormData] = useState({
    N: '', P: '', K: '', temperature: '', humidity: '', ph: '', rainfall: ''
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisMode, setAnalysisMode] = useState('auto');
  const { t, language } = useLanguage();
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  const handleAutoAnalyze = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch('http://localhost:5000
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({})
      });
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      const data = await response.json();
      const transformedData = {
        recommended_crop: data.recommended_crop,
        features: data.features,
        data_sources: data.data_sources,
        location: data.location,
        mode: data.mode,
        confidence: data.confidence,
        soil_health: { 
          health_class: 'Good', 
          health_score: 75,
          component_scores: { nitrogen: 70, phosphorus: 65, potassium: 80 }
        },
        weather_suitability: 'Good',
        fertilizer_recommendations: [
          { nutrient: 'Nitrogen', fertilizer: 'Urea', quantity: '50-100 kg/hectare' }
        ],
        overall_recommendations: ['Conditions are good for ' + data.recommended_crop + ' cultivation!'],
        analysis_timestamp: new Date().toISOString()
      };
      setResults(transformedData);
      setAnalysisMode('auto');
      setCurrentPage('results');
    } catch (error) {
      console.error('Auto analysis error:', error);
      alert(`${t('analysisError')}: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };
  const handleManualAnalyze = async () => {
    const requiredFields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
    for (const field of requiredFields) {
      if (!formData[field] || formData[field] === '') {
        alert(`${t('fillAllFields')} ${field} ${t('isMissing')}.`);
        return;
      }
    }
    setLoading(true);
    try {
      const currentLanguage = localStorage.getItem("language") || "en";
      const response = await fetch('http://localhost:5000
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, language: currentLanguage })
      });
      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      setResults(data);
      setAnalysisMode('manual');
      setCurrentPage('results');
    } catch (error) {
      console.error('Analysis error:', error);
      alert(`${t('analysisError')}: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };
  const renderPage = () => {
    switch(currentPage) {
      case 'home':
        return <HomePage onNext={() => setCurrentPage('input')} />;
      case 'input':
        return <InputPage 
          formData={formData} 
          onChange={handleChange} 
          onAutoAnalyze={handleAutoAnalyze}
          onManualAnalyze={handleManualAnalyze}
          onBack={() => setCurrentPage('home')} 
          loading={loading}
        />;
      case 'results':
        return <ResultsPage results={results} onBack={() => setCurrentPage('input')} onHome={() => setCurrentPage('home')} analysisMode={analysisMode} />;
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
  const { t } = useLanguage();
  return (
    <div className="page home-page">
      <div className="hero-content">
        <h1>🌾 {t('smartAgriPlatform')}</h1>
        <p>{t('aiPoweredCrop')}</p>
        <div className="features">
          <div className="feature-card">
            <span className="icon">🔮</span>
            <h3>{t('cropPrediction')}</h3>
            <p>{t('aiBasedCropRec')}</p>
          </div>
          <div className="feature-card">
            <span className="icon">🌍</span>
            <h3>{t('soilAnalysis')}</h3>
            <p>{t('soilHealthAssessment')}</p>
          </div>
          <div className="feature-card">
            <span className="icon">🧪</span>
            <h3>{t('fertilizerGuide')}</h3>
            <p>{t('personalizedFertilizer')}</p>
          </div>
        </div>
        <button className="btn-large" onClick={onNext}>{t('getStarted')} →</button>
      </div>
    </div>
  );
}
function InputPage({ formData, onChange, onAutoAnalyze, onManualAnalyze, onBack, loading }) {
  const { t } = useLanguage();
  const [showManual, setShowManual] = useState(false);
  return (
    <div className="page input-page">
      <div className="page-header">
        <button className="btn-back" onClick={onBack}>← {t('back')}</button>
        <h2>📊 {t('enterFarmParams')}</h2>
      </div>
      <div className="input-container">
        {!showManual ? (
          <div className="auto-mode">
            <div style={{ textAlign: 'center', padding: '30px 20px' }}>
              <div style={{ fontSize: '60px', marginBottom: '20px' }}>🤖</div>
              <h3>Automatic Crop Prediction</h3>
              <p style={{ color: '#666', marginBottom: '30px' }}>
                Our system will automatically fetch weather data and simulate soil parameters.
              </p>
              <button 
                className="btn-large" 
                onClick={onAutoAnalyze}
                disabled={loading}
                style={{ backgroundColor: loading ? '#ccc' : '#27ae60' }}
              >
                {loading ? '🤔 Analyzing...' : '🚀 Get Automatic Recommendation'}
              </button>
              <p style={{ marginTop: '20px', fontSize: '14px', color: '#999' }}>
                No manual input required
              </p>
            </div>
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button 
                onClick={() => setShowManual(true)} 
                style={{ background: 'none', border: 'none', color: '#3498db', cursor: 'pointer', textDecoration: 'underline' }}
              >
                Or enter manual parameters →
              </button>
            </div>
          </div>
        ) : (
          <div className="manual-mode">
            <div className="input-grid">
              <div className="input-group">
                <label>{t('nitrogen')} (N)</label>
                <input type="number" name="N" value={formData.N} onChange={onChange} required />
              </div>
              <div className="input-group">
                <label>{t('phosphorus')} (P)</label>
                <input type="number" name="P" value={formData.P} onChange={onChange} required />
              </div>
              <div className="input-group">
                <label>{t('potassium')} (K)</label>
                <input type="number" name="K" value={formData.K} onChange={onChange} required />
              </div>
              <div className="input-group">
                <label>{t('temperature')}</label>
                <input type="number" name="temperature" value={formData.temperature} onChange={onChange} required />
              </div>
              <div className="input-group">
                <label>{t('humidity')} (%)</label>
                <input type="number" name="humidity" value={formData.humidity} onChange={onChange} required />
              </div>
              <div className="input-group">
                <label>{t('phLevel')}</label>
                <input type="number" step="0.1" name="ph" value={formData.ph} onChange={onChange} required />
              </div>
              <div className="input-group">
                <label>{t('rainfall')}</label>
                <input type="number" name="rainfall" value={formData.rainfall} onChange={onChange} required />
              </div>
            </div>
            <button 
              className="btn-large" 
              onClick={onManualAnalyze}
              disabled={loading}
            >
              {loading ? '🤔 Analyzing...' : `${t('analyzeFarm')} →`}
            </button>
            <div style={{ textAlign: 'center', marginTop: '15px' }}>
              <button 
                onClick={() => setShowManual(false)} 
                style={{ background: 'none', border: 'none', color: '#3498db', cursor: 'pointer', textDecoration: 'underline' }}
              >
                ← Use automatic prediction
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
function ResultsPage({ results, onBack, onHome }) {
  const { t } = useLanguage();
  if (!results) return null;
  const getWeatherText = (suitability) => {
    if (suitability === 'Excellent') return t('perfectWeather');
    if (suitability === 'Good') return t('goodWeather');
    if (suitability === 'Fair') return t('moderateWeather');
    if (suitability === 'Poor') return t('poorWeather');
    return t('goodWeather');
  };
  return (
    <div className="page results-page">
      <div className="page-header">
        <button className="btn-back" onClick={onBack}>← {t('back')}</button>
        <h2>📈 {t('comprehensiveAnalysis')}</h2>
        <button className="btn-home" onClick={onHome}>🏠 {t('home')}</button>
      </div>
      <div className="results-grid">
        <div className="result-card featured">
          <h3>🌾 {t('recommendedCrop')}</h3>
          <div className="crop-display">{results.recommended_crop}</div>
          {results.yield_prediction && (
            <div className="yield-info">
              <span>📊 {t('expectedYield')}: {results.yield_prediction.estimated_yield} {results.yield_prediction.unit}</span>
            </div>
          )}
        </div>
        <div className="result-card">
          <h3>🌍 {t('soilHealth')}</h3>
          <div className={`health-badge ${results.soil_health.health_class.toLowerCase()}`}>
            {results.soil_health.health_class}
          </div>
          <div className="score">{results.soil_health.health_score}/100</div>
          <div className="scores-list">
            <div className="score-item">
              <span>{t('nitrogen')}</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.nitrogen}%`}}></div>
              </div>
            </div>
            <div className="score-item">
              <span>{t('phosphorus')}</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.phosphorus}%`}}></div>
              </div>
            </div>
            <div className="score-item">
              <span>{t('potassium')}</span>
              <div className="bar">
                <div className="fill" style={{width: `${results.soil_health.component_scores.potassium}%`}}></div>
              </div>
            </div>
          </div>
        </div>
        <div className="result-card">
          <h3>🌤️ {t('weatherSuitability')}</h3>
          <div className={`suitability-badge ${results.weather_suitability?.toLowerCase() || 'good'}`}>
            {results.weather_suitability || 'Good'}
          </div>
          <p className="suitability-text">{getWeatherText(results.weather_suitability)}</p>
        </div>
        <div className="result-card">
          <h3>🧪 {t('fertilizerRecommendations')}</h3>
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
        {results.price_analysis && (
          <div className="result-card">
            <h3>💰 {t('marketAnalysis')}</h3>
            <div className="price-info">
              <div className="price-row">
                <span>{t('currentPrice')}:</span>
                <strong>₹{results.price_analysis.current_price}/quintal</strong>
              </div>
              <div className="price-row">
                <span>{t('trend')}:</span>
                <span className={`trend ${results.price_analysis.trend.toLowerCase()}`}>
                  {results.price_analysis.trend}
                </span>
              </div>
              <div className="price-row">
                <span>{t('change')}:</span>
                <span>{results.price_analysis.change_percentage > 0 ? '+' : ''}{results.price_analysis.change_percentage}%</span>
              </div>
            </div>
            {results.price_analysis.future_prices && results.price_analysis.future_prices.length > 0 && (
              <div className="future-prices">
                <h4>📈 {t('forecast')}</h4>
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
        <div className="result-card full-width">
          <h3>💡 {t('overallRecommendations')}</h3>
          <ul className="overall-rec">
            {results.overall_recommendations && results.overall_recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
        <div className="result-card timestamp">
          <p>{t('analysisCompleted')}: {results.analysis_timestamp}</p>
        </div>
      </div>
    </div>
  );
}
export default MultiPageDashboard;