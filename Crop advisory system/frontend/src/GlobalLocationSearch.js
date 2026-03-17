import React, { useState } from 'react';
import axios from 'axios';
import './GlobalLocationSearch.css';
function GlobalLocationSearch() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [detectingLocation, setDetectingLocation] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(
    JSON.parse(localStorage.getItem('selectedLocation')) || null
  );

  // Auto-detect location on mount if not set
  React.useEffect(() => {
    if (!currentLocation) {
      detectCurrentLocation();
    }
  }, []);

  const detectCurrentLocation = async () => {
    setDetectingLocation(true);
    setError('');
    
    if (!navigator.geolocation) {
      setError('Geolocation not supported by browser');
      setDetectingLocation(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          const token = localStorage.getItem('token');
          
          const response = await axios.post(
            'http://localhost:5000/api/detect-location',
            { latitude, longitude },
            { headers: token ? { Authorization: `Bearer ${token}` } : {} }
          );

          if (response.data.success) {
            const location = response.data.location;
            localStorage.setItem('selectedLocation', JSON.stringify(location));
            setCurrentLocation(location);
          }
        } catch (err) {
          console.error('Location detection failed:', err);
          setError('Failed to detect location');
        } finally {
          setDetectingLocation(false);
        }
      },
      (err) => {
        console.error('Geolocation error:', err);
        setError('Location access denied');
        setDetectingLocation(false);
      }
    );
  };
  const searchLocation = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await axios.post('http://localhost:5000/api/search-location', {
        query: query.trim()
      });
      if (response.data.success) {
        setResult(response.data.location);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Location not found');
    } finally {
      setLoading(false);
    }
  };
  const useThisLocation = async () => {
    if (result) {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          await axios.put(
            'http://localhost:5000/api/update-location',
            {
              latitude: result.latitude,
              longitude: result.longitude,
              district: result.district,
              state: result.state,
              city: result.city
            },
            { headers: { Authorization: `Bearer ${token}` } }
          );
        } catch (err) {
          console.error('Failed to update location in database:', err);
        }
      }
      localStorage.setItem('selectedLocation', JSON.stringify(result));
      setCurrentLocation(result);
      setIsOpen(false);
      alert(`Location updated to: ${result.city}, ${result.state}`);
      window.location.reload();
    }
  };
  const clearLocation = () => {
    localStorage.removeItem('selectedLocation');
    setCurrentLocation(null);
    window.location.reload();
  };
  return (
    <>
      <button className="global-location-btn" onClick={() => setIsOpen(true)}>
        {detectingLocation ? '📍 Detecting...' : currentLocation ? `📍 ${currentLocation.city || currentLocation.district || 'Location'}` : '📍 Detect Location'}
      </button>
      {isOpen && (
        <div className="location-modal-overlay" onClick={() => setIsOpen(false)}>
          <div className="location-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🌍 Location & Weather</h3>
              <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
            </div>
            
            <button onClick={detectCurrentLocation} disabled={detectingLocation} className="detect-btn">
              {detectingLocation ? '📍 Detecting...' : '📍 Detect My Location'}
            </button>
            
            {currentLocation && (
              <div className="current-location-info">
                <h4>📍 Current Location</h4>
                <p><strong>City:</strong> {currentLocation.city || 'N/A'}</p>
                <p><strong>District:</strong> {currentLocation.district || 'N/A'}</p>
                <p><strong>State:</strong> {currentLocation.state || 'N/A'}</p>
                {currentLocation.weather && (
                  <div className="weather-info">
                    <h5>🌤️ Real-Time Weather</h5>
                    <div className="weather-grid">
                      <div className="weather-item">
                        <span className="icon">🌡️</span>
                        <span className="label">Temperature</span>
                        <span className="value">{currentLocation.weather.temperature}°C</span>
                      </div>
                      <div className="weather-item">
                        <span className="icon">💧</span>
                        <span className="label">Humidity</span>
                        <span className="value">{currentLocation.weather.humidity}%</span>
                      </div>
                      <div className="weather-item">
                        <span className="icon">🌧️</span>
                        <span className="label">Rainfall</span>
                        <span className="value">{currentLocation.weather.rainfall}mm</span>
                      </div>
                    </div>
                  </div>
                )}
                <button onClick={clearLocation} className="clear-btn">Clear & Search New</button>
              </div>
            )}
            <form onSubmit={searchLocation} className="search-form">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search any city, district, or area..."
                className="search-input"
                autoFocus
              />
              <button type="submit" disabled={loading} className="search-btn">
                {loading ? '🔍 Searching...' : '🔍 Search'}
              </button>
            </form>
            {error && <div className="error-msg">⚠️ {error}</div>}
            {result && (
              <div className="search-result">
                <h4>📍 Found Location</h4>
                <div className="result-details">
                  <p><strong>City:</strong> {result.city || 'N/A'}</p>
                  <p><strong>District:</strong> {result.district || 'N/A'}</p>
                  <p><strong>State:</strong> {result.state || 'N/A'}</p>
                  <p><strong>Coordinates:</strong> {result.latitude?.toFixed(4)}, {result.longitude?.toFixed(4)}</p>
                </div>
                {result.weather && (
                  <div className="weather-preview">
                    <h5>🌤️ Weather</h5>
                    <div className="weather-items">
                      <span>🌡️ {result.weather.temperature}°C</span>
                      <span>💧 {result.weather.humidity}%</span>
                      <span>🌧️ {result.weather.rainfall}mm</span>
                    </div>
                  </div>
                )}
                <button onClick={useThisLocation} className="use-location-btn">
                  ✓ Use This Location for Analysis
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
export default GlobalLocationSearch;