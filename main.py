from pyrogram import Client, filters
from pyrogram.types import Message
from getstring import create_user_string
from utils import get_latency, get_cpu_info, get_uptime
from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("BOT_API_ID"))
API_HASH = os.getenv("BOT_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_states = {}

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply(
        "👋 Selamat datang di Bot Pembuat String Session!\n\n"
        "**Perintah yang tersedia:**\n"
        "/getstring - Buat string session dengan login user Telegram\n"
        "/latensi - Cek ping, uptime, dan info CPU bot"
    )

@app.on_message(filters.command("latensi"))
async def latensi_handler(client, message: Message):
    ping = get_latency(message.date)
    uptime = get_uptime()
    cpu = get_cpu_info()
    await message.reply(f"🏓 Ping: `{ping} ms`\n⏱ Uptime: `{uptime}`\n🖥 CPU: `{cpu}`")

@app.on_message(filters.command("getstring"))
async def getstring_handler(client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {"step": "awaiting_api_id"}
    await message.reply("📥 Kirim **API ID** Anda:")

@app.on_message(filters.private & filters.text)
async def input_handler(client, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if not state:
        return

    text = message.text.strip()

    if state["step"] == "awaiting_api_id":
        if not text.isdigit():
            return await message.reply("❌ API ID harus berupa angka.")
        state["api_id"] = int(text)
        state["step"] = "awaiting_api_hash"
        await message.reply("🧩 Kirim **API HASH** Anda:")

    elif state["step"] == "awaiting_api_hash":
        state["api_hash"] = text
        state["step"] = "awaiting_phone"
        await message.reply("📱 Kirim **Nomor Telepon** Anda (format internasional, contoh: `+628xxxxxxxxx`):")

    elif state["step"] == "awaiting_phone":
        state["phone"] = text
        await message.reply("📤 Kode verifikasi akan dikirim ke Telegram Anda. Silakan tunggu...")

        async def ask_code(phone, app_session):
            await client.send_message(user_id, "🔑 Silakan masukkan **kode verifikasi** dari Telegram:")
            state["step"] = "awaiting_code"
            state["app_session"] = app_session
            return await wait_user_input(user_id)

        async def ask_password():
            await client.send_message(user_id, "🔒 Akun Anda memiliki verifikasi dua langkah.\nKirimkan **password akun Telegram** Anda:")
            return await wait_user_input(user_id)

        try:
            string_session, name = await create_user_string(
                state["api_id"],
                state["api_hash"],
                state["phone"],
                ask_code,
                ask_password
            )
            await message.reply(
                f"✅ String session berhasil dibuat!\n\n`{string_session}`\n\n📨 Juga telah dikirim ke *Pesan Tersimpan* Anda, {name}."
            )
        except Exception as e:
            await message.reply(f"❌ Gagal: {e}")

        user_states.pop(user_id, None)

async def wait_user_input(user_id):
    import asyncio

    loop = asyncio.get_event_loop()
    future = loop.create_future()

    def response_handler(client, msg: Message):
        if msg.from_user.id == user_id:
            future.set_result(msg.text)
            app.remove_handler(handler)

    handler = app.add_handler(filters.private & filters.text, response_handler)
    return await future

app.run()
