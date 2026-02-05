# Personal AI Assistant

A robust multi-container Docker application featuring a Modern Web View and a Telegram Bot for Gold Market Analysis and general AI interaction. Powered by Ollama and Qwen 2.5.

## 🚀 Key Improvements & Architecture
The project has been refactored for better stability and modularity:
- **Decoupled Architecture**: Shared logic (news fetching, AI interaction, prompt management) is extracted into `core.py`. This ensures the Web server and Telegram bot are independent.
- **Resilient WebUI**: The Web interface no longer crashes if the Telegram token is missing. It now validates the token dynamically and provides real-time status updates.
- **Centralized Configuration**: All services are consolidated into a single `docker-compose.yml` for simplified deployment.

## 📁 Project Structure
- `core.py`: Centralized logic for AI, News, and Configuration.
- `server.py`: FastAPI server for the Web Interface.
- `main.py`: Telegram Bot entry point.
- `static/`: Frontend assets (Logo, HTML, CSS, JS).
- `docker-compose.yml`: Orchestrates `ollama-engine`, `assistant-bot`, and `assistant-webui`.

## 🛠️ Features
- **Premium Web UI**: Sleek dark theme with glassmorphism effects and modern branding.
- **Bot Token Management**: Update and validate your Telegram Bot token directly from the Web **Settings** tab.
- **Smart Chat**: Integrated chat for general assistance and specialized gold price predictions.
- **News Insights**: Automatic scraping of gold market headlines via RSS.
- **Secure Access**: Protected by a login screen (Default: `admin` / `password123`).

## 📋 Setup Guide

### 1. Requirements
- Docker and Docker Compose installed.
- (Optional) GPU support (requires NVIDIA Docker runtime).

### 2. Configuration
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
MODEL_NAME=qwen3:latest
NEWS_URL=https://goldbroker.com/news.rss
```
*Note: The WebUI will load even if the token stays empty, allowing you to configure it via settings later.*

### 3. Start the Application
```bash
docker compose up -d --build
```

### 4. Usage
- **Web App**: Visit `http://localhost:8000`
- **Telegram Bot**: Send `/analyze` to your bot for a sentiment report.

## 📜 License
MIT License - see [LICENSE](LICENSE) for details.
