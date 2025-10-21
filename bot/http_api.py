from fastapi import FastAPI, Header, HTTPException
import os
from pydantic import BaseModel
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
BOT_SECRET = os.getenv("BOT_SHARED_SECRET")

bot = Bot(token=BOT_TOKEN)
app = FastAPI(title="Telegram Bot HTTP API")

class SendMessageRequest(BaseModel):
    telegram_id: int
    message: str

@app.post("/send/")
async def send_message(payload: SendMessageRequest, x_bot_secret: str = Header(...)):
    if x_bot_secret != BOT_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    await bot.send_message(payload.telegram_id, payload.message)
    return {"status": "ok"}