import os
import time
import psutil
from datetime import timedelta
from pyrogram import Client, filters
from dotenv import load_dotenv
import pymongo
from pyrogram.errors import PhoneNumberInvalid
from pyrogram.client import Client as PyrogramClient

# Memuat variabel dari .env
load_dotenv()

# Ambil informasi dari .env
bot_token = os.getenv("BOT_TOKEN")
mongo_uri = os.getenv("MONGO_URI")
owner_api_id = os.getenv("OWNER_API_ID")
owner_api_hash = os.getenv("OWNER_API_HASH")

# Setup client Pyrogram untuk bot
app = Client("my_bot", bot_token=bot_token)

# Setup MongoDB Client
client = pymongo.MongoClient(mongo_uri)
db = client['telegram_sessions']
collection = db['sessions']

# Fungsi untuk mendapatkan latensi, uptime, dan penggunaan CPU
@app.on_message(filters.command("latensi"))
async def latensi_handler(client, message):
    start_time = time.time()

    # Menghitung latency (ping)
    latency = round((time.time() - start_time) * 1000, 2)
    
    # Mendapatkan uptime bot dalam format waktu
    uptime_seconds = time.time() - message.date.timestamp()
    uptime = str(timedelta(seconds=round(uptime_seconds)))
    
    # Mendapatkan CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Menampilkan hasil latensi, uptime, dan CPU usage
    await message.reply(
        f"🏓 Ping: {latency} ms\n"
        f"⏱️ Uptime: {uptime}\n"
        f"🖥 CPU: {cpu_usage}%"
    )

# Fungsi untuk menangani perintah /getstring
@app.on_message(filters.command("getstring"))
async def get_string_handler(client, message):
    # Memberikan instruksi kepada user
    await message.reply("📥 Kirim API ID Anda:")
    
    @app.on_message(filters.text)
    async def get_api_id(client, msg):
        api_id = msg.text
        await msg.reply("🧩 Kirim API HASH Anda:")
        
        @app.on_message(filters.text)
        async def get_api_hash(client, msg):
            api_hash = msg.text
            await msg.reply("📱 Kirim Nomor Telepon Anda (format internasional, contoh: +628xxxxxxxxx):")
            
            @app.on_message(filters.text)
            async def get_phone_number(client, msg):
                phone_number = msg.text
                try:
                    # Proses login ke Telegram menggunakan API ID, API HASH, dan nomor telepon
                    await client.send_code(phone_number, api_id=api_id, api_hash=api_hash)
                    await msg.reply("📤 Kode verifikasi telah dikirim ke Telegram Anda. Silakan tunggu...")
                    
                    # Setelah verifikasi berhasil, simpan string session di MongoDB
                    session_string = await client.export_session_string()
                    collection.insert_one({"user_id": msg.from_user.id, "session_string": session_string})
                    await msg.reply(f"📥 String session Anda:\n{session_string}")
                    
                    # Hapus string session dari database setelah dikirim
                    collection.delete_one({"user_id": msg.from_user.id})
                except PhoneNumberInvalid:
                    await msg.reply("❌ Nomor telepon tidak valid. Silakan coba lagi.")
                except Exception as e:
                    await msg.reply(f"❌ Terjadi kesalahan: {e}")

# Fungsi untuk memulai bot
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply(
        "Selamat datang! Gunakan perintah /getstring untuk mendapatkan string session Anda.\n"
        "Gunakan /latensi untuk memeriksa ping dan uptime bot."
    )

# Jalankan bot
app.run()
