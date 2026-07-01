from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./krishinova.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    village = Column(String)
    district = Column(String)
    state = Column(String, default="Maharashtra")
    language = Column(String, default="hindi")

class FarmerReport(Base):
    __tablename__ = "farmer_reports"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer)
    crop = Column(String)
    soil_type = Column(String)
    district = Column(String)
    problem = Column(Text)
    solution = Column(Text)
    outcome = Column(String)  # success/failure
    season = Column(String)
    language = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CropData(Base):
    __tablename__ = "crop_data"
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String)
    district = Column(String)
    crop = Column(String)
    season = Column(String)
    area = Column(Float)
    production = Column(Float)
    yield_per_hectare = Column(Float)

class DiseaseLog(Base):
    __tablename__ = "disease_logs"
    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String)
    disease = Column(String)
    district = Column(String)
    severity = Column(String)
    treatment = Column(Text)
    detected_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()