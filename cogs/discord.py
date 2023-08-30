from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands

from utils import default

if TYPE_CHECKING:
    from utils.data import DiscordBot


class DiscordInfo(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot

    server = app_commands.Group(name="server", description="Check info about current server")

    @app_commands.command(name="avatar")
    @app_commands.describe(member="The user you want to get info about.")
    @app_commands.guild_only()
    async def avatar(self, interaction: discord.Interaction[DiscordBot], member: Optional[discord.Member] = None):
        """Get the avatar of you or someone else"""
        user: discord.Memebr = member or interaction.user  # type: ignore # it's a Member dwai

        avatars_list = []

        def target_avatar_formats(target: discord.Asset):
            formats = ["JPEG", "PNG", "WebP"]
            if target.is_animated():
                formats.append("GIF")
            return formats

        if not user.avatar and not user.guild_avatar:
            return await interaction.response.send_message(f"**{user}** has no avatar set, at all...", ephemeral=True)

        if user.avatar:
            avatars_list.append(
                "**Account avatar:** "
                + " **-** ".join(
                    f"[{img_format}]({user.avatar.replace(format=img_format.lower(), size=1024)})"
                    for img_format in target_avatar_formats(user.avatar)
                )
            )

        embed = discord.Embed(colour=user.top_role.colour.value)

        if user.guild_avatar:
            avatars_list.append(
                "**Server avatar:** "
                + " **-** ".join(
                    f"[{img_format}]({user.guild_avatar.replace(format=img_format.lower(), size=1024)})"
                    for img_format in target_avatar_formats(user.guild_avatar)
                )
            )
            embed.set_thumbnail(url=user.avatar.replace(format="png"))

        embed.set_image(url=f"{user.display_avatar.with_size(256).with_static_format('png')}")
        embed.description = "\n".join(avatars_list)

        await interaction.response.send_message(f"🖼 Avatar to **{user}**", embed=embed)

    @app_commands.command(name="roles")
    @app_commands.guild_only()
    async def roles(self, interaction: discord.Interaction[DiscordBot]) -> None:
        """Get all roles in current server"""
        # won't happen, just to shut the linter
        if not interaction.guild:
            return await interaction.response.send_message("This command only works in servers.")

        roles = [
            f"[{str(num).zfill(2)}] {role.id}\t{role.name}\t[ Users: {len(role.members)} ]\r"
            for num, role in enumerate(sorted(interaction.guild.roles, reverse=True), start=1)
        ]

        data = BytesIO("\n".join(roles).encode("utf-8"))
        await interaction.response.send_message(
            content=f"Roles in **{interaction.guild.name}**",
            file=discord.File(data, filename=f"{default.timetext('Roles')}"),
        )

    @app_commands.command(name="joindat")
    @app_commands.describe(member="The user you want to get info about.")
    @app_commands.guild_only()
    async def joinedat(self, interaction: discord.Interaction[DiscordBot], member: Optional[discord.Member] = None):
        """Check when a user joined the current server"""
        user: discord.Memebr = member or interaction.user  # type: ignore # it's a Member dwai
        await interaction.response.send_message(
            f"**{user}** joined **{interaction.guild.name}**\n" f"{default.date(user.joined_at, ago=True)}"
        )

    @app_commands.command(name="mods")
    @app_commands.guild_only()
    async def mods(self, interaction: discord.Interaction[DiscordBot]):
        """Check which mods are online on current guild"""
        # won't happen, just to shut the linter
        if not interaction.guild:
            return await interaction.response.send_message("This command only works in servers.")

        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"},
        }

        for user in interaction.guild.members:
            user_perm = interaction.channel.permissions_for(user)  # type: ignore # can't be None
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"

        await interaction.response.send_message(f"Mods in **{interaction.guild.name}**\n{message}")

    @server.command(name="info")
    @app_commands.guild_only()
    async def server_info(self, interaction: discord.Interaction[DiscordBot]):
        """Check info about current server"""
        # won't happen, just to shut the linter
        if not interaction.guild:
            return await interaction.response.send_message("This command only works in servers.")

        find_bots = sum(1 for member in interaction.guild.members if member.bot)

        embed = discord.Embed()

        embed.add_field(name="Server Name", value=interaction.guild.name)
        embed.add_field(name="Server ID", value=interaction.guild.id)
        embed.add_field(name="Members", value=interaction.guild.member_count)
        embed.add_field(name="Bots", value=find_bots)
        embed.add_field(name="Owner", value=interaction.guild.owner)
        embed.add_field(name="Created", value=default.date(interaction.guild.created_at, ago=True))
        if interaction.guild.banner:
            embed.set_image(url=interaction.guild.banner.with_size(1024))
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon)

        await interaction.response.send_message(f"ℹ information about **{interaction.guild.name}**", embed=embed)

    @server.command(name="avatar")
    async def server_avatar(self, interaction: discord.Interaction[DiscordBot]):
        """Get the current server icon"""
        # won't happen, just to shut the linter
        if not interaction.guild:
            return await interaction.response.send_message("This command only works in servers.")

        if not interaction.guild.icon:
            return await interaction.response.send_message("This server does not have an icon...", ephemeral=True)

        format_list = []
        formats = ["JPEG", "PNG", "WebP"]
        if interaction.guild.icon.is_animated():
            formats.append("GIF")

        for img_format in formats:
            format_list.append(f"[{img_format}]({interaction.guild.icon.replace(format=img_format.lower(), size=1024)})")  # type: ignore

        embed = discord.Embed()
        embed.set_image(url=f"{interaction.guild.icon.with_size(256)}")
        embed.title = "Icon formats"
        embed.description = " **-** ".join(format_list)

        await interaction.response.send_message(f"🖼 Icon to **{interaction.guild.name}**", embed=embed)

    @server.command(name="banner")
    async def server_banner(self, interaction: discord.Interaction[DiscordBot]):
        """Get the current banner image"""
        # won't happen, just to shut the linter
        if not interaction.guild:
            return await interaction.response.send_message("This command only works in servers.")

        if not interaction.guild.banner:
            return await interaction.response.send_message("This server does not have a banner...")

        await interaction.response.send_message(
            f"Banner of **{interaction.guild.name}**\n" f"{interaction.guild.banner}"
        )

    @app_commands.command(name="user")
    @app_commands.describe(member="The user you want to get info about.")
    @app_commands.guild_only()
    async def user(self, interaction: discord.Interaction[DiscordBot], member: Optional[discord.Member] = None):
        """Get user information"""
        # won't happen, just to shut the linter
        if not interaction.guild:
            return await interaction.response.send_message("This command only works in servers.")

        user: discord.Memebr = member or interaction.user  # type: ignore # it's a Member dwai
        roles = (
            ", ".join(r.mention for r in sorted(user.roles[1:], key=lambda x: x.position, reverse=True))
            if len(user.roles) > 1
            else f"{len(user.roles[1:])}"
        )

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar)

        embed.add_field(name="Full name", value=user)
        embed.add_field(name="Nickname", value=user.nick if hasattr(user, "nick") else "None")
        embed.add_field(name="Account created", value=default.date(user.created_at, ago=True))
        embed.add_field(name="Joined this server", value=default.date(user.joined_at, ago=True))
        embed.add_field(name="Roles", value=roles, inline=False)

        await interaction.response.send_message(content=f"ℹ About **{user.id}**", embed=embed)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(DiscordInfo(bot))
