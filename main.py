import os
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env file
load_dotenv()

# Get values from .env
bot_token = os.getenv("BOT_TOKEN")
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
mongo_uri = os.getenv("MONGO_URI")  # MongoDB URI

# Setup MongoDB client
client_mongo = MongoClient(mongo_uri)
db = client_mongo["sessions"]
collection = db["strings"]

# Create the Pyrogram Client instance
app = Client("my_bot", bot_token=bot_token, api_id=api_id, api_hash=api_hash)

# State to track the steps
user_state = {}

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
    # Track user state to manage steps
    user_state[message.from_user.id] = {"step": 1}
    await message.reply("Masukkan API_ID Anda:")

@app.on_message(filters.text)
async def handle_text(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_state:
        state = user_state[user_id]

        # Check the current step in the flow
        if state["step"] == 1:
            # Step 1: Get API_ID
            api_id = message.text
            user_state[user_id]["api_id"] = api_id
            user_state[user_id]["step"] = 2
            await message.reply("Masukkan API_HASH Anda:")
        
        elif state["step"] == 2:
            # Step 2: Get API_HASH
            api_hash = message.text
            user_state[user_id]["api_hash"] = api_hash
            user_state[user_id]["step"] = 3
            await message.reply("Masukkan nomor telepon Anda:")
        
        elif state["step"] == 3:
            # Step 3: Get Phone Number
            phone_number = message.text
            user_state[user_id]["phone_number"] = phone_number

            try:
                # Using API_ID, API_HASH, and phone number to generate session string
                async with Client("my_bot_session", api_id=int(user_state[user_id]["api_id"]), api_hash=user_state[user_id]["api_hash"]) as userbot:
                    # Sign in using phone number (this will automatically ask for the code if needed)
                    await userbot.sign_in(phone_number)
                    session_string = userbot.export_session_string()

                    # Save session string to MongoDB
                    collection.insert_one({"session_string": session_string, "user_id": user_id})

                    await message.reply(f"String session Anda: `{session_string}`")

                    # After sending the session string, delete it from MongoDB
                    collection.delete_one({"session_string": session_string})

            except Exception as e:
                await message.reply(f"Terjadi kesalahan: {str(e)}")

            # Clear the state after process is finished
            del user_state[user_id]

if __name__ == "__main__":
    app.run()
