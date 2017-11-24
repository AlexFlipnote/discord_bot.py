import time
import subprocess
import io
import textwrap
import traceback
import contextlib
import inspect
import discord

from assets import repo
from discord.ext import commands
from contextlib import redirect_stdout


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command()
    async def amiadmin(self, ctx):
        """ Are you admin? """
        if ctx.author.id in repo.owners:
            return await ctx.send(f"Yes **{ctx.author.name}** you are admin! ✅")

        # Please do not remove this part :( #
        if ctx.author.id == 86477779717066752:
            return await ctx.send(f"Well kinda **{ctx.author.name}**.. you still own the source code")

        await ctx.send(f"no, heck off {ctx.author.name}")

    @commands.command()
    @commands.check(repo.is_owner)
    async def reload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```\n{e}```")
            return
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command()
    @commands.check(repo.is_owner)
    async def reboot(self, ctx):
        """ Reboot the bot """
        await ctx.send('Rebooting now...')
        time.sleep(1)
        await self.bot.logout()

    @commands.command()
    @commands.check(repo.is_owner)
    async def load(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```diff\n- {e}```")
            return
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(repo.is_owner)
    async def unload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```diff\n- {e}```")
            return
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command(aliases=['exec'])
    @commands.check(repo.is_owner)
    async def execute(self, ctx, *, text: str):
        """ Do a shell command. """
        text_parsed = list(filter(None, text.split(" ")))
        output = subprocess.check_output(text_parsed).decode()
        await ctx.send(f"```fix\n{output}\n```")

    # Eval code from: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
    @commands.command(hidden=True, name='eval')
    @commands.check(repo.is_owner)
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            "message": ctx.message,
            "author": ctx.message.author,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "ctx": ctx,
            "self": self,
            "bot": self.bot,
            "inspect": inspect,
            "discord": discord,
            "contextlib": contextlib
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Admin(bot))
