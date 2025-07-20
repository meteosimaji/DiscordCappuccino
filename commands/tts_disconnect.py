from discord.ext import commands

from ._tts_core import tts_controller


class TTSDisconnect(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        tts_controller.set_bot(bot)

    @commands.hybrid_command(name="disconnect", description="Disconnect from VC")
    async def disconnect(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await tts_controller.stop_loop(ctx.guild.id)
        await ctx.send("切断しました")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TTSDisconnect(bot))
