import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed, humanize_delta

log = logging.getLogger(__name__)


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
            delta = datetime.utcnow() - getattr(self.bot, "launch_time", datetime.utcnow())
            human = humanize_delta(delta.total_seconds())
            embed = discord.Embed(
                title="\u23F0 Uptime",
                description=human,
                color=0x42A5F5,
                timestamp=datetime.utcnow(),
            )
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("uptime command failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to get uptime"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Uptime(bot))
