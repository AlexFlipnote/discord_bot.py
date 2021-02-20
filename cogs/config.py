import time
import aiohttp
import discord
import importlib
import os
import sys
import json

from io import BytesIO
from discord.ext import commands
from utils import lists, permissions, http, default, argparser

server_id = cxt.guild.id

with open(f'ss_{server_id}.json', 'r') as server_config:
    data = server_config.read()
    obj = json.loads(data)

custom_server_prefix = str(obj['prefix'])
mod_log_channel = str(obj['mod_log_channel'])


class Server_Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()

    @commands.command()
    async def testmodlogs(self):
        channel = client.get_channel(mod_log_channel)
        await channel.send("ModLog test")


def setup(bot):
    bot.add_cog(Server_Config(bot))
