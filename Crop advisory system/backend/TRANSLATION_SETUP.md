# Translation Service Setup

## Installation

Install the required package for enhanced translation:

```bash
pip install googletrans==4.0.0-rc1
```

## Features

1. **Google Translate API Integration**
   - Accurate translation for full sentences
   - Supports English, Telugu, Hindi, and Tamil

2. **Agricultural Term Dictionary**
   - 50+ agricultural terms with accurate translations
   - Crops: rice, wheat, maize, cotton, sugarcane, etc.
   - Nutrients: nitrogen, phosphorus, potassium
   - Farming terms: soil, irrigation, fertilizer, pest, disease

3. **Fallback System**
   - If Google Translate fails, uses dictionary-based translation
   - Ensures translation always works

## Usage

The translation service is automatically used by the `/api/translate` endpoint.

### Example Request:

```json
POST /api/translate
{
  "text": "Rice cultivation requires proper irrigation and fertilizer",
  "from": "en",
  "to": "te"
}
```

### Example Response:

```json
{
  "original_text": "Rice cultivation requires proper irrigation and fertilizer",
  "translated_text": "వరి సాగుకు సరైన నీటిపారుదల మరియు ఎరువు అవసరం",
  "from_language": "en",
  "to_language": "te"
}
```

## Supported Languages

- `en` - English
- `te` - Telugu
- `hi` - Hindi
- `ta` - Tamil

## Agricultural Terms Covered

- All major crops (rice, wheat, maize, cotton, sugarcane, pulses, fruits)
- Soil nutrients (NPK)
- Farming operations (sowing, planting, irrigation, harvest)
- Agricultural inputs (fertilizer, pesticide, herbicide)
- Weather terms (temperature, humidity, rainfall)
- Analysis terms (prediction, recommendation, yield)
