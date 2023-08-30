from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional, Union

import aiohttp
import discord
import importlib
import os

from discord import app_commands
from discord.ext import commands

from utils import default, http

if TYPE_CHECKING:
    from utils.data import DiscordBot


class Admin(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot

    async def reload_all_extensions(self, interaction: discord.Interaction[DiscordBot]) -> None:
        error_collection = []
        for file in os.listdir("cogs"):
            if not file.endswith(".py"):
                continue

            name = file[:-3]
            try:
                await self.bot.reload_extension(f"cogs.{name}")
            except Exception as e:
                error_collection.append([file, default.traceback_maker(e, advance=False)])

        if error_collection:
            output = "\n".join([f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])

            return await interaction.response.send_message(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}",
                ephemeral=True,
            )

        await interaction.response.send_message("Successfully reloaded all extensions")

    change = app_commands.Group(name="change", description="Change the bot's appearances.")

    @app_commands.command()
    @app_commands.describe(action="The action to perform.", name="The extension to perform the action on. If any.")
    async def extensions(
        self,
        interaction: discord.Interaction[DiscordBot],
        action: Literal[
            "list",
            "load",
            "unload",
            "reload",
            "reloadall",
        ],
        name: Optional[str] = None,
    ):
        if action == "list":
            exts = "\n".join(e for e in self.bot.extensions.keys())
            embed = discord.Embed(
                title="Extensions",
                description=f"fHere are all the extensions:\n\n{exts}",
                color=discord.Color.blurple(),
            )
            await interaction.response.send_message(embed=embed)
        elif action in ("load", "unload", "reload"):
            if not name:
                return await interaction.response.send_message("You need to specify an extension name.", ephemeral=True)

            to_call = getattr(self.bot, action)
            try:
                await to_call(f"cogs.{name}")
            except Exception as e:
                return await interaction.response.send_message(default.traceback_maker(e))
            else:
                await interaction.response.send_message(
                    f"Successfully {action}ed **{name}.py**",
                )
        elif action == "reloadall":
            return await self.reload_all_extensions(interaction)

    @app_commands.command()
    @app_commands.describe(name="The utils module to reload.")
    async def reloadutils(self, interaction: discord.Interaction[DiscordBot], name: str):
        """Reloads a utils module."""
        name_maker = f"utils/{name}.py"
        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await interaction.response.send_message(
                f"Couldn't find module named **{name_maker}**", ephemeral=True
            )
        except Exception as e:
            error = default.traceback_maker(e)
            return await interaction.response.send_message(
                f"Module **{name_maker}** returned error and was not reloaded...\n{error}", ephemeral=True
            )

        await interaction.response.send_message(f"Reloaded module **{name_maker}**")

    @app_commands.command()
    async def dm(
        self, interaction: discord.Interaction[DiscordBot], user: Union[discord.Member, discord.User], message: str
    ):
        """DM the user of your choice"""
        if user.bot:
            return await interaction.response.send_message(f"Bot users can't be DMed!", ephemeral=True)

        try:
            await user.send(message)
            await interaction.response.send_message(f"✉️ Sent a DM to **{user}**")
        except discord.Forbidden:
            await interaction.response.send_message("This user might have blocked our bot.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Looks like this user's DMs are not open.", ephemeral=True)

    @change.command(name="username")
    async def change_username(self, interaction: discord.Interaction[DiscordBot], name: Optional[str] = None):
        """Change username."""
        try:
            await self.bot.user.edit(username=name)  # type: ignore # can't be None here
        except discord.HTTPException as err:
            await interaction.response.send_message(f"Failed to change username: {err}", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"Successfully changed username to **{name}**.\nYou may have to wait a few minutes for the change to be visible."
            )

    @change.command(name="nickname")
    async def change_nickname(self, interaction: discord.Interaction[DiscordBot], name: Optional[str] = None):
        """Change nickname."""
        try:
            await interaction.guild.me.edit(nick=name)  # type: ignore # can't be None here
            if name:
                return await interaction.response.send_message(f"Successfully changed nickname to **{name}**")
            await interaction.response.send_message("Successfully removed nickname")
        except Exception as err:
            await interaction.response.send_message(f"Failed to change nickname: {err}", ephemeral=True)

    @change.command(name="avatar")
    async def change_avatar(
        self,
        interaction: discord.Interaction[DiscordBot],
        url: Optional[str] = None,
        attachment: Optional[discord.Attachment] = None,
    ):
        """Change avatar."""
        url = attachment.url if attachment else url
        if url:
            url = url.strip("<>")
        else:
            return await interaction.response.send_message(
                "You need to provide an image URL or upload one with the command", ephemeral=True
            )

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio.response)  # type: ignore # can't be None here
            await interaction.response.send_message(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await interaction.response.send_message("The URL is invalid...")
        except ValueError:
            await interaction.response.send_message("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await interaction.response.send_message(err)
        except TypeError:
            await interaction.response.send_message(
                "You need to either provide an image URL or upload one with the command"
            )


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Admin(bot), guild=discord.Object(gid) if (gid := bot.config.owner_guild_id) else None)
