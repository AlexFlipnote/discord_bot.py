import json
import logging
import os

from discord_http import Client, DiscordHTTP, Context
from discord_http.gateway import Intents, GatewayCacheFlags

with open("config.json", encoding="utf8") as f:
    config = json.load(f)
    config_debug = config.get("debug", {})


class CustomClient(Client):
    def __init__(self, config: dict, **kwargs):
        super().__init__(
            **kwargs,
            disable_http_server=True
        )

        # Types
        self.config: dict = config

        # Re-define to apply custom kwargs to the Context
        self.backend = DiscordHTTP(client=self)

        # Shortcuts
        self.http = self.state.http

    async def setup_hook(self):
        for file in os.listdir("./cogs"):
            if not file.endswith(".py"):
                continue
            await self.load_extension(f"cogs.{file[:-3]}")


class CustomContext(Context):
    """ Mostly used for types. """

    def __init__(self, bot: CustomClient, data: dict):
        super().__init__(bot, data)
        self.bot: CustomClient


client = CustomClient(
    token=config["token"],
    sync=config["sync"],
    guild_id=config_debug.get("guild_id"),
    config=config,
    logging_level=(
        logging.DEBUG
        if config_debug.get("logging")
        else logging.INFO
    ),
    intents=(
        # For now, we only need the guild intent
        Intents.guilds
    ),
    gateway_cache=(
        # You control what you want to store on the bot
        GatewayCacheFlags.guilds |
        GatewayCacheFlags.emojis |
        GatewayCacheFlags.roles |
        GatewayCacheFlags.channels |
        GatewayCacheFlags.threads |
        GatewayCacheFlags.stickers
    ),
)

client.start()
