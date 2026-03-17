import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Analysis from "./pages/Analysis";
import History from "./pages/History";
import About from "./pages/About";
import AnalyticsDashboard from "./AnalyticsDashboard";
import { LanguageProvider } from "./LanguageContext";
import FarmerChatbot from "./FarmerChatbot";
import LanguageSelector from "./LanguageSelector";
import GlobalLocationSearch from "./GlobalLocationSearch";
import "./theme.css"; 
function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <LanguageSelector />
        <GlobalLocationSearch />
        <Navbar />
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/analytics" element={<AnalyticsDashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/about" element={<About />} />
        </Routes>
        <FarmerChatbot />
      </BrowserRouter>
    </LanguageProvider>
  );
}
export default App;