import aiohttp
import random
import secrets

from discord_http import commands, Context, AllowedMentions, Member, DeferResponse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..index import CustomClient


class FunCommands(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot: CustomClient = bot

    @commands.command(name="8ball")
    @commands.describe(
        question="The question you want want answers too",
    )
    async def eightball(self, ctx: Context, question: str):
        """ Consult 8ball to receive an answer. """
        ballresponse = [
            "Yes", "No", "Take a wild guess...", "Very doubtful",
            "Sure", "Without a doubt", "Most likely", "Might be possible",
            "You'll be the judge", "no... (╯°□°）╯︵ ┻━┻", "no... baka",  # ruff: ignore[ambiguous-unicode-character-string]
            "senpai, pls no ;-;"
        ]

        return ctx.response.send_message(
            f"🎱 **Question:** {question}\n"
            f"**Answer:** {random.choice(ballresponse)}"
        )

    async def randomimageapi(
        self, ctx: Context,
        url: str, *endpoint: str
    ) -> DeferResponse:
        async def call_after():
            try:
                r = await self.bot.http.request("GET", url, res_method="json")
            except aiohttp.ClientConnectorError:
                return await ctx.edit_original_response(content="The API seems to be down...")
            except aiohttp.ContentTypeError:
                return await ctx.edit_original_response(content="The API returned an error or didn't return JSON...")

            result = r.response
            for step in endpoint:
                result = result[step]

            return await ctx.edit_original_response(content=str(result))

        return ctx.response.defer(thinking=True, call_after=call_after)

    @commands.command()
    async def duck(self, ctx: Context):
        """ Posts a random duck. """
        return await self.randomimageapi(ctx, "https://random-d.uk/api/v1/random", "url")

    @commands.command()
    async def coffee(self, ctx: Context):
        """ Posts a random coffee. """
        return await self.randomimageapi(ctx, "https://coffee.alexflipnote.dev/random.json", "file")

    @commands.command()
    async def birb(self, ctx: Context):
        """ Posts a random birb. """
        return await self.randomimageapi(ctx, "https://api.alexflipnote.dev/birb", "file")

    @commands.command()
    async def sadcat(self, ctx: Context):
        """ Post a random sadcat. """
        return await self.randomimageapi(ctx, "https://api.alexflipnote.dev/sadcat", "file")

    @commands.command()
    async def cat(self, ctx: Context):
        """ Posts a random cat. """
        return await self.randomimageapi(ctx, "https://api.alexflipnote.dev/cats", "file")

    @commands.command()
    async def dog(self, ctx: Context):
        """ Posts a random dog. """
        return await self.randomimageapi(ctx, "https://api.alexflipnote.dev/dogs", "file")

    @commands.command()
    async def coinflip(self, ctx: Context):
        """ Coinflip! """
        coinsides = ["Heads", "Tails"]

        return ctx.response.send_message(
            f"**{ctx.user.name}** flipped a coin and got "
            f"**{random.choice(coinsides)}**!"
        )

    @commands.command()
    @commands.describe(
        text="What are we paying respect for?"
    )
    async def f(self, ctx: Context, text: str | None = None):
        """ Press F to pay respect. """
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""

        return ctx.response.send_message(
            f"**{ctx.user.name}** has paid their respect "
            f"{reason}{random.choice(hearts)}"
        )

    @commands.command()
    @commands.describe(
        search="The search term you want to search for"
    )
    async def urban(self, ctx: Context, search: str):
        """ Find the 'best' definition to your words. """
        async def call_after():
            try:
                r = await self.bot.http.request(
                    "GET",
                    f"https://api.urbandictionary.com/v0/define?term={search}",
                    res_method="json"
                )
            except Exception:
                return await ctx.edit_original_response(content="Urban API returned invalid data... might be down atm.")

            if not r.response:
                return await ctx.edit_original_response(content="I think the API broke...")
            if not len(r.response["list"]):
                return await ctx.edit_original_response(content="Couldn't find your search in the dictionary...")

            result = max(r.response["list"], key=lambda g: int(g["thumbs_up"]))

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            return await ctx.edit_original_response(
                content=f"📚 Definitions for **{result['word']}**```fix\n{definition}```"
            )

        return ctx.response.defer(thinking=True, call_after=call_after)

    @commands.command()
    @commands.describe(
        text="The text you want to reverse"
    )
    async def reverse(self, ctx: Context, text: str):
        """ !poow ,ffuts esreveR """  # ruff: ignore[missing-terminal-punctuation]
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        return ctx.response.send_message(
            f"🔁 {t_rev}",
            allowed_mentions=AllowedMentions.none()
        )

    @commands.command()
    @commands.describe(
        nbytes="The number of bytes you want to generate a password for"
    )
    async def password(self, ctx: Context, nbytes: commands.Range[int, 3, 1400] = 14):
        """ Generates a random password string for you. """
        return ctx.response.send_message(
            f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}",
            ephemeral=True
        )

    @commands.command()
    @commands.describe(
        thing="The thing you want to rate"
    )
    async def rate(self, ctx: Context, thing: str):
        """ Rates what you desire. """
        rate_amount = random.uniform(0.0, 100.0)
        return ctx.response.send_message(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    @commands.command()
    @commands.describe(
        user="The user you want to rate, leave empty to rate yourself"
    )
    async def hotcalc(self, ctx: Context, member: Member | None = None):
        """ Returns a random percent for how hot is a discord user. """
        member = member or ctx.user  # pyright: ignore[reportAssignmentType]
        random.seed(member.id)
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

        return ctx.response.send_message(
            f"**{member.display_name}** is **{hot:.2f}%** hot {emoji}"
        )

    @commands.command()
    async def slot(self, ctx: Context):
        """ Roll the slot machine. """
        a, b, c = [random.choice("🍎🍊🍐🍋🍉🍇🍓🍒") for _ in range(3)]

        if (a == b == c):
            results = "All matching, you won! 🎉"
        elif a in (b, c) or b == c:
            results = "2 in a row, you won! 🎉"
        else:
            results = "No match, you lost 😢"

        return ctx.response.send_message(f"**[ {a} {b} {c} ]\n{ctx.user.name}**, {results}")

    @commands.command()
    async def dice(self, ctx: Context):
        """ Dice game. Good luck. """
        bot_dice, player_dice = [random.randint(1, 6) for g in range(2)]

        results = "\n".join([
            f"**{self.bot.user.name}:** 🎲 {bot_dice}",
            f"**{ctx.user.display_name}** 🎲 {player_dice}"
        ])

        match player_dice:
            case x if x > bot_dice:
                final_message = "Congrats, you won 🎉"
            case x if x < bot_dice:
                final_message = "You lost, try again... 🍃"
            case _:
                final_message = "It's a tie 🎲"

        return ctx.response.send_message(f"{results}\n> {final_message}")

    @commands.command()
    @commands.describe(
        colour="The colour you want to 'bet' on"
    )
    @commands.choices(
        colour={
            "blue": "🔵 Blue",
            "red": "🔴 Red",
            "green": "🟢 Green",
            "yellow": "🟡 Yellow"
        }
    )
    async def roulette(self, ctx: Context, colour: commands.Choice[str]):
        """ Colour roulette. """
        colour_table = ["blue", "red", "green", "yellow"]
        winner_colour = random.choice(colour_table)

        if winner_colour == colour.key:
            return ctx.response.send_message(f"Congrats, you won! 🎉\n> The colour was **{colour.value}**")
        return ctx.response.send_message(f"You lost, try again... 🍃\n> The colour was **{winner_colour}**")


async def setup(bot: CustomClient):
    """ Setup for this extension. """
    await bot.add_cog(FunCommands(bot))
