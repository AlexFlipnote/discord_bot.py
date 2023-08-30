from __future__ import annotations

import discord
from discord import app_commands


class NotOwner(app_commands.CheckFailure):
    def __init__(self, user_id: int, message: str = "You are not the owner of this bot.") -> None:
        self.user_id: int = user_id
        super().__init__(message)



class NoPrivilege(app_commands.AppCommandError):
    pass