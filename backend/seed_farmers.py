from google import genai
import json
import time
import os
from dotenv import load_dotenv
from database import SessionLocal, Farmer, FarmerReport, init_db

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DISTRICTS = ["Nashik", "Pune", "Amravati", "Nagpur", "Solapur", "Kolhapur", "Aurangabad", "Latur"]
CROPS = ["Onion", "Soybean", "Cotton", "Sugarcane", "Wheat", "Rice", "Tur Dal", "Jowar"]
SOILS = ["Black Cotton", "Red Laterite", "Alluvial", "Sandy Loam"]
LANGUAGES = ["hindi", "marathi", "english"]
OUTCOMES = ["success", "failure", "partial"]

def generate_farmer_reports(batch_size=10):
    prompt = f"""
    Generate {batch_size} realistic Indian farmer experience reports from Maharashtra.
    Return ONLY a JSON array, no markdown, no extra text.
    Each object must have exactly these fields:
    - farmer_name (Indian name)
    - village (Maharashtra village name)
    - district (one of: {DISTRICTS})
    - crop (one of: {CROPS})
    - soil_type (one of: {SOILS})
    - season (Kharif/Rabi/Summer)
    - problem (specific farming problem they faced, in 1-2 sentences)
    - solution (what they tried, in 1-2 sentences)
    - outcome (one of: success/failure/partial)
    - language (one of: hindi/marathi/english)
    
    Make problems and solutions very specific and realistic — pest attacks, 
    weather issues, soil problems, market timing etc.
    """

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    text = response.text.strip()  
    # Clean response
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    
    return json.loads(text)

def seed_database(total=150):
    db = SessionLocal()
    count = 0
    
    while count < total:
        try:
            batch = generate_farmer_reports(10)
            for item in batch:
                # Create farmer
                farmer = Farmer(
                    name=item['farmer_name'],
                    village=item['village'],
                    district=item['district'],
                    language=item['language']
                )
                db.add(farmer)
                db.flush()
                
                # Create report
                report = FarmerReport(
                    farmer_id=farmer.id,
                    crop=item['crop'],
                    soil_type=item['soil_type'],
                    district=item['district'],
                    problem=item['problem'],
                    solution=item['solution'],
                    outcome=item['outcome'],
                    season=item['season'],
                    language=item['language']
                )
                db.add(report)
                count += 1
            
            db.commit()
            print(f"✅ Seeded {count} farmer reports...")
            time.sleep(30)
        except Exception as e:
            print(f"Error in batch: {e}")
            db.rollback()
            continue
    
    db.close()
    print(f"🌾 Done! {count} farmer reports seeded into database.")

if __name__ == "__main__":
    init_db()
    seed_database(150)