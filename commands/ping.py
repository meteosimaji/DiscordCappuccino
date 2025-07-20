import logging
import time

from discord.ext import commands

log = logging.getLogger(__name__)

class Ping(commands.Cog):
    """Simple ping command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Show bot latency.")
    async def ping(self, ctx: commands.Context) -> None:
        start = time.perf_counter()
        try:
            if ctx.interaction:
                await ctx.interaction.response.defer()
                api_latency = (time.perf_counter() - start) * 1000
                ws_latency = self.bot.latency * 1000
                await ctx.interaction.followup.send(
                    f"Pong!\nAPI: {api_latency:.0f} ms\nWebSocket: {ws_latency:.0f} ms"
                )
            else:
                message = await ctx.reply("Pong!")
                api_latency = (time.perf_counter() - start) * 1000
                ws_latency = self.bot.latency * 1000
                await message.edit(
                    content=f"Pong!\nAPI: {api_latency:.0f} ms\nWebSocket: {ws_latency:.0f} ms"
                )
        except Exception:
            log.exception("Failed to execute ping command")
            try:
                if ctx.interaction:
                    await ctx.interaction.followup.send("エラーが発生しました。", ephemeral=True)
                else:
                    await ctx.reply("エラーが発生しました。")
            except Exception:
                pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
