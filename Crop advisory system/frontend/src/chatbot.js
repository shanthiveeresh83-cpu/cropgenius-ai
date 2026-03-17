import React, { useState, useEffect } from "react";
import axios from "axios";
import { useLanguage } from "./LanguageContext";
import "./Chatbot.css";
function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const { t, language } = useLanguage();
  const [recognition, setRecognition] = useState(null);
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
  const startListening = () => {
    if (recognition) {
      setIsListening(true);
      recognition.start();
    }
  };
  const speak = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      const langMap = { en: 'en-US', hi: 'hi-IN', te: 'te-IN', ta: 'ta-IN' };
      utterance.lang = langMap[language] || 'en-US';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = { text: input, sender: "user" };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        const errorMessage = { text: "Please login to use the chatbot", sender: "bot" };
        setMessages([...newMessages, errorMessage]);
        return;
      }
      const response = await axios.post(
        "http://localhost:5000
        { message: input, language: localStorage.getItem("language") || "en" },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const botMessage = { text: response.data.response, sender: "bot" };
      setMessages([...newMessages, botMessage]);
      speak(response.data.response);
    } catch (error) {
      let errorText = "Error connecting to chatbot";
      if (error.response) {
        if (error.response.status === 401) {
          errorText = "Session expired. Please login again.";
          localStorage.removeItem("token");
        } else if (error.response.status === 404) {
          errorText = "Chat service not found. Please restart the backend.";
        } else {
          errorText = `Server error: ${error.response.status}`;
        }
      } else if (error.request) {
        errorText = "Cannot reach server. Is the backend running on port 5000?";
      } else {
        errorText = "Error setting up request. Please try again.";
      }
      const errorMessage = { text: errorText, sender: "bot" };
      setMessages([...newMessages, errorMessage]);
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
        <div className="chatbot">
          <div className="chat-header">
            🌾 {t('chatAssistant')}
            <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
          </div>
          <div className="chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.sender}`}>
                {msg.text}
              </div>
            ))}
          </div>
          <form onSubmit={sendMessage} className="chat-input">
            <button 
              type="button" 
              onClick={startListening} 
              disabled={isListening}
              className="voice-btn"
              title="Voice Input"
            >
              {isListening ? '🎤' : '🎙️'}
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t('askAboutCrops')}
            />
            <button type="submit">➤</button>
          </form>
        </div>
      )}
    </>
  );
}
export default Chatbot;