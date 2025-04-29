from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
import asyncio
import os

async def create_user_string(api_id, api_hash, phone_number, send_code_func, ask_password_func):
    session_name = f"sessions/{phone_number}"
    app = Client(session_name, api_id=api_id, api_hash=api_hash)

    await app.connect()
    if not await app.check_authorization():
        code = await send_code_func(phone_number, app)
        try:
            await app.sign_in(phone_number, code)
        except SessionPasswordNeeded:
            password = await ask_password_func()
            await app.check_password(password)

    string_session = await app.export_session_string()
    me = await app.get_me()
    await app.send_message("me", f"✅ Ini string session Anda:\n\n`{string_session}`\n\n🔐 Jangan bagikan ke siapa pun!")
    await app.disconnect()

    return string_session, me.first_name
