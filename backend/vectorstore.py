import chromadb
from chromadb.utils import embedding_functions
from database import SessionLocal, FarmerReport, Farmer
import os
from dotenv import load_dotenv

load_dotenv()

# Setup ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="farmer_reports",
    embedding_function=embedding_fn
)

def embed_all_reports():
    db = SessionLocal()
    reports = db.query(FarmerReport).all()
    
    print(f"Embedding {len(reports)} farmer reports...")
    
    documents = []
    metadatas = []
    ids = []
    
    for report in reports:
        farmer = db.query(Farmer).filter(Farmer.id == report.farmer_id).first()
        
        # Combine problem + solution into one searchable document
        text = f"Crop: {report.crop}. District: {report.district}. Soil: {report.soil_type}. Season: {report.season}. Problem: {report.problem} Solution: {report.solution}"
        
        documents.append(text)
        metadatas.append({
            "crop": report.crop,
            "district": report.district,
            "soil_type": report.soil_type,
            "outcome": report.outcome,
            "season": report.season,
            "language": report.language,
            "farmer_name": farmer.name if farmer else "Unknown"
        })
        ids.append(f"report_{report.id}")
    
    # Add to ChromaDB in batches
    batch_size = 50
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
        print(f"Embedded {min(i+batch_size, len(documents))}/{len(documents)} reports...")
    
    db.close()
    print("✅ All reports embedded into ChromaDB!")

def query_similar_reports(query_text, n_results=5):
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results

if __name__ == "__main__":
    embed_all_reports()
    
    # Test query
    print("\nTesting similarity search...")
    results = query_similar_reports("onion disease in black soil nashik")
    print(f"Found {len(results['documents'][0])} similar reports")
    for i, doc in enumerate(results['documents'][0]):
        print(f"\n--- Result {i+1} ---")
        print(doc[:200])
        print("Outcome:", results['metadatas'][0][i]['outcome'])