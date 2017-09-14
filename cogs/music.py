import asyncio
import glob
import os
import logging
import discord
import youtube_dl

from assets import lists, music
from discord.ext import commands

"""
    License: MIT
    Originally By Rapptz. Modified and Adapted By Joshwoo70. Further Tweaks thanks to AlexFlipnote
"""

userairia = 1
longvids = False
volume = 0.5
skipsreq = 3

ffbefopts = '-nostdin'
ffopts = '-vn -reconnect 1'

ytdlnpl = youtube_dl.YoutubeDL(lists.ytdl_noplaylist)
ytdl = youtube_dl.YoutubeDL(lists.ytdl_format_options)
ytdlaria = youtube_dl.YoutubeDL(lists.ytdl_aria)


# Try Deleting message Function
async def trydel(ctx, quiet=True):
    try:
        await ctx.delete()
    except discord.Forbidden:
        if quiet:
            await ctx.send("Unable to Delete Message.")
        else:
            pass
    except AttributeError:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            if quiet:
                await ctx.send("Unable to Delete Message.")
            else:
                pass
        except AttributeError as e:
            print(f"Attribute Error! Please Check code. {e.__traceback__}")


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, aria=False):
        loop = loop or asyncio.get_event_loop()
        if aria:
            data = await loop.run_in_executor(None, ytdlaria.extract_info, url)
        else:
            data = await loop.run_in_executor(None, ytdlnpl.extract_info, url)
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = (ytdlnpl.prepare_filename(data))
        return cls(discord.FFmpegPCMAudio(filename, before_options=ffbefopts, options=ffopts), data=data)


class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.requester = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()  # a set of user_ids that voted

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False
        return not self.voice.is_playing()

    @property
    def player(self):
        return self.current.player


class Music:
    """
    Voice related commands.
    Works in multiple servers at once.
    """

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, guild):
        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[guild.id] = state
        return state

    async def create_voice_bot(self, channel):
        voice = await channel.connect()
        state = self.get_voice_state(channel.guild)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    async def playlist(self, ctx, url):
        state = self.get_voice_state(ctx.message.guild)
        getinfo = music.exinfo(url, playlist=True)
        for x in getinfo['entries']:
            print(x)
            try:
                await state.songs.put(x['webpage_url'])
            except TypeError:
                pass
            except KeyError:
                await state.songs.put(f"https://www.youtube.com/watch?v={x['url']}")
        if state.voice.is_playing():
            pass
        else:
            await self.getnextsong(ctx)

    @commands.command(pass_context=True, no_pm=True)  # Done
    async def summon(self, ctx):
        try:
            summoned_channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send('Your are not in a voice channel!')
            await trydel(ctx)
            return False

        state = self.get_voice_state(ctx.message.guild)
        if state.voice is None:
            state.voice = await summoned_channel.connect()
            await ctx.send(f"Ready to Play Music at #{summoned_channel} Channel.")
        else:
            await state.voice.move_to(summoned_channel)
            await ctx.send(f"Ready to Play Music at #{summoned_channel} Channel.")

        return True

    @commands.command(pass_context=True, no_pm=True)  # Done
    async def play(self, ctx, *, url: str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.guild)
        aria = userairia
        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return
        if 'playlist?list=' in url:
            await ctx.send("Sent playlist to processing... **NOTE: This might take a while! (Seriously long time.)**")
            await self.playlist(ctx, url)
            return
        try:
            if state.voice.is_playing():
                getinfo = music.exinfo(url, playlist=False)
                print(getinfo)
                if 'entries' in getinfo:
                    FYI = 1
                    getinfo = getinfo['entries'][0]
                    url = getinfo['webpage_url']
                else:
                    FYI = 0
                await ctx.send(f"Added **{getinfo['title']}**")
                await trydel(ctx)
                await state.songs.put(url)
                return
        except AttributeError as e:
            print("Attribute Error! Do Not Be alarmed")
            print(e)
            # Since it's NoneType that means nothing is playing.
            pass
        await trydel(ctx)
        message = await ctx.send("Processing Video...")
        if ctx.voice_client is not None:
            getinfo = music.exinfo(url, playlist=False)
            print(getinfo)
            if 'entries' in getinfo:
                FYI = 1
                getinfo = getinfo['entries'][0]
                url = getinfo['webpage_url']
            else:
                FYI = 0
            durationsecs = getinfo['duration']
            if durationsecs >= 3600 and longvids is False:
                return await ctx.send('This video is over an hour... Administrators has enabled "No long videos".')
            if int(aria) == 1:
                state.current = await YTDLSource.from_url(url, loop=self.bot.loop, aria=True)
            else:
                state.current = await YTDLSource.from_url(url, loop=self.bot.loop)
            source = discord.PCMVolumeTransformer(state.current)
            source.volume = volume
            state.current.player = source
            state.requester = str(ctx.message.author.name)
            await trydel(message)
            m, s = divmod(getinfo['duration'], 60)
            title, vc, avrate = getinfo['title'], getinfo['view_count'], round(getinfo['average_rating'])
            link = getinfo['webpage_url']
            uploader = getinfo['uploader']
            embed = discord.Embed(title='Now Playing', color=0x43B581)
            desclist = []
            desclist.append(f"Title: {str(title)}\n")
            desclist.append(f"Length: **{m}m{s}s**\n")
            desclist.append(f"Views: {str(vc)}\n")
            desclist.append(f"Average Ratings: {str(avrate)}\n")
            desclist.append(f"Link: {str(link)}\n")
            desclist.append(f"Uploaded By: {str(uploader)}\n")
            if FYI == 1:
                desclist.append("This Video is in a playlist. To get the playlist instead, send the playlist instead of the video.")
            embed.description = ''.join(desclist)
            embed.set_thumbnail(url=getinfo['thumbnail'])
            await ctx.send(embed=embed)
            ctx.voice_client.play(source, after=lambda e: self.nextsongandlog(ctx))
        else:
            await ctx.send("Not connected to channel")

    @commands.command(pass_context=True, no_pm=True)  # Done
    async def volume(self, ctx, value=None):
        """Sets/Gets the volume of the currently playing song."""
        state = self.get_voice_state(ctx.message.guild)
        player = state.player
        try:
            value = int(value)
        except ValueError:
            return await ctx.send("""Can't Change volume!""")
        except TypeError:
            pass
        if value is None:
            await ctx.send(f'Current Volume: {player.volume:.0%}')
        else:
            global volume
            if state.voice.is_playing():
                player.volume = value / 100
                volume = float(player.volume)
                await ctx.send(f'Set the volume to {player.volume:.0%}')
            else:
                volume = float(player.volume)
                await ctx.send(f'Set the volume to {player.volume:.0%}, for next time.')

    async def getnextsong(self, ctx):
        print("get nextsong issued.")
        aria = userairia
        print("aria : {str(aria)}")
        state = self.get_voice_state(ctx.message.guild)
        if ctx.voice_client is None:
            print("voice client is none")
            return
        try:
            songurl = state.songs.get_nowait()
        except asyncio.QueueEmpty:
            print("empty queue")
            return
        getinfo = music.exinfo(songurl, playlist=False)
        if getinfo is None:
            return await self.getnextsong(ctx)
        durationsecs = getinfo['duration']
        if durationsecs >= 3600 and longvids is False:
            await self.getnextsong(ctx)
            return await ctx.send('This video is over an hour... Administrators has enabled "No long videos".')
        print(aria)
        if int(aria) == 1:
            state.current = await YTDLSource.from_url(songurl, loop=self.bot.loop, aria=True)
        else:
            state.current = await YTDLSource.from_url(songurl, loop=self.bot.loop)
        source = discord.PCMVolumeTransformer(state.current)
        source.volume = volume
        state.current.player = source
        m, s = divmod(getinfo['duration'], 60)
        title, vc, avrate = getinfo['title'], getinfo['view_count'], round(getinfo['average_rating'])
        link = getinfo['webpage_url']
        uploader = getinfo['uploader']
        embed = discord.Embed(title='Now Playing', color=0x43B581)
        desclist = []
        desclist.append(f"Title: {title}\n")
        desclist.append(f"Length: **{m}m{s}s**\n")
        desclist.append(f"Views: {vc}\n")
        desclist.append(f"Average Ratings: {avrate}\n")
        desclist.append(f"Link: {link}\n")
        desclist.append(f"Uploaded By: {uploader}\n")
        embed.description = ''.join(desclist)
        embed.set_thumbnail(url=getinfo['thumbnail'])
        await ctx.send(embed=embed)
        ctx.voice_client.play(source, after=lambda e: self.nextsongandlog(ctx))

    @commands.command(pass_context=True, no_pm=True)  # Done
    async def pause(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.guild)
        if state.voice.is_paused():
            ctx.send("Paused Music Playing.")
            state.voice.resume()
        else:
            ctx.send("Resumed Music Playing.")
            state.voice.pause()

    @commands.command(pass_context=True, no_pm=True)  # Done
    async def disconnect(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        guild = ctx.message.guild
        state = self.get_voice_state(ctx.message.guild)
        state.current = None
        if state.is_playing():
            player = state.player
            try:
                player.stop()
            except AttributeError:
                pass
        try:
            print('Stopping!')
            del self.voice_states[guild.id]
            await state.voice.disconnect()
            await ctx.send(f"Disconnected From #{state.voice.channel.name}")
        except Exception as e:
            print(e)
            pass
        for file in glob.glob('youtube-*.*'):
            try:
                os.remove(file)
            except PermissionError:
                pass

    def nextsongandlog(self, ctx):
        print("next song")
        coro = self.getnextsong(ctx)
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            result = fut.result()
            print(result)
        except Exception as e:
            print(e)
            pass

    @commands.command(pass_context=True, no_pm=True)  # Done
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.guild)
        if not state.voice.is_playing():
            await ctx.send('Not playing any music right now...')
            return
        voter = ctx.message.author
        if voter.name == state.requester:
            await ctx.send('Requester requested to skip song. skipping song...')
            state.skip_votes.clear()
            if state.voice.is_playing():
                state.voice.stop()
                await self.getnextsong(ctx)
        elif (ctx.message.channel.permissions_for(ctx.message.author)).move_members:
            await ctx.send(f'{ctx.message.author.name} Forced to skip song. Skipping...')
            state.skip_votes.clear()
            if state.voice.is_playing():
                state.voice.stop()
                await self.getnextsong(ctx)
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= skipsreq:
                votemessage = await ctx.say('Skipping song...')
                await asyncio.sleep(1)
                await trydel(votemessage)
                state.skip_votes.clear()
                if state.voice.is_playing():
                    state.voice.stop()
                    await self.getnextsong(ctx)

            else:
                await ctx.send(f'Skip vote added, currently at [{total_votes}/{skipsreq}]')
        else:
            await ctx.send(f'You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)  # Done
    async def queue(self, ctx):
        """Shows info about the queue."""
        state = self.get_voice_state(ctx.message.guild)
        skip_count = len(state.skip_votes)
        queue = []
        dembed = discord.Embed(title="Bot playlist:", color=0x7289DA)
        try:
            if state.current is None:
                dembed.add_field(name="Currently playing", value="Emptiness of the void.")
                return await ctx.send(embed=dembed)
            # HACK: uses internal _queue function.
            l = list(state.songs._queue)
            for x in l[:5]:
                info = music.exinfo(x)
                m, s = divmod(info['duration'], 60)
                y = f"""Title: **{info['title']}**\nLength: **{m}m{s}s**\n"""
                queue.append(y)
            if len(l) > 5:
                queue.append("{} More Not listed.".format(str(len(l) - 5)))

            fqueue = ''.join(queue)
            cm, cs = divmod(state.current.data['duration'], 60)
            dembed.add_field(name='Currently playing:',
                             value='Title: **{}**\nLength: **{}m{}s**\n[skips: {}/3]'.format(
                                 state.current.data['title'],
                                 cm, cs, skip_count))
            if not fqueue == '':
                dembed.add_field(name='Up Next:', value=fqueue)
            else:
                pass
            await ctx.send(embed=dembed)
        except AttributeError as e:
            print("attribute error! {}".format(e))

    @commands.command(pass_context=True, no_pm=True)
    async def debugstate(self, ctx):
        state = self.get_voice_state(ctx.message.guild)
        logging.info(state.voice.__dict__)
        logging.info(state.current.__dict__)
        logging.info(state.player.__dict__)
        logging.info(state.songs._queue)


def setup(bot):
    bot.add_cog(Music(bot))
