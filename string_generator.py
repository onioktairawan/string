from pyrogram import Client
import asyncio
import io

async def create_string_session(api_id, api_hash):
    output = io.StringIO()

    async with Client(
        name="session",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True
    ) as app:
        string = await app.export_session_string()
        output.write(string)

    return output.getvalue()
