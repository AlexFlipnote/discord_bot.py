import discord
import os

from utils import permissions
from discord.ext import commands
from discord.ext.commands import AutoShardedBot, DefaultHelpCommand


class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix

    async def setup_hook(self):
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                await self.load_extension(f"cogs.{name}")

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not permissions.can_handle(msg, "send_messages"):
            return

        await self.process_commands(msg)


class CustomHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page)
            await destination.send(embed=embed)
