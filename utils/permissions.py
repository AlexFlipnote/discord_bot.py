import discord

from typing import Union
from discord.ext import commands


async def is_owner(ctx: discord.Interaction, user: discord.User = None) -> bool:
    """ Checks if the author is one of the owners """
    owners = ctx.client.config.discord_owner_ids
    if ctx.user is not None and (str(ctx.user.id) in owners):
        return True

    if user is not None and (str(user.id) in owners):
        return True

    await ctx.response.send_message("You are not allowed to run this command!")
    return False


async def check_permissions(
    ctx: discord.Interaction,
    perms,
    *,
    check=all
) -> bool:
    """ Checks if author has permissions to a permission """
    owners = ctx.client.config.discord_owner_ids
    if str(ctx.user.id) in owners:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(
        getattr(resolved, name, None) == value
        for name, value in perms.items()
    )


async def check_perms(ctx: discord.Interaction, perms, *, check=all) -> bool:
    """ Checks if author has permissions to a permission """
    owners = ctx.client.config.discord_owner_ids
    if str(ctx.user.id) in owners:
        return True

    resolved = ctx.guild.permissions_for(ctx.member)
    return check(
        getattr(resolved, name, None) == value
        for name, value in perms.items()
    )


def has_permissions(*, check=all, **perms) -> bool:
    """ discord.Commands method to check if author has permissions """
    async def pred(ctx: discord.Interaction):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)


async def check_priv(
    ctx: discord.Interaction,
    member: discord.Member,
    bool: bool=False, # Option To Return just a Boolean
) -> Union[discord.Message, bool, None]:
    """
    Custom (weird) way to check permissions
    when handling moderation commands
    """

    try:
        owners = ctx.client.config.discord_owner_ids

        # Self checks
        if member.id == ctx.user.id:
            if not bool: await ctx.response.send_message(
                f"You can't do that to yourself"
            )
            return True

        if member.id == ctx.client.user.id:
            if not bool: await ctx.response.send_message(
                "So that's what you think of me huh..? sad ;-;"
            )
            return True
        if str(member.id) in owners:
            if not bool: await ctx.response.send_message(
                f"You can't do that to my developer, lol"
            )
            return True
        if int(ctx.guild.me.top_role.position - member.top_role.position) <= 0:
            if not bool: await ctx.response.send_message(
                f"Nope, I can't do that to someone of "
                "the same rank or higher than myself."
            )
            return True
        if member.id == ctx.guild.owner.id:
            if not bool: await ctx.response.send_message(
                f"You can't do that to the server owner, lol"
            )
            return True
        if ctx.user.id == ctx.guild.owner.id:
            return False
        if int(ctx.user.top_role.position - member.top_role.position) <= 0:
            if not bool: await ctx.response.send_message(
                f"Nope, you can't do that to someone "
                "of the same rank or higher than yourself."
            )
            return True
    except Exception:
        pass


def can_handle(ctx: discord.Interaction, permission: str) -> bool:
    """ Checks if bot has permissions or is in DMs right now """
    return isinstance(ctx.channel, discord.DMChannel) or \
        getattr(ctx.channel.permissions_for(ctx.guild.me), permission)
