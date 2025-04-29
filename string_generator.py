import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded

async def generate_string_session(bot, message: Message):
    try:
        await message.reply("🔐 Silakan masukkan `API_ID` Anda:")
        
        # Menyimpan status pengguna untuk mendapatkan input berikutnya
        def check_api_id(msg: Message):
            return msg.chat.id == message.chat.id

        # Menunggu sampai pengguna memberi input
        api_id_msg = await bot.listen(message.chat.id, filters.text, timeout=120, check=check_api_id)
        api_id = int(api_id_msg.text)

        await message.reply("🔐 Sekarang masukkan `API_HASH` Anda:")
        def check_api_hash(msg: Message):
            return msg.chat.id == message.chat.id

        api_hash_msg = await bot.listen(message.chat.id, filters.text, timeout=120, check=check_api_hash)
        api_hash = api_hash_msg.text

        await message.reply("📞 Masukkan nomor telepon Anda (format internasional, contoh: +628123...):")
        def check_phone(msg: Message):
            return msg.chat.id == message.chat.id

        phone_msg = await bot.listen(message.chat.id, filters.text, timeout=120, check=check_phone)
        phone_number = phone_msg.text

        await message.reply("📲 Mengirim OTP ke akun Anda...")

        # Client in-memory
        user_client = Client(
            name="user_session",
            api_id=api_id,
            api_hash=api_hash,
            in_memory=True
        )

        await user_client.connect()
        sent_code = await user_client.send_code(phone_number)

        await message.reply("🔑 Masukkan kode OTP yang Anda terima (tanpa spasi):")
        def check_otp(msg: Message):
            return msg.chat.id == message.chat.id

        otp_msg = await bot.listen(message.chat.id, filters.text, timeout=120, check=check_otp)
        otp_code = otp_msg.text.strip().replace(" ", "")

        try:
            await user_client.sign_in(phone_number, sent_code.phone_code_hash, otp_code)
        except SessionPasswordNeeded:
            await message.reply("🔐 Anda perlu memasukkan password 2FA untuk melanjutkan.")
            await user_client.disconnect()
            return
        except Exception as e:
            await message.reply(f"❌ Gagal login: {e}")
            await user_client.disconnect()
            return

        string_session = await user_client.export_session_string()
        await user_client.disconnect()

        await message.reply("✅ **Berhasil!** String session Anda:\n\n"
                            f"```\n{string_session}\n```\n\n"
                            "⚠️ Jangan bagikan string ini ke siapapun!", quote=True)

    except asyncio.TimeoutError:
        await message.reply("⏰ Waktu habis. Silakan mulai kembali dengan perintah /getstring.")
    except Exception as e:
        await message.reply(f"❌ Terjadi kesalahan: {e}")
