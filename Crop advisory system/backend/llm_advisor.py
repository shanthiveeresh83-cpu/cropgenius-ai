import os
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class FarmingLLM:

    def __init__(self, provider='groq'):
        self.provider = provider
        self.client = None

        if provider == 'openai' and OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.model = 'gpt-3.5-turbo'

        elif provider == 'groq' and GROQ_AVAILABLE:
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                self.client = Groq(api_key=api_key)
                self.model = 'llama-3.1-8b-instant'  # Free fast model

        if not self.client:
            print(f"⚠️ LLM not configured. Using fallback system.")
            self.provider = 'fallback'

    def get_farming_advice(self, crop, soil_data, weather_data, language='en'):

        if self.provider == 'fallback':
            return self._fallback_advice(crop, soil_data, language)

        prompt = self._build_prompt(crop, soil_data, weather_data, language)

        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert agricultural advisor helping farmers."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                return response.choices[0].message.content

            elif self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert agricultural advisor helping farmers."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                return response.choices[0].message.content

        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_advice(crop, soil_data, language)

    def explain_fertilizer(self, npk_values, crop, language='en'):

        if self.provider == 'fallback':
            return self._fallback_fertilizer_explanation(npk_values, crop, language)

        prompt = f"""Explain in simple {language} language why {crop} needs:
- Nitrogen (N): {npk_values['N']}
- Phosphorus (P): {npk_values['P']}
- Potassium (K): {npk_values['K']}

Keep it under 100 words and farmer-friendly."""

        try:
            if self.provider in ['openai', 'groq']:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a farming expert explaining to farmers."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content
        except:
            pass

        return self._fallback_fertilizer_explanation(npk_values, crop, language)

    def answer_question(self, question, context, language='en'):

        if self.provider == 'fallback':
            return self._fallback_answer(question, language)

        prompt = f"""Context: {json.dumps(context)}
Question: {question}
Language: {language}

Provide a helpful answer in {language} for a farmer."""

        try:
            if self.provider in ['openai', 'groq']:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful farming assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content
        except:
            pass

        return self._fallback_answer(question, language)

    def _build_prompt(self, crop, soil_data, weather_data, language):
        return f"""As an agricultural expert, provide farming advice for:

Crop: {crop}
Soil: N={soil_data.get('N')}, P={soil_data.get('P')}, K={soil_data.get('K')}, pH={soil_data.get('ph')}
Weather: Temp={weather_data.get('temperature')}°C, Humidity={weather_data.get('humidity')}%, Rainfall={weather_data.get('rainfall')}mm

Provide advice in {language} on:
1. Best practices for this crop
2. Fertilizer timing
3. Irrigation schedule
4. Pest prevention

Keep it concise and practical."""

    def _fallback_advice(self, crop, soil_data, language='en'):
        advice = {
            'en': f"For {crop}: Apply balanced NPK fertilizer. Water regularly based on soil moisture. Monitor for pests weekly. Harvest at proper maturity.",
            'hi': f"{crop} के लिए: संतुलित NPK उर्वरक डालें। मिट्टी की नमी के अनुसार पानी दें। साप्ताहिक कीट निगरानी करें।",
            'te': f"{crop} కోసం: సమతుల్య NPK ఎరువులు వేయండి. నేల తేమ ఆధారంగా నీరు పెట్టండి. వారానికి తెగుళ్ల పర్యవేక్షణ చేయండి.",
            'ta': f"{crop} க்கு: சமநிலையான NPK உரம் இடுங்கள். மண் ஈரப்பதத்தின் அடிப்படையில் தண்ணீர் பாய்ச்சுங்கள்."
        }
        return advice.get(language, advice['en'])

    def _fallback_fertilizer_explanation(self, npk, crop, language='en'):
        explanations = {
            'en': f"{crop} needs Nitrogen for leaf growth, Phosphorus for strong roots, and Potassium for disease resistance. Your soil has N={npk['N']}, P={npk['P']}, K={npk['K']}.",
            'hi': f"{crop} को पत्ती वृद्धि के लिए नाइट्रोजन, मजबूत जड़ों के लिए फास्फोरस, और रोग प्रतिरोध के लिए पोटेशियम चाहिए।",
            'te': f"{crop}కు ఆకు పెరుగుదలకు నత్రజని, బలమైన వేర్లకు భాస్వరం, వ్యాధి నిరోధకతకు పొటాషియం అవసరం.",
            'ta': f"{crop}க்கு இலை வளர்ச்சிக்கு நைட்ரஜன், வலுவான வேர்களுக்கு பாஸ்பரஸ், நோய் எதிர்ப்புக்கு பொட்டாசியம் தேவை."
        }
        return explanations.get(language, explanations['en'])

    def _fallback_answer(self, question, language='en'):
        q = question.lower()

        if 'water' in q or 'irrigation' in q:
            return "Water crops early morning or evening. Check soil moisture before watering. Avoid overwatering."
        elif 'fertilizer' in q or 'npk' in q:
            return "NPK fertilizer provides Nitrogen (leaf growth), Phosphorus (roots), Potassium (disease resistance). Apply based on soil test."
        elif 'pest' in q or 'disease' in q:
            return "Monitor crops regularly. Use neem oil for organic pest control. Remove infected plants immediately."
        else:
            return "For specific advice, consult local agricultural extension office or use our analysis tool."

def get_llm_instance():

    if os.getenv('GROQ_API_KEY'):
        return FarmingLLM(provider='groq')
    elif os.getenv('OPENAI_API_KEY'):
        return FarmingLLM(provider='openai')
    else:
        return FarmingLLM(provider='fallback')