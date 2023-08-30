from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional

import base64
import binascii
import codecs
from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands

from utils import default, http

if TYPE_CHECKING:
    from utils.data import DiscordBot


class Encryption(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot

    encode = app_commands.Group(name="encode", description="Encode text")
    decode = app_commands.Group(name="decode", description="Decode text")

    async def handle_input(self, text: Optional[str], text_file: Optional[discord.Attachment]) -> str:
        """Detect if user uploaded a file to convert longer text"""
        if text:
            return text

        if not text_file:
            raise app_commands.AppCommandError("You need to provide a text file or text to convert")

        if not text_file.content_type == "text/plain":
            raise app_commands.AppCommandError(".txt files only")

        try:
            content = await http.get(text_file.url)
        except Exception:
            raise app_commands.AppCommandError("Invalid .txt file")

        if not content.response:
            raise app_commands.AppCommandError("File you've provided is empty")

        return content.response

    async def encryptout(
        self, interaction: discord.Interaction[DiscordBot], convert: str, _input: Union[bytes, str]
    ) -> None:
        """The main, modular function to control encrypt/decrypt commands"""
        await interaction.response.defer()
        if len(_input) > 1900:
            if isinstance(_input, str):
                data = BytesIO(_input.encode("utf-8"))
            else:
                data = BytesIO(_input)

            try:
                return await interaction.followup.send(
                    content=f"📑 **{convert}**", file=discord.File(data, filename=default.timetext("Encryption"))
                )
            except discord.HTTPException as err:
                # https://discord.com/developers/docs/topics/opcodes-and-status-codes
                if err.code == 50045:
                    return await interaction.followup.send(
                        f"The file I returned was too big, sorry {interaction.user.name}..."
                    )

                return await interaction.followup.send(f"An error occured while sending a file: {err}")

        if isinstance(_input, bytes):
            await interaction.followup.send(f"📑 **{convert}**```fix\n{_input.decode('utf-8')}```")
        else:
            await interaction.followup.send(f"📑 **{convert}**```fix\n{_input}```")

    @encode.command(name="base32")
    async def encode_base32(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Encode in base32"""
        _input = await self.handle_input(text, text_file)
        await self.encryptout(interaction, "Text -> base32", base64.b32encode(_input.encode("utf-8")))

    @decode.command(name="base32")
    async def decode_base32(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Decode in base32"""
        _input = await self.handle_input(text, text_file)
        try:
            await self.encryptout(interaction, "base32 -> Text", base64.b32decode(_input.encode("utf-8")))
        except Exception:
            await interaction.response.send_message("Invalid base32...")

    @encode.command(name="base64")
    async def encode_base64(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Encode in base64"""
        _input = await self.handle_input(text, text_file)
        await self.encryptout(interaction, "Text -> base64", base64.urlsafe_b64encode(_input.encode("utf-8")))

    @decode.command(name="base64")
    async def decode_base64(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Decode in base64"""
        _input = await self.handle_input(text, text_file)
        try:
            await self.encryptout(interaction, "base64 -> Text", base64.urlsafe_b64decode(_input.encode("utf-8")))
        except Exception:
            await interaction.response.send_message("Invalid base64...")

    @encode.command(name="rot13")
    async def encode_rot13(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Encode in rot13"""
        _input = await self.handle_input(text, text_file)
        await self.encryptout(interaction, "Text -> rot13", codecs.decode(_input, "rot_13"))

    @decode.command(name="rot13")
    async def decode_rot13(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Decode in rot13"""
        _input = await self.handle_input(text, text_file)
        try:
            await self.encryptout(interaction, "rot13 -> Text", codecs.decode(_input, "rot_13"))
        except Exception:
            await interaction.response.send_message("Invalid rot13...")

    @encode.command(name="hex")
    async def encode_hex(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Encode in hex"""
        _input = await self.handle_input(text, text_file)
        await self.encryptout(interaction, "Text -> hex", binascii.hexlify(_input.encode("utf-8")))

    @decode.command(name="hex")
    async def decode_hex(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Decode in hex"""
        _input = await self.handle_input(text, text_file)
        try:
            await self.encryptout(interaction, "hex -> Text", binascii.unhexlify(_input.encode("utf-8")))
        except Exception:
            await interaction.response.send_message("Invalid hex...")

    @encode.command(name="base85")
    async def encode_base85(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Encode in base85"""
        _input = await self.handle_input(text, text_file)
        await self.encryptout(interaction, "Text -> base85", base64.b85encode(_input.encode("utf-8")))

    @decode.command(name="base85")
    async def decode_base85(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Decode in base85"""
        _input = await self.handle_input(text, text_file)
        try:
            await self.encryptout(interaction, "base85 -> Text", base64.b85decode(_input.encode("utf-8")))
        except Exception:
            await interaction.response.send_message("Invalid base85...")

    @encode.command(name="ascii85")
    async def encode_ascii85(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Encode in ASCII85"""
        _input = await self.handle_input(text, text_file)
        await self.encryptout(interaction, "Text -> ASCII85", base64.a85encode(_input.encode("utf-8")))

    @decode.command(name="ascii85")
    async def decode_ascii85(
        self,
        interaction: discord.Interaction[DiscordBot],
        text: Optional[str],
        text_file: Optional[discord.Attachment] = None,
    ):
        """Decode in ASCII85"""
        _input = await self.handle_input(text, text_file)
        try:
            await self.encryptout(interaction, "ASCII85 -> Text", base64.a85decode(_input.encode("utf-8")))
        except Exception:
            await interaction.response.send_message("Invalid ASCII85...")


async def setup(bot: DiscordBot):
    await bot.add_cog(Encryption(bot))
