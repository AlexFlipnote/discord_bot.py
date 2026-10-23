import logging

from discord_http import commands
from discord_http.gateway import PlayingStatus, StatusType, ActivityType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..index import CustomClient

_log = logging.getLogger("discord_http")


class FunCommands(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot: CustomClient = bot

    @commands.listener()
    async def on_gateway_ready(self, bot: CustomClient):
        _log.info(f"Ready: {bot.user.name} | Servers: {len(self.bot.guilds)}")

        await self.bot.gateway.change_presence(PlayingStatus(
            name=self.bot.config["playing"],
            status=StatusType.online,
            type=ActivityType.custom
        ))


async def setup(bot: CustomClient):
    """ Setup for this extension. """
    await bot.add_cog(FunCommands(bot))
