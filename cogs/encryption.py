import base64
import binascii
import codecs
import discord

from io import BytesIO
from discord.ext import commands
from utils.default import CustomContext
from discord.ext.commands.errors import BadArgument
from utils import default, http
from utils.data import DiscordBot
from discord import app_commands


class Encryption(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        
    group = app_commands.Group(name="encode", description="All encode methods")
    groupTwo = app_commands.Group(name="decode", description="All encode methods")

    async def detect_file(self, ctx: discord.Interaction):
        """ Detect if user uploaded a file to convert longer text """
        if ctx.message.attachments:
            file = ctx.message.attachments[0].url

            if not file.endswith(".txt"):
                raise BadArgument(".txt files only")

        try:
            content = await http.get(file)
        except Exception:
            raise BadArgument("Invalid .txt file")

        if not content.response:
            raise BadArgument("File you've provided is empty")
        return content.response

    async def encryptout(self, ctx: discord.Interaction, convert: str, input: str):
        """ The main, modular function to control encrypt/decrypt commands """
        if not input:
            return await ctx.response.send_message(f"Aren't you going to give me anything to encode/decode **{ctx.user.name}**")

        async with ctx.channel.typing():
            if len(input) > 1900:
                try:
                    data = BytesIO(input.encode("utf-8"))
                except AttributeError:
                    data = BytesIO(input)

                try:
                    return await ctx.response.send_message(
                        content=f"📑 **{convert}**",
                        file=discord.File(data, filename=default.timetext("Encryption"))
                    )
                except discord.HTTPException:
                    return await ctx.response.send_message(f"The file I returned was over 8 MB, sorry {ctx.user.name}...")

            try:
                await ctx.response.send_message(f"📑 **{convert}**```fix\n{input.decode('utf-8')}```")
            except AttributeError:
                await ctx.response.send_message(f"📑 **{convert}**```fix\n{input}```")

    @group.command(name="base32")
    async def encode_base32(self, ctx: discord.Interaction, *, input: str = None):
        """ Encode in base32 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base32", base64.b32encode(input.encode("utf-8"))
        )

    @groupTwo.command(name="base32")
    async def decode_base32(self, ctx: discord.Interaction, *, input: str = None):
        """ Decode in base32 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "base32 -> Text", base64.b32decode(input.encode("utf-8")))
        except Exception:
            await ctx.response.send_message("Invalid base32...")

    @group.command(name="base64")
    async def encode_base64(self, ctx: discord.Interaction, *, input: str = None):
        """ Encode in base64 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base64", base64.urlsafe_b64encode(input.encode("utf-8"))
        )

    @groupTwo.command(name="base64")
    async def decode_base64(self, ctx: discord.Interaction, *, input: str = None):
        """ Decode in base64 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "base64 -> Text", base64.urlsafe_b64decode(input.encode("utf-8")))
        except Exception:
            await ctx.response.send_message("Invalid base64...")

    @group.command(name="rot13")
    async def encode_rot13(self, ctx: discord.Interaction, *, input: str = None):
        """ Encode in rot13 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> rot13", codecs.decode(input, "rot_13")
        )

    @groupTwo.command(name="rot13")
    async def decode_rot13(self, ctx: discord.Interaction, *, input: str = None):
        """ Decode in rot13 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "rot13 -> Text", codecs.decode(input, "rot_13"))
        except Exception:
            await ctx.response.send_message("Invalid rot13...")

    @group.command(name="hex")
    async def encode_hex(self, ctx: discord.Interaction, *, input: str = None):
        """ Encode in hex """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> hex", binascii.hexlify(input.encode("utf-8"))
        )

    @groupTwo.command(name="hex")
    async def decode_hex(self, ctx: discord.Interaction, *, input: str = None):
        """ Decode in hex """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "hex -> Text", binascii.unhexlify(input.encode("utf-8")))
        except Exception:
            await ctx.response.send_message("Invalid hex...")

    @group.command(name="base85")
    async def encode_base85(self, ctx: discord.Interaction, *, input: str = None):
        """ Encode in base85 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> base85", base64.b85encode(input.encode("utf-8"))
        )

    @groupTwo.command(name="base85")
    async def decode_base85(self, ctx: discord.Interaction, *, input: str = None):
        """ Decode in base85 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "base85 -> Text", base64.b85decode(input.encode("utf-8")))
        except Exception:
            await ctx.response.send_message("Invalid base85...")

    @group.command(name="ascii85")
    async def encode_ascii85(self, ctx: discord.Interaction, *, input: str = None):
        """ Encode in ASCII85 """
        if not input:
            input = await self.detect_file(ctx)

        await self.encryptout(
            ctx, "Text -> ASCII85", base64.a85encode(input.encode("utf-8"))
        )

    @groupTwo.command(name="ascii85")
    async def decode_ascii85(self, ctx: discord.Interaction, *, input: str = None):
        """ Decode in ASCII85 """
        if not input:
            input = await self.detect_file(ctx)

        try:
            await self.encryptout(ctx, "ASCII85 -> Text", base64.a85decode(input.encode("utf-8")))
        except Exception:
            await ctx.response.send_message("Invalid ASCII85...")


async def setup(bot):
    await bot.add_cog(Encryption(bot))
