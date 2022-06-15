import discord
import os

from utils import permissions
from discord.ext import commands
from discord.ext.commands import AutoShardedBot


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
    def get_destination(self, no_pm: bool = False):
        if no_pm:
            return self.context.channel
        else:
            return self.context.author

    async def send_error_message(self, error):
        destination = self.get_destination(no_pm=True)
        await destination.send(error)

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages(no_pm=True)
    
    async def send_pages(self, no_pm: bool = False):
        try:
            if permissions.can_handle(self.context, "add_reactions"):
                await self.context.message.add_reaction(chr(0x2709)) # Letter emoji
        except discord.Forbidden:
            pass

        try:
            destination = self.get_destination()
            for page in self.paginator.pages:
                embed = discord.Embed(description=page)
                await destination.send(embed=embed)
        except discord.Forbidden:
            destination = self.get_destination(no_pm=True)
            await destination.send("Couldn't send help to you due to blocked DMs...")