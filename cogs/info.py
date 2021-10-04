import time
import discord
import psutil
import os
from PyDictionary import PyDictionary
import wikipedia

from discord.ext import commands
from utils import default, http


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command(aliases=["joinme", "join", "botinvite"])
    async def invite(self, ctx):
        """ Invite me to your server """
        await ctx.send(f"**{ctx.author.name}**, use this URL to invite me\n<{discord.utils.oauth_url(self.bot.user.id)}>")

    @commands.command()
    async def source(self, ctx):
        """ Check out my source code <3 """
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT, don't change output either.
        # Reference: https://github.com/AlexFlipnote/discord_bot.py/blob/master/LICENSE
        await ctx.send(f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/AlexFlipnote/discord_bot.py")

    @commands.command(aliases=["supportserver", "feedbackserver"])
    async def botserver(self, ctx):
        """ Get an invite to our support server! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 86484642730885120:
            return await ctx.send(f"**Here you go {ctx.author.name} 🍻**\nhttps://discord.gg/DpxkY3x")
        await ctx.send(f"**{ctx.author.name}** this is my home you know :3")

    @commands.command()
    async def covid(self, ctx, *, country: str):
        """Covid-19 Statistics for any countries"""
        async with ctx.channel.typing():
            r = await http.get(f"https://disease.sh/v3/covid-19/countries/{country.lower()}", res_method="json")

            if "message" in r:
                return await ctx.send(f"The API returned an error:\n{r['message']}")

            json_data = [
                ("Total Cases", r["cases"]), ("Total Deaths", r["deaths"]),
                ("Total Recover", r["recovered"]), ("Total Active Cases", r["active"]),
                ("Total Critical Condition", r["critical"]), ("New Cases Today", r["todayCases"]),
                ("New Deaths Today", r["todayDeaths"]), ("New Recovery Today", r["todayRecovered"])
            ]

            embed = discord.Embed(
                description=f"The information provided was last updated <t:{int(r['updated'] / 1000)}:R>"
            )

            for name, value in json_data:
                embed.add_field(
                    name=name, value=f"{value:,}" if isinstance(value, int) else value
                )

            await ctx.send(
                f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
                f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*",
                embed=embed
            )

            
    @commands.command(aliases=['dict', 'dic'])
    async def dictionary(self, ctx, *, keyword):
        dictionary = PyDictionary()

        def check(what_to_do):
            return ctx.author == what_to_do.author and what_to_do.channel == ctx.channel

        await ctx.send(embed=discord.Embed(title="What would you like to find?", color=discord.Color.random()))
        what_to_do = await self.bot.wait_for("message", check=check)

        try:
            if "meaning" in str(what_to_do.content).lower():
                try:
                    meaning = dictionary.meaning(keyword)
                    embed = discord.Embed(
                        title=f"The Meaning of {keyword}.", color=discord.Color.random())

                    if meaning.get('Noun') is not None:
                        for i in range(0, len(meaning['Noun'])):
                            embed.add_field(name=f"Noun Meaning {i + 1}:", value=f"{(meaning['Noun'])[i]}",
                                            inline=False)
                    if meaning.get('Verb') is not None:
                        for i in range(0, len(meaning['Verb'])):
                            embed.add_field(name=f"Verb Meaning {i + 1}:", value=f"{(meaning['Verb'])[i]}",
                                            inline=False)
                    await ctx.send(embed=embed)
                except:
                    await ctx.send(embed=discord.Embed(title='Meaning not found', color=discord.Color.random()))

            if "synonym" in str(what_to_do.content).lower():
                try:
                    synonym_list = dictionary.synonym(keyword)
                    string = ""
                    for i in range(0, len(synonym_list)):
                        string += f"{i + 1}. {synonym_list[i]}\n"
                    embed = discord.Embed(
                        title=f"The Synonyms of {keyword}.", description=string, color=discord.Color.random())
                    await ctx.send(embed=embed)
                except:
                    await ctx.send(embed=discord.Embed(title='Synonym not found', color=discord.Color.random()))

            if "antonym" in str(what_to_do.content).lower():
                try:
                    antonym_list = dictionary.antonym(keyword)
                    string = ""
                    for i in range(0, len(antonym_list)):
                        string += f"{i + 1}. {antonym_list[i]}\n"
                    embed = discord.Embed(
                        title=f"The Antonyms of the {keyword}.", description=string, color=discord.Color.random())
                    await ctx.send(embed=embed)
                except:
                    await ctx.send(embed=discord.Embed(title='Antonym not found', color=discord.Color.random()))

        except:
            embed = discord.Embed(title="Error! Could not find")
            await ctx.send(embed=embed)
            
    @commands.command()
    async def wiki(self, ctx, *, question):
        try:
            wiki = wikipedia.summary(question, 2)
            embed = discord.Embed(
                title="According to Wikipedia: ",
                description=f"{wiki}"
            )
            embed.set_footer(text="Information requested by: {}".format(
                ctx.author.display_name))
            embed.color = discord.Color.random()
            await ctx.send(embed=embed)
        except:
            await ctx.send(f"Could not find wikipedia results for: {question}")

    
    @commands.command(aliases=["info", "stats", "status"])
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)

        embedColour = discord.Embed.Empty
        if hasattr(ctx, "guild") and ctx.guild is not None:
            embedColour = ctx.me.top_role.colour

        embed = discord.Embed(colour=embedColour)
        embed.set_thumbnail(url=ctx.bot.user.avatar)
        embed.add_field(name="Last boot", value=default.date(self.bot.uptime, ago=True))
        embed.add_field(
            name=f"Developer{'' if len(self.config['owners']) == 1 else 's'}",
            value=", ".join([str(self.bot.get_user(x)) for x in self.config["owners"]])
        )
        embed.add_field(name="Library", value="discord.py")
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )")
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]))
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB")

        await ctx.send(content=f"ℹ About **{ctx.bot.user}**", embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
