import pandas as pd
from database import SessionLocal, CropData, init_db
import os

def load_crop_data():
    db = SessionLocal()
    
    # Find the CSV file
    csv_path = r"C:\Users\Neha\krishinova\data\raw\crop-production\India Agriculture Crop Production.csv"
    
    print("Loading crop production data...")
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} records")
    print(df.columns.tolist())  # show columns
    print(df.head(3))           # show first 3 rows
    
    # Load into DB
    count = 0
    for _, row in df.iterrows():
        try:
            crop = CropData(
                state=str(row.get('State_Name', '')),
                district=str(row.get('District_Name', '')),
                crop=str(row.get('Crop', '')),
                season=str(row.get('Season', '')),
                area=float(row.get('Area', 0) or 0),
                production=float(row.get('Production', 0) or 0),
                yield_per_hectare=float(row.get('Yield', 0) or 0)
            )
            db.add(crop)
            count += 1
            if count % 1000 == 0:
                db.commit()
                print(f"Loaded {count} records...")
        except Exception as e:
            continue
    
    db.commit()
    db.close()
    print(f"✅ Done! Loaded {count} crop records into database.")

if __name__ == "__main__":
    init_db()
    load_crop_data()