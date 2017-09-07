import json

from data import Bot
from assets import helper

description = """
A simple starter bot code
Made by AlexFlipnote
"""

print("Logging in...")

with open("config.json") as f:
    data = json.load(f)
    token = data["token"]
    prefix = data["prefix"]

help_attrs = dict(hidden=True)

bot = Bot(command_prefix=prefix, prefix=prefix, pm_help=True, help_attrs=help_attrs)
helper.loadcogs(bot, "cogs")
bot.run(token)
