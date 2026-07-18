# 🌾 Crop Genius AI — Smart Farm Advisory System

An AI-powered crop advisory platform that helps farmers make data-driven decisions through disease detection, intelligent recommendations, and real-time analysis.

---

## Features

- **CNN-Based Disease Detection** — Upload a crop/leaf image to identify diseases and get treatment & prevention advice
- **LLM Intelligent Advisor** — Ask farming questions in plain language; get crop-specific, actionable answers
- **Crop Recommendation** — Predicts the best crop based on soil nutrients, pH, and climate
- **Fertilizer Recommendation** — Suggests optimal fertilizer based on soil and crop type
- **Yield Prediction** — Estimates expected yield using historical and environmental data
- **Weather Analysis** — Integrates real-time weather data for suitability checks
- **Market Price Prediction** — Forecasts crop prices to help plan harvests
- **Soil Health Analysis** — Evaluates soil condition and recommends improvements
- **Multi-language Support** — English, Hindi, Telugu, Tamil
- **User Authentication** — JWT-based login and registration

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router, Chart.js, Axios |
| Backend | Python, Flask, Flask-JWT-Extended |
| ML / AI | scikit-learn, OpenCV, Pillow, TensorFlow (optional) |
| Database | SQLite |
| Deployment | Gunicorn |

---

## Project Structure

```
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── disease_detection.py    # Image-based disease detector
│   ├── llm_advisor.py          # Rule-based / LLM advisor
│   ├── advanced_cnn.py         # CNN architecture (MobileNetV2 / ResNet50)
│   ├── crop_data.csv           # Training dataset
│   ├── train_model.py          # Model training scripts
│   ├── REQUIREMENTS.txt        # Python dependencies
│   └── .env.example            # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── pages/              # Login, Dashboard, Analysis, History
│   │   ├── components/         # Navbar
│   │   ├── FarmerChatbot.js    # AI chatbot UI
│   │   ├── ImageUpload.js      # Disease detection UI
│   │   └── App.js
│   └── package.json
├── AI_ARCHITECTURE.md
├── AI_FEATURES_GUIDE.md
├── AWS_ARCHITECTURE_GUIDE.md
└── QUICK_START.md
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm

### Backend Setup

```bash
cd backend
pip install -r REQUIREMENTS.txt
cp .env.example .env   # fill in your values
python app.py
```

The API will be available at `http://127.0.0.1:5000`.

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000`.

---

## Environment Variables

Create `backend/.env` based on `.env.example`:

```env
SECRET_KEY=<your_secret_key>
JWT_SECRET_KEY=<your_jwt_secret>
WEATHER_API_KEY=<openweathermap_api_key>
GROQ_API_KEY=<groq_api_key>          # optional — for LLM upgrade
```

---

## Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | User registration |
| POST | `/api/login` | User login |
| POST | `/api/predict` | Crop recommendation |
| POST | `/api/detect-disease` | Disease detection from image |
| POST | `/api/llm-advice` | AI farming advice |
| POST | `/api/ask-question` | Ask the AI advisor |
| POST | `/api/comprehensive-analysis` | Full soil + weather + AI analysis |
| GET | `/api/weather` | Current weather data |

---

## Disease Detection

Supports detection of the following rice/crop diseases:

- Bacterial Blight
- Brown Spot
- Leaf Blast
- Tungro
- Bacterial Leaf Streak
- Sheath Blight
- Healthy (no disease)

Works out-of-the-box with a color-analysis fallback — no TensorFlow required. Optionally upgrade to MobileNetV2 or ResNet50 for higher accuracy.

---

## Screenshots

> _Add screenshots of the dashboard, disease detection, and chatbot pages here._

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request

---

## License

This project is licensed under the MIT License.
