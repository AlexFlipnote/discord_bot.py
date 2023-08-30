from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

import re
import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils import permissions, default

if TYPE_CHECKING:
    from utils.data import DiscordBot


class Moderator(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot

    find = app_commands.Group(
        name="find",
        description="Finds a user within your search term.",
    )
    prune = app_commands.Group(
        name="prune",
        description="Removes messages from the current server.",
        default_permissions=discord.Permissions(manage_messages=True),
    )

    @app_commands.command()
    @app_commands.describe(member="The member to kick.", reason="The reason for kicking. Optional")
    @app_commands.guild_only()
    @app_commands.default_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(
        self, interaction: discord.Interaction[DiscordBot], member: discord.Member, reason: Optional[str] = None
    ):
        """Kicks a user from the current server."""
        permissions.check_priv(interaction, member)

        try:
            await member.kick(reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage("kicked"))
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)

    @app_commands.command()
    @app_commands.describe(
        member="The member to change the nickname of.", name="The name to change the nickname to. Leave blank to reset."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_nicknames=True)
    @app_commands.checks.bot_has_permissions(manage_nicknames=True)
    async def nickname(
        self, interaction: discord.Interaction[DiscordBot], member: discord.Member, *, name: Optional[str] = None
    ):
        """Change the nickname of a member in the current server."""
        try:
            await member.edit(nick=name, reason=default.responsible(interaction.user, "Changed by command"))
            message = f"Changed **{member.name}'s** nickname to **{name}**"
            if name is None:
                message = f"Reset **{member.name}'s** nickname"
            await interaction.response.send_message(message)
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)

    @app_commands.command()
    @app_commands.describe(member="The member to ban.", reason="The reason for the ban. Optional")
    @app_commands.guild_only()
    @app_commands.default_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(
        self, interaction: discord.Interaction[DiscordBot], member: discord.Member, reason: Optional[str] = None
    ):
        """Bans a user from the current server."""
        permissions.check_priv(interaction, member)

        try:
            await member.ban(reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage("banned"))
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)

    @app_commands.command()
    @app_commands.describe(member="The member to unban.", reason="The reason for unbanning. Optional")
    @app_commands.guild_only()
    @app_commands.default_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def unban(
        self, interaction: discord.Interaction[DiscordBot], member: discord.User, reason: Optional[str] = None
    ):
        """Unbans a user from the current server."""
        try:
            await interaction.guild.unban(
                discord.Object(id=member.id), reason=default.responsible(interaction.user, reason)
            )
            await interaction.response.send_message(default.actionmessage("unbanned"))
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def mute(
        self, interaction: discord.Interaction[DiscordBot], member: discord.Member, reason: Optional[str] = None
    ):
        """Mutes a user from the current server."""
        permissions.check_priv(interaction, member)

        muted_role = next((g for g in interaction.guild.roles if g.name == "Muted"), None)

        if not muted_role:
            return await interaction.response.send_message(
                "Are you sure you've made a role called **Muted**? Remember that it's case sensitive too..."
            )

        try:
            await member.add_roles(muted_role, reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage("muted"))
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def unmute(
        self, interaction: discord.Interaction[DiscordBot], member: discord.Member, reason: Optional[str] = None
    ):
        """Unmutes a user from the current server."""
        permissions.check_priv(interaction, member)

        muted_role = next((g for g in interaction.guild.roles if g.name == "Muted"), None)

        if not muted_role:
            return await interaction.response.send_message(
                "Are you sure you've made a role called **Muted**? Remember that it's case sensitive too..."
            )

        try:
            await member.remove_roles(muted_role, reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage("unmuted"))
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def announcerole(self, interaction: discord.Interaction[DiscordBot], *, role: discord.Role):
        """Makes a role mentionable and removes it whenever you mention the role"""
        if role == interaction.guild.default_role:
            return await interaction.response.send_message(
                "To prevent abuse, I won't allow mentionable role for everyone/here role."
            )

        if interaction.user.top_role.position <= role.position:
            return await interaction.response.send_message(
                "It seems like the role you attempt to mention is over your permissions, therefore I won't allow you."
            )

        if interaction.me.top_role.position <= role.position:
            return await interaction.response.send_message(
                "This role is above my permissions, I can't make it mentionable ;-;"
            )

        await role.edit(mentionable=True, reason=f"[ {interaction.user} ] announcerole command")
        msg = await interaction.response.send_message(
            f"**{role.name}** is now mentionable, if you don't mention it within 30 seconds, I will revert the changes."
        )

        while True:

            def role_checker(m):
                if role.mention in m.content:
                    return True
                return False

            try:
                checker = await self.bot.wait_for("message", timeout=30.0, check=role_checker)
                if checker.author.id == interaction.user.id:
                    await role.edit(mentionable=False, reason=f"[ {interaction.user} ] announcerole command")
                    return await interaction.edit_original_response(
                        content=f"**{role.name}** mentioned by **{interaction.user}** in {checker.channel.mention}"
                    )
                else:
                    await checker.delete()
            except asyncio.TimeoutError:
                await role.edit(mentionable=False, reason=f"[ {interaction.user} ] announcerole command")
                return await interaction.edit_original_response(
                    content=f"**{role.name}** was never mentioned by **{interaction.user}**..."
                )

    @find.command(name="playing")
    async def find_playing(self, interaction: discord.Interaction[DiscordBot], *, search: str):
        """Find By: Game status"""
        loop = []
        for i in interaction.guild.members:
            if i.activities and (not i.bot):
                for g in i.activities:
                    if g.name and (search.lower() in g.name.lower()):
                        loop.append(f"{i} | {type(g).__name__}: {g.name} ({i.id})")

        await default.pretty_results(
            interaction, "playing", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="username")
    async def find_name(self, interaction: discord.Interaction[DiscordBot], *, search: str):
        """Find By: Username"""
        loop = [f"{i} ({i.id})" for i in interaction.guild.members if search.lower() in i.name.lower() and not i.bot]
        await default.pretty_results(
            interaction, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="nickname")
    async def find_nickname(self, interaction: discord.Interaction[DiscordBot], *, search: str):
        """Find By: Nickname"""
        loop = [
            f"{i.nick} | {i} ({i.id})"
            for i in interaction.guild.members
            if i.nick
            if (search.lower() in i.nick.lower()) and not i.bot
        ]
        await default.pretty_results(
            interaction, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="id")
    async def find_id(self, interaction: discord.Interaction[DiscordBot], *, search: int):
        """Find By: ID"""
        loop = [f"{i} | {i} ({i.id})" for i in interaction.guild.members if (str(search) in str(i.id)) and not i.bot]
        await default.pretty_results(
            interaction, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="discriminator")
    async def find_discriminator(self, interaction: discord.Interaction[DiscordBot], *, search: str):
        """Find By: discriminator"""
        if not len(search) == 4 or not re.compile("^[0-9]*$").search(search):
            return await interaction.response.send_message("You must provide exactly 4 digits")

        loop = [f"{i} ({i.id})" for i in interaction.guild.members if search == i.discriminator]
        await default.pretty_results(
            interaction, "discriminator", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    async def do_removal(
        self,
        interaction: discord.Interaction[DiscordBot],
        limit: int,
        predicate: Callable[..., Any],
        *,
        before: Optional[Union[datetime, int, discord.Object]] = None,
        after: Optional[Union[datetime, int, discord.Object]] = None,
        message: bool = True,
    ) -> None:
        await interaction.response.defer()
        if limit > 2000:
            return await interaction.followup.send(f"Too many messages to search given ({limit}/2000)")

        if not before:
            before = interaction.created_at
        elif isinstance(before, int):
            before = discord.Object(id=before)

        if after and isinstance(after, int):
            after = discord.Object(id=after)

        try:
            deleted = await interaction.channel.purge(limit=limit, before=before, after=after, check=predicate)  # type: ignore
        except discord.Forbidden:
            return await interaction.followup.send("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await interaction.followup.send(f"Error: {e} (try a smaller search?)")

        deleted = len(deleted)
        if message is True:
            return await interaction.followup.send(
                f"🚮 Successfully removed {deleted} message{'' if deleted == 1 else 's'}."
            )

    @prune.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def embeds(self, interaction: discord.Interaction[DiscordBot], search: int = 100):
        """Removes messages that have embeds in them."""
        await self.do_removal(interaction, search, lambda e: len(e.embeds))

    @prune.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def files(self, interaction: discord.Interaction[DiscordBot], search: int = 100):
        """Removes messages that have attachments in them."""
        await self.do_removal(interaction, search, lambda e: len(e.attachments))

    @prune.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def mentions(self, interaction: discord.Interaction[DiscordBot], search: int = 100):
        """Removes messages that have mentions in them."""
        await self.do_removal(interaction, search, lambda e: len(e.mentions) or len(e.role_mentions))

    @prune.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def images(self, interaction: discord.Interaction[DiscordBot], search: int = 100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(interaction, search, lambda e: len(e.embeds) or len(e.attachments))

    @prune.command(name="all")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def _remove_all(self, interaction: discord.Interaction[DiscordBot], search: int = 100):
        """Removes all messages."""
        await self.do_removal(interaction, search, lambda e: True)

    @prune.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def user(self, interaction: discord.Interaction[DiscordBot], member: discord.Member, search: int = 100):
        """Removes all messages by the member."""
        await self.do_removal(interaction, search, lambda e: e.author == member)

    @prune.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def contains(self, interaction: discord.Interaction[DiscordBot], *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await interaction.response.send_message("The substring length must be at least 3 characters.")
        else:
            await self.do_removal(interaction, 100, lambda e: substr in e.content)

    @prune.command(name="bots")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def _bots(self, interaction: discord.Interaction[DiscordBot], search: int = 100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return m.webhook_id is None and m.author.bot

        await self.do_removal(interaction, search, predicate)

    @prune.command(name="users")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def _users(self, interaction: discord.Interaction[DiscordBot], search: int = 100):
        """Removes only user messages."""

        def predicate(m):
            return m.author.bot is False

        await self.do_removal(interaction, search, predicate)

    @prune.command(name="emojis")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def _emojis(self, interaction: discord.Interaction[DiscordBot], search: int = 100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(interaction, search, predicate)

    @prune.command(name="reactions")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def _reactions(
        self, interaction: discord.Interaction[DiscordBot], search: app_commands.Range[int, 1, 2000] = 100
    ):
        """Removes all reactions from messages that have them."""
        if search > 2000:
            return await interaction.response.send_message(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in interaction.channel.history(limit=search, before=interaction.created_at):  # type: ignore
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await interaction.response.send_message(f"Successfully removed {total_reactions} reactions.")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Moderator(bot))
