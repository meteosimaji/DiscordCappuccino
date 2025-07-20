from discord import app_commands
from discord.ext import commands

from ._tts_core import tts_controller


class TTSSetVoice(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        tts_controller.set_bot(bot)

    @commands.hybrid_command(name="setvoice", description="Set speaker and speed")
    @app_commands.describe(speaker="VOICEVOX speaker id", speed="Speed scale 0.5-2.0")
    async def setvoice(
        self, ctx: commands.Context, speaker: int, speed: float = 1.0
    ) -> None:
        state = tts_controller.get_state(ctx.guild.id)
        state.speaker = speaker
        state.speed = speed
        await ctx.send(f"話者:{speaker} 速度:{speed}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TTSSetVoice(bot))
