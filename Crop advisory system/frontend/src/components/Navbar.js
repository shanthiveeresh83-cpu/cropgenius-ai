import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useLanguage } from "../LanguageContext";
import "./Navbar.css";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();
  const token = localStorage.getItem("token");
  
  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };
  
  if (!token) return null;
  
  return (
    <nav className="navbar">
      <div className="nav-brand">🌾 CropGenius AI</div>
      <div className="nav-links">
        <Link to="/dashboard" className={location.pathname === "/dashboard" ? "active" : ""}>{t('dashboard')}</Link>
        <Link to="/analysis" className={location.pathname === "/analysis" ? "active" : ""}>{t('analysis')}</Link>
        <Link to="/analytics" className={location.pathname === "/analytics" ? "active" : ""}>{t('analytics') || '📊 Analytics'}</Link>
        <Link to="/history" className={location.pathname === "/history" ? "active" : ""}>{t('history')}</Link>
        <Link to="/about" className={location.pathname === "/about" ? "active" : ""}>{t('about')}</Link>
        
        <button onClick={handleLogout} className="logout-btn">{t('logout')}</button>
      </div>
    </nav>
  );
}

export default Navbar;