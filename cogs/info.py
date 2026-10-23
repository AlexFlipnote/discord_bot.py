from discord_http import commands, Context, Embed
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..index import CustomClient


class Information(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot: CustomClient = bot

    @commands.command()
    async def ping(self, ctx: Context):
        """ Pong. """
        return ctx.response.send_message("🏓 Pong")

    @commands.command()
    async def invite(self, ctx: Context):
        return ctx.response.send_message(
            f"**{ctx.user}**, use this URL to invite me:\n"
            "<https://discord.com/api/oauth2/authorize"
            f"?client_id={self.bot.application_id}"
            "&scope=bot%20applications.commands>"
        )

    @commands.command()
    async def source(self, ctx: Context):
        """ Check out my source code <3. """
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT, don't change output either.
        # Reference: https://github.com/AlexFlipnote/discord_bot.py/blob/master/LICENSE
        return ctx.response.send_message(
            f"📜 **{ctx.bot.user}** is powered by this source code:\n"
            "https://github.com/AlexFlipnote/discord_bot.py"
        )

    @commands.command()
    async def about(self, ctx: Context):
        """ About the bot. """
        embed = Embed(colour=0x14bae4)
        embed.set_thumbnail(url=ctx.bot.user.avatar)
        embed.add_field(name="Developer", value="alexflipnote")
        embed.add_field(name="Library", value="discord.http")

        return ctx.response.send_message(
            f"ℹ️ About **{ctx.bot.user}**",  # ruff: ignore[ambiguous-unicode-character-string]
            embed=embed
        )


async def setup(bot: CustomClient):
    """ Setup for this extension. """
    await bot.add_cog(Information(bot))
