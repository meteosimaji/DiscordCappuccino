from discord.ext import commands

from ._tts_core import tts_controller


class TTSJoin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        tts_controller.set_bot(bot)

    @commands.hybrid_command(name="join", description="Join VC and start reading")
    async def join(self, ctx: commands.Context) -> None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("VCに参加してから実行してね")
            return
        voice = ctx.author.voice.channel
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            vc = await voice.connect()
        state = tts_controller.get_state(ctx.guild.id)
        state.channel_id = ctx.channel.id
        await tts_controller.start_loop(ctx.guild.id, vc)
        await ctx.send("読み上げを開始します")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TTSJoin(bot))
