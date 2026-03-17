import React, { useState, useEffect } from "react";
import axios from "axios";
import "./History.css";
function History() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get("http://localhost:5000/api/history", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPredictions(response.data.predictions || []);
    } catch (error) {
      console.error("Failed to fetch history");
    } finally {
      setLoading(false);
    }
  };
  const clearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all prediction history? This action cannot be undone.')) {
      return;
    }
    try {
      const token = localStorage.getItem("token");
      await axios.delete("http://localhost:5000/api/history", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPredictions([]);
      alert('Prediction history cleared successfully!');
    } catch (error) {
      console.error("Failed to clear history", error);
      alert('Failed to clear history. Please try again.');
    }
  };
  useEffect(() => {
    fetchHistory();
  }, []);
  if (loading) return <div className="history-container"><p>Loading...</p></div>;
  return (
    <div className="history-container">
      <div className="history-header-section">
        <h1>📊 Prediction History</h1>
        {predictions.length > 0 && (
          <button onClick={clearHistory} className="clear-history-btn">
            🗑️ Clear History
          </button>
        )}
      </div>
      {predictions.length === 0 ? (
        <p className="no-data">No predictions yet. Start by analyzing your crops!</p>
      ) : (
        <div className="history-grid">
          {predictions.map((pred, idx) => (
            <div key={idx} className="history-card">
              <div className="history-header">
                <span className="crop-name">🌾 {pred.crop}</span>
                <span className="timestamp">{new Date(pred.timestamp).toLocaleDateString()}</span>
              </div>
              <div className="history-details">
                <p>N: {pred.n} | P: {pred.p} | K: {pred.k}</p>
                <p>Temp: {pred.temperature}°C | pH: {pred.ph}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
export default History;