import discord

from utils import http

ballresponse = [
  'Yes', 'No', 'Take a wild guess...', 'Very doubtful',
  'Sure', 'Without a doubt', 'Most likely', 'Might be possible',
  "You'll be the judge", 'no... (╯°□°）╯︵ ┻━┻', 'no... baka',
  'senpai, pls no ;-;'
]


async def hardstyle(ctx):
    req, url = await http.get(f'https://live.slam.nl/slam-hardstyle/metadata/hardstyle_livewall', as_json=True)

    if url is None:
        return await ctx.send("I think the API broke...")

    embed = discord.Embed(colour=0xC29FAF, description=f"**Live from [Slam!](https://live.slam.nl)**\n\n**{url['nowArtist']} - {url['nowTitle']}**")
    embed.set_thumbnail(url=url['nowImage'])
    return await ctx.send(embed=embed)


async def listenmoe(ctx):
    get, req = await http.get('https://crimsonxv.pro/listenmoe', as_json=True)
    if req is None:
        return await ctx.send("I think the API broke...")

    embed = discord.Embed(colour=0xC29FAF, description=f"**Live from [Listen.moe](https://listen.moe)**\n\n**{req}**")
    embed.set_thumbnail(url='https://listen.moe/files/images/favicons/apple-touch-icon.png')
    return await ctx.send(embed=embed)


async def los40(ctx):
    get, req = await http.get('https://api.radio.net/info/v2/search/nowplaying?_=1513772392174&apikey=e8e10939b65da5e2c00301830d8ae12eecb24238&numberoftitles=12&station=10732', as_json=True)

    if req is None:
        return await ctx.send("I think the API broke...")

    embed = discord.Embed(colour=0xC29FAF, description=f"**Live from [Los40](http://www.emisora.org.es/)**\n\n**{req[0]['streamTitle']}**")
    embed.set_thumbnail(url='http://static.radio.net/images/broadcasts/4c/ce/10732/1/c175.png')
    return await ctx.send(embed=embed)


async def p5(ctx):
    get, req = await http.get('http://oslo.p5.no/backend/onairinformation.ashx?channel=8&items=1', as_json=True)
    if req is None:
        return await ctx.send("I think the API broke...")

    embed = discord.Embed(colour=0xC29FAF, description=f"**Live from [P5 Hits](http://oslo.p5.no/player/)**\n\n**{req['ProgramInstance']['Elements'][1]['Title']}**")
    embed.set_thumbnail(url='http://oslo.p5.no/mmo/channelimages/2038ba8d-a2dc-41a9-8df8-313fcb2cd113.png')
    return await ctx.send(embed=embed)


async def kcrw(ctx):
    get, req = await http.get('https://api.radio.net/info/v2/search/nowplaying?_=1511176792760&apikey=219883e4ea191cda3fdf0b8e6962166e7e15beb2&numberoftitles=10&station=2091', as_json=True)
    if req is None:
        return await ctx.send("I think the API broke...")

    embed = discord.Embed(colour=0xC29FAF, description=f"**Live from [KCRW](http://kcrwmusic.radio.net/)**\n\n**{req[0]['streamTitle']}**")
    return await ctx.send(embed=embed)
