from urllib.parse import urlparse, parse_qs
from async_timeout import timeout
from discord.ext import commands
import youtube_dl
import itertools
import functools
import aiohttp
import asyncio
import discord
import random
import json
import math
import os

youtube_dl.utils.bug_reports_message = lambda: ''
youtube_apiv3_key = os.environ['DEMIDO_DISCORD_YOUTUBE_APIV3_KEY']  # youtube_apiv3_key = "your key"
""" The YouTube APIv3 key. It's higly reccomended to create an environment variable like the one above instead of 
setting it like shown in the lateral comment.
"""


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    """This class manages the youtube video data as well as returning the url of the audio file from the google servers.
    Attributes:
        ctx (commands.Context): The context value of the command
        source (discord.FFmpegPCMAudio): The song YouTube url
        data (dict): Other data related to the source
        volume (float): The volume of the player
    """
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': False,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
    """ The options for the youtube-dl software. """
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }
    """ The options for the FFMpeg software. """
    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        """ Creates the variables that will be used in the whole extension. """
        super().__init__(source, volume)
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data
        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        """ Creates a YTDLSource to use for playing music.
        Args:
            ctx (commands.Context): The context of the command
            search (str): String containing the searched song (It can also be an url)
            loop (asyncio.BaseEventLoop): The loop if there is one
        Returns:
            YTDLSource using the url of the audio file from the google servers
        Raises:
            YTDLError
        """
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int) -> str:
        """
        Args:
            duration:
        Returns:
            The formatted duration
        """
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))
        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self) -> str:
        """ Creates the embed for songs.
            Returns:
                The discord.py embed to be sent
            """
        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .add_field(name='Views', value='{0.source.views}'.format(self))
                 .add_field(name='Likes', value='{0.source.likes}'.format(self))
                 .set_thumbnail(url=self.source.thumbnail)
                 .set_footer(text= "Epifiz Music", icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png"))
        return embed


class Playlist:

    def __init__(self, bot, ctx, playlist_id):
        self.bot = bot
        self.ctx = ctx
        self.playlist_id = playlist_id

    async def play(self):
        """ Creates and sends an embed for the playlist and adds the songs to the queue.
        """
        playlist_info_url = "https://youtube.googleapis.com/youtube/v3/playlists?part=snippet&id={playlist_id}&" \
                            "maxResults=20&key={youtube_apiv3_key}" \
            .format(youtube_apiv3_key=youtube_apiv3_key, playlist_id=self.playlist_id)
        playlist_info = {}
        async with aiohttp.ClientSession() as session:
            async with session.get(playlist_info_url) as resp:
                playlist_item = json.loads(await resp.text())['items'][0]['snippet']
                playlist_info["name"] = playlist_item['title']
                playlist_info["default_thumbnail"] = playlist_item["thumbnails"]["medium"]["url"]
        playlist_content_url = "https://www.googleapis.com/youtube/v3/playlistItems?key={youtube_apiv3_key}&" \
                               "playlistId={playlist_id}&maxResults=20&part=contentDetails" \
            .format(playlist_id=self.playlist_id, youtube_apiv3_key=youtube_apiv3_key)
        async with aiohttp.ClientSession() as session:
            async with session.get(playlist_content_url) as resp:
                videoList = json.loads(await resp.text())['items']
                embed_message = (discord.Embed(title='Queue updated',
                                               description='```css\nAdded {songs_number} songs to the current '
                                                           'queue\n```'.format(songs_number=len(videoList)),
                                               color=discord.Color.blurple())
                                 .add_field(name='Playlist', value="[{playlist_name}](https://www.youtube.com/"
                                                                   "playlist?list={playlist_id})"
                                            .format(playlist_name=playlist_info['name'], playlist_id=self.playlist_id))
                                 .add_field(name='Requested by', value="{author_mention}"
                                            .format(author_mention=self.ctx.author.mention))
                                 .add_field(name='URL', value='[Click](https://www.youtube.com/playlist?'
                                                              'list={playlist_id})'
                                            .format(playlist_id=self.playlist_id))
                                 .set_thumbnail(url=playlist_info["default_thumbnail"]))
                message = await self.ctx.send(embed=embed_message)
                VoiceState.delete_messages.append(message)
                for video in videoList:
                    videoUrl = "https://youtube.com/watch?v={videoId}" \
                        .format(videoId=video['contentDetails']['videoId'])
                    source = await YTDLSource.create_source(self.ctx, videoUrl, loop=self.bot.loop)
                    song = Song(source)
                    await self.ctx.voice_state.songs.put(song)


class SongQueue(asyncio.Queue):
    """ Management of queues """
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        """ Clears the current queue """
        self._queue.clear()

    def shuffle(self):
        """ Randomizes the songs order for the current queue. """
        random.shuffle(self._queue)

    def remove(self, index: int):
        """ Removes a song from the current queue.
        Args:
            index (int): The song index (number) in the current queue
        """
        del self._queue[index]


class VoiceState:
    """ Songs control
    Arguments:
        bot (commands.Bot): The client
        ctx (commands.Context): Command context
    """
    delete_messages = []

    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self) -> bool:
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        """ Loops the currently playing song.
        Args:
            value (bool): Activates (True) or deactivates (False) the loop.
        """
        self._loop = value

    @property
    def volume(self) -> float:
        """
        Returns:
            The volume of the current player
        """
        return self._volume

    @volume.setter
    def volume(self, value: float):
        """ Sets the volume for the current player
        Args:
            value (float): The volume of the player
        """
        self._volume = value

    @property
    def is_playing(self) -> bool:
        """
        Returns:
            The play status of the player. (If there is any song playing or not)
        """
        return self.voice and self.current

    async def audio_player_task(self):
        """ Creates a task for the current player queue. """
        while True:
            self.next.clear()
            if not self.loop:
                try:
                    async with timeout(180):
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return
            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            self.delete_messages.append(await self.current.source.channel.send(embed=self.current.create_embed()))
            await self.next.wait()

    def play_next_song(self, error=None):
        """ Plays the next song from the queue. """
        if error:
            raise VoiceError(str(error))
        for deletable_message in self.delete_messages:
            self.bot.loop.create_task(deletable_message.delete())
        self.next.set()

    def skip(self):
        """ Skips the song that is currently playing. """
        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        """ Stops the currently playing song and deletes the queue. """
        self.songs.clear()
        if self.voice is not None:
            self.voice.stop()


class Music(commands.Cog):
    """ Class related to the Music commands.
    Attributes:
        bot (commands.Bot): The client
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        """
        Args:
            ctx (commands.context): The command context
        Returns:
            The voice state of the current player.
        """
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context) -> bool:
        """ Performs checks on the commands.
        Returns:
            True if the check went well and there were no errors otherwise False.
        """
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')
        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    @commands.command(name='join', aliases=["enter", "connect"], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """ Makes the bot join the channel where the ctx author is currently in.
        Args:
            ctx (commands.Context): The command context
        """
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """ The bot joins a channel given by the user.
        If no channel is specified the bot will join the command author channel.
        Args:
            ctx (commands.Context): The command context
            channel (discord.VoiceChannel): The channel where the bot should join.
        """
        if not channel and not ctx.author.voice:
            raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')
        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    async def _leave(self, ctx: commands.Context):
        """ The bot leaves the channel in which it currently is in.
        Args:
            ctx (commands.Context): The command context
        """
        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.')
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """ Sets the volume for the player.
        Args:
            ctx (commands.Context): The command context
            volume (int): The volume to be set. (between 0 and 100)
        """
        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')
        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100')
        ctx.voice_state.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing', "song"])
    async def _now(self, ctx: commands.Context):
        """ Sends a message containing the currently playing song.
        Args:
            ctx (commands.Context): The command context
        """
        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """ Pauses the currently playing song
        Args:
            ctx (commands.Context): The command context
        """
        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        """ Resumes the song that was playing and was paused
        Args:
            ctx (commands.Context): The command context
        """
        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        """ Stops the currently playing or paused song.
        Args:
             ctx (commands.Context): The command context
        """
        ctx.voice_state.songs.clear()
        if ctx is not None and ctx.voice_state is not None and ctx.voice_state.is_playing is not None:
            await ctx.voice_state.stop()

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """ Skips the currently playing song and plays the next one in the queue if present.
        Args:
            ctx (commands.Context): The command context
        """
        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')
        ctx.voice_state.skip()

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """ Sends a message with the current songs queue
        Args:
            ctx (commands.Context): The message context
            page (int): The page of the queue (if there are more than one page)
        """
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')
        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)
        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed, delete_after=20)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """ Shuffles the current queue songs so that they'll play randomly.
        Args:
            ctx (commands.Context): The command context
        """
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')
        ctx.voice_state.songs.shuffle()

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        """ Removes a song from teh current queue
        Args:
            ctx (commands.Context): The command context
            index (int): The page number
        """
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')
        ctx.voice_state.songs.remove(index - 1)

    @commands.command(name='loop', aliases=["repeat"])
    async def _loop(self, ctx: commands.Context):
        """ Loops the current song
        Args:
            ctx (commands.Context): The command context
        """
        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')
        ctx.voice_state.loop = not ctx.voice_state.loop

    @commands.command(name='play', aliases=["p"])
    async def _play(self, ctx: commands.Context, *, search: str):
        """ Plays a song
        Args:
            ctx (commands.Context): The command context
            search (str): The search content. It can also be an URL.
        """
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        if search.__contains__('?list=') or search.__contains__('&list='):
            parsed_url = urlparse(search)
            playlist_id = parse_qs(parsed_url.query)['list'][0]
            playlist = Playlist(self.bot, ctx, playlist_id)
            await playlist.play()
        else:
            async with ctx.typing():
                try:
                    source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
                except YTDLError as e:
                    await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                else:
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    message = await ctx.send('Enqueued {}'.format(str(source)), delete_after=20)
                    VoiceState.delete_messages.append(message)

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        """ Checks the connection to voice channels
        Args:
            ctx (commands.Context): The command context
        """
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')


def setup(bot):
    bot.add_cog(Music(bot))