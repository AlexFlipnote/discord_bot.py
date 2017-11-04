import discord
import json

from discord.ext.commands import errors

with open("config.json") as f:
    data = json.load(f)


class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.CommandInvokeError):
            await ctx.send(f"There was an error processing the command ;-;\n```diff\n- {err.original}\n```")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.0f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    async def status_change(self):
        await self.bot.wait_until_ready()
        while True:
            await self.bot.change_presence(game=discord.Game(type=0, name=data["playing"]))

    async def on_ready(self):
        print(f'Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}')


def setup(bot):
    bot.add_cog(Events(bot))
