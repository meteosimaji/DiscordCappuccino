import asyncio
import collections
from typing import Deque, Tuple

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

YTDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "default_search": "ytsearch",
}

FFMPEG_OPTS = {
    "options": "-vn",
}


class MusicState:
    def __init__(self):
        self.queue: Deque[Tuple[str, str]] = collections.deque()
        self.current: Tuple[str, str] | None = None
        self.source: discord.PCMVolumeTransformer | None = None
        self.volume: float = 1.0
        self.next_event = asyncio.Event()
        self.position: int = 0

    def reduce_volume(self) -> None:
        if self.source:
            self.source.volume = 0.3

    def restore_volume(self) -> None:
        if self.source:
            self.source.volume = self.volume


class MusicController:
    def __init__(self) -> None:
        self.states: dict[int, MusicState] = {}
        self.ytdl = YoutubeDL(YTDL_OPTS)
        self.bot: commands.Bot | None = None

    def set_bot(self, bot: commands.Bot) -> None:
        if self.bot is None:
            self.bot = bot

    def get_state(self, guild_id: int) -> MusicState:
        return self.states.setdefault(guild_id, MusicState())

    async def ensure_voice(self, ctx: commands.Context) -> discord.VoiceClient | None:
        if ctx.voice_client and ctx.voice_client.is_connected():
            return ctx.voice_client
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("VCに参加してから実行してね")
            return None
        return await ctx.author.voice.channel.connect()

    async def start_player(self, ctx: commands.Context, state: MusicState) -> None:
        if self.bot is None:
            return
        vc = ctx.voice_client
        while state.queue and vc and vc.is_connected():
            title, url = state.queue.popleft()
            state.current = (title, url)
            before = f"-ss {state.position}" if state.position else ""
            src = discord.FFmpegPCMAudio(url, before_options=before, **FFMPEG_OPTS)
            state.source = discord.PCMVolumeTransformer(src, volume=state.volume)
            vc.play(
                state.source,
                after=lambda e: self.bot.loop.call_soon_threadsafe(
                    state.next_event.set
                ),
            )
            await ctx.send(f"Now playing: {title}")
            await state.next_event.wait()
            state.next_event.clear()
            state.position = 0
            state.source = None
            state.current = None
        if vc and vc.is_connected():
            await vc.disconnect()

    def reduce_volume(self, guild_id: int) -> None:
        state = self.states.get(guild_id)
        if state:
            state.reduce_volume()

    def restore_volume(self, guild_id: int) -> None:
        state = self.states.get(guild_id)
        if state:
            state.restore_volume()


music_controller = MusicController()
