import os
import requests
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
from core import ask_ollama, fetch_gold_news, get_ai_analysis, get_bot_status, set_bot_token, TELEGRAM_BOT_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal AI Assistant API")

# Simple Hardcoded User Configuration
USER_DB = {
    "admin": "password123"
}

# Settings state (In-memory for simplicity for now)
settings = {
    "ai_mode": "local",  # "local" or "api"
    "api_key": ""
}

class ChatMessage(BaseModel):
    message: str

class SettingsUpdate(BaseModel):
    ai_mode: str
    api_key: Optional[str] = None

# Authentication (Very basic for demo)
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_password = USER_DB.get(form_data.username)
    if not user_password or user_password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": "dummy-token", "token_type": "bearer"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    logger.info(f"Chat request: {msg.message}")
    
    if settings["ai_mode"] == "local":
        # Use existing Ollama logic
        try:
            # Check if it's a gold prediction request
            if "gold" in msg.message.lower() and ("price" in msg.message.lower() or "predict" in msg.message.lower()):
                news = fetch_gold_news()
                analysis = get_ai_analysis(news)
                return {"response": analysis}
            
            response = ask_ollama(msg.message)
            return {"response": response}
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Placeholder for API mode
        return {"response": "API Mode is currently a placeholder. Please configure a valid API key and endpoint if implemented."}

@app.get("/settings")
async def get_settings():
    is_ok, status_msg = get_bot_status()
    return {
        **settings,
        "telegram_bot_token": TELEGRAM_BOT_TOKEN,
        "bot_status": {
            "ok": is_ok,
            "message": status_msg
        }
    }

@app.post("/settings")
async def update_settings(update: SettingsUpdate):
    if update.ai_mode not in ["local", "api"]:
        raise HTTPException(status_code=400, detail="Invalid AI mode")
    settings["ai_mode"] = update.ai_mode
    if update.api_key is not None:
        settings["api_key"] = update.api_key
    
    if update.telegram_bot_token is not None:
        set_bot_token(update.telegram_bot_token)
        # Note: In a real app, you'd save this to .env or a DB
        # And potentially restart the bot polling if it's running
    
    is_ok, status_msg = get_bot_status()
    return {
        "status": "success", 
        "settings": {
            **settings, 
            "telegram_bot_token": update.telegram_bot_token,
            "bot_status": {"ok": is_ok, "message": status_msg}
        }
    }

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
