# Backend (FastAPI + LangChain)

## Setup
1. Create a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in required values.

## Run
```sh
uvicorn main:app --reload
```

## Structure
- `main.py` — FastAPI entry point
- `db/` — Database connectors (MongoDB, MySQL)
- `langchain_agent/` — LangChain chains, query logic
- `schemas.py` — Pydantic models
- `config.py` — Settings loader
