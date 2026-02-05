import os
import telebot
import logging
from core import ask_ollama, fetch_gold_news, get_ai_analysis, SYSTEM_PROMPTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TELEGRAM_BOT_TOKEN:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
else:
    logger.error("TELEGRAM_BOT_TOKEN is not set. Bot will not function.")
    bot = None

if bot:
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
        reply = f" *Gold Market Sentiment Report* 📊\n\n*Latest Headlines:*\n{news_summary}\n\n*AI Deep Analysis:* 🤖\n{analysis}"
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
    elif bot:
        logger.info("Starting Telegram Bot...")
        bot.infinity_polling()
