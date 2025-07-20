from discord.ext import commands

from ._tts_core import tts_controller


class TTSSkip(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        tts_controller.set_bot(bot)

    @commands.hybrid_command(name="skip", description="Skip current speech")
    async def skip(self, ctx: commands.Context) -> None:
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("スキップしました")
        else:
            await ctx.send("再生中の読み上げがありません")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TTSSkip(bot))
