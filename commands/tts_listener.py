from discord.ext import commands

from ._tts_core import tts_controller


class TTSListener(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        tts_controller.set_bot(bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        await tts_controller.enqueue(message)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TTSListener(bot))
