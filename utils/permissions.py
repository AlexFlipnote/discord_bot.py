from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Optional

import discord

from utils.errors import NotOwner, NoPrivilege

if TYPE_CHECKING:
    from utils.data import DiscordBot


async def is_owner(interaction: discord.Interaction[DiscordBot], user: Optional[discord.User] = None) -> bool:
    """Checks if the author is one of the owners"""
    owners = interaction.client.config.discord_owner_ids
    if str(interaction.user.id) in owners:
        return True

    if user is not None and (str(user.id) in owners):
        return True

    raise NotOwner(interaction.user.id, "You are not the owner of this bot.")


async def check_permissions(
    interaction: discord.Interaction[DiscordBot],
    check: Callable[..., bool] = all,
    **perms: bool,
) -> bool:
    """Checks if author has permissions to a permission"""
    owners = interaction.client.config.discord_owner_ids
    if str(interaction.user.id) in owners:
        return True

    if not interaction.channel or not isinstance(interaction.user, discord.Member):
        return False

    resolved = interaction.channel.permissions_for(interaction.user)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def check_priv(interaction: discord.Interaction[DiscordBot], member: discord.Member) -> None:
    """
    Custom (weird) way to check permissions
    when handling moderation commands
    """
    owners = interaction.client.config.discord_owner_ids

    author_id = interaction.user.id
    command_name = interaction.command.name  # type: ignore
    if member.id == author_id:
        raise NoPrivilege(f"You can't {command_name} yourself.")

    if member.id == interaction.client.user.id:  # type: ignore
        raise NoPrivilege("So that's what you think of me huh..? sad ;-;")

    if str(member.id) in owners:
        raise NoPrivilege(f"You can't {command_name} my developer, lol")

    if member.top_role.position >= interaction.guild.me.top_role.position:  # type: ignore
        raise NoPrivilege(f"Nope, I can't {command_name} someone of the same rank or higher than myself.")

    if member.top_role.position >= interaction.author.top_role.position:  # type: ignore
        raise NoPrivilege(f"Nope, you can't {command_name} someone of the same rank or higher than yourself.")

    if member.id == interaction.guild.owner.id:  # type: ignore
        raise NoPrivilege(f"You can't {command_name} the server owner, lol")
