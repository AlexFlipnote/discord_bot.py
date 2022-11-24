import discord

from utils import default
from typing import Union
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands._types import BotT

owners = default.load_json()["owners"]


def is_owner(ctx: Context[BotT]) -> bool:
    """ Checks if the author is one of the owners """
    return ctx.author.id in owners


async def check_permissions(ctx: Context[BotT], perms, *, check=all) -> bool:
    """ Checks if author has permissions to a permission """
    if ctx.author.id in owners:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms) -> bool:
    """ discord.Commands method to check if author has permissions """
    async def pred(ctx: Context[BotT]):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)


async def check_priv(ctx: Context[BotT], member: discord.Member) -> Union[discord.Message, bool, None]:
    """ Custom (weird) way to check permissions when handling moderation commands """
    try:
        # Self checks
        if member.id == ctx.author.id:
            return await ctx.send(f"You can't {ctx.command.name} yourself")
        if member.id == ctx.bot.user.id:
            return await ctx.send("So that's what you think of me huh..? sad ;-;")

        # Check if user bypasses
        if ctx.author.id == ctx.guild.owner.id:
            return False

        # Now permission check
        if member.id in owners:
            if ctx.author.id not in owners:
                return await ctx.send(f"I can't {ctx.command.name} my creator ;-;")
            else:
                pass
        if member.id == ctx.guild.owner.id:
            return await ctx.send(f"You can't {ctx.command.name} the owner, lol")
        if ctx.author.top_role == member.top_role:
            return await ctx.send(f"You can't {ctx.command.name} someone who has the same permissions as you...")
        if ctx.author.top_role < member.top_role:
            return await ctx.send(f"Nope, you can't {ctx.command.name} someone higher than yourself.")
    except Exception:
        pass


def can_handle(ctx: Context[BotT], permission: str) -> bool:
    """ Checks if bot has permissions or is in DMs right now """
    return isinstance(ctx.channel, discord.DMChannel) or \
        getattr(ctx.channel.permissions_for(ctx.guild.me), permission)
