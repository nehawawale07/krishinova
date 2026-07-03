import chromadb
from chromadb.utils import embedding_functions
from database import SessionLocal, FarmerReport, Farmer
import os

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path="./chroma_db")
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        _collection = _client.get_or_create_collection(
            name="farmer_reports",
            embedding_function=embedding_fn
        )
    return _collection

def query_similar_reports(query_text, n_results=3):
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
    except Exception as e:
        return {"documents": [[]], "metadatas": [[]]}
