import asyncio
import aiohttp
import os
import io
from typing import Dict

import discord
from discord.ext import commands
from gtts import gTTS

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

    async def fetch_audio(
        self, sess: aiohttp.ClientSession, text: str, speaker: int, speed: float
    ) -> bytes | None:
        """Fetch audio data from VOICEVOX or fall back to gTTS."""
        try:
            query_url = f"{VOICEVOX_URL}/audio_query"
            synthesis_url = f"{VOICEVOX_URL}/synthesis"
            params = {"text": text, "speaker": speaker}
            async with sess.post(query_url, params=params) as r:
                query = await r.json()
            query["speedScale"] = speed
            async with sess.post(
                synthesis_url, params={"speaker": speaker}, json=query
            ) as r:
                return await r.read()
        except Exception:
            pass

        try:
            loop = asyncio.get_running_loop()
            tts = gTTS(text=text, lang="ja", slow=False)
            buf = io.BytesIO()
            await loop.run_in_executor(None, tts.write_to_fp, buf)
            return buf.getvalue()
        except Exception:
            return None

    async def generate_audio(
        self, text: str, speaker: int, speed: float
    ) -> bytes | None:
        async with aiohttp.ClientSession() as sess:
            return await self.fetch_audio(sess, text, speaker, speed)

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
                    audio = await self.fetch_audio(sess, text, state.speaker, state.speed)
                    if not audio:
                        continue
                    source = discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(audio, pipe=True)
                    )
                    await music_controller.reduce_volume(guild_id)
                    voice.play(source)
                    while voice.is_playing():
                        await asyncio.sleep(0.1)
                    await music_controller.restore_volume(guild_id)
                except Exception:
                    pass

    async def enqueue(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return
        state = self.states.get(message.guild.id)
        if not state or state.channel_id != message.channel.id:
            return
        await state.queue.put(message.clean_content)

    async def enqueue_text(self, guild_id: int, text: str) -> None:
        state = self.get_state(guild_id)
        await state.queue.put(text)

    async def start_loop(self, guild_id: int, vc: discord.VoiceClient) -> None:
        if guild_id not in self.loop_task or self.loop_task[guild_id].done():
            task = self.bot.loop.create_task(self.tts_loop(guild_id, vc))
            self.loop_task[guild_id] = task

    async def stop_loop(self, guild_id: int) -> None:
        if guild_id in self.loop_task:
            self.loop_task[guild_id].cancel()


tts_controller = TTSController()
