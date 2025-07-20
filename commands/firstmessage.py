import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

log = logging.getLogger(__name__)


class FirstMessage(commands.Cog):
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

    @commands.hybrid_command(name="firstmessage", description="Show the first message in a channel")
    async def firstmessage(self, ctx: commands.Context, channel: discord.TextChannel | None = None) -> None:
        target = channel or ctx.channel
        if not isinstance(target, discord.TextChannel):
            await self._reply(ctx, embed=error_embed(desc="Channel type not supported."))
            return
        try:
            msg = None
            async for m in target.history(limit=1, oldest_first=True):
                msg = m
            if msg is None:
                await self._reply(ctx, embed=error_embed(desc="Channel has no messages."))
                return
            content = (msg.content[:180] + "...") if len(msg.content) > 180 else msg.content
            embed = discord.Embed(
                title=f"\U0001F4AC First Message – #{target.name}",
                description=content or "(embed/attachment)",
                color=0x42A5F5,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Author", value=msg.author.mention, inline=True)
            embed.add_field(name="Jump", value=f"[Link]({msg.jump_url})", inline=True)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("firstmessage failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to fetch first message"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FirstMessage(bot))
