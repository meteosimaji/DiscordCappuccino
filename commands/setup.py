import logging
from datetime import timedelta, timezone as dt_timezone

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

# Allowable UTC offset range
MIN_OFFSET = -12
MAX_OFFSET = 14

CHOICES = [
    discord.app_commands.Choice(name=f"{i:+d}", value=i)
    for i in range(MIN_OFFSET, MAX_OFFSET + 1)
]


class Setup(commands.Cog):
    """Timezone configuration command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        if not hasattr(self.bot, "timezone"):
            self.bot.timezone = dt_timezone.utc

    @commands.hybrid_command(
        name="setup",
        description="Configure the bot timezone offset.",
    )
    @discord.app_commands.describe(
        timezone="UTC offset (-12 to +14). Omit to reset to UTC."
    )
    @discord.app_commands.choices(timezone=CHOICES)
    async def setup_command(
        self,
        ctx: commands.Context,
        timezone: int | None = None,
    ) -> None:
        offset = 0 if timezone is None else int(timezone)
        if offset < MIN_OFFSET or offset > MAX_OFFSET:
            await ctx.send(
                f"Invalid timezone offset. Choose between {MIN_OFFSET} and {MAX_OFFSET}."
            )
            return

        self.bot.timezone = dt_timezone(timedelta(hours=offset))
        await ctx.send(f"Timezone set to UTC{offset:+d}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
