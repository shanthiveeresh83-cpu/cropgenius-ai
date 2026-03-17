import React, { useState } from 'react';
import axios from 'axios';
import './LocationSearch.css';
function LocationSearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const searchLocation = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await axios.post('http://localhost:5000
        query: query.trim()
      });
      if (response.data.success) {
        setResult(response.data.location);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Location not found. Try another search.');
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="location-search">
      <div className="search-header">
        <h3>🔍 Explore Other Locations</h3>
        <p>Search for any city or district in India to view its agricultural details</p>
      </div>
      <form onSubmit={searchLocation} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter city, district, or area name..."
          className="search-input"
        />
        <button type="submit" disabled={loading} className="search-btn">
          {loading ? '🔍 Searching...' : '🌍 Search Location'}
        </button>
      </form>
      {error && (
        <div className="search-error">
          ⚠️ {error}
        </div>
      )}
      {result && (
        <div className="search-result">
          <div className="result-header">
            <h4>📍 Location Found</h4>
          </div>
          <div className="result-grid">
            <div className="result-item">
              <span className="label">🏙️ City:</span>
              <span className="value">{result.city || 'N/A'}</span>
            </div>
            <div className="result-item">
              <span className="label">🏛️ District:</span>
              <span className="value">{result.district || 'N/A'}</span>
            </div>
            <div className="result-item">
              <span className="label">🗺️ State:</span>
              <span className="value">{result.state || 'N/A'}</span>
            </div>
            <div className="result-item">
              <span className="label">🌐 Coordinates:</span>
              <span className="value">
                {result.latitude?.toFixed(4)}, {result.longitude?.toFixed(4)}
              </span>
            </div>
          </div>
          {result.weather && (
            <div className="weather-info">
              <h5>🌤️ Current Weather</h5>
              <div className="weather-grid">
                <div className="weather-item">
                  <span className="weather-icon">🌡️</span>
                  <span className="weather-label">Temperature</span>
                  <span className="weather-value">{result.weather.temperature}°C</span>
                </div>
                <div className="weather-item">
                  <span className="weather-icon">💧</span>
                  <span className="weather-label">Humidity</span>
                  <span className="weather-value">{result.weather.humidity}%</span>
                </div>
                <div className="weather-item">
                  <span className="weather-icon">🌧️</span>
                  <span className="weather-label">Rainfall</span>
                  <span className="weather-value">{result.weather.rainfall} mm</span>
                </div>
              </div>
            </div>
          )}
          <div className="result-address">
            <strong>Full Address:</strong>
            <p>{result.formatted_address}</p>
          </div>
          <div className="result-note">
            💡 This location's weather data can be used for crop recommendations
          </div>
        </div>
      )}
    </div>
  );
}
export default LocationSearch;