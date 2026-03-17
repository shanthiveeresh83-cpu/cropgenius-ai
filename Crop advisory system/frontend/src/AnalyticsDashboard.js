import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = () => {
  const [priceData, setPriceData] = useState([]);
  const [cropComparison, setCropComparison] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState('rice');
  const [loading, setLoading] = useState(true);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/analytics-data', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPriceData(response.data.price_trends);
      setCropComparison(response.data.crop_comparison);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      // Use mock data if API fails
      loadMockData();
    }
  };

  const loadMockData = () => {
    const months = ['Jan 23', 'Apr 23', 'Jul 23', 'Oct 23', 'Jan 24', 'Apr 24', 'Jul 24', 'Oct 24'];
    
    const priceHistory = {
      rice: [2400, 2450, 2500, 2480, 2520, 2550, 2500, 2530],
      wheat: [1950, 2000, 1980, 2020, 2050, 2100, 2080, 2120],
      maize: [1750, 1800, 1820, 1850, 1880, 1900, 1850, 1870],
      cotton: [5800, 5900, 6000, 6100, 6050, 6200, 6150, 6250],
      chickpea: [4300, 4400, 4500, 4550, 4600, 4650, 4700, 4750],
      kidneybeans: [5800, 5900, 6000, 6050, 6100, 6150, 6100, 6200],
      pigeonpeas: [4800, 4900, 5000, 5050, 5100, 5150, 5100, 5200],
      mungbean: [5800, 5900, 6000, 6050, 6100, 6150, 6100, 6200],
      blackgram: [5300, 5400, 5500, 5550, 5600, 5650, 5600, 5700],
      lentil: [4600, 4700, 4800, 4850, 4900, 4950, 4900, 5000]
    };

    const trends = months.map((month, idx) => ({
      month,
      ...Object.keys(priceHistory).reduce((acc, crop) => {
        acc[crop] = priceHistory[crop][idx];
        return acc;
      }, {})
    }));

    const comparison = [
      { crop: 'Cotton', price: 6250, yield: 2.5, profit: 15625, trend: 'rising', season: 'kharif' },
      { crop: 'Rice', price: 2530, yield: 5.0, profit: 12650, trend: 'stable', season: 'kharif' },
      { crop: 'Kidneybeans', price: 6200, yield: 2.0, profit: 12400, trend: 'rising', season: 'kharif' },
      { crop: 'Mungbean', price: 6200, yield: 1.2, profit: 7440, trend: 'rising', season: 'kharif' },
      { crop: 'Chickpea', price: 4750, yield: 2.5, profit: 11875, trend: 'rising', season: 'rabi' },
      { crop: 'Maize', price: 1870, yield: 6.0, profit: 11220, trend: 'rising', season: 'kharif' },
      { crop: 'Wheat', price: 2120, yield: 4.5, profit: 9540, trend: 'rising', season: 'rabi' },
      { crop: 'Blackgram', price: 5700, yield: 1.0, profit: 5700, trend: 'rising', season: 'kharif' },
      { crop: 'Pigeonpeas', price: 5200, yield: 1.8, profit: 9360, trend: 'rising', season: 'kharif' },
      { crop: 'Lentil', price: 5000, yield: 1.5, profit: 7500, trend: 'rising', season: 'rabi' }
    ];

    setPriceData(trends);
    setCropComparison(comparison);
    setLoading(false);
  };

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h1>📊 CropGenius AI — Analytics Dashboard</h1>
        <p>2-Year Historical Data & Market Trends - {cropComparison.length} Crops Analyzed</p>
        {cropComparison.length > 0 && cropComparison[0].season && (
          <p className="season-info">🌱 Current Season Crops Highlighted</p>
        )}
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>Total Crops</h3>
            <p className="stat-value">{cropComparison.length}</p>
            <span className="stat-label">Analyzed</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h3>Avg Price</h3>
            <p className="stat-value">₹{Math.round(cropComparison.reduce((a, b) => a + b.price, 0) / cropComparison.length)}</p>
            <span className="stat-label">Per Quintal</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🌾</div>
          <div className="stat-content">
            <h3>Avg Yield</h3>
            <p className="stat-value">{(cropComparison.reduce((a, b) => a + b.yield, 0) / cropComparison.length).toFixed(1)}</p>
            <span className="stat-label">Tons/Hectare</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>Data Period</h3>
            <p className="stat-value">24</p>
            <span className="stat-label">Months</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card full-width">
          <h2>📈 Price Trends (2 Years)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={priceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="rice" stroke="#8884d8" strokeWidth={2} />
              <Line type="monotone" dataKey="wheat" stroke="#82ca9d" strokeWidth={2} />
              <Line type="monotone" dataKey="maize" stroke="#ffc658" strokeWidth={2} />
              <Line type="monotone" dataKey="cotton" stroke="#ff7300" strokeWidth={2} />
              <Line type="monotone" dataKey="chickpea" stroke="#0088fe" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>💰 Current Market Prices</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={cropComparison}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="crop" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="price" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>🌾 Expected Yield</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={cropComparison}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="crop" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="yield" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>💵 Profitability Comparison</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={cropComparison}
                dataKey="profit"
                nameKey="crop"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {cropComparison.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>📊 Market Trends</h2>
          <div className="trend-list">
            {cropComparison.map((crop, idx) => (
              <div key={idx} className="trend-item">
                <div className="trend-crop">
                  <span className="crop-name">{crop.crop}</span>
                  <span className={`trend-badge ${crop.trend}`}>
                    {crop.trend === 'rising' ? '📈' : crop.trend === 'falling' ? '📉' : '➡️'} {crop.trend}
                  </span>
                </div>
                <div className="trend-details">
                  <span>₹{crop.price}/q</span>
                  <span>{crop.yield}t/ha</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="comparison-table">
        <h2>📋 Detailed Crop Comparison</h2>
        <table>
          <thead>
            <tr>
              <th>Crop</th>
              <th>Market Price (₹/q)</th>
              <th>Expected Yield (t/ha)</th>
              <th>Profitability (₹/ha)</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            {cropComparison.map((crop, idx) => (
              <tr key={idx}>
                <td><strong>{crop.crop}</strong></td>
                <td>₹{crop.price}</td>
                <td>{crop.yield}</td>
                <td>₹{crop.profit.toLocaleString()}</td>
                <td>
                  <span className={`trend-badge ${crop.trend}`}>
                    {crop.trend === 'rising' ? '📈' : crop.trend === 'falling' ? '📉' : '➡️'} {crop.trend}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
