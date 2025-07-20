from discord.ext import commands

from ._music_core import music_controller


class MusicQueue(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        music_controller.set_bot(bot)

    @commands.hybrid_command(name="queue", description="Show music queue")
    async def queue_cmd(self, ctx: commands.Context) -> None:
        state = music_controller.states.get(ctx.guild.id)
        if not state or not state.queue:
            await ctx.send("キューは空だよ")
            return
        desc = "\n".join(f"{i+1}. {t}" for i, (t, _) in enumerate(state.queue))
        await ctx.send(desc)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicQueue(bot))
