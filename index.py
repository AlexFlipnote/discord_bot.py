import discord

from utils import default
from utils.data import Bot, HelpFormat

config = default.load_json()
print("Logging in...")

bot = Bot(
    command_prefix=config["prefix"], prefix=config["prefix"],
    owner_ids=config["owners"], command_attrs=dict(hidden=True), help_command=HelpFormat(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
    intents=discord.Intents(  # kwargs found at https://docs.pycord.dev/en/master/api.html?highlight=discord%20intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True, presences=True, message_content=True,
    )
)

try:
    bot.run(config["token"])
except Exception as e:
    print(f"Error when logging in: {e}")
