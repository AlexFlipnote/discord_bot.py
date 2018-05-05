from utils import default

version = "v1.2.4"
invite = "https://discord.gg/DpxkY3x"


def is_owner(ctx):
    return ctx.author.id in default.get("config.json").owners
