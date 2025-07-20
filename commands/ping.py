import logging
import time
from datetime import datetime, timezone

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

class Ping(commands.Cog):
    """Simple ping command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="ping",
        description="Check the bot's responsiveness with style and speed!",
    )
    async def ping(self, ctx: commands.Context) -> None:
        try:
            if ctx.interaction:
                start = time.perf_counter()
                await ctx.interaction.response.defer()
                api_latency = (time.perf_counter() - start) * 1000
            else:
                start = time.perf_counter()
                await ctx.typing()
                api_latency = (time.perf_counter() - start) * 1000
            ws_latency = self.bot.latency * 1000

            now_utc = datetime.now(timezone.utc)
            embed = discord.Embed(
                title="\U0001F3D3 Cappuccino Ping",
                description="Here's how fast I can respond!",
                color=0xFFC0CB,
                timestamp=now_utc,
            )
            embed.add_field(
                name="\U0001F4BB API Latency", value=f"{api_latency:.0f} ms", inline=True
            )
            embed.add_field(
                name="\U0001F4E1 WebSocket", value=f"{ws_latency:.0f} ms", inline=True
            )
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")

            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)
        except Exception:
            log.exception("Failed to execute ping command")
            error_embed = discord.Embed(
                title="\u26A0\ufe0f Ping Failed",
                description="An error occurred while measuring latency.",
                color=0xFF0000,
            )
            try:
                if ctx.interaction:
                    await ctx.interaction.followup.send(embed=error_embed, ephemeral=True)
                else:
                    await ctx.send(embed=error_embed)
            except Exception:
                pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
