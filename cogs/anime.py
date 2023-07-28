import discord
from discord.ext import commands
import aiohttp

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def randomanime(self, ctx):
        """Fetch a random anime image."""
        # Send the "Processing..." message
        await ctx.send("Fetching a random anime image...")

        # Make the API request
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.nekosapi.com/v2/images/random") as response:
                    data = await response.json()
                    image_url = data["data"]["attributes"]["file"]
                    title = data["data"]["attributes"]["title"]
        except Exception as e:
            await ctx.send(f"Failed to fetch a random anime image.\nError: {e}")
            return

        # Send the image and title as an embed
        embed = discord.Embed(title=title)
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Anime(bot))
