# uv pip install discord.py

# https://discord.com/developers/applications
# Go to bot page
# Enable: Message Content Intent

# Go to OAuth2
# Enable: bot
# Enable: View Channels
# Enable: Read Message History
# Enable: Send Messages
# Copy, paste the generated URL to browser & approve

import asyncio
import os
from typing import Optional

import discord


class DiscordClient:
    def __init__(self):
        self.tvgbot_channel_id = 1477003441111826664
        self.api_token = os.getenv("DISCORD_API_TOKEN")

        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)

        self.q = asyncio.Queue()
        self.bot_last_message = None

        @self.client.event
        async def on_ready():
            print(f"Discord Connected: {self.client.user}")
            for guild in self.client.guilds:
                print("Guild:", guild.name)
                for channel in guild.text_channels:
                    print(" - Channel:", channel.name, channel.id)

        @self.client.event
        async def on_message(message):
            if message.channel.id == self.tvgbot_channel_id:
                data = {
                    "content": message.content,
                    "channel_id": message.channel.id,
                    "author": str(message.author),
                    "message_id": message.id,
                }
                if message.author.bot:
                    self.bot_last_message = data
                    return
                await self.q.put(data)

    async def start(self):
        asyncio.create_task(self.client.start(self.api_token))
        await asyncio.sleep(2)
        await self.send_message("✅ tvgbot connected!", self.tvgbot_channel_id)

    async def send_message(
        self, text: str, channel_id: int, message_id: Optional[int] = None
    ):
        channel = await self.client.fetch_channel(channel_id)
        if message_id is None:
            return await channel.send(text)
        message = await channel.fetch_message(message_id)
        thread = (
            message.thread
            if message.thread
            else await message.create_thread(name="Auto Thread")
        )
        return await thread.send(text)

    async def receive_message(self):
        return await self.q.get()
