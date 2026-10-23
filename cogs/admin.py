from discord_http import commands, Context, User, CheckFailed
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..index import CustomClient, CustomContext


def is_owner(ctx: CustomContext):
    """ Check if the user is owner. """
    if not ctx.user.id == ctx.bot.config["owner_id"]:
        raise CheckFailed("You are not the owner of this bot")

    return True


class Admin(commands.Cog):
    def __init__(self, bot: CustomClient):
        self.bot: CustomClient = bot

    @commands.command()
    async def amiadmin(self, ctx: Context):
        """ Are you an admin of this bot? """
        if ctx.user.id == self.bot.config["owner_id"]:
            return ctx.response.send_message(
                f"Yes **{ctx.user.name}** you are an admin! ✅"
            )

        # Please do not remove this part.
        # I would love to be credited as the original creator of the source code.
        #   -- AlexFlipnote
        if ctx.user.id == 86477779717066752:
            return ctx.response.send_message(
                f"Well kinda **{ctx.user.name}**.. "
                "you still own the source code"
            )

        return ctx.response.send_message(
            f"no, heck off {ctx.user.name}"
        )

    @commands.command()
    @commands.check(is_owner)
    @commands.describe(
        user="The user to DM",
        message="The message to send to the user",
    )
    async def dm(self, ctx: Context, user: User, message: str):
        async def call_after():
            try:
                await user.send(message)
                await ctx.edit_original_response(content="✉️ Message sent")
            except Exception as e:
                await ctx.edit_original_response(content=f"❌ Failed to send message\n> {e}")

        return ctx.response.defer(
            ephemeral=True, thinking=True,
            call_after=call_after
        )


async def setup(bot: CustomClient):
    """ Setup for this extension. """
    await bot.add_cog(Admin(bot))
