import discord

from utils import config, data

config = config.Config.from_env(".env")
print("Logging in...")

bot = data.DiscordBot(
    config=config, command_prefix=config.discord_prefix,
    prefix=config.discord_prefix, command_attrs=dict(hidden=True),
    help_command=data.HelpFormat(),
    allowed_mentions=discord.AllowedMentions(
        everyone=False, roles=False, users=True
    ),
    intents=discord.Intents(
        # kwargs found at https://docs.pycord.dev/en/master/api.html?highlight=discord%20intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True,
        presences=True, message_content=True,
    )
)

try:
    bot.run(config.discord_token)
except Exception as e:
    print(f"Error when logging in: {e}")
