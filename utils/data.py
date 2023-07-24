import os

from utils.config import Config
from discord.ext.commands import AutoShardedBot


class DiscordBot(AutoShardedBot):
    def __init__(self, config: Config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    async def setup_hook(self):
        for file in os.listdir("cogs"):
            if not file.endswith(".py"):
                # Skip non-python files
                continue

            await self.load_extension(
                # [:-3] is there to remove the .py extension
                f"cogs.{file[:-3]}"
            )

    """async def on_message(self, msg: discord.Message):
        if (
            not self.is_ready() or
            msg.author.bot or
            not permissions.can_handle(msg, "send_messages")
        ):
            return

        await self.process_commands(msg)"""

    """async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=default.CustomContext)
        await self.invoke(ctx)"""
