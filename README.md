# Natural Language Cross-Platform Data Query RAG Agent

This project enables business users to query multiple data sources using natural language and receive answers in text, tables, and graphs. It is built with ReactJS (frontend) and Python (FastAPI + LangChain, backend).

## Features
- Query MongoDB (client profiles) and MySQL (transactions) with plain English
- LangChain-powered RAG agent for natural language understanding
- Results as text, tables, and charts

## Structure
- `frontend/` — React (Vite) app
- `backend/` — Python FastAPI, LangChain, MySQL/MongoDB connectors

## Quick Start
1. Install Node.js and Python 3.11
2. See `frontend/` and `backend/` folders for setup instructions
3. Configure `.env` files for backend (API keys, DB credentials) and frontend (backend URL)

## Development
- Requires local or remote MongoDB & MySQL instances (not containerized)
- See `.env.example` in backend and `.env.example` in frontend for configuration

---

## Status
- [x] Frontend scaffold (React + Vite + MUI)
- [x] Backend scaffold (FastAPI + LangChain)
- [x] MySQL/MongoDB connectors
- [x] LLM-to-SQL and query execution
- [x] Hardcoded SQL for key business queries
- [x] Environment variable-based deployment
- [ ] LLM-driven MongoDB query support (planned)
- [ ] Unit tests & Dockerization (planned)
