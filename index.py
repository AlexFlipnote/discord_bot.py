import os

from utils import default
from utils.data import ClientBot, HelpFormat

config = default.get("config.json")
print("Logging in...")

bot = ClientBot(
    command_prefix=config.prefix,
    prefix=config.prefix,
    command_attrs=dict(hidden=True),
    help_command=HelpFormat(),
)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

try:
    bot.run(config.token)
except Exception as e:
    print(f'Error when logging in: {e}')
