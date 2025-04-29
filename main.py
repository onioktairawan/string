from pyrogram import Client, filters
from pyrogram.types import Message

app = Client("my_bot", bot_token="7768837888:AAFp9J3EwuaNL_c7MRXAzbFWdI2uYyM1Mhw")

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "Halo! Saya bot yang dapat membantu Anda menghasilkan string session Pyrogram.\n"
        "Gunakan /ping untuk melihat latensi bot, dan /getstring untuk menghasilkan string session Pyrogram."
    )

@app.on_message(filters.command("ping"))
async def ping(client, message: Message):
    import time
    start_time = time.time()
    await message.reply("Pong!")
    ping_time = time.time() - start_time
    await message.reply(f"Bot latency: {ping_time*1000:.2f} ms")

@app.on_message(filters.command("getstring"))
async def get_string(client, message: Message):
    await message.reply("Masukkan API_ID Anda:")

    @app.on_message(filters.text)
    async def get_api_id(client, message: Message):
        api_id = message.text
        await message.reply("Masukkan API_HASH Anda:")

        @app.on_message(filters.text)
        async def get_api_hash(client, message: Message):
            api_hash = message.text
            await message.reply("Masukkan nomor telepon Anda:")

            @app.on_message(filters.text)
            async def get_phone_number(client, message: Message):
                phone_number = message.text
                try:
                    # Menggunakan API_ID, API_HASH, dan nomor telepon untuk menghasilkan string session
                    async with Client("my_bot_session", api_id=int(api_id), api_hash=api_hash) as userbot:
                        await userbot.send_message(phone_number, "Testing connection...")
                        session_string = userbot.export_session_string()
                        await message.reply(f"String session Anda: `{session_string}`")
                except Exception as e:
                    await message.reply(f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    app.run()
