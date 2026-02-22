import os
import requests
import logging
import json
import re
import google.generativeai as genai
from openai import OpenAI
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
AI_PROVIDER = os.getenv("AI_PROVIDER", "local").lower()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama-engine:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:latest")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Gemini Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# OpenAI Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo-preview")
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# Supabase Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

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
    Parses prompts/system_prompts.md and returns a dictionary of prompts.
    """
    prompts = {
        "analysis": "You are a professional assistant.",
        "chat": "You are a helpful assistant."
    }
    prompt_file = "prompts/system_prompts.md"
    try:
        if os.path.exists(prompt_file):
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            analysis_match = re.search(r"## Analysis Prompt\n(.*?)(?=\n##|$)", content, re.DOTALL)
            chat_match = re.search(r"## Chat Prompt\n(.*?)(?=\n##|$)", content, re.DOTALL)
            
            if analysis_match:
                prompts["analysis"] = analysis_match.group(1).strip()
            if chat_match:
                prompts["chat"] = chat_match.group(1).strip()
                
            logger.info(f"System prompts loaded from {prompt_file}")
    except Exception as e:
        logger.error(f"Error loading prompts: {e}")
    return prompts

# Initial load
SYSTEM_PROMPTS = load_prompts()

def get_context(query):
    """
    Searches data/posts.json for relevant context based on the query.
    Simple keyword-based search for now.
    """
    context_file = "data/posts.json"
    if not os.path.exists(context_file):
        return ""
    
    try:
        if not os.path.exists(context_file) or os.path.getsize(context_file) == 0:
            return ""
            
        with open(context_file, "r", encoding="utf-8") as f:
            posts = json.load(f)
            
        # Basic keyword matching
        keywords = query.lower().split()
        relevant_posts = []
        for post in posts:
            content = post.get("content", "").lower()
            if any(kw in content for kw in keywords):
                relevant_posts.append(post.get("content"))
        
        return "\n\n".join(relevant_posts[:5]) # Limit to top 5 matches
    except Exception as e:
        logger.error(f"Error reading context: {e}")
        return ""

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

def ask_gemini(user_input, system_instruction):
    """
    Helper for Gemini.
    """
    if not GEMINI_API_KEY:
        return "Gemini API Key is not configured."
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
    response = model.generate_content(user_input)
    return response.text

def ask_openai(user_input, system_instruction):
    """
    Helper for OpenAI.
    """
    if not client:
        return "OpenAI client is not configured."
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

def get_ai_response(user_input, context=""):
    """
    Universal AI response function that selects provider based on config.
    """
    system_instruction = SYSTEM_PROMPTS.get("chat", "You are a helpful assistant.")
    if context:
        system_instruction += f"\n\nUse the following context to answer:\n{context}"

    try:
        if AI_PROVIDER == "gemini":
            return ask_gemini(user_input, system_instruction)
        elif AI_PROVIDER == "openai":
            return ask_openai(user_input, system_instruction)
        else:
            # Fallback to local (Ollama)
            return ask_ollama(user_input, system_instruction)
    except Exception as e:
        logger.error(f"Error from AI provider ({AI_PROVIDER}): {e}")
        return f"Error contacting AI Provider: {str(e)}"

# Alias for backward compatibility if needed, but we should update callers
def get_gemini_response(user_input, context=""):
    return get_ai_response(user_input, context)
