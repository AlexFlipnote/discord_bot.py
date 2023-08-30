from __future__ import annotations
from typing import TYPE_CHECKING

import time
import psutil
import os

import discord
from discord import app_commands
from discord.ext import commands

from utils import default, http

if TYPE_CHECKING:
    from utils.data import DiscordBot


class Information(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot
        self.process = psutil.Process(os.getpid())

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction[DiscordBot]):
        """Pong!"""
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        msg = await interaction.response.send_message("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await interaction.edit_original_response(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @app_commands.command()
    async def invite(self, interaction: discord.Interaction[DiscordBot]):
        """Invite me to your server"""
        await interaction.response.send_message(
            "\n".join(
                [
                    f"**{interaction.user.name}**, use this URL to invite me",
                    f"<{discord.utils.oauth_url(self.bot.user.id)}>",  # type: ignore
                ]
            )
        )

    @app_commands.command()
    async def source(self, interaction: discord.Interaction[DiscordBot]):
        """Check out my source code <3"""
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT, don't change output either.
        # Reference: https://github.com/AlexFlipnote/discord_bot.py/blob/master/LICENSE
        await interaction.response.send_message(
            f"📜 **{self.bot.user}** is powered by this source code:\n" "https://github.com/AlexFlipnote/discord_bot.py"
        )

    @app_commands.command()
    async def botserver(self, interaction: discord.Interaction[DiscordBot]):
        """Get an invite to our support server!"""
        if isinstance(interaction.channel, discord.DMChannel) or interaction.guild.id != 86484642730885120:
            return await interaction.response.send_message(
                f"**Here you go {interaction.user.name} 🍻**\nhttps://discord.gg/DpxkY3x"
            )
        await interaction.response.send_message(f"**{interaction.user.name}** this is my home you know :3")

    @app_commands.command()
    async def covid(self, interaction: discord.Interaction[DiscordBot], *, country: str):
        """Covid-19 Statistics for any countries"""
        await interaction.response.defer()

        r = await http.get(f"https://disease.sh/v3/covid-19/countries/{country.lower()}", res_method="json")

        if "message" in r.response:
            return await interaction.response.send_message(f"The API returned an error:\n{r['message']}")

        r = r.response

        json_data = [
            ("Total Cases", r["cases"]),
            ("Total Deaths", r["deaths"]),
            ("Total Recover", r["recovered"]),
            ("Total Active Cases", r["active"]),
            ("Total Critical Condition", r["critical"]),
            ("New Cases Today", r["todayCases"]),
            ("New Deaths Today", r["todayDeaths"]),
            ("New Recovery Today", r["todayRecovered"]),
        ]

        embed = discord.Embed(
            description=("The information provided was last " f"updated <t:{int(r['updated'] / 1000)}:R>")
        )

        for name, value in json_data:
            embed.add_field(name=name, value=f"{value:,}" if isinstance(value, int) else value)

        await interaction.followup.send(
            f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
            f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*",
            embed=embed,
        )

    @app_commands.command()
    async def about(self, interaction: discord.Interaction[DiscordBot]):
        """About the bot"""
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)

        embedColour = None
        if interaction.guild:
            embedColour = interaction.guild.me.top_role.colour

        embed = discord.Embed(colour=embedColour)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name="Last boot", value=default.date(self.bot.uptime, ago=True))
        embed.add_field(name="Developer", value=str(self.bot.get_user(self.bot.config.discord_owner_ids[0])))
        embed.add_field(name="Library", value="discord.py")
        embed.add_field(name="User ID", value=f"{self.bot.user.id}")
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )")
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB")

        await interaction.response.send_message(content=f"ℹ About **{self.bot.user}**", embed=embed)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Information(bot))
