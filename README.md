# Personal AI Assistant (Web Interface)

A versatile, enterprise-grade AI assistant featuring a **Modern Web Interface**. Supporting multiple AI backends including **Google Gemini 1.5 Flash**, **OpenAI**, and **Local Ollama** models.

## 🚀 Key Features

- **Flexible AI Providers**: Switch between Gemini, OpenAI, or Local Ollama via a single environment variable.
- **Supabase Authentication**: Secure registration and login flow using Supabase JWTs.
- **Contextual Retrieval (RAG)**: Uses local `data/posts.json` to provide expert answers based on your specific content.
- **Industrial Dashboard**: Modern glassmorphic Web UI for chatting with the AI.

## 📁 Project Structure

This project is structured as a multi-container stack with a decoupled frontend and backend.

### `/backend`
- **Python / FastAPI Engine**: Handles the orchestration of AI providers, routing, and Webhooks.
- **Supabase Auth**: Authenticates users and issues verified JWT sessions natively.
- `server.py`: FastAPI Web API and Facebook Webhooks endpoints.
- `main.py`: Telegram Bot logic polling loop.
- `db/` & `data/`: SQLAlchemy database abstraction and RAG knowledge bases.

### `/frontend`
- **Nginx Web Server**: An optimized Alpine Nginx container serving the Web UI.
- **Static Assets**: Contains HTML, CSS, client-side JS, and the modern Glassmorphism UI elements.
- **Reverse Proxy**: Configuration effortlessly routes `/login`, `/register`, and `/chat` to the backend.

## 🛠️ Setup Guide

### 1. Prerequisites
- Docker & Docker Compose.
- API Keys for your chosen provider (Gemini or OpenAI).
- **Supabase Account**: A Supabase project URL and Anon Key are required for the Authentication layer.

### 2. Configuration
Create your `backend/.env` file based on `backend/.env.example`:
```env
# Provider Selection: 'gemini', 'openai', or 'local'
AI_PROVIDER=gemini

# Provider Keys
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
OPENAI_MODEL_NAME=gpt-4-turbo-preview

# Supabase Auth
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
DATABASE_URL=postgresql://your_connection_string

# Local AI (Ollama)
MODEL_NAME=qwen3:latest
OLLAMA_URL=http://ollama-engine:11434
```

### 3. Knowledge Base
Populate `backend/data/posts.json` with your data to enable contextual answers.

### 4. Deployment
Run with Docker (3-container stack: Frontend Nginx + Backend API + Ollama):
```bash
docker compose up -d --build
```
* The web UI is automatically exposed on `http://localhost/`.

## 📜 License
MIT License - see [LICENSE](LICENSE) for details.
