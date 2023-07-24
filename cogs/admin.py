import aiohttp
import discord
import importlib
import os

from discord import app_commands
from discord.ext import commands
from utils import permissions, default, http
from utils.data import DiscordBot


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    group = app_commands.Group(name="change", description="Change the bot's appearances.")

    @app_commands.command()
    async def amiadmin(self, ctx: discord.Interaction):
        """ Are you an admin? """
        owners = self.bot.config.discord_owner_ids
        if str(ctx.user.id) in owners:
            return await ctx.response.send_message(
                f"Yes **{ctx.user.name}** you are an admin! ✅"
            )

        # Please do not remove this part.
        # I would love to be credited as the original creator of the source code.
        #   -- AlexFlipnote
        if ctx.user.id == 86477779717066752:
            return await ctx.response.send_message(
                f"Well kinda **{ctx.user.name}**.. "
                "you still own the source code"
            )

        await ctx.response.send_message(f"no, heck off {ctx.user.name}")

    @app_commands.command()
    @app_commands.check(permissions.is_owner)
    async def load(self, ctx: discord.Interaction, name: str):
        """ Loads an extension. """
        try:
            await self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.response.send_message(default.traceback_maker(e))
        await ctx.response.send_message(f"Loaded extension **{name}.py**")

    @app_commands.command()
    @app_commands.check(permissions.is_owner)
    async def unload(self, ctx: discord.Interaction, name: str):
        """ Unloads an extension. """
        try:
            await self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.response.send_message(default.traceback_maker(e))
        await ctx.response.send_message(f"Unloaded extension **{name}.py**")

    @app_commands.command()
    @app_commands.check(permissions.is_owner)
    async def reload(self, ctx: discord.Interaction, name: str):
        """ Reloads an extension. """
        try:
            await self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.response.send_message(default.traceback_maker(e))
        await ctx.response.send_message(f"Reloaded extension **{name}.py**")

    @app_commands.command()
    @app_commands.check(permissions.is_owner)
    async def reloadall(self, ctx: discord.Interaction):
        """ Reloads all extensions. """
        error_collection = []
        for file in os.listdir("cogs"):
            if not file.endswith(".py"):
                continue

            name = file[:-3]
            try:
                await self.bot.reload_extension(f"cogs.{name}")
            except Exception as e:
                error_collection.append(
                    [file, default.traceback_maker(e, advance=False)]
                )

        if error_collection:
            output = "\n".join([
                f"**{g[0]}** ```diff\n- {g[1]}```"
                for g in error_collection
            ])

            return await ctx.response.send_message(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}"
            )

        await ctx.response.send_message("Successfully reloaded all extensions")

    @app_commands.command()
    @app_commands.check(permissions.is_owner)
    async def reloadutils(self, ctx: discord.Interaction, name: str):
        """ Reloads a utils module. """
        name_maker = f"utils/{name}.py"
        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.response.send_message(f"Couldn't find module named **{name_maker}**")
        except Exception as e:
            error = default.traceback_maker(e)
            return await ctx.response.send_message(f"Module **{name_maker}** returned error and was not reloaded...\n{error}")
        await ctx.response.send_message(f"Reloaded module **{name_maker}**")

    @app_commands.command()
    @app_commands.check(permissions.is_owner)
    async def dm(self, ctx: discord.Interaction, user: discord.User, *, message: str):
        """ DM the user of your choice """
        try:
            await user.send(message)
            await ctx.response.send_message(f"✉️ Sent a DM to **{user}**")
        except discord.Forbidden:
            await ctx.response.send_message("This user might be having DMs blocked or it's a bot account...")

    @group.command(name="username")
    @app_commands.check(permissions.is_owner)
    async def change_username(self, ctx: discord.Interaction, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.response.send_message(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.response.send_message(err)

    @group.command(name="nickname")
    @app_commands.check(permissions.is_owner)
    async def change_nickname(self, ctx: discord.Interaction, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                return await ctx.response.send_message(f"Successfully changed nickname to **{name}**")
            await ctx.response.send_message("Successfully removed nickname")
        except Exception as err:
            await ctx.response.send_message(err)

    @group.command(name="avatar")
    @app_commands.check(permissions.is_owner)
    async def change_avatar(self, ctx: discord.Interaction, url: str = None):
        """ Change avatar. """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio.response)
            await ctx.response.send_message(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.response.send_message("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.response.send_message("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await ctx.response.send_message(err)
        except TypeError:
            await ctx.response.send_message("You need to either provide an image URL or upload one with the command")


async def setup(bot):
    await bot.add_cog(Admin(bot))
