# 🌾 KrishiNova — AI-Powered Hyperlocal Farmer Intelligence Network

> *The AI brain behind every Indian farm*

[![Live Demo](https://img.shields.io/badge/Live%20Demo-krishinova--agri--insight.lovable.app-green)](https://krishinova-agri-insight.lovable.app)
[![API](https://img.shields.io/badge/API-krishinova--api--yygp.onrender.com-blue)](https://krishinova-api-yygp.onrender.com/docs)
[![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red)](https://krishinova-2nkrw6qtv3c2b9jghzwtcn.streamlit.app/)

---

## 🚀 What is KrishiNova?

KrishiNova is a full-stack AI platform that captures and preserves hyperlocal farming knowledge across Maharashtra — the kind of ground-truth knowledge that lives in farmers' heads and nowhere else.

LLMs like GPT-4 don't know that in Nashik, onion crops fail specifically when night temperature drops below 12°C in black cotton soil regions. **KrishiNova captures it, preserves it, and makes it queryable** — before it's lost forever.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌿 **Crop Disease Detection** | Upload a crop photo → instant AI diagnosis with treatment in Hindi/Marathi/English |
| 📊 **Yield Intelligence** | ML model trained on 345K real records predicts yield for any crop, district & season |
| 🕸️ **Knowledge Graph** | Live network of crops, diseases, districts and outcomes from crowdsourced farmer reports |
| 🗣️ **Multilingual Voice** | Hindi, Marathi, English — voice input and output |
| 📈 **Analytics Dashboard** | 6-page Streamlit dashboard with real Maharashtra farming insights |
| 🤖 **AI Agent** | LangGraph + Gemini agent that reasons across image, weather, market and community data |

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Lovable) |
| Backend API | FastAPI |
| AI Agent | LangGraph + Gemini 2.0 Flash |
| Vector Store | ChromaDB + SentenceTransformer |
| Database | SQLite (345K+ real crop records) |
| ML Model | Random Forest (scikit-learn) + MLflow |
| Disease Detection | ResNet18 (PyTorch) → lightweight fallback for deployment |
| Dashboard | Streamlit + Plotly |
| Knowledge Graph | NetworkX + PyVis |
| Containerization | Docker + Docker Compose |

---

## 📊 Model Performance

| Model | Metric | Score |
|---|---|---|
| Yield Prediction | R² Score | **0.938** |
| Yield Prediction | MAE | **8.03 kg/hectare** |
| Disease Detection | Classes | **32 disease types** |
| Knowledge Base | Crop Records | **345,407** |
| Knowledge Base | Farmer Reports | **150** |

---

## 🌐 Live Links

| Service | URL |
|---|---|
| 🌐 Frontend | [krishinova-agri-insight.lovable.app](https://krishinova-agri-insight.lovable.app) |
| ⚙️ API Docs | [krishinova-api-yygp.onrender.com/docs](https://krishinova-api-yygp.onrender.com/docs) |
| 📊 Dashboard | [Streamlit App](https://krishinova-2nkrw6qtv3c2b9jghzwtcn.streamlit.app/) |

---

## 📁 Project Structure

```
krishinova/
├── backend/
│   ├── main.py              # FastAPI — 7 endpoints
│   ├── agent.py             # LangGraph AI agent
│   ├── database.py          # SQLite schema
│   ├── vectorstore.py       # ChromaDB embeddings
│   ├── disease_model.py     # Crop disease detection
│   ├── yield_model.py       # Random Forest yield predictor
│   ├── knowledge_graph.py   # NetworkX + PyVis graph
│   ├── load_data.py         # 345K crop records loader
│   └── requirements.txt
├── streamlit_app/
│   └── app.py               # 6-page analytics dashboard
├── frontend/                # React frontend
├── docker-compose.yml
└── README.md
```

---

## ⚙️ API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/query` | POST | Ask farming questions in any language |
| `/detect-disease` | POST | Upload crop image for disease detection |
| `/predict-yield` | POST | Predict yield for crop/district/season |
| `/submit-report` | POST | Submit farmer experience report |
| `/insights/{district}` | GET | District-level crop analytics |
| `/stats` | GET | Platform statistics |

---

## 🏃 Quick Start

```bash
# Clone
git clone https://github.com/nehawawale07/krishinova.git
cd krishinova

# Backend
cd backend
pip install -r requirements.txt
python database.py
python load_data.py
uvicorn main:app --reload

# Streamlit Dashboard
cd ../streamlit_app
streamlit run app.py

# Docker (all services)
cd ..
docker-compose up --build
```

---

## 💡 The Problem We Solve

Every year in India, **10,000+ farmers commit suicide** — mostly due to wrong farming decisions caused by lack of hyperlocal knowledge. Agricultural extension officers are overwhelmed (1 per 1000 farmers), generic AI gives useless advice, and experienced farmers' knowledge is disappearing.

KrishiNova gives every farmer access to the **collective wisdom of their entire region** — in their own language, on their phone.

---

## 🎯 Built For Bharat

- 🇮🇳 Designed for Maharashtra's farming districts
- 🗣️ Hindi, Marathi, English support
- 📱 Mobile-first voice interface
- 🌾 Real data from India's agriculture records

---

*Built with ❤️ for Indian farmers | KrishiNova v1.0*
