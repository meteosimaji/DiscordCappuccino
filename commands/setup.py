import logging
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
from discord import app_commands

log = logging.getLogger(__name__)

TIMEZONE_CHOICES = [
    discord.app_commands.Choice(name="UTC", value="UTC"),
    discord.app_commands.Choice(name="Asia/Tokyo", value="Asia/Tokyo"),
    discord.app_commands.Choice(name="America/New_York", value="America/New_York"),
]


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setup", description="Configure the bot")
    @app_commands.describe(timezone="Timezone to use for uptime")
    @app_commands.choices(timezone=TIMEZONE_CHOICES)
    async def setup_command(
        self, ctx: commands.Context, timezone: str | None = None
    ) -> None:
        if timezone is None:
            tzname = getattr(self.bot.timezone, "key", str(self.bot.timezone))
            await ctx.send(f"Current timezone: {tzname}", ephemeral=True)
            return
        try:
            tz = ZoneInfo(timezone)
        except Exception:
            await ctx.send("Invalid timezone", ephemeral=True)
            return
        self.bot.timezone = tz
        await ctx.send(f"Timezone set to {timezone}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
