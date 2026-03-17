import React from "react";
import "./About.css";
function About() {
  return (
    <div className="about-container">
      <div className="about-content">
        <h1>🌾 CropGenius AI</h1>
        <p className="about-subtitle">A Multilingual Intelligent Crop Advisory and Recommendation System</p>
        <section className="about-section">
          <h2>🎯 Our Mission</h2>
          <p>Empowering farmers with AI-driven insights for better crop decisions and sustainable farming practices.</p>
        </section>
        <section className="about-section">
          <h2>✨ Features</h2>
          <div className="features-grid">
            <div className="feature-item">
              <span className="feature-icon">🔮</span>
              <h3>Crop Prediction</h3>
              <p>ML-powered recommendations based on soil and weather data</p>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📊</span>
              <h3>Comprehensive Analysis</h3>
              <p>Yield prediction, fertilizer advice, and soil health assessment</p>
            </div>
            <div className="feature-item">
              <span className="feature-icon">💬</span>
              <h3>AI Chatbot</h3>
              <p>24/7 farming assistant with voice support in 4 languages</p>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📷</span>
              <h3>Image Analysis</h3>
              <p>Upload crop photos for instant recommendations</p>
            </div>
          </div>
        </section>
        <section className="about-section">
          <h2>🌍 Multi-Language Support</h2>
          <p>Available in English, Hindi, Telugu, and Tamil</p>
        </section>
        <section className="about-section">
          <h2>🤖 Technology Stack</h2>
          <p>React • Flask • Machine Learning • XGBoost • Random Forest</p>
        </section>
      </div>
    </div>
  );
}
export default About;