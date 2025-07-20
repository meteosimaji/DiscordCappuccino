import logging
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
log = logging.getLogger(__name__)

TIMEZONE_MAP = {
    "UTC": "UTC",
    "Etc/GMT+12": "Etc/GMT+12",
    "Etc/GMT+11": "Etc/GMT+11",
    "Etc/GMT+10": "Etc/GMT+10",
    "Etc/GMT+9": "Etc/GMT+9",
    "Etc/GMT+8": "Etc/GMT+8",
    "Etc/GMT+7": "Etc/GMT+7",
    "Etc/GMT+6": "Etc/GMT+6",
    "Etc/GMT+5": "Etc/GMT+5",
    "Etc/GMT+4": "Etc/GMT+4",
    "Etc/GMT+3": "Etc/GMT+3",
    "Etc/GMT+2": "Etc/GMT+2",
    "Etc/GMT+1": "Etc/GMT+1",
    "Etc/GMT-1": "Etc/GMT-1",
    "Etc/GMT-2": "Etc/GMT-2",
    "Etc/GMT-3": "Etc/GMT-3",
    "Etc/GMT-4": "Etc/GMT-4",
    "Etc/GMT-5": "Etc/GMT-5",
    "Etc/GMT-6": "Etc/GMT-6",
    "Etc/GMT-7": "Etc/GMT-7",
    "Etc/GMT-8": "Etc/GMT-8",
    "Etc/GMT-9": "Etc/GMT-9",
    "Etc/GMT-10": "Etc/GMT-10",
    "Etc/GMT-11": "Etc/GMT-11",
    "Etc/GMT-12": "Etc/GMT-12",
    "Europe/London": "Europe/London",
    "Europe/Paris": "Europe/Paris",
    "Europe/Berlin": "Europe/Berlin",
    "Europe/Moscow": "Europe/Moscow",
    "Africa/Cairo": "Africa/Cairo",
    "Africa/Johannesburg": "Africa/Johannesburg",
    "Asia/Tokyo": "Asia/Tokyo",
    "Asia/Seoul": "Asia/Seoul",
    "Asia/Shanghai": "Asia/Shanghai",
    "Asia/Hong_Kong": "Asia/Hong_Kong",
    "Asia/Singapore": "Asia/Singapore",
    "Asia/Kolkata": "Asia/Kolkata",
    "Asia/Bangkok": "Asia/Bangkok",
    "Australia/Sydney": "Australia/Sydney",
    "Pacific/Auckland": "Pacific/Auckland",
    "America/New_York": "America/New_York",
    "America/Chicago": "America/Chicago",
    "America/Denver": "America/Denver",
    "America/Los_Angeles": "America/Los_Angeles",
    "America/Mexico_City": "America/Mexico_City",
    "America/Sao_Paulo": "America/Sao_Paulo",
}


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setup", description="Configure the bot")
    async def setup_command(
        self, ctx: commands.Context, timezone: str | None = None
    ) -> None:
        if timezone is None:
            tzname = getattr(self.bot.timezone, "key", str(self.bot.timezone))
            await ctx.send(f"Current timezone: {tzname}")
            return

        if timezone not in TIMEZONE_MAP:
            await ctx.send("Unknown timezone. Use one of: " + ", ".join(TIMEZONE_MAP.keys()))
            return

        self.bot.timezone = ZoneInfo(TIMEZONE_MAP[timezone])
        await ctx.send(f"Timezone set to **{timezone}**")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
