from google import genai
from vectorstore import query_similar_reports
from database import SessionLocal, CropData
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def detect_language(text):
    hindi_chars = set('अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह')
    marathi_specific = ['आहे', 'माझ', 'शेत', 'पीक', 'मला']
    
    if any(char in hindi_chars for char in text):
        if any(word in text for word in marathi_specific):
            return 'marathi'
        return 'hindi'
    return 'english'

def translate_to_english(text, source_lang):
    if source_lang == 'english':
        return text
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Translate this {source_lang} text to English. Return only the translation, nothing else: {text}"
    )
    return response.text.strip()

def query_crop_data(crop, district):
    db = SessionLocal()
    results = db.query(CropData).filter(
        CropData.crop.ilike(f"%{crop}%"),
        CropData.district.ilike(f"%{district}%")
    ).limit(5).all()
    db.close()
    
    if not results:
        return "No historical yield data found for this crop and district."
    
    avg_yield = sum(r.yield_per_hectare for r in results if r.yield_per_hectare) / len(results)
    return f"Historical average yield for {crop} in {district}: {avg_yield:.2f} kg/hectare based on {len(results)} records."

def generate_response(query, language, similar_reports, crop_data):
    # Format similar reports
    reports_text = ""
    for i, (doc, meta) in enumerate(zip(
        similar_reports['documents'][0],
        similar_reports['metadatas'][0]
    )):
        reports_text += f"\nReport {i+1} ({meta['outcome']}): {doc[:300]}\n"
    
    prompt = f"""You are KrishiNova, an expert AI agricultural advisor for Indian farmers in Maharashtra.

A farmer asked: "{query}"

Similar experiences from other farmers in the region:
{reports_text}

Historical crop data: {crop_data}

Provide a helpful, specific, and practical response in {language} language.
- Be conversational and empathetic
- Give concrete actionable advice
- Mention what worked for other farmers in similar situations
- Keep response under 200 words
- If responding in Hindi or Marathi, use simple everyday language not formal language"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def run_agent(user_query):
    print(f"\n🌾 KrishiNova Agent Processing: '{user_query}'")
    
    # Step 1: Detect language
    language = detect_language(user_query)
    print(f"📍 Detected language: {language}")
    
    # Step 2: Translate to English for processing
    english_query = translate_to_english(user_query, language)
    print(f"🔄 English query: {english_query}")
    
    # Step 3: Query ChromaDB for similar reports
    similar = query_similar_reports(english_query, n_results=3)
    print(f"🔍 Found {len(similar['documents'][0])} similar farmer reports")
    
    # Step 4: Extract crop name for SQL query
    crop_keywords = ["onion", "soybean", "cotton", "sugarcane", "wheat", "rice", "tur", "jowar"]
    detected_crop = next((c for c in crop_keywords if c in english_query.lower()), "wheat")
    crop_data = query_crop_data(detected_crop, "Nashik")
    print(f"📊 Crop data: {crop_data}")
    
    # Step 5: Generate final response
    response = generate_response(english_query, language, similar, crop_data)
    print(f"\n✅ KrishiNova Response:\n{response}")
    
    return {
        "query": user_query,
        "language": language,
        "response": response
    }

if __name__ == "__main__":
    # Test with English
    run_agent("My onion crop has purple blotch disease in Nashik, what should I do?")
    
    # Test with Hindi
    run_agent("मेरी सोयाबीन की फसल में पानी भर गया है, क्या करूं?")