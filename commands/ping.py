import logging
import time

from discord.ext import commands

log = logging.getLogger(__name__)

class Ping(commands.Cog):
    """Simple ping command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Show bot latency.")
    async def ping(self, ctx: commands.Context) -> None:
        start = time.monotonic()
        try:
            if ctx.interaction:
                await ctx.interaction.response.defer()
                api_latency = (time.monotonic() - start) * 1000
                await ctx.followup.send(
                    f"Pong! API latency: {api_latency:.0f} ms\nWebSocket latency: {self.bot.latency * 1000:.0f} ms"
                )
            else:
                message = await ctx.reply("Pong!")
                api_latency = (time.monotonic() - start) * 1000
                await message.edit(
                    content=f"Pong! API latency: {api_latency:.0f} ms\nWebSocket latency: {self.bot.latency * 1000:.0f} ms"
                )
        except Exception:
            log.exception("Failed to execute ping command")
            if ctx.interaction:
                await ctx.followup.send("エラーが発生しました。", ephemeral=True)
            else:
                await ctx.reply("エラーが発生しました。")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
