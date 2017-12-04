import json
import os

from discord.ext.commands import HelpFormatter
from data import Bot
from assets import permissions

description = """
A simple starter bot code
Made by AlexFlipnote
"""


class HelpFormat(HelpFormatter):
    async def format_help_for(self, context, command_or_bot):
        if permissions.can_react(context):
            await context.message.add_reaction(chr(0x2709))

        return await super().format_help_for(context, command_or_bot)


with open("config.json") as f:
    data = json.load(f)
    token = data["token"]
    prefix = data["prefix"]

print("Logging in...")
help_attrs = dict(hidden=True)
bot = Bot(command_prefix=prefix, prefix=prefix, pm_help=True, help_attrs=help_attrs, formatter=HelpFormat())

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(token)
