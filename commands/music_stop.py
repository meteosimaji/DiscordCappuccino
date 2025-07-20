from discord.ext import commands

from ._music_core import music_controller


class MusicStop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        music_controller.set_bot(bot)

    @commands.hybrid_command(name="stop", description="Disconnect and clear queue")
    async def stop(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        if ctx.guild.id in music_controller.states:
            music_controller.states.pop(ctx.guild.id)
        await ctx.send("停止しました")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicStop(bot))
