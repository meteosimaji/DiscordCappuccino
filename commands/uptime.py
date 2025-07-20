import logging
from datetime import datetime, timezone

import discord
from discord.ext import commands

from utils import error_embed, humanize_delta

log = logging.getLogger(__name__)

PROGRESS_BLOCKS = 20  # 20分割のミニバー

def day_progress_bar(seconds_today: float) -> tuple[str, float]:
    """0時を基準にした今日の進捗バー."""
    ratio = max(0.0, min(1.0, seconds_today / 86400))
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
            launch_time: datetime = getattr(self.bot, "launch_time", datetime.now(timezone.utc))
            if launch_time.tzinfo is None:
                launch_time = launch_time.replace(tzinfo=timezone.utc)
            now_utc = datetime.now(timezone.utc)
            delta = now_utc - launch_time
            total_seconds = int(delta.total_seconds())

            human = humanize_delta(total_seconds)
            days = total_seconds // 86400
            rem = total_seconds % 86400
            hours = rem // 3600
            rem %= 3600
            minutes = rem // 60
            seconds = rem % 60

            local_now = now_utc.astimezone(self.bot.timezone)
            midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_today = (local_now - midnight).total_seconds()
            bar, pct = day_progress_bar(seconds_today)

            embed = discord.Embed(
                title="\U0001F464 Cappuccino \u2615 Uptime",
                description="Here's how long I've been awake!",
                color=0x42A5F5,
                timestamp=now_utc
            )

            embed.add_field(
                name="\u23F3 Uptime",
                value=f"{human}\n`{days}d {hours}h {minutes}m {seconds}s`",
                inline=True
            )

            ts = int(launch_time.timestamp())
            embed.add_field(
                name="\U0001F4C5 Started",
                value=f"<t:{ts}:F>\n<t:{ts}:R>",
                inline=True
            )

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
