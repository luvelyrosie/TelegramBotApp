import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import logging


load_dotenv()

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
BOT_SECRET = os.getenv("BOT_SHARED_SECRET")
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000/")


logging.basicConfig(level=logging.INFO)

dp = Dispatcher()

MAX_TELEGRAM_LENGTH = 4096

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "Hello! Use /bind <code> to link your account.\n"
        "Use /mytasks to list your tasks.\n"
        "Use /done <id> to mark a task as done."
    )

@dp.message(Command("bind"))
async def cmd_bind(message: types.Message):
    args = message.text.replace("/bind", "").strip()
    if not args:
        await message.reply("Usage: /bind <code>")
        return

    data = {"code": args, "telegram_id": message.from_user.id}
    headers = {"X-BOT-SECRET": BOT_SECRET}
    url = f"{API_BASE.rstrip('/')}/accounts/api/bot/bind/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers, timeout=10) as resp:
                text = await resp.text()
                if resp.status == 200:
                    await message.reply("Successfully bound your account!")
                else:
                    await message.reply(f"Binding failed ({resp.status}): {text}")
        except Exception as e:
            await message.reply(f"Error reaching server: {e}")



@dp.message(Command("mytasks"))
async def cmd_mytasks(message: types.Message):
    headers = {"X-BOT-SECRET": BOT_SECRET}
    tg_id = str(message.from_user.id)
    url = f"{API_BASE.rstrip('/')}/api/tasks/?assigned_to_tg={tg_id}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if not data:
                        await message.reply("No tasks yet.")
                        return
                    text = "\n\n".join(
                        f"{t['id']}. {t['title']} — {'Done' if t['is_done'] else 'Pending'} "
                        f"(Created by: {t.get('created_by') or 'System'})"
                        for t in data
                    )
                    # truncate if too long
                    text = text[:MAX_TELEGRAM_LENGTH]
                    await message.reply(text)
                else:
                    await message.reply(f"Error fetching tasks: {resp.status}")
        except Exception as e:
            await message.reply(f"Server error: {e}")         
            

@dp.message(Command("done"))
async def cmd_done(message: types.Message):
    task_id = message.text.replace("/done", "").strip()
    if not task_id:
        await message.reply("Usage: /done <task_id>")
        return

    headers = {"X-BOT-SECRET": BOT_SECRET}
    url = f"{API_BASE.rstrip('/')}/api/tasks/{task_id}/done/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, timeout=10) as resp:
                text = await resp.text()
                if resp.status == 200:
                    await message.reply("Task marked as done!")
                else:
                    await message.reply(f"Failed to mark task ({resp.status}): {text}")
        except Exception as e:
            await message.reply(f"Server error: {e}")


async def main():
    async with Bot(token=BOT_TOKEN) as bot:
        logging.info(f"Starting bot @{(await bot.get_me()).username}")
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually")