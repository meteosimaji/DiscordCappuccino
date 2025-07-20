import asyncio
import collections
import re
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

    def reduce_volume(self):
        if self.source:
            self.source.volume = 0.3

    def restore_volume(self):
        if self.source:
            self.source.volume = self.volume

class Music(commands.Cog):
    """Simple music player using yt-dlp and ffmpeg."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.states: dict[int, MusicState] = {}
        self.ytdl = YoutubeDL(YTDL_OPTS)

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
        vc = ctx.voice_client
        while state.queue and vc and vc.is_connected():
            title, url = state.queue.popleft()
            state.current = (title, url)
            before = f"-ss {state.position}" if state.position else ""
            src = discord.FFmpegPCMAudio(url, before_options=before, **FFMPEG_OPTS)
            state.source = discord.PCMVolumeTransformer(src, volume=state.volume)
            vc.play(state.source, after=lambda e: self.bot.loop.call_soon_threadsafe(state.next_event.set))
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

    @commands.hybrid_command(name="play", description="Add music to queue")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        vc = await self.ensure_voice(ctx)
        if not vc:
            return
        loop = self.bot.loop
        data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(query, download=False))
        if "entries" in data:
            data = data["entries"][0]
        url = data["url"]
        title = data.get("title", "Unknown")
        state = self.get_state(ctx.guild.id)
        state.queue.append((title, url))
        await ctx.send(f"Queued: {title}")
        if not vc.is_playing() and not vc.is_paused():
            await self.start_player(ctx, state)

    @commands.hybrid_command(name="queue", description="Show music queue")
    async def queue_cmd(self, ctx: commands.Context) -> None:
        state = self.states.get(ctx.guild.id)
        if not state or not state.queue:
            await ctx.send("キューは空だよ")
            return
        desc = "\n".join(f"{i+1}. {t}" for i, (t, _) in enumerate(state.queue))
        await ctx.send(desc)

    @commands.hybrid_command(name="remove", description="Remove track from queue")
    async def remove(self, ctx: commands.Context, index: int) -> None:
        state = self.states.get(ctx.guild.id)
        if not state or not (1 <= index <= len(state.queue)):
            await ctx.send("番号が無効です")
            return
        removed = state.queue[index-1]
        del state.queue[index-1]
        await ctx.send(f"Removed: {removed[0]}")

    # HybirdCommand cannot handle variable positional arguments when registering
    # as an application command. Disable the app command version so that the
    # prefix command can still accept multiple indices.
    @commands.hybrid_command(
        name="keep",
        description="Keep only specified tracks",
        with_app_command=False,
    )
    async def keep(self, ctx: commands.Context, *indices: int) -> None:
        state = self.states.get(ctx.guild.id)
        if not state or not indices:
            await ctx.send("番号を指定してね")
            return
        new_queue = [t for i, t in enumerate(state.queue, 1) if i in indices]
        state.queue = collections.deque(new_queue)
        await ctx.send("キューを更新しました")

    @commands.hybrid_command(name="seek", description="Seek current track")
    async def seek(self, ctx: commands.Context, position: int) -> None:
        state = self.states.get(ctx.guild.id)
        if not state or not state.current or not ctx.voice_client:
            await ctx.send("再生中の曲がありません")
            return
        state.position = position
        ctx.voice_client.stop()
        await ctx.send(f"{position}秒から再生します")

    @commands.hybrid_command(name="rewind", description="Rewind current track")
    async def rewind(self, ctx: commands.Context, seconds: int) -> None:
        state = self.states.get(ctx.guild.id)
        if not state or not state.current:
            await ctx.send("再生中の曲がありません")
            return
        new_pos = max(0, state.position - seconds)
        state.position = new_pos
        if ctx.voice_client:
            ctx.voice_client.stop()
        await ctx.send(f"{seconds}秒巻き戻し")

    @commands.hybrid_command(name="forward", description="Forward current track")
    async def forward(self, ctx: commands.Context, seconds: int) -> None:
        state = self.states.get(ctx.guild.id)
        if not state or not state.current:
            await ctx.send("再生中の曲がありません")
            return
        state.position += seconds
        if ctx.voice_client:
            ctx.voice_client.stop()
        await ctx.send(f"{seconds}秒早送り")

    @commands.hybrid_command(name="stop", description="Disconnect and clear queue")
    async def stop(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        if ctx.guild.id in self.states:
            self.states.pop(ctx.guild.id)
        await ctx.send("停止しました")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
