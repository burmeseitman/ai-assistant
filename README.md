# Multi-Platform AI Assistant (Facebook, Telegram & Web)

A versatile, enterprise-grade AI assistant featuring **Facebook Messenger**, **Telegram Bot**, and a **Modern Web Interface**. Supporting multiple AI backends including **Google Gemini 1.5 Flash**, **OpenAI GPT-4**, and **Local Ollama** models.

## 🚀 Key Features

- **Flexible AI Providers**: Switch between Gemini, OpenAI, or Local Ollama via a single environment variable.
- **Facebook Messenger Integration**: Full Webhook support with secure token verification.
- **Telegram Bot Support**: Real-time interaction via Telegram.
- **Contextual Retrieval (RAG)**: Uses local `data/posts.json` to provide expert answers based on your specific content.
- **Burmese Localization**: Pre-configured with a professional "Technology Software Engineer" personality in Burmese.
- **Industrial Dashboard**: Modern Web UI for chat and system settings.

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
- Facebook Developer App (for Messenger Webhook).

### 2. Configuration
Create your `backend/.env` file based on `backend/.env.example`:
```env
# Provider Selection: 'gemini', 'openai', or 'local'
AI_PROVIDER=gemini

# Provider Keys
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
OPENAI_MODEL_NAME=gpt-4-turbo-preview

# Facebook & Telegram
FB_PAGE_ACCESS_TOKEN=your_token
FB_VERIFY_TOKEN=your_verify_token
TELEGRAM_BOT_TOKEN=your_token

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
* For Facebook Webhook, map port 8000 via a secure HTTPS tunnel (e.g., `ngrok`).

## 📜 License
MIT License - see [LICENSE](LICENSE) for details.
