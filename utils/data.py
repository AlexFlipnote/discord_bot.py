from typing import Any

import os

from utils.config import Config
from discord.ext.commands import AutoShardedBot


class DiscordBot(AutoShardedBot):
    def __init__(self, config: Config, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.config = config

    async def setup_hook(self) -> None:
        for file in os.listdir("cogs"):
            if not file.endswith(".py"):
                # Skip non-python files
                continue

            await self.load_extension(
                # [:-3] is there to remove the .py extension
                f"cogs.{file[:-3]}"
            )
