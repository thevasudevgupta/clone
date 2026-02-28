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

import discord


class DiscordClient:
    def __init__(self):
        self.api_token = os.getenv("DISCORD_API_TOKEN")

        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)

        self.q = asyncio.Queue()

        @self.client.event
        async def on_ready():
            print(f"Discord Connected: {self.client.user}")
            for guild in self.client.guilds:
                print("Guild:", guild.name)
                for channel in guild.text_channels:
                    print(" - Channel:", channel.name, channel.id)

        @self.client.event
        async def on_message(message):
            if message.author.bot:
                return
            await self.q.put(
                {
                    "content": message.content,
                    "channel_id": message.channel.id,
                    "author": str(message.author),
                    "message_id": message.id,
                }
            )

    async def start(self):
        asyncio.create_task(self.client.start(self.api_token))
        # https://discordapp.com/channels/1476906398934630521/1477003441111826664
        await asyncio.sleep(2)
        await self.send_message("✅ tvgbot connected!", 1477003441111826664)

    async def send_message(self, text: str, channel_id: int):
        channel = self.client.get_channel(channel_id)
        return await channel.send(text)

    async def receive_message(self):
        return await self.q.get()
