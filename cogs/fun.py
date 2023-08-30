from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional

import random
import secrets
import asyncio
from io import BytesIO

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils import http

if TYPE_CHECKING:
    from utils.data import DiscordBot


class FunCommands(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot

    @app_commands.command(name="8ball")
    @app_commands.describe(question="The question to ask the magic 8ball.")
    async def eightball(self, interaction: discord.Interaction[DiscordBot], question: str):
        """ Consult 8ball to receive an answer """
        ballresponse = [
            "Yes", "No", "Take a wild guess...", "Very doubtful",
            "Sure", "Without a doubt", "Most likely", "Might be possible",
            "You'll be the judge", "no... (╯°□°）╯︵ ┻━┻", "no... baka",
            "senpai, pls no ;-;"
        ]

        answer = random.choice(ballresponse)
        await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    async def randomimageapi(
        self, interaction: discord.Interaction[DiscordBot], url: str, *endpoint: str
    ) -> None:
        try:
            r = await http.get(url, res_method="json")
        except aiohttp.ClientConnectorError:
            return await interaction.response.send_message("The API seems to be down...", ephemeral=True)
        except aiohttp.ContentTypeError:
            return await interaction.response.send_message("The API returned an error or didn't return JSON...", ephemeral=True)

        result = r.response
        for step in endpoint:
            result = result[step]  # type: ignore

        await interaction.response.send_message(result)

    async def api_img_creator(
        self, interaction: discord.Interaction[DiscordBot], url: str, filename: str, content: Optional[str] = None
    ) -> None:
        await interaction.response.defer()
        req = await http.get(url, res_method="read")

        if not req.response:
            return await interaction.followup.send("I couldn't create the image ;-;")

        bio = BytesIO(req.response)  # type: ignore
        bio.seek(0)
        await interaction.followup.send(content or discord.utils.MISSING, file=discord.File(bio, filename=filename))

    @app_commands.command()
    async def duck(self, interaction: discord.Interaction[DiscordBot]):
        """ Posts a random duck """
        await self.randomimageapi(interaction, "https://random-d.uk/api/v1/random", "url")

    @app_commands.command()
    async def coffee(self, interaction: discord.Interaction[DiscordBot]):
        """ Posts a random coffee """
        await self.randomimageapi(interaction, "https://coffee.alexflipnote.dev/random.json", "file")

    @app_commands.command()
    async def birb(self, interaction: discord.Interaction[DiscordBot]):
        """ Posts a random birb """
        await self.randomimageapi(interaction, "https://api.alexflipnote.dev/birb", "file")

    @app_commands.command()
    async def sadcat(self, interaction: discord.Interaction[DiscordBot]):
        """ Post a random sadcat """
        await self.randomimageapi(interaction, "https://api.alexflipnote.dev/sadcat", "file")

    @app_commands.command()
    async def cat(self, interaction: discord.Interaction[DiscordBot]):
        """ Posts a random cat """
        await self.randomimageapi(interaction, "https://api.alexflipnote.dev/cats", "file")

    @app_commands.command()
    async def dog(self, interaction: discord.Interaction[DiscordBot]):
        """ Posts a random dog """
        await self.randomimageapi(interaction, "https://api.alexflipnote.dev/dogs", "file")

    @app_commands.command()
    async def coinflip(self, interaction: discord.Interaction[DiscordBot]):
        """ Coinflip! """
        coinsides = ["Heads", "Tails"]
        await interaction.response.send_message(f"**{interaction.user.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @app_commands.command()
    @app_commands.describe(text="The thing to pay respect to. (Optional)")
    async def f(self, interaction: discord.Interaction[DiscordBot], *, text: Optional[str] = None):
        """ Press F to pay respect """
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""
        await interaction.response.send_message(f"**{interaction.user.name}** has paid their respect {reason}{random.choice(hearts)}")

    @app_commands.command()
    @app_commands.describe(text="The word to search for.")
    async def urban(self, interaction: discord.Interaction[DiscordBot], search: str):
        """ Find the 'best' definition to your words """
        await interaction.response.defer()
        try:
            r = await http.get(f"https://api.urbandictionary.com/v0/define?term={search}", res_method="json")
        except Exception:
            return await interaction.followup.send("Urban API returned invalid data... might be down atm.")

        if not r.response:
            return await interaction.followup.send("I think the API broke...")
        if not len(r.response["list"]):  # type: ignore
            return await interaction.followup.send("Couldn't find your search in the dictionary...")

        result = sorted(r.response["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]  # type: ignore

        definition = result["definition"]  # type: ignore
        if len(definition) >= 1000:
            definition = definition[:1000]
            definition = definition.rsplit(" ", 1)[0]
            definition += "..."

        await interaction.followup.send(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")  # type: ignore

    @app_commands.command()
    @app_commands.describe(text="The text to reverse.")
    async def reverse(self, interaction: discord.Interaction[DiscordBot], text: str):
        """ !poow ,ffuts esreveR
        Everything you type after reverse will of course, be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await interaction.response.send_message(
            f"🔁 {t_rev}",
            allowed_mentions=discord.AllowedMentions.none()
        )

    @app_commands.command()
    @app_commands.describe(obytes="The amount of numbers to generate. Defaults to 18", dm="Whether to DM the password or not. Defaults to False")
    async def password(self, interaction: discord.Interaction[DiscordBot], nbytes: int = 18, dm: bool = False):
        """ Generates a random password string for you

        This returns a random URL-safe text string, containing nbytes random bytes.
        The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        """
        if nbytes not in range(3, 1401):
            return await interaction.response.send_message("I only accept any numbers between 3-1400", ephemeral=True)
        
        if not dm:
            return await interaction.response.send_message(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}\n\nOnly you can see this btw!", ephemeral=True)

        try:
            await interaction.user.send(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}")
        except discord.HTTPException:
            await interaction.response.send_message("I couldn't DM you the password, maybe you disabled DMs?")
        else:
            await interaction.response.send_message("I sent you a DM with the password!")

    @app_commands.command()
    @app_commands.describe(thing="The thing to rate.")
    async def rate(self, interaction: discord.Interaction[DiscordBot], *, thing: str):
        """ Rates what you desire """
        rate_amount = random.uniform(0.0, 100.0)
        await interaction.response.send_message(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    @app_commands.command()
    @app_commands.describe(
        user="The user to give a beer to.",
        reason="The reason why you are giving the beer."
    )
    async def beer(self, interaction: discord.Interaction[DiscordBot], user: Optional[discord.Member] = None, *, reason: Optional[str] = None):
        """ Give someone a beer! 🍻 """
        if not user or user.id == interaction.user.id:
            return await interaction.response.send_message(f"**{interaction.user.name}**: paaaarty!🎉🍺")
        if user.id == self.bot.user.id:  # type: ignore 
            return await interaction.response.send_message("*drinks beer with you* 🍻")
        if user.bot:
            return await interaction.response.send_message(f"I would love to give beer to the bot **{interaction.user.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{interaction.user.name}**" + (f"\n\n**Reason:** {reason}" if reason else "")
        await interaction.response.send_message(beer_offer)
        msg = await interaction.original_response()
        await msg.add_reaction("🍻")

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False

        try:
            await self.bot.wait_for("raw_reaction_add", timeout=30.0, check=reaction_check)
        except asyncio.TimeoutError:
            await interaction.edit_original_response(content=f"~~{beer_offer}~~\nwell, doesn't seem like **{user.name}** wanted a beer with you **{interaction.user.name}** ;-;")  # type: ignore
        else:
            await interaction.edit_original_response(content=f"**{user.name}** and **{interaction.user.name}** are enjoying a lovely beer together 🍻")
    
    @app_commands.command()
    @app_commands.describe(user="The user to check.")
    async def hotcalc(self, interaction: discord.Interaction[DiscordBot], *, member: Optional[discord.Member] = None):
        """ Returns a random percent for how hot is a discord user """
        user = member or interaction.user
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

        await interaction.response.send_message(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @app_commands.command()
    async def noticeme(self, interaction: discord.Interaction[DiscordBot]):
        """ Notice me senpai! owo """
        if not interaction.channel.permissions_for(interaction.guild.me).attach_files:  # type: ignore
            return await interaction.response.send_message("I cannot send images here ;-;")

        r = await http.get("https://i.alexflipnote.dev/500ce4.gif", res_method="read")
        await interaction.response.send_message(
            file=discord.File(
                BytesIO(r.response),  # type: ignore
                filename="noticeme.gif"
            )
        )

    @app_commands.command()
    async def slot(self, interaction: discord.Interaction[DiscordBot]):
        """ Roll the slot machine """
        a, b, c = [random.choice("🍎🍊🍐🍋🍉🍇🍓🍒") for _ in range(3)]

        if (a == b == c):
            results = "All matching, you won! 🎉"
        elif (a == b) or (a == c) or (b == c):
            results = "2 in a row, you won! 🎉"
        else:
            results = "No match, you lost 😢"

        await interaction.response.send_message(f"**[ {a} {b} {c} ]\n{interaction.user.name}**, {results}")

    @app_commands.command()
    async def dice(self, interaction: discord.Interaction[DiscordBot]):
        """ Dice game. Good luck """
        bot_dice, player_dice = [random.randint(1, 6) for g in range(2)]

        results = "\n".join([
            f"**{self.bot.user.display_name}:** 🎲 {bot_dice}",
            f"**{interaction.user.display_name}** 🎲 {player_dice}"
        ])

        match player_dice:
            case x if x > bot_dice:
                final_message = "Congrats, you won 🎉"
            case x if x < bot_dice:
                final_message = "You lost, try again... 🍃"
            case _:
                final_message = "It's a tie 🎲"

        await interaction.response.send_message(f"{results}\n> {final_message}")

    @app_commands.command()
    @app_commands.describe(colour="The colour to pick.")
    async def roulette(self, interaction: discord.Interaction[DiscordBot], picked_colour: Literal["blue", "red", "green", "yellow"]):
        """ Colours roulette """
        colour_table = ["blue", "red", "green", "yellow"]

        msg = await interaction.response.send_message("Spinning 🔵🔴🟢🟡")
        chosen_color = random.choice(colour_table)
        await asyncio.sleep(2)
        result = f"Result: {chosen_color.upper()}"

        if chosen_color == picked_colour:
            return await interaction.edit_original_response(content=f"> {result}\nCongrats, you won 🎉!")
        await interaction.edit_original_response(content=f"> {result}\nBetter luck next time")


    @app_commands.command()
    async def amiadmin(self, interaction: discord.Interaction[DiscordBot]):
        """ Are you an admin? """
        owners = self.bot.config.discord_owner_ids

        if str(interaction.user.id) in owners:
            return await interaction.response.send_message(
                f"Yes **{interaction.user.name}** you are an admin! ✅"
            )
        # Please do not remove this part.
        # I would love to be credited as the original creator of the source code.
        #   -- AlexFlipnote
        elif interaction.user.id == 86477779717066752:
            return await interaction.response.send_message(
                f"Well kinda **{interaction.user.name}**.. "
                "you still own the source code"
            )

        await interaction.response.send_message(f"no, heck off {interaction.user.name}")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(FunCommands(bot))
