import logging
import re
from datetime import timedelta, timezone as fixed_tz

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

MIN_OFFSET = -12
MAX_OFFSET = 14

# +10 / -5 / 10 / UTC / UTC+9 / UTC-3 などを許容
OFFSET_PATTERN = re.compile(r"^(?:UTC)?([+-]?)(\d{1,2})?$", re.IGNORECASE)
# マッチ結果:
#  "UTC"        -> sign="", number=None  (0扱い)
#  "+9"         -> sign="+", number=9
#  "9"          -> sign="", number=9
#  "-5"         -> sign="-", number=5
#  "UTC+10"     -> sign="+", number=10
#  "UTC-3"      -> sign="-", number=3

class Setup(commands.Cog):
    """Timezone configuration command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        if not hasattr(self.bot, "timezone"):
            self.bot.timezone = fixed_tz.utc

    @commands.hybrid_command(
        name="setup",
        description="Configure the bot timezone (UTC offset).",
    )
    @discord.app_commands.describe(
        timezone="Offset like +9, -5, UTC+9, UTC, 10. Omit to reset to UTC."
    )
    async def setup_command(
        self,
        ctx: commands.Context,
        timezone: str | None = None,
    ) -> None:
        if timezone is None:
            # reset to UTC
            self.bot.timezone = fixed_tz.utc
            await ctx.send("Timezone reset to UTC")
            return

        tz_input = timezone.strip().upper()
        m = OFFSET_PATTERN.fullmatch(tz_input)
        if not m:
            await ctx.send(
                f"Invalid format. Examples: `UTC`, `+9`, `-5`, `UTC+9`, `10`\n"
                f"Allowed range: {MIN_OFFSET} to {MAX_OFFSET}"
            )
            return

        sign = m.group(1)
        num = m.group(2)

        if num is None:
            offset = 0  # "UTC" only
        else:
            offset = int(num)
            if sign == "-":
                offset = -offset
            # sign == "+" or "" -> positive

        if offset < MIN_OFFSET or offset > MAX_OFFSET:
            await ctx.send(f"Out of range. Use between {MIN_OFFSET} and {MAX_OFFSET}.")
            return

        self.bot.timezone = fixed_tz(timedelta(hours=offset))
        label = "UTC" if offset == 0 else f"UTC{offset:+d}"
        await ctx.send(f"Timezone set to {label}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
