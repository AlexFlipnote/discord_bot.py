import discord
import asyncio

from discord.ext import commands
from assets import lists


class Radio:
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    @commands.group()
    @commands.guild_only()
    async def radio(self, ctx):
        """ 24/7 radio for your server! """
        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    async def radio_switch(self, ctx, target, stream):
        if ctx.author.voice is None:
            return await ctx.send("Join a voice channel first")

        if ctx.voice_client is not None:
            if ctx.voice_client.channel.id is not ctx.author.voice.channel.id:
                return await ctx.send("You can only switch streams if you're in my voicechannel ;-;")
            vc = ctx.voice_client
        else:
            try:
                vc = await ctx.author.voice.channel.connect(reconnect=True)
            except asyncio.TimeoutError:
                return await ctx.send("I couldn't establish a connection to your channel in time ;-;")

        status = {ctx.guild.id: target}
        self.players.update(status)  # Sets playing source

        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio(source=stream))
        await ctx.send(f"Ready to play {target} in **{ctx.voice_client.channel.name}**")

    @radio.command(name="hardstyle", aliases=["hs"])
    async def play_hardstyle(self, ctx):
        """ Let's party with hardstyle! """
        await self.radio_switch(ctx, 'hardstyle', 'http://20403.live.streamtheworld.com/WEB11_MP3_SC')

    @radio.command(name="p5")
    async def play_p5(self, ctx):
        """ Music from Norwegian radio """
        await self.radio_switch(ctx, 'P5', 'http://stream.p4.no/p5oslo_mp3_mq?Nettplayer_Oslo.P5.no')

    @radio.command(name="listen.moe", aliases=["lm"])
    async def play_listenmoe(self, ctx):
        """ Weeb music within Japanese/KPop stuff """
        await self.radio_switch(ctx, 'listenmoe', 'https://listen.moe/stream')

    @radio.command(name="kcrw")
    async def play_kcrw(self, ctx):
        """ Music from KCRW Radio """
        await self.radio_switch(ctx, 'kcrw', 'https://kcrw.streamguys1.com/kcrw_192k_mp3_e24_internet_radio')

    @commands.command(aliases=["np", "name", "song"])
    async def playing(self, ctx):
        """ Checks the song currently playing """
        if ctx.voice_client is None:
            return await ctx.send("I'm not connected to a voicechannel ;-;")

        if ctx.guild.id not in self.players:
            return await ctx.send("I couldn't determine what radio is playing ;-;")

        if self.players[ctx.guild.id] == "hardstyle":
            return await lists.hardstyle(ctx)
        if self.players[ctx.guild.id] == "listenmoe":
            return await lists.listenmoe(ctx)
        if self.players[ctx.guild.id] == "P5":
            return await lists.p5(ctx)
        if self.players[ctx.guild.id] == "kcrw":
            return await lists.kcrw(ctx)
        else:
            await ctx.send("Somehow, I didn't find out what radio is playing...")

    @commands.command(aliases=["stop", "leave"])
    async def disconnect(self, ctx, *, command: str = None):
        """ Stops the radio """
        if ctx.voice_client is None:
            return await ctx.send("I'm not playing...")

        if command == "force":
            if ctx.author.id == ctx.guild.owner.id:
                await ctx.voice_client.disconnect()
                return await ctx.send(f"🍻 Successfully force killed the music")
            else:
                return await ctx.send(f"📜 Only **{ctx.guild.owner}** can use this command, sorry")

        if ctx.author.voice is None:
            return await ctx.send("You're not even in a voice channel...")

        if ctx.voice_client.channel.id is not ctx.author.voice.channel.id:
            return await ctx.send("Why are you trying to disconnect me from a different channel?")

        channel_name = ctx.voice_client.channel.name
        await ctx.voice_client.disconnect()
        await ctx.send(f"Disconnected From **{channel_name}**")


def setup(bot):
    bot.add_cog(Radio(bot))
