# 🤖 AI Features Setup Guide

## Overview

Your Smart Farm Assistant now includes:
1. **CNN Disease Detection** - Detect crop diseases from leaf images
2. **LLM Intelligent Advisor** - Get AI-powered farming advice
3. **Weather + Smart Recommendations** - Combined analysis

---

## 🔧 Installation

### Option 1: Basic Setup (No External APIs)
```bash
cd backend
pip install pillow numpy
```
This uses fallback systems - works offline!

### Option 2: CNN with TensorFlow
```bash
pip install tensorflow pillow numpy
```
Enables MobileNetV2 disease detection

### Option 3: LLM with Groq (FREE)
```bash
pip install groq
```
Get free API key: https://console.groq.com

### Option 4: LLM with OpenAI
```bash
pip install openai
```
Requires OpenAI API key (paid)

---

## 🔑 API Keys Setup

Create `.env` file in `backend/` folder:

```env
# Optional: For LLM features
GROQ_API_KEY=your_groq_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Existing keys
JWT_SECRET_KEY=supersecretkey
OPENWEATHERMAP_API_KEY=your_weather_key
```

---

## 🚀 API Endpoints

### 1. Disease Detection
```http
POST /api/detect-disease
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "disease": "blight",
  "confidence": 85.5,
  "status": "Blight Detected",
  "severity": "High",
  "treatment": "Apply copper-based fungicide immediately",
  "prevention": "Remove infected leaves, improve air circulation"
}
```

### 2. LLM Farming Advice
```http
POST /api/llm-advice
Content-Type: application/json

{
  "crop": "rice",
  "soil_data": {"N": 80, "P": 40, "K": 50, "ph": 6.5},
  "weather_data": {"temperature": 28, "humidity": 75, "rainfall": 200},
  "language": "en"
}
```

**Response:**
```json
{
  "advice": "For rice cultivation: Apply nitrogen in split doses...",
  "provider": "groq",
  "crop": "rice"
}
```

### 3. Explain Fertilizer (Simple Language)
```http
POST /api/explain-fertilizer
Content-Type: application/json

{
  "npk": {"N": 80, "P": 40, "K": 50},
  "crop": "rice",
  "language": "en"
}
```

### 4. Ask Questions
```http
POST /api/ask-question
Content-Type: application/json

{
  "question": "When should I water my rice crop?",
  "context": {"crop": "rice", "season": "kharif"},
  "language": "en"
}
```

---

## 🎯 Features

### CNN Disease Detection
- **Model**: MobileNetV2 (pretrained on ImageNet)
- **Diseases**: Blight, Rust, Leaf Spot, Wilt, Healthy
- **Fallback**: Color-based analysis if TensorFlow unavailable
- **Languages**: All 4 languages supported

### LLM Advisor
- **Providers**: Groq (free), OpenAI (paid), Fallback (rule-based)
- **Features**:
  - Intelligent farming advice
  - Fertilizer explanations in simple language
  - Question answering
  - Multi-language support (en, hi, te, ta)

### Smart Recommendations
- Combines weather data + soil analysis + LLM reasoning
- Provides actionable insights
- Considers local conditions

---

## 📊 System Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask Backend  │
│  ┌───────────┐  │
│  │ CNN Model │  │ ◄── Disease Detection
│  └───────────┘  │
│  ┌───────────┐  │
│  │    LLM    │  │ ◄── Intelligent Advice
│  └───────────┘  │
│  ┌───────────┐  │
│  │  Weather  │  │ ◄── Smart Recommendations
│  └───────────┘  │
└─────────────────┘
```

---

## 🧪 Testing

### Test Disease Detection
```python
import requests
import base64

with open('leaf_image.jpg', 'rb') as f:
    img_data = base64.b64encode(f.read()).decode()

response = requests.post('http://127.0.0.1:5000/api/detect-disease', json={
    'image': f'data:image/jpeg;base64,{img_data}'
})

print(response.json())
```

### Test LLM Advice
```python
import requests

response = requests.post('http://127.0.0.1:5000/api/llm-advice', json={
    'crop': 'wheat',
    'soil_data': {'N': 60, 'P': 35, 'K': 40, 'ph': 7.0},
    'weather_data': {'temperature': 22, 'humidity': 65, 'rainfall': 50},
    'language': 'en'
})

print(response.json())
```

---

## 🎓 For Project Presentation

### Highlight These Points:

1. **AI-Powered System**
   - CNN for disease detection (Deep Learning)
   - LLM for intelligent advice (NLP)
   - Multi-modal AI integration

2. **Practical Implementation**
   - Pretrained models (efficient)
   - Fallback systems (reliable)
   - Multi-language support (accessible)

3. **Real-World Impact**
   - Helps farmers detect diseases early
   - Provides expert advice in local language
   - Combines multiple data sources

4. **Technical Excellence**
   - Modern tech stack (TensorFlow, LLM APIs)
   - RESTful API design
   - Scalable architecture

---

## 📈 Future Enhancements

- [ ] Train custom CNN on crop disease dataset
- [ ] Add more disease categories
- [ ] Integrate AWS Rekognition
- [ ] Add voice input/output
- [ ] Real-time monitoring dashboard
- [ ] Mobile app integration

---

## 🐛 Troubleshooting

### TensorFlow Installation Issues
```bash
# Use CPU-only version
pip install tensorflow-cpu
```

### LLM Not Working
- Check API key in `.env`
- System will use fallback automatically
- Check console for error messages

### Disease Detection Errors
- Ensure image is base64 encoded
- Check image format (JPEG/PNG)
- Verify image size < 5MB

---

## 📚 Resources

- **TensorFlow**: https://tensorflow.org
- **Groq API**: https://console.groq.com
- **OpenAI API**: https://platform.openai.com
- **MobileNetV2**: https://arxiv.org/abs/1801.04381

---

## ✅ Verification Checklist

- [ ] Backend starts without errors
- [ ] Disease detection endpoint responds
- [ ] LLM advice endpoint works (or fallback)
- [ ] All 4 languages supported
- [ ] Error handling works properly
- [ ] Frontend can call new endpoints

---

**Your project is now an AI-Powered Intelligent Agriculture Decision System! 🚀**
