import os
import telebot
import logging
from core import get_context, get_ai_response, SYSTEM_PROMPTS

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
        bot.reply_to(message, "Welcome to your AI Assistant! I am now powered by multiple AI providers (Gemini, OpenAI, or Local). Feel free to ask me anything.")

    @bot.message_handler(func=lambda message: True)
    def handle_chat(message):
        """
        Handles free conversation with the AI using selected provider and local context.
        """
        chat_id = message.chat.id
        user_input = message.text
        
        # Show typing status
        bot.send_chat_action(chat_id, 'typing')
        
        logger.info(f"User is chatting: {user_input[:50]}...")
        
        # 1. Get Context
        context = get_context(user_input)
        
        # 2. Get AI Response
        response = get_ai_response(user_input, context)
        
        bot.reply_to(message, response)

if __name__ == "__main__":
    from core import get_bot_status
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
    elif bot:
        status, msg = get_bot_status(TELEGRAM_BOT_TOKEN)
        if status:
            logger.info("Starting Telegram Bot...")
            bot.infinity_polling()
        else:
            logger.error(f"Telegram Bot error: {msg}. Please check the token.")
