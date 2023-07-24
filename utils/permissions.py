import discord
import array as arr

from typing import Union, TYPE_CHECKING
from discord.ext import commands

if TYPE_CHECKING:
    from utils.default import CustomContext


def is_owner(ctx: discord.Interaction, user: discord.User = None) -> bool:
    """ Checks if the author is one of the owners """
    owners = ctx.client.config.discord_owner_id
    if ctx.user is not None and (str(ctx.user.id) in owners):
        return True

    if user is not None and (str(user.id) in owners):
        return True

    return False


async def check_permissions(self,ctx: discord.Interaction, perms, *, check=all) -> bool:
    """ Checks if author has permissions to a permission """
    owners = ctx.client.config.discord_owner_id
    if str(ctx.user.id) in owners:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


async def check_perms(ctx: discord.Interaction, perms, *, check=all) -> bool:
    """ Checks if author has permissions to a permission """
    owners = ctx.client.config.discord_owner_id
    if str(ctx.user.id) in owners:
        return True

    resolved = ctx.guild.permissions_for(ctx.member)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_permissions(*, check=all, **perms) -> bool:
    """ discord.Commands method to check if author has permissions """
    async def pred(ctx: discord.Interaction):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)


async def check_priv(ctx: discord.Interaction, member: discord.Member) -> Union[discord.Message, bool, None]:
    """ Custom (weird) way to check permissions when handling moderation commands """

    try:
        owners = ctx.client.config.discord_owner_id

        # Self checks
        if member.id == ctx.user.id:
            return await ctx.response.send_message(f"You can't {ctx.command.name} yourself")
        if member.id == ctx.client.user.id:
            return await ctx.response.send_message("So that's what you think of me huh..? sad ;-;")
        if str(member.id) in owners:
            return await ctx.response.send_message(f"You can't {ctx.command.name} my developer, lol")
        if int(ctx.guild.me.top_role.position - member.top_role.position) <= 0:
            return await ctx.response.send_message(f"Nope, I can't {ctx.command.name} someone of the same rank or higher than myself.")
        if member.id == ctx.guild.owner.id:
            return await ctx.response.send_message("You can't {ctx.command.name} the server owner, lol")
        if ctx.user.id == ctx.guild.owner.id:
           return False
        if int(ctx.user.top_role.position - member.top_role.position) <= 0:
            return await ctx.response.send_message(f"Nope, you can't {ctx.command.name} someone of the same rank or higher than yourself.")
        # Check if user bypasses
    except Exception:
        pass


def can_handle(ctx: discord.Interaction, permission: str) -> bool:
    """ Checks if bot has permissions or is in DMs right now """
    return isinstance(ctx.channel, discord.DMChannel) or \
        getattr(ctx.channel.permissions_for(ctx.guild.me), permission)