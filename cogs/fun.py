import random
import discord
import secrets
import asyncio
import aiohttp

from io import BytesIO
from discord.ext import commands
from utils import permissions, http
from utils.data import DiscordBot
from discord import app_commands


class Fun_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @app_commands.command(name="8ball")
    async def eightball(self, ctx: discord.Interaction, *, question: str):
        """ Consult 8ball to receive an answer """
        ballresponse = [
            "Yes", "No", "Take a wild guess...", "Very doubtful",
            "Sure", "Without a doubt", "Most likely", "Might be possible",
            "You'll be the judge", "no... (╯°□°）╯︵ ┻━┻", "no... baka",
            "senpai, pls no ;-;"
        ]

        answer = random.choice(ballresponse)
        await ctx.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    async def randomimageapi(
        self, ctx: discord.Interaction,
        url: str, *endpoint: str
    ) -> discord.Message:
        try:
            r = await http.get(url, res_method="json")
        except aiohttp.ClientConnectorError:
            return await ctx.response.send_message("The API seems to be down...")
        except aiohttp.ContentTypeError:
            return await ctx.response.send_message("The API returned an error or didn't return JSON...")

        result = r.response
        for step in endpoint:
            result = result[step]

        await ctx.response.send_message(result)

    async def api_img_creator(
        self, ctx: discord.Interaction, url: str,
        filename: str, content: str = None
    ) -> discord.Message:
        async with ctx.channel.typing():
            req = await http.get(url, res_method="read")

            if not req.response:
                return await ctx.response.send_message("I couldn't create the image ;-;")

            bio = BytesIO(req.response)
            bio.seek(0)
            return await ctx.response.send_message(content=content, file=discord.File(bio, filename=filename))

    @app_commands.command()
    async def duck(self, ctx: discord.Interaction):
        """ Posts a random duck """
        await self.randomimageapi(ctx, "https://random-d.uk/api/v1/random", "url")

    @app_commands.command()
    async def coffee(self, ctx: discord.Interaction):
        """ Posts a random coffee """
        await self.randomimageapi(ctx, "https://coffee.alexflipnote.dev/random.json", "file")

    @app_commands.command()
    async def birb(self, ctx: discord.Interaction):
        """ Posts a random birb """
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/birb", "file")

    @app_commands.command()
    async def sadcat(self, ctx: discord.Interaction):
        """ Post a random sadcat """
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/sadcat", "file")

    @app_commands.command()
    async def cat(self, ctx: discord.Interaction):
        """ Posts a random cat """
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/cats", "file")

    @app_commands.command()
    async def dog(self, ctx: discord.Interaction):
        """ Posts a random dog """
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/dogs", "file")

    @app_commands.command()
    async def coinflip(self, ctx: discord.Interaction):
        """ Coinflip! """
        coinsides = ["Heads", "Tails"]
        await ctx.response.send_message(f"**{ctx.user.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @app_commands.command()
    async def f(self, ctx: discord.Interaction, *, text: str = None):
        """ Press F to pay respect """
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""
        await ctx.response.send_message(f"**{ctx.user.name}** has paid their respect {reason}{random.choice(hearts)}")

    @app_commands.command()
    async def urban(self, ctx: discord.Interaction, *, search: str):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            try:
                r = await http.get(f"https://api.urbandictionary.com/v0/define?term={search}", res_method="json")
            except Exception:
                return await ctx.response.send_message("Urban API returned invalid data... might be down atm.")

            if not r.response:
                return await ctx.response.send_message("I think the API broke...")
            if not len(r.response["list"]):
                return await ctx.response.send_message("Couldn't find your search in the dictionary...")

            result = sorted(r.response["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            await ctx.response.send_message(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")

    @app_commands.command()
    async def reverse(self, ctx: discord.Interaction, *, text: str):
        """ !poow ,ffuts esreveR
        Everything you type after reverse will of course, be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.response.send_message(
            f"🔁 {t_rev}",
            allowed_mentions=discord.AllowedMentions.none()
        )

    @app_commands.command()
    async def password(self, ctx: discord.Interaction, nbytes: int = 18):
        """ Generates a random password string for you

        This returns a random URL-safe text string, containing nbytes random bytes.
        The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        """
        if nbytes not in range(3, 1401):
            return await ctx.response.send_message("I only accept any numbers between 3-1400")
        if hasattr(ctx, "guild") and ctx.guild is not None:
            await ctx.response.send_message(f"Sending you a private message with your random generated password **{ctx.user.name}**")
        await ctx.user.response.send_message(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}")

    @app_commands.command()
    async def rate(self, ctx: discord.Interaction, *, thing: str):
        """ Rates what you desire """
        rate_amount = random.uniform(0.0, 100.0)
        await ctx.response.send_message(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    @app_commands.command()
    async def beer(self, ctx: discord.Interaction, user: discord.Member = None, *, reason: str = ""):
        """ Give someone a beer! 🍻 """
        if not user or user.id == ctx.user.id:
            return await ctx.response.send_message(f"**{ctx.user.name}**: paaaarty!🎉🍺")
        if user.id == self.bot.user.id:
            return await ctx.response.send_message("*drinks beer with you* 🍻")
        if user.bot:
            return await ctx.response.send_message(f"I would love to give beer to the bot **{ctx.user.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.user.name}**"
        beer_offer = f"{beer_offer}\n\n**Reason:** {reason}" if reason else beer_offer
        await ctx.response.send_message(content="Sent your beer request 🍻", silent=True, ephemeral=True)
        msg = await ctx.channel.send(beer_offer)
        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for("raw_reaction_add", timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.name}** and **{ctx.user.name}** are enjoying a lovely beer together 🍻")
            return True
        
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.channel.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.user.name}** ;-;")
        except discord.Forbidden:
            # Yeah so, bot doesn't have reaction permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.user.name}**"
            beer_offer = f"{beer_offer}\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @app_commands.command()
    async def hotcalc(self, ctx: discord.Interaction, *, user: discord.Member = None):
        """ Returns a random percent for how hot is a discord user """
        user = user or ctx.user
        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        match hot:
            case x if x > 75:
                emoji = "💞"
            case x if x > 50:
                emoji = "💖"
            case x if x > 25:
                emoji = "❤"
            case _:
                emoji = "💔"

        await ctx.response.send_message(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @app_commands.command()
    async def noticeme(self, ctx: discord.Interaction):
        """ Notice me senpai! owo """
        if not permissions.can_handle(ctx, "attach_files"):
            return await ctx.response.send_message("I cannot send images here ;-;")

        r = await http.get("https://i.alexflipnote.dev/500ce4.gif", res_method="read")
        await ctx.response.send_message(
            file=discord.File(
                BytesIO(r.response),
                filename="noticeme.gif"
            )
        )

    @app_commands.command()
    async def slot(self, ctx: discord.Interaction):
        """ Roll the slot machine """
        a, b, c = [random.choice("🍎🍊🍐🍋🍉🍇🍓🍒") for _ in range(3)]

        if (a == b == c):
            results = "All matching, you won! 🎉"
        elif (a == b) or (a == c) or (b == c):
            results = "2 in a row, you won! 🎉"
        else:
            results = "No match, you lost 😢"

        await ctx.response.send_message(f"**[ {a} {b} {c} ]\n{ctx.user.name}**, {results}")

    @app_commands.command()
    async def dice(self, ctx: discord.Interaction):
        """ Dice game. Good luck """
        bot_dice, player_dice = [random.randint(1, 6) for g in range(2)]

        results = "\n".join([
            f"**{self.bot.user.display_name}:** 🎲 {bot_dice}",
            f"**{ctx.user.display_name}** 🎲 {player_dice}"
        ])

        match player_dice:
            case x if x > bot_dice:
                final_message = "Congrats, you won 🎉"
            case x if x < bot_dice:
                final_message = "You lost, try again... 🍃"
            case _:
                final_message = "It's a tie 🎲"

        await ctx.response.send_message(f"{results}\n> {final_message}")

    @app_commands.command()
    async def roulette(self, ctx: discord.Interaction, picked_colour: str = None):
        """ Colours roulette """
        colour_table = ["blue", "red", "green", "yellow"]
        if not picked_colour:
            pretty_colours = ", ".join(colour_table)
            return await ctx.response.send_message(f"Please pick a colour from: {pretty_colours}")

        picked_colour = picked_colour.lower()
        if picked_colour not in colour_table:
            return await ctx.response.send_message("Please give correct color")

        chosen_color = random.choice(colour_table)
        msg = await ctx.response.send_message("Spinning 🔵🔴🟢🟡")
        await asyncio.sleep(2)
        result = f"Result: {chosen_color.upper()}"

        if chosen_color == picked_colour:
            return await msg.edit(content=f"> {result}\nCongrats, you won 🎉!")
        await msg.edit(content=f"> {result}\nBetter luck next time")


async def setup(bot):
    await bot.add_cog(Fun_Commands(bot))
