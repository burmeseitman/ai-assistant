# Telegram AI Trading Assistant

A multi-container Docker environment featuring a Gold Market News Scraper, a Telegram Bot, and an AI Engine powered by Ollama and Qwen 2.5.

## Project Structure
- `ollama-engine`: Container running Ollama to serve the LLM.
- `trading-bot`: Python application that handles news scraping, Telegram bot interaction, and AI chat.

## Features
- **RSS News Scraping**: Fetches live gold news from `GoldBroker.com`.
- **Market Analysis**: Use `/analyze` to get automated sentiment scores (Bullish/Bearish) for the latest news.
- **Free Chat**: Type any message to have a professional conversation with the AI gold analyst.
- **Qwen 2.5 Support**: Powered by the latest Qwen architecture for high-quality financial insights.

## Setup Instructions

### 1. Configuration
Create a `.env` file in the root directory based on `.env.example`:
```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
```

### 2. Start the Containers
Run the following command to build and start the environment:
```bash
docker compose -f docker-compose.yaml up -d --build
```

### 3. Initialize the AI Model
Once the containers are running, pull the `qwen2.5` model inside the Ollama container:

```bash
docker exec -it ollama-engine ollama pull qwen2.5
```

### 4. Usage
Open Telegram and find your bot.
- Send `/start` to see the welcome message.
- Send `/analyze` to fetch current gold news and get AI-generated sentiment scores.
- **Just Chat**: Send any message to talk to your AI Trading Assistant.

## Requirements
- Docker and Docker Compose installed.
- CPU operation by default (GPU support commented out in `docker-compose.yaml`).
