import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

log = logging.getLogger(__name__)


class Purge(commands.Cog):
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

    @commands.hybrid_command(name="purge", description="Bulk delete messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int, user: discord.Member | None = None) -> None:
        if ctx.guild is None or not isinstance(ctx.channel, discord.TextChannel):
            await self._reply(ctx, embed=error_embed(desc="Run this in a text channel."))
            return
        if amount < 1 or amount > 200:
            await self._reply(ctx, embed=error_embed(desc="Amount must be between 1 and 200"))
            return
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await self._reply(ctx, embed=error_embed(desc="You lack the required permission: Manage Messages"))
            return
        try:
            def check(m: discord.Message) -> bool:
                return user is None or m.author.id == user.id

            deleted = await ctx.channel.purge(limit=amount, check=check, bulk=True)
            embed = discord.Embed(
                title="\U0001F5D1\ufe0f Purge Complete",
                color=0xFFAA33,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Requested", value=str(amount), inline=True)
            embed.add_field(name="Deleted", value=str(len(deleted)), inline=True)
            embed.add_field(name="Filter", value=user.mention if user else "None", inline=True)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("purge failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to purge messages"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Purge(bot))
