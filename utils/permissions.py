import discord

from typing import Union, TYPE_CHECKING
from discord.ext import commands

if TYPE_CHECKING:
    from utils.default import CustomContext


def is_owner(ctx: "CustomContext") -> bool:
    """ Checks if the author is one of the owners """
    return ctx.author.id == ctx.bot.config.discord_owner_id


async def check_permissions(ctx: "CustomContext", perms, *, check=all) -> bool:
    """ Checks if author has permissions to a permission """
    if ctx.author.id == ctx.bot.config.discord_owner_id:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms) -> bool:
    """ discord.Commands method to check if author has permissions """
    async def pred(ctx: "CustomContext"):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)


async def check_priv(ctx: "CustomContext", member: discord.Member) -> Union[discord.Message, bool, None]:
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
        if member.id == ctx.bot.config.discord_owner_id:
            if ctx.author.id != ctx.bot.config.discord_owner_id:
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


def can_handle(ctx: "CustomContext", permission: str) -> bool:
    """ Checks if bot has permissions or is in DMs right now """
    return isinstance(ctx.channel, discord.DMChannel) or \
        getattr(ctx.channel.permissions_for(ctx.guild.me), permission)
