import time
import aiohttp
import discord
import importlib
import os
import sys
import json

from discord.ext import commands
from utils import permissions, default, http

server_id = cxt.guild.id

with open(f'ss_{server_id}.json', 'r') as server_config:
    data = server_config.read()
    obj = json.loads(data)

custom_server_prefix = str(obj['prefix'])
mod_log_channel = str(obj['mod_log_channel'])
