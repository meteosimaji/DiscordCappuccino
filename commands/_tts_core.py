import asyncio
import aiohttp
import os
import discord
from discord.ext import commands
from typing import Dict

from ._music_core import music_controller

VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://localhost:50021")


class TTSState:
    def __init__(self):
        self.channel_id: int | None = None
        self.speaker: int = 1
        self.speed: float = 1.0
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.playing: bool = False


class TTSController:
    def __init__(self) -> None:
        self.bot: commands.Bot | None = None
        self.states: Dict[int, TTSState] = {}
        self.loop_task: Dict[int, asyncio.Task] = {}

    def set_bot(self, bot: commands.Bot) -> None:
        if self.bot is None:
            self.bot = bot

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
                    async with sess.post(
                        synthesis_url, params={"speaker": state.speaker}, json=query
                    ) as r:
                        audio = await r.read()
                    source = discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(audio, pipe=True)
                    )
                    music_controller.reduce_volume(guild_id)
                    voice.play(source)
                    while voice.is_playing():
                        await asyncio.sleep(0.1)
                    music_controller.restore_volume(guild_id)
                except Exception:
                    pass

    async def enqueue(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return
        state = self.states.get(message.guild.id)
        if not state or state.channel_id != message.channel.id:
            return
        await state.queue.put(message.clean_content)

    async def start_loop(self, guild_id: int, vc: discord.VoiceClient) -> None:
        if guild_id not in self.loop_task or self.loop_task[guild_id].done():
            task = self.bot.loop.create_task(self.tts_loop(guild_id, vc))
            self.loop_task[guild_id] = task

    async def stop_loop(self, guild_id: int) -> None:
        if guild_id in self.loop_task:
            self.loop_task[guild_id].cancel()


tts_controller = TTSController()
