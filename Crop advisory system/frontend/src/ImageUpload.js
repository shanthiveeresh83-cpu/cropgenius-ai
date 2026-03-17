import React, { useState } from "react";
import axios from "axios";
import { useLanguage } from "./LanguageContext";
import "./ImageUpload.css";
function ImageUpload() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useLanguage();
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setResult(null);
      setLoading(false);
      if (preview) {
        URL.revokeObjectURL(preview);
      }
      setImage(file);
      setPreview(URL.createObjectURL(file));
      e.target.value = null;
    }
  };
  const analyzeImage = async () => {
    if (!image) return;
    setLoading(true);
    setResult(null); 
    const reader = new FileReader();
    reader.onloadend = async () => {
      try {
        const token = localStorage.getItem("token");
        const currentLanguage = localStorage.getItem("language") || "en";
        const base64Data = reader.result;
        console.log("Sending NEW image to backend for analysis...");
        console.log("Image data length:", base64Data.length);
        const response = await axios.post(
          "http://localhost:5000
          { 
            image: base64Data, 
            language: currentLanguage,
            timestamp: Date.now() 
          },
          { 
            headers: { 
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
              "Cache-Control": "no-cache" 
            } 
          }
        );
        console.log("Analysis result:", response.data);
        setResult(response.data);
      } catch (error) {
        console.error("Analysis error:", error.response?.data || error.message);
        const errorMessage = error.response?.data?.error || "Failed to analyze image";
        setResult({ error: errorMessage });
      }
      setLoading(false);
    };
    reader.readAsDataURL(image);
  };
  return (
    <>
      {!isOpen && (
        <button className="image-toggle" onClick={() => setIsOpen(true)} title="Upload Crop Photo">
          📷
        </button>
      )}
      {isOpen && (
        <div className="image-upload-modal">
          <div className="modal-header">
            📷 {t('cropAnalysis')}
            <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
          </div>
          <div className="modal-content">
            {!preview && (
              <div className="instructions">
                <h4>👇 {t('howToUse')}</h4>
                <div className="step">
                  <span className="step-icon">📸</span>
                  <p>{t('step1')}</p>
                </div>
                <div className="step">
                  <span className="step-icon">📁</span>
                  <p>{t('step2')}</p>
                </div>
                <div className="step">
                  <span className="step-icon">🔍</span>
                  <p>{t('step3')}</p>
                </div>
              </div>
            )}
            <div className="upload-area">
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleImageChange}
                id="file-input"
              />
              <label htmlFor="file-input" className="upload-label">
                {preview ? `🔄 ${t('changePhoto')}` : `📸 ${t('takePhoto')}`}
              </label>
            </div>
            {preview && (
              <div className="preview">
                <img src={preview} alt="Crop Preview" />
                <button onClick={analyzeImage} disabled={loading} className="analyze-btn">
                  {loading ? `⏳ ${t('analyzing')}` : `🔍 ${t('analyzeCrop')}`}
                </button>
              </div>
            )}
            {result && !result.error && (
              <div className="result-card">
                <div className="result-header">
                  <h4>✅ {result.detected_crop}</h4>
                </div>
                <div className="result-item">
                  <span className="icon">🧪</span>
                  <div>
                    <strong>{t('fertilizerNeeded')}</strong>
                    <p>{result.fertilizer}</p>
                  </div>
                </div>
                <div className="result-item">
                  <span className="icon">💧</span>
                  <div>
                    <strong>{t('waterRequirement')}</strong>
                    <p>{result.irrigation}</p>
                  </div>
                </div>
                <div className="result-item">
                  <span className="icon">📅</span>
                  <div>
                    <strong>{t('plantingSeason')}</strong>
                    <p>{result.season}</p>
                  </div>
                </div>
                <div className="result-item advice">
                  <span className="icon">💡</span>
                  <div>
                    <strong>{t('expertAdvice')}</strong>
                    <p>{result.advice}</p>
                  </div>
                </div>
              </div>
            )}
            {result && result.error && (
              <div className="error">
                <span>⚠️</span> {result.error}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
export default ImageUpload;