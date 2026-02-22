import os
import requests
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import logging
from core import get_bot_status, set_bot_token, TELEGRAM_BOT_TOKEN, get_context, get_ai_response, supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal AI Assistant API")

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN")

from db.database import get_db, engine, Base
from db.models import User, ChatSession, DbChatMessage as DbChatMessage

from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

@app.on_event("startup")
async def startup():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified")
    except Exception as e:
        logger.error(f"Database startup error: {e}")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
        user_uuid = response.user.id
        user_email = response.user.email
    except Exception as e:
        logger.error(f"Supabase auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        # Sync to local DB if they logged in but don't exist
        user = User(id=user_uuid, email=user_email)
        db.add(user)
        db.commit()
    return user

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

@app.post("/register")
async def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    try:
        # Call Supabase
        res = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password,
            "options": { "data": { "full_name": req.full_name } }
        })
        user_uuid = res.user.id
        
        # Keep native User record for relation bindings
        if not db.query(User).filter(User.id == user_uuid).first():
            new_user = User(
                id=user_uuid,
                email=req.email,
                full_name=req.full_name
            )
            db.add(new_user)
            db.commit()
        
        return {
            "message": "User created successfully",
            "access_token": res.session.access_token if res.session else None,
            "token_type": "bearer",
            "user": {
                "id": user_uuid,
                "email": req.email,
                "full_name": req.full_name
            }
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

class ChatRequest(BaseModel):
    message: str

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        user_uuid = res.user.id
        
        # Verify sync exists
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            user = User(
                id=user_uuid, 
                email=res.user.email, 
                full_name=res.user.user_metadata.get("full_name") if res.user.user_metadata else None
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return {
            "access_token": res.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            }
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Incorrect email or password")


@app.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "created_at": current_user.created_at
    }

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Facebook Webhook verification (GET).
    """
    if hub_mode == "subscribe" and hub_verify_token == FB_VERIFY_TOKEN:
        logger.info("Webhook verified successfully.")
        return int(hub_challenge)
    else:
        logger.warning("Webhook verification failed.")
        raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Facebook Webhook message handling (POST).
    """
    body = await request.json()
    logger.info(f"Received webhook: {body}")

    if body.get("object") == "page":
        for entry in body.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")

                    if message_text:
                        logger.info(f"Received message from {sender_id}: {message_text}")
                        # 1. Get Context
                        context = get_context(message_text)
                        # 2. Get AI Response
                        ai_response = get_ai_response(message_text, context)
                        # 3. Send Message back to Facebook
                        send_fb_message(sender_id, ai_response)

        return "EVENT_RECEIVED"
    else:
        raise HTTPException(status_code=404)

def send_fb_message(recipient_id, message_text):
    """
    Sends a message back to the user via Facebook Graph API.
    """
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Sent message to {recipient_id}")
    except Exception as e:
        logger.error(f"Error sending FB message: {e}")

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(msg: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Chat endpoint for Web UI, requires JWT auth and saves history to the database.
    """
    logger.info(f"Chat request from {current_user.email}: {msg.message}")
    
    try:
        # Find or create active session for this user (simple logic for now)
        session = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).first()
        if not session:
            session = ChatSession(user_id=current_user.id, title="Main Chat")
            db.add(session)
            db.commit()
            db.refresh(session)
            
        # Save user message
        user_db_msg = DbChatMessage(session_id=session.id, role="user", content=msg.message)
        db.add(user_db_msg)
        
        # 1. Get Context
        context = get_context(msg.message)
        # 2. Get AI Response
        response = get_ai_response(msg.message, context)
        
        # Save AI message
        ai_db_msg = DbChatMessage(session_id=session.id, role="ai", content=response)
        db.add(ai_db_msg)
        db.commit()
        
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/settings")
async def get_settings():
    is_ok, status_msg = get_bot_status()
    return {
        "telegram_bot_token": TELEGRAM_BOT_TOKEN,
        "bot_status": {
            "ok": is_ok,
            "message": status_msg
        }
    }

@app.post("/settings")
async def update_settings(update: dict):
    # Simplified settings for now, focusing on tokens
    if "telegram_bot_token" in update:
        set_bot_token(update["telegram_bot_token"])
    
    is_ok, status_msg = get_bot_status()
    return {
        "status": "success", 
        "settings": {
            "telegram_bot_token": TELEGRAM_BOT_TOKEN,
            "bot_status": {"ok": is_ok, "message": status_msg}
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
