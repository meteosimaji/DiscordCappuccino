import logging
from datetime import datetime, timezone

import discord
from discord.ext import commands

from utils import error_embed, humanize_delta

log = logging.getLogger(__name__)

PROGRESS_BLOCKS = 12  # 12分割のミニバー

def day_progress_bar(seconds: float) -> str:
    """その日の経過割合(0-1)から簡易バーを作成."""
    within_day = seconds % 86400
    ratio = within_day / 86400
    filled = int(ratio * PROGRESS_BLOCKS)
    empty = PROGRESS_BLOCKS - filled
    return "▰" * filled + "▱" * empty, ratio * 100


class Uptime(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _reply(self, ctx: commands.Context, **kwargs) -> None:
        if ctx.interaction:
            if ctx.interaction.response.is_done():
                await ctx.interaction.followup.send(**kwargs)
            else:
                await ctx.interaction.response.send_message(**kwargs)
        else:
            await ctx.send(**kwargs)

    @commands.hybrid_command(name="uptime", description="Show how long the bot has been running")
    async def uptime(self, ctx: commands.Context) -> None:
        try:
            launch_time: datetime = getattr(self.bot, "launch_time", datetime.utcnow().replace(tzinfo=timezone.utc))
            now = datetime.utcnow().replace(tzinfo=timezone.utc)
            delta = now - launch_time
            total_seconds = int(delta.total_seconds())

            human = humanize_delta(total_seconds)
            days = total_seconds // 86400
            rem = total_seconds % 86400
            hours = rem // 3600
            rem %= 3600
            minutes = rem // 60
            seconds = rem % 60

            bar, pct = day_progress_bar(total_seconds)

            embed = discord.Embed(
                title="⏱ Cappuccino Uptime",
                description="Here's how long I've been awake!",
                color=0x42A5F5,
                timestamp=now
            )

            # Uptime (メイン)
            embed.add_field(
                name="🟢 Uptime",
                value=f"{human}\n`{days}d {hours}h {minutes}m {seconds}s`",
                inline=True
            )

            # 起動時刻 (絶対 + 相対)
            ts = int(launch_time.timestamp())
            embed.add_field(
                name="🗓 Started",
                value=f"<t:{ts}:F>\n<t:{ts}:R>",
                inline=True
            )

            # 1日内の経過率 (進捗バー)
            embed.add_field(
                name="🌅 Day Progress",
                value=f"`{bar}` {pct:4.1f}%",
                inline=False
            )

            embed.set_footer(text="Brewed with love ☕✨")

            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("uptime command failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to get uptime"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Uptime(bot))
