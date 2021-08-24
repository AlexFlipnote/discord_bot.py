import os
import discord

from utils import default
from utils.data import Bot, HelpFormat
from discord.ext import commands

config = default.config()
print("Logging in...")

bot = Bot(
    command_prefix=commands.when_mentioned_or(config["prefix"]),
    prefix=config["prefix"], strip_after_prefix=True,
    owner_ids=config["owners"], command_attrs=dict(hidden=True), help_command=HelpFormat(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
    intents=discord.Intents(  # kwargs found at https://discordpy.readthedocs.io/en/latest/api.html?highlight=intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True, presences=True
    )
)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

try:
    bot.run(config["token"])
except Exception as e:
    print(f"Error when logging in: {e}")
