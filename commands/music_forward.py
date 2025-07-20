from discord.ext import commands

from ._music_core import music_controller


class MusicForward(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        music_controller.set_bot(bot)

    @commands.hybrid_command(name="forward", description="Forward current track")
    async def forward(self, ctx: commands.Context, seconds: int) -> None:
        state = music_controller.states.get(ctx.guild.id)
        if not state or not state.current:
            await ctx.send("再生中の曲がありません")
            return
        state.position += seconds
        if ctx.voice_client:
            ctx.voice_client.stop()
        await ctx.send(f"{seconds}秒早送り")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicForward(bot))
