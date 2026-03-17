import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './LocationDetector.css';
function LocationDetector({ onLocationDetected }) {
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [permissionStatus, setPermissionStatus] = useState('prompt');
  useEffect(() => {
    fetchSavedLocation();
    if (navigator.permissions) {
      navigator.permissions.query({ name: 'geolocation' }).then((result) => {
        setPermissionStatus(result.state);
      });
    }
  }, []);
  const fetchSavedLocation = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      const response = await axios.get('http://localhost:5000/api/get-location', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setLocation(response.data.location);
        if (onLocationDetected) {
          onLocationDetected(response.data.location);
        }
      }
    } catch (err) {
      console.log('No saved location');
    }
  };
  const detectLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }
    setLoading(true);
    setError('');
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const token = localStorage.getItem('token');
          const response = await axios.post(
            'http://localhost:5000/api/detect-location',
            { latitude, longitude },
            { headers: { Authorization: `Bearer ${token}` } }
          );
          if (response.data.success) {
            const locationData = response.data.location;
            setLocation(locationData);
            setPermissionStatus('granted');
            setError(''); 
            localStorage.setItem('selectedLocation', JSON.stringify(locationData));
            if (onLocationDetected) {
              onLocationDetected(locationData);
            }
            alert(`Location updated: ${locationData.city}, ${locationData.state}`);
          }
        } catch (err) {
          console.error('Location save error:', err);
          setError(err.response?.data?.error || 'Failed to save location');
        } finally {
          setLoading(false);
        }
      },
      (err) => {
        setLoading(false);
        setPermissionStatus('denied');
        switch (err.code) {
          case err.PERMISSION_DENIED:
            setError('Location permission denied. Please enable location access in your browser settings.');
            break;
          case err.POSITION_UNAVAILABLE:
            setError('Location information unavailable.');
            break;
          case err.TIMEOUT:
            setError('Location request timed out.');
            break;
          default:
            setError('An unknown error occurred.');
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };
  const manualLocationUpdate = async (lat, lon) => {
    const token = localStorage.getItem('token');
    try {
      const response = await axios.put(
        'http://localhost:5000/api/update-location',
        { latitude: lat, longitude: lon },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.data.success) {
        setLocation(response.data.location);
        if (onLocationDetected) {
          onLocationDetected(response.data.location);
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update location');
    }
  };
  return (
    <div className="location-detector">
      <div className="location-header">
        <h3>📍 Your Location</h3>
        {location && (
          <span className="location-status">✓ Detected</span>
        )}
      </div>
      {!location && (
        <div className="location-prompt">
          <p>Enable location for personalized crop recommendations based on your area's weather and soil conditions.</p>
          <button 
            onClick={detectLocation} 
            disabled={loading}
            className="btn-detect-location"
          >
            {loading ? '🔍 Detecting...' : '📍 Detect My Location'}
          </button>
          {permissionStatus === 'denied' && (
            <div className="permission-help">
              <p>⚠️ Location access is blocked. To enable:</p>
              <ol>
                <li>Click the lock icon in your browser's address bar</li>
                <li>Allow location access for this site</li>
                <li>Refresh the page</li>
              </ol>
            </div>
          )}
        </div>
      )}
      {location && (
        <div className="location-display">
          <div className="location-info">
            <div className="location-item">
              <span className="label">📍 City:</span>
              <span className="value">{location.city || 'Unknown'}</span>
            </div>
            <div className="location-item">
              <span className="label">🏛️ District:</span>
              <span className="value">{location.district || 'Unknown'}</span>
            </div>
            <div className="location-item">
              <span className="label">🗺️ State:</span>
              <span className="value">{location.state || 'Unknown'}</span>
            </div>
            <div className="location-item">
              <span className="label">🌐 Coordinates:</span>
              <span className="value">
                {location.latitude?.toFixed(4)}, {location.longitude?.toFixed(4)}
              </span>
            </div>
          </div>
          <div className="location-actions">
            <button 
              onClick={detectLocation} 
              className="btn-update-location"
              disabled={loading}
            >
              🔄 Update Location
            </button>
          </div>
        </div>
      )}
      {error && (
        <div className="location-error">
          ⚠️ {error}
        </div>
      )}
      <div className="privacy-note">
        <small>
          🔒 Your location is stored securely and used only for personalized recommendations. 
          You can change or remove it anytime.
        </small>
      </div>
    </div>
  );
}
export default LocationDetector;