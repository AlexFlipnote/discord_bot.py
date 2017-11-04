owners = [
    86477779717066752      # AlexFlipnote
]

version = "v1.1"
invite = "https://discord.gg/DpxkY3x"


def is_owner(ctx):
    return ctx.author.id in owners
