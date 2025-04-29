import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import get_uptime, get_system_stats, get_ping
from string_generator import generate_string_session

# Load .env file
load_dotenv()

# Ambil variabel dari .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# Inisialisasi Bot
bot = Client("getstring_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Start command
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    await message.reply(
        "**🤖 Selamat datang di String Session Generator Bot!**\n\n"
        "**Berikut perintah yang tersedia:**\n"
        "`/getstring` - Buat string session akun Telegram Anda\n"
        "`/latensi` - Cek kecepatan bot dan penggunaan CPU\n"
        "\n📌 Jangan bagikan string session Anda ke orang lain!"
    )

# Getstring command
@bot.on_message(filters.command("getstring") & filters.private)
async def get_string_handler(_, message: Message):
    await generate_string_session(bot, message)

# Latency / status command
@bot.on_message(filters.command("latensi") & filters.private)
async def latency_handler(_, message: Message):
    stats = get_system_stats()
    ping = get_ping(message.date)
    uptime = get_uptime()

    await message.reply(
        f"**Ping:** `{ping} ms`\n"
        f"**CPU:** `{stats['cpu']}%`\n"
        f"**RAM:** `{stats['ram']}%`\n"
        f"**Uptime:** `{uptime}`"
    )

if __name__ == "__main__":
    print("Bot sedang berjalan... cek di bot anda")
    bot.run()
