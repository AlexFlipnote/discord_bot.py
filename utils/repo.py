from utils import default

version = "v1.2.4"
invite = "https://discord.gg/DpxkY3x"
owners = default.get("config.json").owners


def is_owner(ctx):
    return ctx.author.id in owners
