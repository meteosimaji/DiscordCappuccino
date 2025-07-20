import logging
import platform
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed, humanize_delta

log = logging.getLogger(__name__)


class BotInfo(commands.Cog):
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

    @commands.hybrid_command(name="botinfo", description="Information about Cappuccino bot")
    async def botinfo(self, ctx: commands.Context) -> None:
        try:
            uptime = datetime.utcnow() - getattr(self.bot, "launch_time", datetime.utcnow())
            user_count = sum(g.member_count or 0 for g in self.bot.guilds)
            embed = discord.Embed(
                title="\U0001F916 Cappuccino Info",
                color=0x42A5F5,
                timestamp=datetime.utcnow(),
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(name="ID", value=str(self.bot.user.id), inline=True)
            embed.add_field(name="Guilds", value=str(len(self.bot.guilds)), inline=True)
            embed.add_field(name="Users", value=str(user_count), inline=True)
            embed.add_field(name="Uptime", value=humanize_delta(uptime.total_seconds()), inline=True)
            embed.add_field(name="Python", value=platform.python_version(), inline=True)
            embed.add_field(name="discord.py", value=discord.__version__, inline=True)
            embed.add_field(name="Latency", value=f"{self.bot.latency*1000:.0f} ms", inline=True)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("botinfo failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to gather info"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotInfo(bot))
