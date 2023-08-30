from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union

import psutil
import os
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands

from utils import default
from utils.errors import NotOwner, NoPrivilege

if TYPE_CHECKING:
    from utils.data import DiscordBot



class Events(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot
        self.process = psutil.Process(os.getpid())
    
    def cog_load(self) -> None:
        # store the old app commands error handler
        self.old_error_handler = self.bot.tree.on_error
        # Set the app commands error handler
        self.bot.tree.on_error = self.on_app_command_error

    def cog_unload(self) -> None:
        # Restore the app commands error handler
        self.bot.tree.on_error = self.old_error_handler
    

    async def on_app_command_error(self, interaction: discord.Interaction, error: Union[app_commands.AppCommandError, Exception]) -> Any:
        """ The event triggered when an error is raised while invoking an app command. """
        TO_IGNORE = (app_commands.CommandNotFound,)
        SEND_MESSAGES = (app_commands.MissingPermissions, app_commands.BotMissingPermissions, NotOwner, NoPrivilege)
        if isinstance(error, app_commands.CommandInvokeError):
            error = error.original

        if isinstance(error, TO_IGNORE):
            return
        elif isinstance(error, SEND_MESSAGES):
            return await interaction.response.send_message(str(error), ephemeral=True)
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                "This command is on cooldown... "
                f"try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            # Better to send to a dev channel...
            trace = default.traceback_maker(error)
            await interaction.response.send_message(f"There was an error processing the command ;-;\n{trace}", ephemeral=True)


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        to_send = next((
            chan for chan in guild.text_channels
            if chan.permissions_for(guild.me).send_messages
        ), None)

        if to_send:
            await to_send.send(
                self.bot.config.discord_join_message
            )

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction) -> None:
        if not interaction.command:  # won't happen, just to shut the linter
            return

        location_name = interaction.guild.name if interaction.guild else "Private message"
        print(f"{location_name} > {interaction.user} > {interaction.command.qualified_name} (arguments: {vars(interaction.namespace)})")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.now()

        # Check if user desires to have something other than online
        from_status_type = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "offline": discord.Status.invisible,
            "invisible": discord.Status.invisible

        }

        # Check if user desires to have a different type of activity
        from_activity_type = {
            "listening": discord.ActivityType.listening,
            "watching": discord.ActivityType.watching,
            "streaming": discord.ActivityType.streaming,
            "competing": discord.ActivityType.competing,
            "custom": discord.ActivityType.custom
        }

        activity_type = self.bot.config.discord_activity_type.lower()
        guild_id = self.bot.config.owner_guild_id
        if activity_type not in from_activity_type:
            raise ValueError(f"Activity type must be one of {', '.join(from_activity_type.keys())}")
        
        activity_url = self.bot.config.streaming_status_url
        if activity_type == "streaming" and not activity_url:
            raise ValueError("Streaming status URL must be set in .env to use the streaming activity type.")
        
        status_type = self.bot.config.discord_status_type.lower()
        if status_type not in from_status_type:
            raise ValueError(f"Status type must be one of {', '.join(from_status_type.keys())}")
        
        activity = discord.Activity(
            name=self.bot.config.discord_activity_name,
            type=from_activity_type[activity_type],
            url=activity_url,
            state=self.bot.config.discord_activity_name if activity_type == "custom" else None
        )

        await self.bot.change_presence(
            status=from_status_type[status_type],
            activity=activity
        )

        global_synced = await self.bot.tree.sync()
        print(f"Synchronized {global_synced} global app commands.")
        if guild_id:
            guild_synced = await self.bot.tree.sync(guild=discord.Object(id=guild_id))
            print(f"Synchronized {guild_synced} guild app commands to {guild_id}.")


        # Indicate that the bot has successfully booted up
        print(f"Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Events(bot))
