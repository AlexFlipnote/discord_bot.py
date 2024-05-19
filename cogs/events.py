import discord
import psutil
import os

from datetime import datetime
from utils.default import CustomContext
from discord.ext import commands
from discord.ext.commands import errors
from utils import default
from utils.data import DiscordBot


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_command_error(self, ctx: CustomContext, err: Exception):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send("\n".join([
                    "You attempted to make the command display more than 2,000 characters...",
                    "Both error and command will be ignored."
                ]))

            await ctx.send(f"There was an error processing the command ;-;\n{error}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        to_send = next((
            chan for chan in guild.text_channels
            if chan.permissions_for(guild.me).send_messages
        ), None)

        if to_send:
            await to_send.send(self.bot.config.discord_join_message)

    @commands.Cog.listener()
    async def on_command(self, ctx: CustomContext):
        location_name = ctx.guild.name if ctx.guild else "Private message"
        print(f"{location_name} > {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.now()

        # Check if user desires to have something other than online
        status = self.bot.config.discord_status_type.lower()
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        # Check if user desires to have a different type of activity
        activity = self.bot.config.discord_activity_type.lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}

        await self.bot.change_presence(
            activity=discord.Activity(
                type=activity_type.get(activity, 0),
                name=self.bot.config.discord_activity_name
            ),
            status=status_type.get(status, discord.Status.online)
        )

        # Indicate that the bot has successfully booted up
        print(f"Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}")


async def setup(bot):
    await bot.add_cog(Events(bot))
