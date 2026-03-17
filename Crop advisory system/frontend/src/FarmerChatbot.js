import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useLanguage } from "./LanguageContext";
import { chatbotTranslations } from "./chatbotTranslations";
import "./FarmerChatbot.css";
function FarmerChatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const { language, setLanguage } = useLanguage();
  const [recognition, setRecognition] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const t = (key) => chatbotTranslations[language]?.[key] || chatbotTranslations.en[key];

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧', short: 'EN' },
    { code: 'hi', name: 'हिंदी', flag: '🇮🇳', short: 'HI' },
    { code: 'te', name: 'తెలుగు', flag: '🇮🇳', short: 'TE' },
    { code: 'ta', name: 'தமிழ்', flag: '🇮🇳', short: 'TA' }
  ];

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadChatHistory();
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && messages.length > 0) {
      const welcomeMsg = messages.find(m => m.type === 'welcome');
      if (welcomeMsg) {
        setMessages(prev => prev.map(m => 
          m.type === 'welcome' ? { ...m, text: getWelcomeMessage() } : m
        ));
      }
    }
  }, [language]);

  const loadChatHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const response = await axios.get(
          'http://localhost:5000/api/chat-history',
          { 
            headers: { Authorization: `Bearer ${token}` },
            params: { language: localStorage.getItem('language') || 'en' }
          }
        );
        if (response.data.history && response.data.history.length > 0) {
          setMessages(response.data.history);
        } else {
          const welcomeMsg = {
            text: getWelcomeMessage(),
            sender: "bot",
            type: "welcome"
          };
          setMessages([welcomeMsg]);
        }
      } else {
        const welcomeMsg = {
          text: getWelcomeMessage(),
          sender: "bot",
          type: "welcome"
        };
        setMessages([welcomeMsg]);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
      const welcomeMsg = {
        text: getWelcomeMessage(),
        sender: "bot",
        type: "welcome"
      };
      setMessages([welcomeMsg]);
    }
  };
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      const langMap = { en: 'en-US', hi: 'hi-IN', te: 'te-IN', ta: 'ta-IN' };
      recognitionInstance.lang = langMap[language] || 'en-US';
      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };
      recognitionInstance.onerror = () => {
        setIsListening(false);
      };
      recognitionInstance.onend = () => {
        setIsListening(false);
      };
      setRecognition(recognitionInstance);
    }
  }, [language]);
  const getWelcomeMessage = () => {
    const messages = {
      en: "Welcome! I'm your Smart Farm Assistant. I can help you with:\n\nCrop information and recommendations\nUpload crop photos for identification\nTranslate information to your language\nIrrigation and fertilizer advice\n\nHow can I help you today?",
      hi: "नमस्ते! मैं आपका स्मार्ट फार्म सहायक हूं। मैं आपकी मदद कर सकता हूं:\n\nफसल की जानकारी और सिफारिशें\nफसल की फोटो अपलोड करें\nअपनी भाषा में जानकारी का अनुवाद करें\nसिंचाई और उर्वरक सलाह\n\nआज मैं आपकी कैसे मदद कर सकता हूं?",
      te: "నమస్కరం! నేను మీ smart farm assistant. నేను మీకు సహాయం చేయగలు:\n\nపంటలు & సిఫార్సులు\nపంట ఫోటోలను అప్లోడ్ చేయండి\nమీ భాషలోకి translate చేయండి\nనీటిపారుదల & ఎరువు సలహ\n\nనేను ఈరోజు మీకు ఎలా సహాయం చేయగలను?",
      ta: "வணக்கம்! நான் உங்கள் Smart Farm Assistant. நான் உங்களுக்கு உதவ முடியும்:\n\nபயிர் தகவல் மற்றும் பரிந்துரைகள்\nபயிர் புகைப்படங்களை பதிவேற்றவும்\nஉங்கள் மொழியில் மொழிபெயர்க்கவும்\nபாசனம் மற்றும் உர ஆலோசனை\n\nஇன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?"
    };
    return messages[language] || messages.en;
  };
  const startListening = () => {
    if (recognition) {
      setIsListening(true);
      recognition.start();
    }
  };
  const speak = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      const langMap = { en: 'en-US', hi: 'hi-IN', te: 'te-IN', ta: 'ta-IN' };
      utterance.lang = langMap[language] || 'en-US';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };
  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };
  const uploadImage = async () => {
    if (!selectedImage) return;
    setIsUploading(true);
    const reader = new FileReader();
    reader.onloadend = async () => {
      try {
        const token = localStorage.getItem("token");
        const currentLanguage = localStorage.getItem("language") || "en";
        const userMsg = { 
          text: t('uploadedImage'), 
          sender: "user",
          image: imagePreview
        };
        setMessages(prev => [...prev, userMsg]);
        setShowImageUpload(false);
        const loadingMsg = { 
          text: t('analyzingImage'), 
          sender: "bot",
          type: "loading"
        };
        setMessages(prev => [...prev, loadingMsg]);
        const response = await axios.post(
          "http://localhost:5000/api/analyze-crop",
          { image: reader.result, language: currentLanguage },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setMessages(prev => prev.filter(m => m.type !== 'loading'));
        const result = response.data;
        if (result.error) {
          const errorMsg = { 
            text: result.error, 
            sender: "bot" 
          };
          setMessages(prev => [...prev, errorMsg]);
          return;
        }
        const analysisText = `CROP ANALYSIS RESULTS\n\nDetected Crop: ${result.detected_crop}\nConfidence Level: ${result.confidence}%\n\nFERTILIZER RECOMMENDATION:\n${result.fertilizer}\n\nIRRIGATION GUIDELINES:\n${result.irrigation}\n\nBEST GROWING SEASON:\n${result.season}\n\nEXPERT ADVICE:\n${result.advice}`;
        const botMsg = { 
          text: analysisText, 
          sender: "bot",
          type: "crop-analysis",
          data: result
        };
        setMessages(prev => [...prev, botMsg]);
        speak(`Detected ${result.detected_crop} with ${result.confidence} percent confidence`);
      } catch (error) {
        setMessages(prev => prev.filter(m => m.type !== 'loading'));
        const errorText = error.response?.data?.error || error.response?.data?.message || t('imageAnalysisError');
        const errorMsg = { 
          text: errorText, 
          sender: "bot" 
        };
        setMessages(prev => [...prev, errorMsg]);
      }
      setIsUploading(false);
      setSelectedImage(null);
      setImagePreview(null);
    };
    reader.readAsDataURL(selectedImage);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = { text: input, sender: "user" };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    const userInput = input;
    setInput("");
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        const errorMessage = { text: t('loginRequired'), sender: "bot" };
        setMessages([...newMessages, errorMessage]);
        return;
      }
      const response = await axios.post(
        "http://localhost:5000/api/rag-chat",
        { question: userInput, language: localStorage.getItem("language") || "en" },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const botMessage = { 
        text: response.data.answer, 
        sender: "bot",
        sources: response.data.sources,
        method: response.data.method
      };
      setMessages([...newMessages, botMessage]);
      speak(response.data.answer);
    } catch (error) {
      let errorText = t('errorConnecting');
      if (error.response) {
        if (error.response.status === 401) {
          errorText = t('sessionExpired');
          localStorage.removeItem("token");
        } else if (error.response.status === 404) {
          errorText = t('serviceNotFound');
        } else {
          errorText = `${t('serverError')}: ${error.response.status}`;
        }
      } else if (error.request) {
        errorText = t('cannotReachServer');
      } else {
        errorText = t('requestError');
      }
      const errorMessage = { text: errorText, sender: "bot" };
      setMessages([...newMessages, errorMessage]);
    }
  };
  const clearChat = async () => {
    if (window.confirm(t('clearConfirm'))) {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          await axios.delete(
            'http://localhost:5000/api/chat-history',
            { headers: { Authorization: `Bearer ${token}` } }
          );
        }
      } catch (error) {
        console.error('Failed to clear history from database:', error);
      }
      setMessages([]);
      const welcomeMsg = {
        text: getWelcomeMessage(),
        sender: "bot",
        type: "welcome"
      };
      setMessages([welcomeMsg]);
    }
  };
  return (
    <>
      {!isOpen && (
        <button className="chat-toggle" onClick={() => setIsOpen(true)}>
          💬
        </button>
      )}
      {isOpen && (
        <div className="chatbot farmer-chatbot">
          <div className="chat-header">
            <span>{t('title')}</span>
            <div className="header-actions">
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                className="lang-select-chatbot"
                title={t('language')}
              >
                {languages.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.flag} {lang.short}
                  </option>
                ))}
              </select>
              <button 
                className="header-btn" 
                onClick={clearChat}
                title={t('clear')}
              >
                {t('clear')}
              </button>
              <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
            </div>
          </div>
          <div className="chat-toolbar">
            <button 
              className={`toolbar-btn ${showImageUpload ? 'active' : ''}`}
              onClick={() => setShowImageUpload(!showImageUpload)}
              title={t('uploadPhoto')}
            >
              📷 {t('photo')}
            </button>
            <button 
              className="toolbar-btn voice-btn"
              onClick={startListening}
              disabled={isListening}
              title={t('voice')}
            >
              {isListening ? t('listening') : t('voice')}
            </button>
          </div>
          {showImageUpload && (
            <div className="chat-panel image-panel">
              <h4>{t('uploadPhoto')}</h4>
              <p className="panel-hint">{t('uploadHint')}</p>
              <div className="image-upload-area">
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleImageSelect}
                  ref={fileInputRef}
                  id="chat-file-input"
                />
                <label htmlFor="chat-file-input" className="upload-label">
                  {imagePreview ? t('changePhoto') : t('takePhoto')}
                </label>
              </div>
              {imagePreview && (
                <div className="image-preview-container">
                  <img src={imagePreview} alt="Preview" className="image-preview" />
                  <button 
                    onClick={uploadImage} 
                    disabled={isUploading}
                    className="analyze-btn"
                  >
                    {isUploading ? t('analyzing') : t('analyzeCrop')}
                  </button>
                </div>
              )}
            </div>
          )}

          <div className="chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.sender} ${msg.type || ''}`}>
                {msg.image && (
                  <div className="message-image">
                    <img src={msg.image} alt="Uploaded crop" />
                  </div>
                )}
                <div className="message-text">{msg.text}</div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="message-sources">
                    <div className="sources-label">{t('sources')}</div>
                    {msg.sources.map((source, i) => (
                      <div key={i} className="source-tag">{source.topic}</div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={sendMessage} className="chat-input">
            <button 
              type="button" 
              onClick={startListening} 
              disabled={isListening}
              className="voice-btn"
              title={t('voice')}
            >
              {isListening ? t('listening') : t('voice')}
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t('askAboutCrops')}
            />
            <button type="submit">{t('send')}</button>
          </form>
        </div>
      )}
    </>
  );
}
export default FarmerChatbot;
