import os
import json
from typing import List, Dict

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class AgriKnowledgeBase:

    def __init__(self):
        self.documents = self._load_knowledge()
        self.embeddings = None
        self.index = None

        if FAISS_AVAILABLE:
            self._build_index()

    def _load_knowledge(self) -> List[Dict]:
        return [
            {
                "id": "rice_001",
                "topic": "Rice Cultivation Complete Guide",
                "content": "Rice cultivation requires flooded fields with 80-85% humidity and temperatures 20-27°C. Plant during monsoon (June-July). Apply nitrogen 80-100 kg/ha in 3 split doses: 50% at planting, 25% at tillering, 25% at panicle initiation. Phosphorus 40-50 kg/ha and Potassium 40-50 kg/ha at planting. Maintain 5-10cm water depth. Harvest after 120-150 days when 80% grains turn golden. Expected yield: 4-6 tons/hectare. Common diseases: Blast, Blight, Sheath rot. Use resistant varieties like Swarna, IR64, Basmati.",
                "keywords": ["rice", "paddy", "cultivation", "monsoon", "nitrogen", "kharif", "water", "flooded"]
            },
            {
                "id": "wheat_001",
                "topic": "Wheat Farming Complete Guide",
                "content": "Wheat grows best in Rabi season (November-December). Requires 12-25°C temperature, well-drained loamy soil, pH 6.0-7.5. Apply nitrogen 120 kg/ha in 3 splits: 50% at sowing, 25% at first irrigation (21 days), 25% at second irrigation (40 days). Phosphorus 60 kg/ha and Potassium 40 kg/ha at sowing. Irrigate at crown root initiation (21 days), tillering (40 days), jointing (60 days), flowering (80 days), milk stage (100 days), dough stage (115 days). Harvest after 120-140 days. Expected yield: 4-5 tons/hectare. Varieties: HD2967, PBW343, DBW17.",
                "keywords": ["wheat", "rabi", "irrigation", "temperature", "winter", "gehu"]
            },
            {
                "id": "maize_001",
                "topic": "Maize Cultivation Detailed",
                "content": "Maize requires 21-27°C temperature, 65-75% humidity. Plant in Kharif (June-July) or Rabi (October-November). Spacing: 60cm x 20cm. Apply nitrogen 120 kg/ha (40% basal, 30% at knee-high, 30% at tasseling), Phosphorus 60 kg/ha, Potassium 40 kg/ha. Irrigate at knee-high stage, tasseling, silking, grain filling. Harvest at 20-25% moisture. Expected yield: 5-7 tons/hectare. Protect from Fall Armyworm, stem borer. Varieties: DHM117, Shaktiman, Pioneer hybrids.",
                "keywords": ["maize", "corn", "kharif", "rabi", "hybrid", "makka"]
            },
            {
                "id": "fert_001",
                "topic": "NPK Fertilizers Complete Guide",
                "content": "NPK fertilizers: Nitrogen (N) promotes vegetative growth, leaf development, chlorophyll formation. Deficiency: yellowing leaves. Sources: Urea (46% N), Ammonium Sulfate (21% N). Phosphorus (P) strengthens roots, promotes flowering, seed formation. Deficiency: purple leaves, stunted growth. Sources: DAP (46% P2O5), SSP (16% P2O5). Potassium (K) improves disease resistance, water regulation, fruit quality. Deficiency: leaf margin burning. Sources: MOP (60% K2O), SOP (50% K2O). Apply based on soil test. Split nitrogen application prevents leaching. Apply phosphorus and potassium as basal dose.",
                "keywords": ["npk", "fertilizer", "nitrogen", "phosphorus", "potassium", "urea", "dap"]
            },
            {
                "id": "pest_001",
                "topic": "Integrated Pest Management",
                "content": "IPM strategy: 1) Cultural control: Crop rotation, resistant varieties, proper spacing, field sanitation. 2) Biological control: Neem oil 5ml/liter, Trichoderma 5g/kg seed, Pseudomonas 10g/liter. 3) Mechanical control: Pheromone traps, light traps, hand picking. 4) Chemical control (last resort): Chlorpyrifos for stem borer, Imidacloprid for aphids, Mancozeb for fungal diseases. Monitor weekly. Economic threshold: 5% damage. Remove infected plants immediately. Spray early morning or evening. Rotate pesticides to prevent resistance.",
                "keywords": ["pest", "disease", "neem", "ipm", "control", "insect", "fungus"]
            },
            {
                "id": "water_001",
                "topic": "Irrigation Management",
                "content": "Drip irrigation: Saves 40-60% water, increases yield 20-30%, reduces disease. Installation cost: Rs 50,000-80,000/acre. Sprinkler irrigation: Suitable for vegetables, saves 30-40% water. Flood irrigation: Traditional for rice, requires 1200-1500mm water. Critical irrigation stages: Flowering, grain filling, fruit development. Check soil moisture: Insert finger 6 inches deep, if dry irrigate. Water early morning (6-8 AM) or evening (4-6 PM). Avoid midday watering. Mulching reduces water loss by 50%. Rainwater harvesting: Build farm ponds.",
                "keywords": ["irrigation", "water", "drip", "sprinkler", "moisture", "pani"]
            },
            {
                "id": "soil_001",
                "topic": "Soil Health Management",
                "content": "Healthy soil pH: 6.0-7.5 for most crops. Test soil every 2-3 years (cost: Rs 200-500). Add organic matter: FYM 10 tons/hectare, Vermicompost 5 tons/hectare, Green manure (Dhaincha, Sunhemp). Crop rotation: Rice-Wheat-Legume prevents nutrient depletion. Avoid excessive chemical fertilizers: causes soil acidification. Add lime 2 tons/hectare for acidic soil (pH<6). Add gypsum 2 tons/hectare for alkaline soil (pH>8). Maintain soil structure: Avoid over-tillage. Deep plowing once a year. Mulching with crop residue improves soil organic carbon.",
                "keywords": ["soil", "ph", "organic", "health", "rotation", "compost", "mitti"]
            },
            {
                "id": "disease_001",
                "topic": "Crop Disease Management",
                "content": "Bacterial Blight: Water-soaked lesions, yellowing. Control: Copper oxychloride 3g/liter, remove infected parts, use resistant varieties. Brown Spot: Circular brown spots. Control: Mancozeb 2g/liter, balanced fertilization. Leaf Blast: Diamond-shaped lesions. Control: Tricyclazole 0.6g/liter, avoid excess nitrogen. Rust: Orange pustules. Control: Sulfur spray 3g/liter. Wilt: Drooping, yellowing. Control: Carbendazim 1g/liter soil drench. Prevention: Seed treatment, crop rotation, proper drainage, resistant varieties, balanced nutrition.",
                "keywords": ["disease", "blight", "rust", "wilt", "fungicide", "bacterial", "bimari"]
            },
            {
                "id": "season_001",
                "topic": "Crop Seasons and Calendar",
                "content": "Kharif (June-October): Rice, Maize, Cotton, Soybean, Groundnut, Bajra, Jowar. Sowing: June-July with monsoon. Harvest: September-October. Rabi (November-March): Wheat, Chickpea, Mustard, Barley, Peas, Lentil. Sowing: November-December. Harvest: March-April. Zaid (March-June): Watermelon, Cucumber, Muskmelon, Bitter gourd. Sowing: March-April. Harvest: May-June. Perennial: Sugarcane (12-18 months), Banana (12 months), Papaya (10 months). Follow local climate patterns. Use weather forecast for sowing decisions.",
                "keywords": ["season", "kharif", "rabi", "zaid", "planting", "calendar", "mausam"]
            },
            {
                "id": "organic_001",
                "topic": "Organic Farming Practices",
                "content": "Organic farming: No synthetic chemicals, uses natural inputs. Benefits: Better soil health, higher prices (20-30% premium), sustainable. Organic fertilizers: FYM 10-15 tons/ha, Vermicompost 5 tons/ha, Neem cake 500 kg/ha, Bone meal 200 kg/ha. Pest control: Neem oil, Panchagavya, Jeevamrut, Cow urine. Certification: Apply to certifying agency, 3-year conversion period. Market: Organic stores, export, direct to consumer. Challenges: Lower initial yield, labor intensive. Government support: PKVY scheme, subsidies available.",
                "keywords": ["organic", "natural", "chemical-free", "certification", "javik"]
            }
        ]

    def _simple_embedding(self, text: str) -> np.ndarray:
        words = text.lower().split()

        vector = np.zeros(128)
        for i, word in enumerate(words[:128]):
            vector[i] = len(word) / 10.0
        return vector

    def _build_index(self):
        if not FAISS_AVAILABLE:
            return

        embeddings = []
        for doc in self.documents:
            text = f"{doc['topic']} {doc['content']} {' '.join(doc['keywords'])}"
            emb = self._simple_embedding(text)
            embeddings.append(emb)

        self.embeddings = np.array(embeddings).astype('float32')

        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        if FAISS_AVAILABLE and self.index:

            query_emb = self._simple_embedding(query).reshape(1, -1).astype('float32')
            distances, indices = self.index.search(query_emb, top_k)
            return [self.documents[i] for i in indices[0]]
        else:

            query_words = set(query.lower().split())
            scored_docs = []
            for doc in self.documents:
                score = sum(1 for kw in doc['keywords'] if kw in query_words)
                if score > 0:
                    scored_docs.append((score, doc))
            scored_docs.sort(reverse=True, key=lambda x: x[0])
            return [doc for _, doc in scored_docs[:top_k]]

class RAGChatbot:

    def __init__(self):
        self.knowledge_base = AgriKnowledgeBase()
        self.llm_client = None

        if GROQ_AVAILABLE:
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                self.llm_client = Groq(api_key=api_key)

    def chat(self, question: str, language: str = 'en') -> Dict:

        relevant_docs = self.knowledge_base.retrieve(question, top_k=3)
        context = "\n\n".join([f"**{doc['topic']}**: {doc['content']}" for doc in relevant_docs])

        if self.llm_client:
            response = self._llm_response(question, context, language)
        else:
            response = self._fallback_response(question, relevant_docs, language)

        if language != 'en':
            response = self._translate_response(response, language)
            translated_sources = []
            for doc in relevant_docs:
                try:
                    from translation import translate_text
                    translated_topic = translate_text(doc['topic'], 'en', language)
                    translated_sources.append({"topic": translated_topic, "id": doc['id']})
                except:
                    translated_sources.append({"topic": doc['topic'], "id": doc['id']})
        else:
            translated_sources = [{"topic": doc['topic'], "id": doc['id']} for doc in relevant_docs]

        return {
            "answer": response,
            "sources": translated_sources,
            "method": "llm" if self.llm_client else "fallback",
            "language": language
        }

    def _llm_response(self, question: str, context: str, language: str) -> str:
        try:
            crop_keywords = ['rice', 'wheat', 'maize', 'corn', 'cotton', 'sugarcane', 'chickpea', 'banana', 'mango', 'potato', 'tomato', 'onion']
            detected_crop = None
            question_lower = question.lower()
            
            for crop in crop_keywords:
                if crop in question_lower:
                    detected_crop = crop.capitalize()
                    break
            
            crop_instruction = f"The farmer is asking about {detected_crop}. " if detected_crop else ""
            
            prompt = f"""You are an expert agricultural advisor helping farmers.

Context from knowledge base:
{context}

Farmer's question: {question}

{crop_instruction}Provide a helpful, practical answer in English. Start by mentioning the crop name if relevant. Keep it simple and actionable."""

            response = self.llm_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful agricultural expert. Always respond in English."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"LLM error: {e}")
            return self._fallback_response(question, self.knowledge_base.retrieve(question), language)

    def _fallback_response(self, question: str, docs: List[Dict], language: str) -> str:
        if not docs:
            return "I don't have specific information about that. Please consult local agricultural experts."
        
        return docs[0]['content']

    def _translate_response(self, text: str, language: str) -> str:
        try:
            from translation import translate_text
            return translate_text(text, 'en', language)
        except:
            return text

_rag_chatbot = None

def get_rag_chatbot():
    global _rag_chatbot
    if _rag_chatbot is None:
        _rag_chatbot = RAGChatbot()
    return _rag_chatbot