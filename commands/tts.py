import asyncio
import aiohttp
import discord
from discord.ext import commands
from typing import Dict, List, Tuple

import os

VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://localhost:50021")

class TTSState:
    def __init__(self):
        self.channel_id: int | None = None
        self.speaker: int = 1
        self.speed: float = 1.0
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.playing: bool = False

class TTS(commands.Cog):
    """Read messages in a channel using VOICEVOX."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.states: Dict[int, TTSState] = {}
        self.loop_task: Dict[int, asyncio.Task] = {}

    def get_state(self, guild_id: int) -> TTSState:
        return self.states.setdefault(guild_id, TTSState())

    async def tts_loop(self, guild_id: int, voice: discord.VoiceClient) -> None:
        state = self.get_state(guild_id)
        async with aiohttp.ClientSession() as sess:
            while voice.is_connected():
                text = await state.queue.get()
                try:
                    query_url = f"{VOICEVOX_URL}/audio_query"
                    synthesis_url = f"{VOICEVOX_URL}/synthesis"
                    params = {"text": text, "speaker": state.speaker}
                    async with sess.post(query_url, params=params) as r:
                        query = await r.json()
                    query["speedScale"] = state.speed
                    async with sess.post(synthesis_url, params={"speaker": state.speaker}, json=query) as r:
                        audio = await r.read()
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio, pipe=True))
                    music_cog = self.bot.get_cog("Music")
                    if music_cog:
                        music_cog.reduce_volume(guild_id)
                    voice.play(source)
                    while voice.is_playing():
                        await asyncio.sleep(0.1)
                    if music_cog:
                        music_cog.restore_volume(guild_id)
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return
        state = self.states.get(message.guild.id)
        if not state or state.channel_id != message.channel.id:
            return
        await state.queue.put(message.clean_content)

    @commands.hybrid_command(name="join", description="Join VC and start reading")
    async def join(self, ctx: commands.Context) -> None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("VCに参加してから実行してね")
            return
        voice = ctx.author.voice.channel
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            vc = await voice.connect()
        state = self.get_state(ctx.guild.id)
        state.channel_id = ctx.channel.id
        if ctx.guild.id not in self.loop_task or self.loop_task[ctx.guild.id].done():
            self.loop_task[ctx.guild.id] = self.bot.loop.create_task(self.tts_loop(ctx.guild.id, vc))
        await ctx.send("読み上げを開始します")

    @commands.hybrid_command(name="disconnect", description="Disconnect from VC")
    async def disconnect(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        if ctx.guild.id in self.loop_task:
            self.loop_task[ctx.guild.id].cancel()
        await ctx.send("切断しました")

    @commands.hybrid_command(name="setvoice", description="Set speaker and speed")
    @commands.app_commands.describe(speaker="VOICEVOX speaker id", speed="Speed scale 0.5-2.0")
    async def setvoice(self, ctx: commands.Context, speaker: int, speed: float = 1.0) -> None:
        state = self.get_state(ctx.guild.id)
        state.speaker = speaker
        state.speed = speed
        await ctx.send(f"話者:{speaker} 速度:{speed}")

    @commands.hybrid_command(name="skip", description="Skip current speech")
    async def skip(self, ctx: commands.Context) -> None:
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("スキップしました")
        else:
            await ctx.send("再生中の読み上げがありません")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TTS(bot))
