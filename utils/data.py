import discord

from utils import permissions, default
from discord.ext.commands import AutoShardedBot, DefaultHelpCommand

config = default.get("config.json")


class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix

        # Check if user desires to have something other than online
        status = config.status_type.lower()
        if status == "idle":
            status_type = discord.Status.idle
        elif status in ("do not disturb", "dnd"):
            status_type = discord.Status.dnd
        else:
            status_type = discord.Status.online

        # Check if user desires to have a different type of activity
        activity = config.activity_type.lower()
        if activity == "listening":
            activity_type = discord.ActivityType.listening
        elif activity == "watching":
            activity_type = discord.ActivityType.watching
        elif activity == "competing":
            activity_type = discord.ActivityType.competing
        else:
            activity_type = discord.ActivityType.playing

        self.activity = discord.Activity(type = activity_type, name = config.activity)
        self.status = status_type

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not permissions.can_send(msg):
            return

        await self.process_commands(msg)


class HelpFormat(DefaultHelpCommand):
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
            if permissions.can_react(self.context):
                await self.context.message.add_reaction(chr(0x2709))
        except discord.Forbidden:
            pass

        try:
            destination = self.get_destination(no_pm=no_pm)
            for page in self.paginator.pages:
                await destination.send(page)
        except discord.Forbidden:
            destination = self.get_destination(no_pm=True)
            await destination.send("Couldn't send help to you due to blocked DMs...")
