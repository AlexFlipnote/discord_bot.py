import discord


def can_send(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).send_messages
