import random
import discord
import secrets
import asyncio
import aiohttp

from io import BytesIO
from utils.default import CustomContext
from discord.ext import commands
from utils import permissions, http
from utils.data import DiscordBot


class Fun_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.command(aliases=["8ball"])
    async def eightball(self, ctx: CustomContext, *, question: commands.clean_content):
        """ Consult 8ball to receive an answer """
        ballresponse = [
            "Yes", "No", "Take a wild guess...", "Very doubtful",
            "Sure", "Without a doubt", "Most likely", "Might be possible",
            "You'll be the judge", "no... (╯°□°）╯︵ ┻━┻", "no... baka",
            "senpai, pls no ;-;", "It is certain.", "Ask again later.",
            "Better not tell you now.", "Don't count on it.", "My sources say no.",
            "Outlook not so good."
        ]

        answer = random.choice(ballresponse)
        await ctx.send(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    async def randomimageapi(
        self, ctx: CustomContext,
        url: str, *endpoint: str
    ) -> discord.Message:
        try:
            r = await http.get(url, res_method="json")
        except aiohttp.ClientConnectorError:
            return await ctx.send("The API seems to be down...")
        except aiohttp.ContentTypeError:
            return await ctx.send("The API returned an error or didn't return JSON...")

        result = r.response
        for step in endpoint:
            result = result[step]

        await ctx.send(result)

    async def api_img_creator(
        self, ctx: CustomContext, url: str,
        filename: str, content: str = None
    ) -> discord.Message:
        async with ctx.channel.typing():
            req = await http.get(url, res_method="read")

            if not req.response:
                return await ctx.send("I couldn't create the image ;-;")

            bio = BytesIO(req.response)
            bio.seek(0)
            return await ctx.send(content=content, file=discord.File(bio, filename=filename))

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, ctx: CustomContext):
        """ Posts a random duck """
        await self.randomimageapi(ctx, "https://random-d.uk/api/v1/random", "url")

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def coffee(self, ctx: CustomContext):
        """ Posts a random coffee """
        await self.randomimageapi(ctx, "https://coffee.alexflipnote.dev/random.json", "file")

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def birb(self, ctx: CustomContext):
        """ Posts a random birb """
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/birb", "file")

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def sadcat(self, ctx: CustomContext):
        """ Post a random sadcat """
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/sadcat", "file")

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def cat(self, ctx: CustomContext):
        """ Posts a random cat """
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/cats", "file")

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def dog(self, ctx: CustomContext):
        """ Posts a random dog """
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/dogs", "file")

    @commands.command(aliases=["flip", "coin"])
    async def coinflip(self, ctx: CustomContext):
        """ Coinflip! """
        coinsides = ["Heads", "Tails"]
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @commands.command()
    async def f(self, ctx: CustomContext, *, text: commands.clean_content = None):
        """ Press F to pay respect """
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

    @commands.command()
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def urban(self, ctx: CustomContext, *, search: commands.clean_content):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            try:
                r = await http.get(f"https://api.urbandictionary.com/v0/define?term={search}", res_method="json")
            except Exception:
                return await ctx.send("Urban API returned invalid data... might be down atm.")

            if not r.response:
                return await ctx.send("I think the API broke...")
            if not len(r.response["list"]):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(r.response["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            await ctx.send(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")

    @commands.command()
    async def reverse(self, ctx: CustomContext, *, text: str):
        """ !poow ,ffuts esreveR
        Everything you type after reverse will of course, be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(
            f"🔁 {t_rev}",
            allowed_mentions=discord.AllowedMentions.none()
        )

    @commands.command()
    async def password(self, ctx: CustomContext, nbytes: int = 18):
        """ Generates a random password string for you

        This returns a random URL-safe text string, containing nbytes random bytes.
        The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        """
        if nbytes not in range(3, 1401):
            return await ctx.send("I only accept any numbers between 3-1400")
        if hasattr(ctx, "guild") and ctx.guild is not None:
            await ctx.send(f"Sending you a private message with your random generated password **{ctx.author.name}**")
        await ctx.author.send(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}")

    @commands.command()
    async def rate(self, ctx: CustomContext, *, thing: commands.clean_content):
        """ Rates what you desire """
        rate_amount = random.uniform(0.0, 100.0)
        await ctx.send(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    @commands.command()
    async def beer(self, ctx: CustomContext, user: discord.Member = None, *, reason: commands.clean_content = ""):
        """ Give someone a beer! 🍻 """
        if not user or user.id == ctx.author.id:
            return await ctx.send(f"**{ctx.author.name}**: paaaarty!🎉🍺")
        if user.id == self.bot.user.id:
            return await ctx.send("*drinks beer with you* 🍻")
        if user.bot:
            return await ctx.send(f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.author.name}**"
        beer_offer = f"{beer_offer}\n\n**Reason:** {reason}" if reason else beer_offer
        msg = await ctx.send(beer_offer)

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for("raw_reaction_add", timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.name}** and **{ctx.author.name}** are enjoying a lovely beer together 🍻")
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            # Yeah so, bot doesn't have reaction permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = f"{beer_offer}\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @commands.command(aliases=["howhot", "hot"])
    async def hotcalc(self, ctx: CustomContext, *, user: discord.Member = None):
        """ Returns a random percent for how hot is a discord user """
        user = user or ctx.author
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

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command(aliases=["noticemesenpai"])
    async def noticeme(self, ctx: CustomContext):
        """ Notice me senpai! owo """
        if not permissions.can_handle(ctx, "attach_files"):
            return await ctx.send("I cannot send images here ;-;")

        r = await http.get("https://i.alexflipnote.dev/500ce4.gif", res_method="read")
        bio = BytesIO(r.response)
        await ctx.send(file=discord.File(bio, filename="noticeme.gif"))

    @commands.command(aliases=["slots", "bet"])
    async def slot(self, ctx: CustomContext):
        """ Roll the slot machine """
        a, b, c = [random.choice("🍎🍊🍐🍋🍉🍇🍓🍒") for _ in range(3)]

        if (a == b == c):
            results = "All matching, you won! 🎉"
        elif (a == b) or (a == c) or (b == c):
            results = "2 in a row, you won! 🎉"
        else:
            results = "No match, you lost 😢"

        await ctx.send(f"**[ {a} {b} {c} ]\n{ctx.author.name}**, {results}")

    @commands.command()
    async def dice(self, ctx: CustomContext):
        """ Dice game. Good luck """
        bot_dice, player_dice = [random.randint(1, 6) for g in range(2)]

        results = "\n".join([
            f"**{self.bot.user.display_name}:** 🎲 {bot_dice}",
            f"**{ctx.author.display_name}** 🎲 {player_dice}"
        ])

        match player_dice:
            case x if x > bot_dice:
                final_message = "Congrats, you won 🎉"
            case x if x < bot_dice:
                final_message = "You lost, try again... 🍃"
            case _:
                final_message = "It's a tie 🎲"

        await ctx.send(f"{results}\n> {final_message}")

    @commands.command(aliases=["roul"])
    async def roulette(self, ctx: CustomContext, picked_colour: str = None):
        """ Colours roulette """
        colour_table = ["blue", "red", "green", "yellow"]
        if not picked_colour:
            pretty_colours = ", ".join(colour_table)
            return await ctx.send(f"Please pick a colour from: {pretty_colours}")

        picked_colour = picked_colour.lower()
        if picked_colour not in colour_table:
            return await ctx.send("Please give correct color")

        chosen_color = random.choice(colour_table)
        msg = await ctx.send("Spinning 🔵🔴🟢🟡")
        await asyncio.sleep(2)
        result = f"Result: {chosen_color.upper()}"

        if chosen_color == picked_colour:
            return await msg.edit(content=f"> {result}\nCongrats, you won 🎉!")
        await msg.edit(content=f"> {result}\nBetter luck next time")

    @commands.command()
    async def randomfact(self, ctx: CustomContext):
        """Sends a random fun fact."""
        facts = [
            "Honey never spoils.",
            "A day on Venus is longer than a year on Venus.",
            "Octopuses have three hearts.",
            "Bananas are berries, but strawberries aren't.",
            "A group of flamingos is called a 'flamboyance'.",
            "Sloths can hold their breath longer than dolphins by slowing their heart rate.",
            "Some turtles can breathe through their butts."
        ]
        fact = random.choice(facts)
        await ctx.send(f"🧠 Fun Fact: {fact}")


async def setup(bot):
    await bot.add_cog(Fun_Commands(bot))
