from discord.ext import commands

from ._music_core import music_controller


class MusicSeek(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        music_controller.set_bot(bot)

    @commands.hybrid_command(name="seek", description="Seek current track")
    async def seek(self, ctx: commands.Context, position: int) -> None:
        state = music_controller.states.get(ctx.guild.id)
        if not state or not state.current or not ctx.voice_client:
            await ctx.send("再生中の曲がありません")
            return
        state.position = position
        ctx.voice_client.stop()
        await ctx.send(f"{position}秒から再生します")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicSeek(bot))
