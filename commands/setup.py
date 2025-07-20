import logging
import re
from datetime import timedelta, timezone as dt_timezone

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

TIMEZONE_RE = re.compile(r"^([+-]?)(\d{1,2})$")

# \u6570\u5024\u30aa\u30d5\u30bb\u30c3\u30c8\u8a31\u53ef\u7bc4\u56f2 (-12..+12) 25\u7a2e\u985e (UTC\u542b\u3080)
MIN_OFFSET = -12
MAX_OFFSET = 12

# +9 / -5 / 9 / UTC+9 / UTC-3 / UTC \u306e\u5f62\u5f0f
OFFSET_PATTERN = re.compile(r"^(?:UTC)?([+-]?)(\d{1,2})?$", re.IGNORECASE)


def parse_timezone_input(raw: str, summertime: int | None) -> tuple[str, object]:
    """Parse input text and return label and tzinfo."""
    s = raw.strip()
    # 1) \u4e3b\u8981\u30bf\u30a4\u30e0\u30be\u30fc\u30f3
    if s in PRIMARY_TZS:
        return s, ZoneInfo(s)

    # 2) IANA\u540d\u306b\u6311\u6226
    try:
        z = ZoneInfo(s)
        return s, z
    except ZoneInfoNotFoundError:
        pass

    # 3) \u6570\u5024\u30aa\u30d5\u30bb\u30c3\u30c8
    m = OFFSET_PATTERN.fullmatch(s.upper())
    if not m:
        raise ValueError(
            "\u5f62\u5f0f\u30a8\u30e9\u30fc: 例 `Asia/Tokyo` / `UTC+9` / `+9` / `-5` / `UTC`"
        )

    sign = m.group(1)
    num_str = m.group(2)

    if num_str is None:
        base_offset = 0
    else:
        base_offset = int(num_str)
        if sign == "-":
            base_offset = -base_offset

    if base_offset < MIN_OFFSET or base_offset > MAX_OFFSET:
        raise ValueError(f"\u30aa\u30d5\u30bb\u30c3\u30c8\u7bc4\u56f2\u5916: {MIN_OFFSET}\u301c{MAX_OFFSET}")

    extra = 0
    if summertime:
        try:
            extra = int(summertime)
        except Exception:
            raise ValueError("summertime \u306f\u6574\u6570\u3067\u6307\u5b9a\u3057\u3066\u304f\u3060\u3055\u3044 (\u4f8b 1)")
        if extra not in (0, 1):
            raise ValueError("summertime \u306f 0 \u307e\u305f\u306f 1 \u3092\u63a8\u5968")

    final_offset = base_offset + extra
    if final_offset < MIN_OFFSET or final_offset > MAX_OFFSET:
        raise ValueError(
            f"\u30b5\u30de\u30fc\u30bf\u30a4\u30e0\u9069\u7528\u5f8c\u30aa\u30d5\u30bb\u30c3\u30c8\u7bc4\u56f2\u5916: {MIN_OFFSET}\u301c{MAX_OFFSET}"
        )

    tzinfo = fixed_tz(timedelta(hours=final_offset))
    label = f"UTC{final_offset:+d}"
    if extra and extra != 0:
        label += f" (base {base_offset:+d} + DST {extra})"
    return label, tzinfo


class Setup(commands.Cog):
    """\u30bf\u30a4\u30e0\u30be\u30fc\u30f3\u8a2d\u5b9a\u7528\u30b3\u30de\u30f3\u30c9."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        if not hasattr(self.bot, "timezone"):
            self.bot.timezone = ZoneInfo("UTC")

    @commands.hybrid_command(
        name="setup",
        description="Configure the bot timezone (primary or manual offset).",
    )
    async def setup_command(
        self,
        ctx: commands.Context,
        timezone: str | None = None,
        summertime: int | None = 0,
    ) -> None:
        if timezone is None:
            current = getattr(self.bot.timezone, "key", str(self.bot.timezone))
            await ctx.send(
                f"Current timezone: **{current}**\n"
                f"\u6307\u5b9a\u4f8b: `Asia/Tokyo`, `UTC+9`, `+9`, `UTC`, `-5` (summertime=1 \u53ef)\n"
                f"\u56fa\u5b9a\u30aa\u30d5\u30bb\u30c3\u30c8\u4e00\u89a7: "
                + " ".join(
                    ["UTC"]
                    + [f"{i:+d}" for i in range(MIN_OFFSET, 0)]
                    + [f"+{i}" for i in range(1, MAX_OFFSET + 1)]
                )
            )
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

