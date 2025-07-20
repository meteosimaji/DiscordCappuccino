from discord.ext import commands

from ._music_core import music_controller


class MusicPlay(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        music_controller.set_bot(bot)

    @commands.hybrid_command(name="play", description="Add music to queue")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        vc = await music_controller.ensure_voice(ctx)
        if not vc:
            return
        loop = self.bot.loop
        data = await loop.run_in_executor(
            None, lambda: music_controller.ytdl.extract_info(query, download=False)
        )
        if "entries" in data:
            data = data["entries"][0]
        url = data["url"]
        title = data.get("title", "Unknown")
        state = music_controller.get_state(ctx.guild.id)
        state.queue.append((title, url))
        await ctx.send(f"Queued: {title}")
        if not vc.is_playing() and not vc.is_paused():
            await music_controller.start_player(ctx, state)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicPlay(bot))
