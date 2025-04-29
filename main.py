from pyrogram import Client, filters
from pyrogram.types import Message
from utils import get_latency, get_cpu_info, get_uptime
from getstring import create_string_session
from dotenv import load_dotenv
import asyncio, os

load_dotenv()

API_ID = int(os.getenv("BOT_API_ID"))
API_HASH = os.getenv("BOT_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_states = {}

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "👋 Selamat datang di Bot Pembuat String Session!\n\n"
        "**Perintah:**\n"
        "/getstring - Untuk mendapatkan string session Pyrogram\n"
        "/latensi - Untuk cek ping, uptime, dan CPU bot"
    )

@app.on_message(filters.command("latensi"))
async def latency(client, message: Message):
    ping = get_latency(message.date)
    uptime = get_uptime()
    cpu = get_cpu_info()
    await message.reply(f"🏓 Ping: `{ping} ms`\n⏱ Uptime: `{uptime}`\n🖥 CPU: `{cpu}`")

@app.on_message(filters.command("getstring"))
async def getstring(client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {"step": "awaiting_api_id"}
    await message.reply("🔐 Silakan kirim **API ID** Anda:")

@app.on_message(filters.private & filters.text)
async def input_handler(client, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if not state:
        return

    if state["step"] == "awaiting_api_id":
        if not message.text.isdigit():
            return await message.reply("❌ API ID harus berupa angka.")
        state["api_id"] = int(message.text)
        state["step"] = "awaiting_api_hash"
        await message.reply("🧩 Sekarang kirim **API HASH** Anda:")

    elif state["step"] == "awaiting_api_hash":
        state["api_hash"] = message.text.strip()
        await message.reply("⏳ Membuat string session, tunggu sebentar...")
        try:
            string = await create_string_session(state["api_id"], state["api_hash"])
            await message.reply(f"✅ Berhasil!\n\n`{string}`\n\n**Simpan baik-baik string session Anda.**")
        except Exception as e:
            await message.reply(f"❌ Gagal membuat string session:\n{e}")
        user_states.pop(user_id, None)

app.run()
