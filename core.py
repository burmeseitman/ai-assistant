import os
import requests
import logging
import feedparser
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama-engine:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:latest")
NEWS_URL = os.getenv("NEWS_URL", "https://goldbroker.com/news.rss")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

def get_bot_status(token=None):
    """
    Validates the Telegram Bot Token using the getMe API.
    Returns (status, message)
    """
    token_to_check = token or TELEGRAM_BOT_TOKEN
    if not token_to_check:
        return False, "Token is missing"
    
    try:
        url = f"https://api.telegram.org/bot{token_to_check}/getMe"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                return True, f"Online (@{bot_info.get('username')})"
        return False, "Invalid Token"
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def set_bot_token(token):
    """
    Updates the global bot token (in memory).
    """
    global TELEGRAM_BOT_TOKEN
    TELEGRAM_BOT_TOKEN = token

def load_prompts():
    """
    Parses system-prompts.md and returns a dictionary of prompts.
    """
    prompts = {
        "analysis": "You are a gold market analyst.",
        "chat": "You are a helpful assistant."
    }
    try:
        if os.path.exists("system-prompts.md"):
            with open("system-prompts.md", "r", encoding="utf-8") as f:
                content = f.read()
                
            analysis_match = re.search(r"## Analysis Prompt\n(.*?)(?=\n##|$)", content, re.DOTALL)
            chat_match = re.search(r"## Chat Prompt\n(.*?)(?=\n##|$)", content, re.DOTALL)
            
            if analysis_match:
                prompts["analysis"] = analysis_match.group(1).strip()
            if chat_match:
                prompts["chat"] = chat_match.group(1).strip()
                
            logger.info("System prompts loaded from system-prompts.md")
    except Exception as e:
        logger.error(f"Error loading prompts: {e}")
    return prompts

# Initial load
SYSTEM_PROMPTS = load_prompts()

def fetch_gold_news():
    """
    Fetches gold news headlines from GoldBroker RSS feed.
    """
    logger.info(f"Fetching gold news from {NEWS_URL}...")
    url = NEWS_URL
    try:
        feed = feedparser.parse(url)
        
        # Extract titles from the first 5 entries
        news_list = [entry.title.strip() for entry in feed.entries[:5] if hasattr(entry, 'title')]
        
        if not news_list:
            return ["No recent news found in the RSS feed."]
            
        return news_list
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return [f"Error fetching news: {str(e)}"]

def ask_ollama(prompt, system_prompt="You are a helpful AI assistant."):
    """
    Generic function to send a prompt to Ollama.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:",
        "stream": False
    }
    
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response from AI.")
    except Exception as e:
        logger.error(f"Error from Ollama: {e}")
        return f"Error contacting AI Engine: {str(e)}"

def get_ai_analysis(news_items):
    """
    Sends news to Ollama for sentiment analysis.
    """
    logger.info("Sending news to AI Engine for analysis...")
    system_prompt = SYSTEM_PROMPTS.get("analysis")
    user_content = "Please analyze the following news headlines and provide a sentiment breakdown:\n" + "\n".join([f"- {item}" for item in news_items])
    
    return ask_ollama(user_content, system_prompt)
