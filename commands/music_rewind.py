from discord.ext import commands

from ._music_core import music_controller


class MusicRewind(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        music_controller.set_bot(bot)

    @commands.hybrid_command(name="rewind", description="Rewind current track")
    async def rewind(self, ctx: commands.Context, seconds: int) -> None:
        state = music_controller.states.get(ctx.guild.id)
        if not state or not state.current:
            await ctx.send("再生中の曲がありません")
            return
        new_pos = max(0, state.position - seconds)
        state.position = new_pos
        if ctx.voice_client:
            ctx.voice_client.stop()
        await ctx.send(f"{seconds}秒巻き戻し")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicRewind(bot))
