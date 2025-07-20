import logging
import re
from datetime import timedelta, timezone as dt_timezone

import discord
from discord.ext import commands
log = logging.getLogger(__name__)

TIMEZONE_RE = re.compile(r"^([+-]?)(\d{1,2})$")


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setup", description="Configure the bot")
    async def setup_command(
        self,
        ctx: commands.Context,
        timezone: str | None = None,
        summertime: int | None = 0,
    ) -> None:
        if timezone is None:
            tzname = getattr(self.bot.timezone, "key", str(self.bot.timezone))
            await ctx.send(f"Current timezone: {tzname}")
            return

        tz_param = timezone.strip().upper()
        if tz_param == "UTC":
            offset = 0
        else:
            m = TIMEZONE_RE.fullmatch(tz_param)
            if not m:
                await ctx.send("Invalid timezone. Use like +9 or -5 or UTC.")
                return
            sign = -1 if m.group(1) == "-" else 1
            offset = sign * int(m.group(2))

        if summertime:
            try:
                offset += int(summertime)
            except ValueError:
                await ctx.send("Invalid summertime offset.")
                return

        self.bot.timezone = dt_timezone(timedelta(hours=offset))
        await ctx.send(f"Timezone set to UTC{offset:+d}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
