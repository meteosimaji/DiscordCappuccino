from __future__ import annotations

import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from ._tts_core import tts_controller
from ._music_core import music_controller


class TTSSay(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        tts_controller.set_bot(bot)
        music_controller.set_bot(bot)

    @commands.hybrid_command(name="tts", description="Speak text in VC")
    @app_commands.describe(text="Text to speak")
    async def tts(self, ctx: commands.Context, *, text: str) -> None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("VCに参加してから実行してね")
            return
        vc = ctx.voice_client or await ctx.author.voice.channel.connect()
        state = tts_controller.get_state(ctx.guild.id)
        audio = await tts_controller.generate_audio(text, state.speaker, state.speed)
        if not audio:
            await ctx.send("音声生成に失敗しました")
            return
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio, pipe=True))
        await music_controller.reduce_volume(ctx.guild.id)
        vc.play(source)
        while vc.is_playing():
            await asyncio.sleep(0.1)
        await music_controller.restore_volume(ctx.guild.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TTSSay(bot))
