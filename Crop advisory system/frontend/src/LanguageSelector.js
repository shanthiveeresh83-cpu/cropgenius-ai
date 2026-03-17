import React from 'react';
import { useLanguage } from './LanguageContext';
import './LanguageSelector.css';
function LanguageSelector() {
  const { language, setLanguage } = useLanguage();
  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
    { code: 'te', name: 'తెలుగు', flag: '🇮🇳' },
    { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' }
  ];
  return (
    <div className="language-selector">
      <span className="lang-icon">🌐</span>
      <select 
        value={language} 
        onChange={(e) => setLanguage(e.target.value)}
        className="lang-dropdown"
      >
        {languages.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}
export default LanguageSelector;