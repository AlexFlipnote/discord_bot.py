import discord

from io import BytesIO
from utils import default
from discord.ext import commands
from utils.data import DiscordBot
from discord import app_commands


class Discord_Info(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    server = app_commands.Group(name="server", description="Check info about current server")

    @app_commands.command(name='avatar')
    @app_commands.guild_only()
    async def avatar(self, ctx: discord.Interaction, *, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        user = user or ctx.user

        avatars_list = []

        def target_avatar_formats(target):
            formats = ["JPEG", "PNG", "WebP"]
            if target.is_animated():
                formats.append("GIF")
            return formats

        if not user.avatar and not user.guild_avatar:
            return await ctx.response.send_message(f"**{user}** has no avatar set, at all...")

        if user.avatar:
            avatars_list.append("**Account avatar:** " + " **-** ".join(
                f"[{img_format}]({user.avatar.replace(format=img_format.lower(), size=1024)})"
                for img_format in target_avatar_formats(user.avatar)
            ))

        embed = discord.Embed(colour=user.top_role.colour.value)

        if user.guild_avatar:
            avatars_list.append("**Server avatar:** " + " **-** ".join(
                f"[{img_format}]({user.guild_avatar.replace(format=img_format.lower(), size=1024)})"
                for img_format in target_avatar_formats(user.guild_avatar)
            ))
            embed.set_thumbnail(url=user.avatar.replace(format="png"))

        embed.set_image(url=f"{user.display_avatar.with_size(256).with_static_format('png')}")
        embed.description = "\n".join(avatars_list)

        await ctx.response.send_message(f"🖼 Avatar to **{user}**", embed=embed)

    @app_commands.command(name="roles")
    @app_commands.guild_only()
    async def roles(self, ctx: discord.Interaction) -> None:
        """ Get all roles in current server """
        allroles = ""

        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            allroles += f"[{str(num).zfill(2)}] {role.id}\t{role.name}\t[ Users: {len(role.members)} ]\r\n"

        data = BytesIO(allroles.encode("utf-8"))
        await ctx.response.send_message(
            content=f"Roles in **{ctx.guild.name}**",
            file=discord.File(data, filename=f"{default.timetext('Roles')}")
        )

    @app_commands.command(name="joindat")
    @app_commands.guild_only()
    async def joinedat(self, ctx: discord.Interaction, *, user: discord.Member = None):
        """ Check when a user joined the current server """
        user = user or ctx.user
        await ctx.response.send_message(
            f"**{user}** joined **{ctx.guild.name}**\n"
            f"{default.date(user.joined_at, ago=True)}"
        )

    @app_commands.command(name="mods")
    @app_commands.guild_only()
    async def mods(self, ctx: discord.Interaction):
        """ Check which mods are online on current guild """
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"

        await ctx.response.send_message(f"Mods in **{ctx.guild.name}**\n{message}")

    @server.command(name="info")
    @app_commands.guild_only()
    async def server_info(self, ctx: discord.Interaction):
        """ Check info about current server """
        find_bots = sum(1 for member in ctx.guild.members if member.bot)

        embed = discord.Embed()

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner.with_format("png").with_size(1024))
                embed.add_field(name="Server Name", value=ctx.guild.name)
                embed.add_field(name="Server ID", value=ctx.guild.id)
                embed.add_field(name="Members", value=ctx.guild.member_count)
                embed.add_field(name="Bots", value=find_bots)
                embed.add_field(name="Owner", value=ctx.guild.owner)
                embed.add_field(name="Created", value=default.date(ctx.guild.created_at, ago=True))
            return await ctx.response.send_message(content=f"ℹ information about **{ctx.guild.name}**", embed=embed)

    @server.command(name="avatar")
    async def server_avatar(self, ctx: discord.Interaction):
        """ Get the current server icon """
        if not ctx.guild.icon:
            return await ctx.response.send_message("This server does not have an icon...")

        format_list = []
        formats = ["JPEG", "PNG", "WebP"]
        if ctx.guild.icon.is_animated():
            formats.append("GIF")

        for img_format in formats:
            format_list.append(f"[{img_format}]({ctx.guild.icon.replace(format=img_format.lower(), size=1024)})")

        embed = discord.Embed()
        embed.set_image(url=f"{ctx.guild.icon.with_size(256).with_static_format('png')}")
        embed.title = "Icon formats"
        embed.description = " **-** ".join(format_list)

        return await ctx.response.send_message(f"🖼 Icon to **{ctx.guild.name}**", embed=embed)

    @server.command(name="banner")
    async def server_banner(self, ctx: discord.Interaction):
        """ Get the current banner image """
        if not ctx.guild.banner:
            return await ctx.response.send_message("This server does not have a banner...")

        await ctx.response.send_message(
            f"Banner of **{ctx.guild.name}**\n"
            f"{ctx.guild.banner.with_format('png')}"
        )

    @app_commands.command(name="user")
    @app_commands.guild_only()
    async def user(self, ctx: discord.Interaction, *, user: discord.Member = None):
        """ Get user information """
        user = user or ctx.user

        show_roles = "None"
        if len(user.roles) > 1:
            show_roles = ", ".join([
                f"<@&{x.id}>" for x in sorted(
                    user.roles, key=lambda x: x.position,
                    reverse=True
                )
                if x.id != ctx.guild.default_role.id
            ])

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar)

        embed.add_field(name="Full name", value=user)
        embed.add_field(name="Nickname", value=user.nick if hasattr(user, "nick") else "None")
        embed.add_field(name="Account created", value=default.date(user.created_at, ago=True))
        embed.add_field(name="Joined this server", value=default.date(user.joined_at, ago=True))
        embed.add_field(name="Roles", value=show_roles, inline=False)

        await ctx.response.send_message(content=f"ℹ About **{user.id}**", embed=embed)


async def setup(bot):
    await bot.add_cog(Discord_Info(bot))
