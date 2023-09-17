import os
import telegram
import asyncio
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
user_id = os.getenv("USER_ID")


async def send_notification(text: str) -> None:
    bot = telegram.Bot(token=api_key)
    await bot.send_message(chat_id=user_id, text=text)
