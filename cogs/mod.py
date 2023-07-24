import discord
import re
import asyncio

from discord.ext import commands
from utils.default import CustomContext
from utils.data import DiscordBot
from utils import permissions, default
from discord import app_commands


# Source: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/mod.py
class MemberID(commands.Converter):
    async def convert(self, ctx: discord.Interaction, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(
                    f"{argument} is not a valid member or member ID."
                ) from None
        else:
            return m.id


class ActionReason(commands.Converter):
    async def convert(self, ctx: discord.Interaction, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(
                f"reason is too long ({len(argument)}/{reason_max})"
            )
        return ret


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    find = app_commands.Group(name="find", description="Finds a user within your search term.")
    prune = app_commands.Group(name="prune", description="Removes messages from the current server.")


    @app_commands.command()
    @app_commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def kick(self, ctx: discord.Interaction, member: discord.Member, *, reason: str = None):
        """ Kicks a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        try:
            await member.kick(reason=default.responsible(ctx.user, reason))
            await ctx.response.send_message(default.actionmessage("kicked"))
        except Exception as e:
            await ctx.response.send_message(e)

    @app_commands.command()
    @app_commands.guild_only()
    @permissions.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx: discord.Interaction, member: discord.Member, *, name: str = None):
        """ Nicknames a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        try:
            await member.edit(nick=name, reason=default.responsible(ctx.user, "Changed by command"))
            message = f"Changed **{member.name}'s** nickname to **{name}**"
            if name is None:
                message = f"Reset **{member.name}'s** nickname"
            await ctx.response.send_message(message)
        except Exception as e:
            await ctx.response.send_message(e)

    @app_commands.command()
    @app_commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def ban(self, ctx: discord.Interaction, member: discord.Member, *, reason: str = None):
        """ Bans a user from the current server. """
        m = ctx.guild.get_member(member.id)
        if m is not None and await permissions.check_priv(ctx, m):
            return

        try:
            await ctx.guild.ban(discord.Object(id=member.id), reason=default.responsible(ctx.user, reason))
            await ctx.response.send_message(default.actionmessage("banned"))
        except Exception as e:
            await ctx.response.send_message(e)

    @app_commands.command()
    @app_commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def unban(self, ctx: discord.Interaction, member: discord.User, *, reason: str = None):
        """ Unbans a user from the current server. """
        try:
            await ctx.guild.unban(discord.Object(id=member.id), reason=default.responsible(ctx.user, reason))
            await ctx.response.send_message(default.actionmessage("unbanned"))
        except Exception as e:
            await ctx.response.send_message(e)

    @app_commands.command()
    @app_commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def mute(self, ctx: discord.Interaction, member: discord.Member, *, reason: str = None):
        """ Mutes a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        muted_role = next((g for g in ctx.guild.roles if g.name == "Muted"), None)

        if not muted_role:
            return await ctx.response.send_message("Are you sure you've made a role called **Muted**? Remember that it's case sensitive too...")

        try:
            await member.add_roles(muted_role, reason=default.responsible(ctx.user, reason))
            await ctx.response.send_message(default.actionmessage("muted"))
        except Exception as e:
            await ctx.response.send_message(e)

    @app_commands.command()
    @app_commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def unmute(self, ctx: discord.Interaction, member: discord.Member, *, reason: str = None):
        """ Unmutes a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        muted_role = next((g for g in ctx.guild.roles if g.name == "Muted"), None)

        if not muted_role:
            return await ctx.response.send_message("Are you sure you've made a role called **Muted**? Remember that it's case sensitive too...")

        try:
            await member.remove_roles(muted_role, reason=default.responsible(ctx.user, reason))
            await ctx.response.send_message(default.actionmessage("unmuted"))
        except Exception as e:
            await ctx.response.send_message(e)

    @app_commands.command()
    @app_commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def announcerole(self, ctx: discord.Interaction, *, role: discord.Role):
        """ Makes a role mentionable and removes it whenever you mention the role """
        if role == ctx.guild.default_role:
            return await ctx.response.send_message("To prevent abuse, I won't allow mentionable role for everyone/here role.")

        if ctx.user.top_role.position <= role.position:
            return await ctx.response.send_message("It seems like the role you attempt to mention is over your permissions, therefore I won't allow you.")

        if ctx.me.top_role.position <= role.position:
            return await ctx.response.send_message("This role is above my permissions, I can't make it mentionable ;-;")

        await role.edit(mentionable=True, reason=f"[ {ctx.user} ] announcerole command")
        msg = await ctx.response.send_message(f"**{role.name}** is now mentionable, if you don't mention it within 30 seconds, I will revert the changes.")

        while True:
            def role_checker(m):
                if (role.mention in m.content):
                    return True
                return False

            try:
                checker = await self.bot.wait_for("message", timeout=30.0, check=role_checker)
                if checker.author.id == ctx.user.id:
                    await role.edit(mentionable=False, reason=f"[ {ctx.user} ] announcerole command")
                    return await msg.edit(content=f"**{role.name}** mentioned by **{ctx.user}** in {checker.channel.mention}")
                else:
                    await checker.delete()
            except asyncio.TimeoutError:
                await role.edit(mentionable=False, reason=f"[ {ctx.user} ] announcerole command")
                return await msg.edit(content=f"**{role.name}** was never mentioned by **{ctx.user}**...")

    @find.command(name="playing")
    async def find_playing(self, ctx: discord.Interaction, *, search: str):
        """Find By: Game status"""
        loop = []
        for i in ctx.guild.members:
            if i.activities and (not i.bot):
                for g in i.activities:
                    if g.name and (search.lower() in g.name.lower()):
                        loop.append(f"{i} | {type(g).__name__}: {g.name} ({i.id})")

        await default.pretty_results(
            ctx, "playing", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="username")
    async def find_name(self, ctx: discord.Interaction, *, search: str):
        """Find By: Username"""
        loop = [f"{i} ({i.id})" for i in ctx.guild.members if search.lower() in i.name.lower() and not i.bot]
        await default.pretty_results(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="nickname")
    async def find_nickname(self, ctx: discord.Interaction, *, search: str):
        """ Find By: Nickname """
        loop = [f"{i.nick} | {i} ({i.id})" for i in ctx.guild.members if i.nick if (search.lower() in i.nick.lower()) and not i.bot]
        await default.pretty_results(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="id")
    async def find_id(self, ctx: discord.Interaction, *, search: int):
        """ Find By: ID"""
        loop = [f"{i} | {i} ({i.id})" for i in ctx.guild.members if (str(search) in str(i.id)) and not i.bot]
        await default.pretty_results(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="discriminator")
    async def find_discriminator(self, ctx: discord.Interaction, *, search: str):
        """ Find By: discriminator """
        if not len(search) == 4 or not re.compile("^[0-9]*$").search(search):
            return await ctx.response.send_message("You must provide exactly 4 digits")

        loop = [f"{i} ({i.id})" for i in ctx.guild.members if search == i.discriminator]
        await default.pretty_results(
            ctx, "discriminator", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    async def do_removal(
        self, ctx: discord.Interaction, limit: int, predicate, *,
        before: int = None, after: int = None, message: bool = True
    ) -> discord.Message:
        if limit > 2000:
            return await ctx.response.send_message(f"Too many messages to search given ({limit}/2000)")

        if not before:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.response.send_message("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await ctx.response.send_message(f"Error: {e} (try a smaller search?)")

        deleted = len(deleted)
        if message is True:
            return await ctx.response.send_message(f"🚮 Successfully removed {deleted} message{'' if deleted == 1 else 's'}.")

    @prune.command()
    @permissions.has_permissions(manage_messages=True)
    async def embeds(self, ctx: discord.Interaction, search: int = 100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @prune.command()
    @permissions.has_permissions(manage_messages=True)
    async def files(self, ctx: discord.Interaction, search: int = 100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @prune.command()
    @permissions.has_permissions(manage_messages=True)
    async def mentions(self, ctx: discord.Interaction, search: int = 100):
        """Removes messages that have mentions in them."""
        await self.do_removal(ctx, search, lambda e: len(e.mentions) or len(e.role_mentions))

    @prune.command()
    @permissions.has_permissions(manage_messages=True)
    async def images(self, ctx: discord.Interaction, search: int = 100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @prune.command(name="all")
    @permissions.has_permissions(manage_messages=True)
    async def _remove_all(self, ctx: discord.Interaction, search: int = 100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @prune.command()
    @permissions.has_permissions(manage_messages=True)
    async def user(self, ctx: discord.Interaction, member: discord.Member, search: int = 100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @prune.command()
    @permissions.has_permissions(manage_messages=True)
    async def contains(self, ctx: discord.Interaction, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.response.send_message("The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @prune.command(name="bots")
    @permissions.has_permissions(manage_messages=True)
    async def _bots(self, ctx: discord.Interaction, search: int = 100, prefix: str = None):
        """Removes a bot user's messages and messages with their optional prefix."""

        getprefix = prefix if prefix else self.bot.config.discord_prefix

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or m.content.startswith(tuple(getprefix))

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="users")
    @permissions.has_permissions(manage_messages=True)
    async def _users(self, ctx: discord.Interaction, search: int = 100):
        """Removes only user messages. """

        def predicate(m):
            return m.author.bot is False

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="emojis")
    @permissions.has_permissions(manage_messages=True)
    async def _emojis(self, ctx: discord.Interaction, search: int = 100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="reactions")
    @permissions.has_permissions(manage_messages=True)
    async def _reactions(self, ctx: discord.Interaction, search: int = 100):
        """Removes all reactions from messages that have them."""
        if search > 2000:
            return await ctx.response.send_message(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.response.send_message(f"Successfully removed {total_reactions} reactions.")


async def setup(bot):
    await bot.add_cog(Moderator(bot))
