import os
import telebot
import requests
import json
import logging
import feedparser
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama-engine:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:latest")
NEWS_URL = os.getenv("NEWS_URL", "https://goldbroker.com/news.rss")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Gold Trading AI Assistant! Use /analyze to get the latest gold market sentiment.")

@bot.message_handler(commands=['analyze'])
def analyze_market(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "🔍 Fetching latest Gold news and analyzing...")
    
    # 1. Fetch News
    news = fetch_gold_news()
    
    # 2. Format News for User
    news_summary = "\n".join([f"📰 {n}" for n in news])
    
    # 3. Get AI Analysis
    analysis = get_ai_analysis(news)
    
    # 4. Final Reply
    reply = f"� *Gold Market Sentiment Report* 📊\n\n*Latest Headlines:*\n{news_summary}\n\n*AI Deep Analysis:* 🤖\n{analysis}"
    bot.send_message(chat_id, reply, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    """
    Handles free conversation with the AI.
    """
    chat_id = message.chat.id
    user_input = message.text
    
    # Show typing status
    bot.send_chat_action(chat_id, 'typing')
    
    logger.info(f"User is chatting: {user_input[:50]}...")
    
    # Use a persistent personality from prompts.md
    system_prompt = SYSTEM_PROMPTS.get("chat")
    
    response = ask_ollama(user_input, system_prompt)
    bot.reply_to(message, response)

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
    else:
        logger.info("Starting Telegram Bot...")
        bot.infinity_polling()
