import time

from datetime import datetime
from discord_http import commands, Context, Member, Embed, File, Role
from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..index import CustomClient


def date(
    target: datetime | float | int,
    clock: bool = True,
    ago: bool = False,
    only_ago: bool = False
) -> str:
    """ Converts a timestamp to a Discord timestamp format. """
    if isinstance(target, (int, float)):
        target = datetime.fromtimestamp(target)

    unix = int(time.mktime(target.timetuple()))
    timestamp = f"<t:{unix}:{'f' if clock else 'D'}>"
    if ago:
        timestamp += f" (<t:{unix}:R>)"
    if only_ago:
        timestamp = f"<t:{unix}:R>"
    return timestamp


class Discord(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot: CustomClient = bot

    server = commands.SubGroup(name="server")

    @commands.command()
    @commands.guild_only()
    @commands.describe(
        member="The user to get information from, leave empty to get your own",
    )
    async def avatar(self, ctx: Context, member: Member | None = None):
        """ Get the avatar of you or someone else. """
        member = member or ctx.user  # pyright: ignore[reportAssignmentType]

        if not member.display_avatar and not member.avatar:
            return ctx.response.send_message(f"**{member}** has no avatar set, at all...")

        embed = Embed()

        if member.avatar:
            embed.set_thumbnail(url=member.display_avatar)
            embed.set_image(url=member.avatar)
        else:
            embed.set_image(url=member.display_avatar)

        container = []
        if member.avatar:
            container.append(f"**[Guild avatar]({member.avatar})**")
        if member.global_avatar:
            container.append(f"**[Original avatar]({member.global_avatar})**")
        embed.description = "\n".join(container)

        return ctx.response.send_message(f"🖼 Avatar to **{member}**", embed=embed)

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx: Context):
        """ Get all roles in current server. """
        async def call_after():
            guild = await ctx.guild.fetch()
            roles = [g for g in guild.roles if isinstance(g, Role)]
            all_roles = [
                f"[{str(num).zfill(2)}] {role.id}\t{role.name}"
                for num, role in enumerate(
                    sorted(roles, key=lambda r: r.position, reverse=True),
                    start=1
                )
            ]

            data = BytesIO("\n".join(all_roles).encode("utf-8"))
            await ctx.edit_original_response(
                content=f"Roles in {guild.name}",
                attachment=File(data, filename="roles.txt")
            )

        return ctx.response.defer(thinking=True, call_after=call_after)

    @commands.command()
    @commands.guild_only()
    @commands.describe(
        member="The member to get information from, leave empty to get your own",
    )
    async def joinedat(self, ctx: Context, member: Member | None = None):
        """ Check when a user joined the current server or yourself. """
        member = member or ctx.user  # pyright: ignore[reportAssignmentType]

        if not member.joined_at:
            return ctx.response.send_message(
                "Somehow, Discord returned no join data....?",
                ephemeral=True
            )

        return ctx.response.send_message(
            f"**{member}** joined this server\n"
            f"{date(member.joined_at, ago=True)}"
        )

    @server.command(name="info")
    @commands.guild_only()
    async def server_info(self, ctx: Context):
        async def call_after():
            guild = await ctx.guild.fetch()
            embed = Embed()

            if guild.icon:
                embed.set_thumbnail(url=guild.icon)
            if guild.banner:
                embed.set_image(url=guild.banner)

            embed.add_field(name="Name", value=guild.name)
            embed.add_field(name="ID", value=str(guild.id))
            embed.add_field(name="Owner", value=f"<@!{guild.owner_id}> ({guild.owner_id})", inline=False)
            embed.add_field(name="Created", value=date(guild.created_at, ago=True), inline=False)

            await ctx.edit_original_response(
                content=f"ℹ️ information about **{guild.name}**",  # ruff: ignore[ambiguous-unicode-character-string]
                embed=embed
            )

        return ctx.response.defer(thinking=True, call_after=call_after)

    @server.command(name="icon")
    @commands.guild_only()
    async def server_icon(self, ctx: Context):
        """ Get the server icon. """
        async def call_after():
            guild = await ctx.guild.fetch()
            if not guild.icon:
                return await ctx.edit_original_response(content=f"**{guild.name}** has no icon set.")

            return await ctx.edit_original_response(
                content=f"🖼 Icon to **{guild.name}**\n{guild.icon}"
            )

        return ctx.response.defer(thinking=True, call_after=call_after)

    @server.command(name="banner")
    @commands.guild_only()
    async def server_banner(self, ctx: Context):
        """ Get the server banner. """
        async def call_after():
            guild = await ctx.guild.fetch()
            if not guild.banner:
                return await ctx.edit_original_response(content=f"**{guild.name}** has no banner set.")

            return await ctx.edit_original_response(
                content=f"🖼 Banner to **{guild.name}**\n{guild.banner}"
            )

        return ctx.response.defer(thinking=True, call_after=call_after)

    @commands.command()
    @commands.guild_only()
    @commands.describe(
        member="The member to get information from, leave empty to get your own",
    )
    async def member(self, ctx: Context, member: Member | None = None):
        """ Get member information. """
        member = member or ctx.user  # pyright: ignore[reportAssignmentType]

        show_roles = "No roles..."
        if len(member.roles) > 1:
            show_roles = ", ".join([
                role.mention for role in member.roles
                if role.id != ctx.guild.id
            ])

        embed = Embed()
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Name", value=member.name)
        if member.nick:
            embed.add_field(name="Nickname", value=member.nick)
        embed.add_field(name="ID", value=str(member.id))
        embed.add_field(name="Created account", value=date(member.created_at, ago=True), inline=False)
        if member.joined_at:
            embed.add_field(
                name="Joined this server",
                value=date(member.joined_at, ago=True),
                inline=False
            )
        embed.add_field(name="Roles", value=show_roles, inline=False)

        return ctx.response.send_message(f"ℹ️ About **{member}**", embed=embed)  # ruff: ignore[ambiguous-unicode-character-string]


async def setup(bot: CustomClient):
    """ Setup for this extension. """
    await bot.add_cog(Discord(bot))
