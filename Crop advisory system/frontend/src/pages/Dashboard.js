import React from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../LanguageContext";
import "./Dashboard.css";
function Dashboard() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  return (
    <div className="dashboard-container">
      <div className="hero-section">
        <div className="hero-background">
          <img src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200" alt="Farm" />
          <div className="hero-overlay"></div>
        </div>
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="gradient-text">🌾 CropGenius AI</span>
          </h1>
          <p className="hero-project-title">A Multilingual Intelligent Crop Advisory and Recommendation System</p>
          <p className="hero-subtitle">AI-powered crop analysis and smart crop recommendations for farmers</p>
          <p className="hero-description">Transform your farming with data-driven decisions, real-time analytics, and intelligent crop recommendations</p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={() => navigate('/analysis')}>
              🚀 Start Analysis
            </button>
            <button className="btn-secondary" onClick={() => navigate('/about')}>
              📖 Learn More
            </button>
          </div>
        </div>
      </div>
      <div className="features-section">
        <h2 className="section-title">🌾 Smart Crop Solutions</h2>
        <div className="features-grid">
          <div className="feature-box" onClick={() => navigate('/analysis')}>
            <div className="feature-img-container">
              <img src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400" alt="Prediction" />
            </div>
            <h3>🔮 Crop Prediction</h3>
            <p>AI-powered recommendations based on soil parameters and weather conditions</p>
            <span className="feature-badge">Advanced ML</span>
          </div>
          <div className="feature-box" onClick={() => navigate('/analysis')}>
            <div className="feature-img-container">
              <img src="https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=400" alt="Soil" />
            </div>
            <h3>🌍 Soil Analysis</h3>
            <p>Comprehensive soil health assessment with NPK levels and pH monitoring</p>
            <span className="feature-badge">Real-time</span>
          </div>
          <div className="feature-box" onClick={() => navigate('/analysis')}>
            <div className="feature-img-container">
              <img src="https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400" alt="Fertilizer" />
            </div>
            <h3>🧪 Fertilizer Guide</h3>
            <p>Personalized fertilizer recommendations for optimal crop growth</p>
            <span className="feature-badge">Customized</span>
          </div>
          <div className="feature-box" onClick={() => navigate('/analysis')}>
            <div className="feature-img-container">
              <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400" alt="Analytics" />
            </div>
            <h3>📈 Analytics Dashboard</h3>
            <p>Track your farming history and monitor crop performance over time</p>
            <span className="feature-badge">Insights</span>
          </div>
        </div>
      </div>
      <div className="stats-section">
        <div className="stat-card">
          <div className="stat-icon-img">
            <img src="https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=200" alt="Farmers" />
          </div>
          <div className="stat-number">10K+</div>
          <div className="stat-label">Farmers Helped</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-img">
            <img src="https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=200" alt="Crops" />
          </div>
          <div className="stat-number">50+</div>
          <div className="stat-label">Crop Types</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-img">
            <img src="https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=200" alt="Accuracy" />
          </div>
          <div className="stat-number">95%</div>
          <div className="stat-label">Accuracy Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-img">
            <img src="https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=200" alt="Support" />
          </div>
          <div className="stat-number">24/7</div>
          <div className="stat-label">AI Support</div>
        </div>
      </div>
      <div className="cta-section">
        <div className="cta-background">
          <img src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200" alt="CTA" />
          <div className="cta-overlay"></div>
        </div>
        <div className="cta-content">
          <h2>Ready to Transform Your Farm?</h2>
          <p>Join thousands of farmers using AI to maximize their harvest</p>
          <button className="btn-cta" onClick={() => navigate('/analysis')}>
            Get Started Now →
          </button>
        </div>
      </div>
    </div>
  );
}
export default Dashboard;
