import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

INVITE_URL = "https://example.com/invite"
SUPPORT_URL = "https://example.com/support"

log = logging.getLogger(__name__)


class Invite(commands.Cog):
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

    @commands.hybrid_command(name="invite", description="Show the bot's invite and support links")
    async def invite(self, ctx: commands.Context) -> None:
        try:
            embed = discord.Embed(
                title="\U0001F517 Invite Cappuccino",
                color=0x42A5F5,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Invite Link", value=f"[Click Here]({INVITE_URL})", inline=False)
            embed.add_field(name="Support Server", value=f"[Join]({SUPPORT_URL})", inline=False)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("invite command failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to create invite"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Invite(bot))
