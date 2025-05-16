import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from pymongo import MongoClient
from pyrogram.raw import functions

from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram import Client as UserClient

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

bot_app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

client = MongoClient(MONGO_URL)
db = client["string_bot"]
col = db["sessions"]

user_state = {}

@bot_app.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("Halo! Kirim /getstring untuk mulai membuat string session.")

@bot_app.on_message(filters.command("ping"))
async def ping(_, msg: Message):
    start = time.time()
    m = await msg.reply("Pong!")
    end = time.time()
    ms = (end - start) * 1000
    await m.edit(f"Bot latency: {ms:.2f} ms")

@bot_app.on_message(filters.command("getstring"))
async def get_string(_, msg: Message):
    user_state[msg.from_user.id] = {"step": "api_id"}
    await msg.reply("Masukkan API_ID Anda:")

@bot_app.on_message(filters.text & ~filters.command(["start", "ping", "getstring"]))
async def handle_steps(_, msg: Message):
    user_id = msg.from_user.id
    if user_id not in user_state:
        return

    state = user_state[user_id]

    if state["step"] == "api_id":
        state["api_id"] = int(msg.text.strip())
        state["step"] = "api_hash"
        await msg.reply("Masukkan API_HASH Anda:")

    elif state["step"] == "api_hash":
        state["api_hash"] = msg.text.strip()
        state["step"] = "phone"
        await msg.reply("Masukkan nomor telepon Anda:")

    elif state["step"] == "phone":
        phone = msg.text.strip()
        api_id = state["api_id"]
        api_hash = state["api_hash"]

        await msg.reply("Sedang mengirim kode OTP ke Telegram Anda...")

        user_client = UserClient(name=str(user_id), api_id=api_id, api_hash=api_hash, in_memory=True)

        try:
            await user_client.connect()
            sent = await user_client.send_code(phone)
            state["phone_code_hash"] = sent.phone_code_hash
            state["phone"] = phone
            state["step"] = "code"
            state["user_client"] = user_client
            await msg.reply("Masukkan kode OTP yang dikirim ke Telegram Anda (cth: 12345):")
        except Exception as e:
            await msg.reply(f"Gagal mengirim kode OTP:\n`{e}`")
            user_state.pop(user_id, None)

    elif state["step"] == "code":
        code = msg.text.replace(" ", "").strip()
        user_client: UserClient = state["user_client"]
        try:
            await user_client.sign_in(
                phone_number=state["phone"],
                phone_code_hash=state["phone_code_hash"],
                phone_code=code
            )

            string_session = await user_client.export_session_string()
            await msg.reply(f"✅ Berhasil! Ini string Anda:\n\n`{string_session}`", parse_mode=ParseMode.MARKDOWN)

            # Simpan ke MongoDB
            col.insert_one({
                "user_id": user_id,
                "string": string_session,
                "created_at": time.time()
            })

            await user_client.disconnect()
            del user_state[user_id]

        except Exception as e:
            await msg.reply(f"Gagal login:\n`{e}`")
            del user_state[user_id]

bot_app.run()
