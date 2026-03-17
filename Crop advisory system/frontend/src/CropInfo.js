import React, { useState } from 'react';
import { useLanguage } from './LanguageContext';
import './CropInfo.css';
const cropData = {
  rice: {
    name: "Rice",
    image: "https:
    season: "Kharif (June-October)",
    temperature: "20-27°C",
    rainfall: "200-300mm",
    soil: "Clay loam, pH 6-7",
    npk: "80-40-40",
    duration: "120-150 days",
    yield: "4-6 tons/hectare",
    diseases: ["Blast", "Brown spot", "Sheath blight"],
    tips: ["Maintain 2-3 inches water level", "Apply nitrogen in 3 splits", "Harvest when 80% grains turn golden"]
  },
  wheat: {
    name: "Wheat",
    image: "https:
    season: "Rabi (November-April)",
    temperature: "12-25°C",
    rainfall: "50-75mm",
    soil: "Loamy, pH 6-7.5",
    npk: "50-30-20",
    duration: "110-130 days",
    yield: "3-5 tons/hectare",
    diseases: ["Rust", "Smut", "Powdery mildew"],
    tips: ["Sow in rows 20cm apart", "Irrigate at critical stages", "Harvest when moisture is 20-25%"]
  },
  maize: {
    name: "Maize",
    image: "https:
    season: "Kharif/Rabi (Feb-Mar, July-Aug)",
    temperature: "21-27°C",
    rainfall: "90-120mm",
    soil: "Well-drained loam, pH 5.5-7",
    npk: "60-40-40",
    duration: "80-110 days",
    yield: "5-8 tons/hectare",
    diseases: ["Blight", "Rust", "Stalk rot"],
    tips: ["Plant 60x20cm spacing", "Apply fertilizer at knee-high stage", "Control weeds in first 30 days"]
  },
  cotton: {
    name: "Cotton",
    image: "https:
    season: "Kharif (April-May)",
    temperature: "21-30°C",
    rainfall: "50-100mm",
    soil: "Black cotton soil, pH 6-8",
    npk: "60-30-30",
    duration: "150-180 days",
    yield: "2-3 tons/hectare",
    diseases: ["Wilt", "Boll rot", "Leaf curl"],
    tips: ["Maintain 90x60cm spacing", "Regular pest monitoring", "Pick cotton when bolls fully open"]
  }
};
function CropInfo() {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState('rice');
  const { t } = useLanguage();
  const crop = cropData[selectedCrop];
  const openModal = (cropKey) => {
    setSelectedCrop(cropKey);
    setIsOpen(true);
  };
  return (
    <>
      {!isOpen && (
        <button className="crop-info-toggle" onClick={() => setIsOpen(true)} title="Crop Information">
          🌱
        </button>
      )}
      {isOpen && (
        <div className="crop-info-modal">
          <div className="modal-header-crop">
            🌱 {t('cropInfoGuide')}
            <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
          </div>
          <div className="modal-content-crop">
            <div className="crop-selector">
              {Object.keys(cropData).map(key => (
                <button
                  key={key}
                  className={selectedCrop === key ? 'active' : ''}
                  onClick={() => setSelectedCrop(key)}
                >
                  <img src={cropData[key].image} alt={cropData[key].name} className="crop-thumb" />
                  {cropData[key].name}
                </button>
              ))}
            </div>
            <div className="crop-details">
              <div className="crop-header">
                <img src={crop.image} alt={crop.name} className="crop-main-image" />
                <h3>{crop.name}</h3>
              </div>
              <div className="info-grid">
                <div className="info-card">
                  <span className="icon">📅</span>
                  <div>
                    <strong>{t('season')}</strong>
                    <p>{crop.season}</p>
                  </div>
                </div>
                <div className="info-card">
                  <span className="icon">🌡️</span>
                  <div>
                    <strong>{t('temperature')}</strong>
                    <p>{crop.temperature}</p>
                  </div>
                </div>
                <div className="info-card">
                  <span className="icon">💧</span>
                  <div>
                    <strong>{t('rainfall')}</strong>
                    <p>{crop.rainfall}</p>
                  </div>
                </div>
                <div className="info-card">
                  <span className="icon">🌍</span>
                  <div>
                    <strong>{t('soilType')}</strong>
                    <p>{crop.soil}</p>
                  </div>
                </div>
                <div className="info-card">
                  <span className="icon">🧪</span>
                  <div>
                    <strong>{t('npkRatio')}</strong>
                    <p>{crop.npk}</p>
                  </div>
                </div>
                <div className="info-card">
                  <span className="icon">⏱️</span>
                  <div>
                    <strong>{t('duration')}</strong>
                    <p>{crop.duration}</p>
                  </div>
                </div>
                <div className="info-card">
                  <span className="icon">📊</span>
                  <div>
                    <strong>{t('expectedYield')}</strong>
                    <p>{crop.yield}</p>
                  </div>
                </div>
              </div>
              <div className="diseases-section">
                <h4>🦠 {t('commonDiseases')}</h4>
                <div className="disease-tags">
                  {crop.diseases.map((disease, idx) => (
                    <span key={idx} className="disease-tag">{disease}</span>
                  ))}
                </div>
              </div>
              <div className="tips-section">
                <h4>💡 {t('farmingTips')}</h4>
                <ul>
                  {crop.tips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
export default CropInfo;