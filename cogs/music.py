import os
import asyncio
import discord
from discord.ext import commands

import youtube_dl
from youtubesearchpython import SearchVideos

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def join(self, ctx):
        self.playlist = []
        if ctx.author.voice == None:
            await ctx.send('pls join a vc')
            return
        if ctx.guild.voice_client in bot.voice_clients:
            await ctx.send('already connected to vc')
            return
        await ctx.author.voice.channel.connect()
        await ctx.send('connected to your vc')
    
    @commands.command()
    async def play(self,ctx,*args):

        if ctx.author.voice == None:
            await ctx.send('pls join a vc')
            return

        self.playlist.append(' '.join(args))
        await ctx.send(f"{' '.join(args)} has been added to queue")

        if ctx.message.guild.voice_client.is_playing()==False:
            self.play_song(ctx.message.guild.voice_client)
    
    def play_song(self,voice_client):

        try:
           song = self.playlist.pop(0)
        except:
            return

        results = SearchVideos(song,offset=1,mode='dict',max_results=1)
        x = results.result()
        for I in x['search_result']:

            ytdl_format_options = {
                'format' : 'bestaudio/best' ,
                'postprocessors' : [{
                       'key' : 'FFmpegExtractAudio' ,
                       'preferredcodec' : 'mp3' ,
                       'preferredquality' : '192' ,
                       }]
                }

            ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

            audio = ytdl.extract_info(I['link'],download = False)
            streamable_url = audio['formats'][0]['url']
            before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            voice_client.play(discord.FFmpegPCMAudio(streamable_url,before_options = before_options),after =lambda e: self.play_song(voice_client))

    @commands.command()
    async def pause(self,ctx):
        if ctx.message.author.voice == None:
            await ctx.send('please join vc')
            return
        ctx.message.guild.voice_client.pause()
        await ctx.send('song paused')
    
    @commands.command()
    async def resume(self,ctx):
        if ctx.message.author.voice == None:
            await ctx.send('please join vc')
            return
        ctx.message.guild.voice_client.resume()
        await ctx.send('song resumed')
    
    @commands.command(aliases = ['poda_patti','s'])
    async def skip(self,ctx):
        if ctx.message.author.voice == None:
            await ctx.send('please join vc')
            return
        ctx.message.guild.voice_client.stop()
        await ctx.send('song skipped')
     
    @commands.command()
    async def queue(self,ctx):

        if  ctx.message.author.voice==None:
            await ctx.send('please join vc')
            return
        if self.playlist== []:
            await ctx.send('empty queue')
            return
        for i,s in enumerate(self.playlist):
            await ctx.send(f'*{i+1})*: **`{s}`**')
    
    @commands.command()
    async def remove(self,ctx,position : int):
 
        if  ctx.message.author.voice==None:
            await ctx.send('please join vc')
            return
        if self.playlist == []:
            await ctx.send('empty queue')
            return
        try:
            removed_song = self.playlist.pop(position-1)
            await ctx.send(f'{removed_song} removed')
        except:
            await ctx.send('number out of range')
    
    @commands.command()
    async def disconnect(self, ctx):
        if  ctx.message.author.voice==None:
            await ctx.send('please join vc')
            return
        for x in self.bot.voice_clients:
            if(x.guild == ctx.message.guild):
                await x.disconnect()
                await ctx.send("Disconnected from VC")
        del self.playlist


def setup(bot):
    bot.add_cog(Music(bot))
