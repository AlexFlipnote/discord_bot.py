import discord
import re

from io import BytesIO
from discord.ext import commands
from utils import permissions, default


# Source: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/mod.py
class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            can_execute = ctx.author.id == ctx.bot.owner_id or \
                          ctx.author == ctx.guild.owner or \
                          ctx.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
            return m.id


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret


class Moderator:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """ Kicks a user from the current server. """
        try:
            await member.kick(reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("kicked"))
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases=["nick"])
    @commands.guild_only()
    @permissions.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, name: str = None):
        """ Nicknames a user from the current server. """
        try:
            await member.edit(nick=name, reason=default.responsible(ctx.author, "Changed by command"))
            message = f"Changed **{member.name}'s** nickname to **{name}**"
            if name is None:
                message = f"Reset **{member.name}'s** nickname"
            await ctx.send(message)
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: str = None):
        """ Bans a user from the current server. """
        try:
            await ctx.guild.ban(discord.Object(id=member), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("banned"))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def massban(self, ctx, reason: ActionReason, *members: MemberID):
        """ Mass bans multiple members from the server. """

        try:
            for member_id in members:
                await ctx.guild.ban(discord.Object(id=member_id), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("massbanned", mass=True))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def unban(self, ctx, member: MemberID, *, reason: str = None):
        """ Unbans a user from the current server. """
        try:
            await ctx.guild.unban(discord.Object(id=member), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("unbanned"))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Mutes a user from the current server. """
        message = []
        for role in ctx.guild.roles:
            if role.name == "Muted":
                message.append(role.id)
        try:
            therole = discord.Object(id=message[0])
        except IndexError:
            return await ctx.send("Are you sure you've made a role called **Muted**? Remember that it's case sensetive too...")

        try:
            await member.add_roles(therole, reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("muted"))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Unmutes a user from the current server. """
        message = []
        for role in ctx.guild.roles:
            if role.name == "Muted":
                message.append(role.id)
        try:
            therole = discord.Object(id=message[0])
        except IndexError:
            return await ctx.send("Are you sure you've made a role called **Muted**? Remember that it's case sensetive too...")

        try:
            await member.remove_roles(therole, reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("unmuted"))
        except Exception as e:
            await ctx.send(e)

    @commands.group()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def find(self, ctx):
        """ Finds a user within your search term """
        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @find.command(name="playing")
    async def find_playing(self, ctx, *, search: str):
        result = [f"{i} | {i.activity.name}\r\n" for i in ctx.guild.members if (i.activity is not None) and (search.lower() in i.activity.name.lower()) and (not i.bot)]
        if len(result) == 0:
            return await ctx.send("Your search result was empty...")
        data = BytesIO(''.join(result).encode('utf-8'))
        await ctx.send(content=f"Found **{len(result)}** on your search for **{search}**",
                       file=discord.File(data, filename=default.timetext(f'PlayingSearch')))

    @find.command(name="username", aliases=["name"])
    async def find_name(self, ctx, *, search: str):
        result = [f"{i}\r\n" for i in ctx.guild.members if (search.lower() in i.name.lower())]
        if len(result) == 0:
            return await ctx.send("Your search result was empty...")
        data = BytesIO(''.join(result).encode('utf-8'))
        await ctx.send(content=f"Found **{len(result)}** on your search for **{search}**",
                       file=discord.File(data, filename=default.timetext(f'NameSearch')))

    @find.command(name="discriminator", aliases=["discrim"])
    async def find_discriminator(self, ctx, *, search: str):
        result = [f"{i}\r\n" for i in ctx.guild.members if (search in i.discriminator)]
        if len(result) == 0:
            return await ctx.send("Your search result was empty...")
        data = BytesIO(''.join(result).encode('utf-8'))
        await ctx.send(content=f"Found **{len(result)}** on your search for **{search}**",
                       file=discord.File(data, filename=default.timetext(f'DiscriminatorSearch')))

    @commands.group()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def prune(self, ctx):
        """ Removes messages from the current server. """

        if ctx.invoked_subcommand is None:
            help_cmd = self.bot.get_command('help')
            await ctx.invoke(help_cmd, 'remove')

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None, message=True):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        deleted = len(deleted)
        if message is True:
            await ctx.send(f'🚮 Successfully removed {deleted} message{"" if deleted == 1 else "s"}.')

    @prune.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @prune.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @prune.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @prune.command(name='all')
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @prune.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @prune.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @prune.command(name='bots')
    async def _bots(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return m.author.bot or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='users')
    async def _users(self, ctx, prefix=None, search=100):
        """Removes only user messages. """

        def predicate(m):
            return m.author.bot is False

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='emoji')
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<:(\w+):(\d+)>')

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f'Successfully removed {total_reactions} reactions.')


def setup(bot):
    bot.add_cog(Moderator(bot))
