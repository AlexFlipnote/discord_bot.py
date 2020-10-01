import discord
import json 
from discord.ext import commands
import requests
import aiohttp
import asyncio


class Reactions(commands.Cog):
    def __init__(self, client):
        self.client = client



    @commands.command(name='lick', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lick(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Lick someone"""
        lick_api = 'https://waifu.pics/api/sfw/lick'
        parameter = dict()
        resp = requests.get(url=lick_api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='Lick', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** licked  **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)  
 
 
  
    @commands.command(name='cuddle', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cuddle(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Cuddle with someone"""
        cuddle_api = 'https://nekos.life/api/v2/img/cuddle'
        parameter = dict()
        resp = requests.get(url=cuddle_api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='Awww', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** cuddled with **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)    

   
    @commands.command(name='baka', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def baka(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Call someone an idiot"""
        baka_api = 'https://nekos.life/api/v2/img/baka'
        parameter = dict()
        resp = requests.get(url=baka_api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='baka', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** called **{member.name}** an Idiot ',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)


    @commands.command(name='blush', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def blush(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Blush at someone"""
        blush_api = 'https://waifu.pics/api/sfw/blush'
        parameter = dict()
        resp = requests.get(url=blush_api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='Blush', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** blushes at **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)  




    @commands.command(name='tickle', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tickle(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Tickle someone"""
        tickle_api = 'https://nekos.life/api/v2/img/tickle'
        parameter = dict()
        resp = requests.get(url=tickle_api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='hehehe', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** tickled  **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)    
       

    @commands.command(name='slap', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slap(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author 
        """Slap someone"""
        api = 'https://nekos.life/api/v2/img/slap'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='It hurts', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author} slapped {member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)


 
    @commands.command(name='kiss', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kiss(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Kiss someone"""
        api = 'https://nekos.life/api/v2/img/kiss'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='Kissi', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** kissed  **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)             

  
    @commands.command(name='pat', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pat(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Pat someone"""
        api = 'https://nekos.life/api/v2/img/pat'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='Pat', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** Patted **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)   

  
    @commands.command(name='hug', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hug(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """hug someone"""
        api = 'https://nekos.life/api/v2/img/hug'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='Awww', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** hugged **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)    
            
  
    @commands.command(name='feed', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def feed(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """feed someone"""
        api = 'https://nekos.life/api/v2/img/feed'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='Feed', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** feeded **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.command(name='poke', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def poke(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """poke someone"""
        api = 'https://nekos.life/api/v2/img/poke'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='poke', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** poked **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)                

    @commands.command(name='slap', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slap(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Slap someone"""
        api = 'https://waifu.pics/api/sfw/slap'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='slap', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** slapped **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)  

    @commands.command(name='bully', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bully(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """bully someone It doesn't promote bullying"""
        api = 'https://waifu.pics/api/sfw/bully'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='bully', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** bullied **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='This does not promote any kind of bullying \n Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)  

    @commands.command(name='bite', ignore_extra=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bite(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.message.author   
        """Bite  someone"""
        api = 'https://waifu.pics/api/sfw/bite'
        parameter = dict()
        resp = requests.get(url=api, params=parameter)
        data = resp.json()
        embed = discord.Embed(title='bite', url=data['url'], color=0xe19fa9, description = f'**{ctx.message.author}** bit **{member.name}**',
                                    timestamp=ctx.message.created_at)
        embed.set_image(url=data['url'])
        embed.set_footer(text='Requested by %s' % ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)  


def setup(client):
    client.add_cog(Reactions(client))





    
