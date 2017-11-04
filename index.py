import json
import os

from data import Bot

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

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(token)
