import collections
from discord.ext import commands

from ._music_core import music_controller


class MusicKeep(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        music_controller.set_bot(bot)

    @commands.hybrid_command(
        name="keep", description="Keep only specified tracks", with_app_command=False
    )
    async def keep(self, ctx: commands.Context, *indices: int) -> None:
        state = music_controller.states.get(ctx.guild.id)
        if not state or not indices:
            await ctx.send("番号を指定してね")
            return
        new_queue = [t for i, t in enumerate(state.queue, 1) if i in indices]
        state.queue = collections.deque(new_queue)
        await ctx.send("キューを更新しました")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicKeep(bot))
