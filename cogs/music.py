import discord

from discord.ext import commands
from assets import http


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    @commands.command()
    async def radio(self, ctx):
        """ Play some lovely hardstyle music from a radio! """
        if ctx.invoked_subcommand is None:
            if ctx.author.voice is None:
                return await ctx.send("Join a voice channel first")
            if ctx.voice_client is not None:
                return await ctx.send(f"I'm already playing in **{ctx.author.voice.channel.name}**")

            vc = await ctx.author.voice.channel.connect(reconnect=True)
            vc.play(discord.FFmpegPCMAudio(source='http://20403.live.streamtheworld.com/WEB11_MP3_SC'))
            await ctx.send(f"Ready to play hardstyle in **{ctx.author.voice.channel.name}**")

    @commands.command(aliases=["np", "name", "song"])
    async def playing(self, ctx):
        """ Checks the song currently playing """
        if ctx.voice_client is None:
            return await ctx.send("I'm not connected to a voicechannel ;-;")

        req, r = await http.get('https://live.slam.nl/slam-hardstyle/metadata/hardstyle_livewall', as_json=True)

        if r is None:
            return await ctx.send("The API returned nothing... :(")

        embed = discord.Embed(colour=0x2ecc71, description=f"**Live from <https://live.slam.nl>**\n\n**{r['nowTitle']}** by {r['nowArtist']}")
        embed.set_thumbnail(url=r['nowImage'])

        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I found something, but have no access to post it... [ Embed permissions ]")

    @commands.command(aliases=["stop", "leave"])
    async def disconnect(self, ctx):
        """ Stops the hardstyle radio """
        if ctx.voice_client is None:
            return await ctx.send("I'm not playing...")
        if ctx.author.voice is None:
            return await ctx.send("You're not even in a voice channel...")
        if ctx.voice_client.channel.id is not ctx.author.voice.channel.id:
            return await ctx.send("Why are you trying to disconnect me from a different channel?")

        await ctx.voice_client.disconnect()
        await ctx.send(f"Disconnected From **{ctx.author.voice.channel.name}**")


def setup(bot):
    bot.add_cog(Music(bot))
