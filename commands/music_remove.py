from discord.ext import commands

from ._music_core import music_controller


class MusicRemove(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        music_controller.set_bot(bot)

    @commands.hybrid_command(name="remove", description="Remove track from queue")
    async def remove(self, ctx: commands.Context, index: int) -> None:
        state = music_controller.states.get(ctx.guild.id)
        if not state or not (1 <= index <= len(state.queue)):
            await ctx.send("番号が無効です")
            return
        removed = state.queue[index - 1]
        del state.queue[index - 1]
        await ctx.send(f"Removed: {removed[0]}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicRemove(bot))
