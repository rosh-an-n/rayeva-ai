# Rayeva AI

Sustainable commerce platform with AI-powered product categorization and B2B proposal generation. Built with FastAPI + Google Gemini.

## Setup

```bash
cd rayeva-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# add your Gemini API key to .env
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

## Run

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) for the web UI.

## API Endpoints

**Categorize a product:**
```bash
curl -X POST http://localhost:8000/api/v1/category/generate \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Bamboo Toothbrush", "product_description": "Biodegradable bamboo toothbrush with charcoal bristles"}'
```

**Generate a B2B proposal:**
```bash
curl -X POST http://localhost:8000/api/v1/proposal/generate \
  -H "Content-Type: application/json" \
  -d '{"company_name": "GreenOffice", "industry": "Corporate", "budget": 50000, "requirements": "Eco-friendly supplies for 200 people", "preferences": ["plastic-free", "recycled"]}'
```

## Architecture

See [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) for the full overview including planned modules (Impact Reporting, WhatsApp Bot).

## Stack

- FastAPI + Uvicorn
- Google Gemini (gemini-1.5-flash)
- SQLite + SQLAlchemy
- Vanilla HTML/CSS/JS frontend
