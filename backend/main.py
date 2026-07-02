import os
from disease_model import predict_disease
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal, FarmerReport, Farmer, CropData, DiseaseLog, init_db
from vectorstore import query_similar_reports
import uvicorn

app = FastAPI(title="KrishiNova API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

init_db()

class QueryRequest(BaseModel):
    query: str
    language: str = "english"
    district: str = "Nashik"

class ReportRequest(BaseModel):
    farmer_name: str
    village: str
    district: str
    crop: str
    soil_type: str
    season: str
    problem: str
    solution: str
    outcome: str
    language: str = "english"

@app.get("/")
def root():
    return {"message": "🌾 KrishiNova API is running!"}

@app.post("/query")
def query_agent(request: QueryRequest):
    # Get similar reports from ChromaDB
    similar = query_similar_reports(request.query, n_results=3)
    
    reports = []
    for doc, meta in zip(similar['documents'][0], similar['metadatas'][0]):
        reports.append({
            "text": doc[:300],
            "crop": meta['crop'],
            "district": meta['district'],
            "outcome": meta['outcome'],
            "farmer": meta['farmer_name']
        })
    
    # Mock AI response for now (will replace with Gemini later)
    response = f"Based on {len(reports)} similar farmer experiences in your region, here are the insights for your query about: {request.query}"
    
    return {
        "query": request.query,
        "language": request.language,
        "similar_reports": reports,
        "response": response
    }

@app.post("/submit-report")
def submit_report(report: ReportRequest):
    db = SessionLocal()
    
    farmer = Farmer(
        name=report.farmer_name,
        village=report.village,
        district=report.district,
        language=report.language
    )
    db.add(farmer)
    db.flush()
    
    new_report = FarmerReport(
        farmer_id=farmer.id,
        crop=report.crop,
        soil_type=report.soil_type,
        district=report.district,
        problem=report.problem,
        solution=report.solution,
        outcome=report.outcome,
        season=report.season,
        language=report.language
    )
    db.add(new_report)
    db.commit()
    db.close()
    
    return {"message": "✅ Report submitted successfully!", "farmer_id": farmer.id}

@app.get("/insights/{district}")
def get_insights(district: str):
    db = SessionLocal()
    
    # Top crops by production
    crops = db.query(CropData).filter(
        CropData.district.ilike(f"%{district}%")
    ).order_by(CropData.production.desc()).limit(5).all()
    
    # Recent reports
    reports = db.query(FarmerReport).filter(
        FarmerReport.district.ilike(f"%{district}%")
    ).limit(10).all()
    
    success_count = len([r for r in reports if r.outcome == 'success'])
    failure_count = len([r for r in reports if r.outcome == 'failure'])
    
    db.close()
    
    return {
        "district": district,
        "top_crops": [{"crop": c.crop, "production": c.production, "season": c.season} for c in crops],
        "total_reports": len(reports),
        "success_rate": f"{(success_count/len(reports)*100):.1f}%" if reports else "0%",
        "recent_problems": [r.problem[:100] for r in reports[:5]]
    }

@app.get("/stats")
def get_stats():
    db = SessionLocal()
    total_farmers = db.query(Farmer).count()
    total_reports = db.query(FarmerReport).count()
    total_crop_records = db.query(CropData).count()
    db.close()
    
    return {
        "total_farmers": total_farmers,
        "total_reports": total_reports,
        "total_crop_records": total_crop_records,
        "districts_covered": 8,
        "crops_tracked": 8
    }
@app.post("/detect-disease")
async def detect_disease(file: UploadFile = File(...)):
    # Save uploaded image temporarily
    temp_path = f"temp_{uuid.uuid4().hex}.jpg"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run disease detection
    result = predict_disease(temp_path)
    
    # Cleanup temp file
    os.remove(temp_path)
    
    return {
        "filename": file.filename,
        "detection": result
    }
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)