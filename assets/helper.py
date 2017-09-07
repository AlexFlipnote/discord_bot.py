import os
import json


def loadcogs(bot, target):
    for file in os.listdir(target):
        if file.endswith(".py"):
            name = file[:-3]
            bot.load_extension(f"{target}.{name}")


def loadgame():
    with open("config.json") as f:
        data = json.load(f)
        return data["playing"]
