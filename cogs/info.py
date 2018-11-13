import time
import discord
import psutil
import os

from datetime import datetime
from discord.ext import commands
from utils import repo, default


class Information:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        message = await ctx.send("Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Pong   |   {int(ping)}ms")

    @commands.command(aliases=['joinme', 'join', 'botinvite'])
    async def invite(self, ctx):
        """ Invite me to your server """
        await ctx.send(f"**{ctx.author.name}**, use this URL to invite me\n<{discord.utils.oauth_url(self.bot.user.id)}>")

    @commands.command()
    async def source(self, ctx):
        """ Check out my source code <3 """
        await ctx.send(f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/AlexFlipnote/discord_bot.py")

    @commands.command(aliases=['supportserver', 'feedbackserver'])
    async def botserver(self, ctx):
        """ Get an invite to our support server! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 86484642730885120:
            return await ctx.send(f"**Here you go {ctx.author.name} 🍻\n<{repo.invite}>**")

        await ctx.send(f"**{ctx.author.name}** this is my home you know :3")

    @commands.command(aliases=['info', 'stats', 'status'])
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = round(len(self.bot.users) / len(self.bot.guilds))

        embed = discord.Embed(colour=ctx.me.top_role.colour)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Last boot", value=default.timeago(datetime.now() - self.bot.uptime), inline=True)
        embed.add_field(
            name=f"Developer{'' if len(self.config.owners) == 1 else 's'}",
            value=', '.join([str(self.bot.get_user(x)) for x in self.config.owners]),
            inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers} users/server )", inline=True)
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)

        await ctx.send(content=f"ℹ About **{ctx.bot.user}** | **{repo.version}**", embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
