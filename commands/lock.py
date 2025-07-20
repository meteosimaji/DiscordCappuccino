import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

log = logging.getLogger(__name__)


def _send_perm_error(ctx: commands.Context, perm: str):
    return error_embed(desc=f"You lack the required permission: {perm}")


class ChannelLock(commands.Cog):
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

    @commands.hybrid_command(name="lock", description="Lock a channel for @everyone")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context, channel: discord.TextChannel | None = None, *, reason: str | None = None) -> None:
        target = channel or ctx.channel
        if not isinstance(target, discord.TextChannel):
            await self._reply(ctx, embed=error_embed(desc="Channel type not supported."))
            return
        if not ctx.channel.permissions_for(ctx.author).manage_channels:
            await self._reply(ctx, embed=_send_perm_error(ctx, "Manage Channels"))
            return
        try:
            overwrite = target.overwrites_for(ctx.guild.default_role)
            if overwrite.send_messages is False:
                await self._reply(ctx, embed=error_embed(desc="Channel is already locked."))
                return
            overwrite.send_messages = False
            await target.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
            embed = discord.Embed(
                title="\U0001F512 Channel Locked",
                color=0xFFAA33,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Channel", value=target.mention, inline=True)
            embed.add_field(name="Reason", value=reason or "None", inline=True)
            embed.add_field(name="Actor", value=ctx.author.mention, inline=True)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("lock failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to lock channel"))

    @commands.hybrid_command(name="unlock", description="Unlock a channel for @everyone")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context, channel: discord.TextChannel | None = None) -> None:
        target = channel or ctx.channel
        if not isinstance(target, discord.TextChannel):
            await self._reply(ctx, embed=error_embed(desc="Channel type not supported."))
            return
        if not ctx.channel.permissions_for(ctx.author).manage_channels:
            await self._reply(ctx, embed=_send_perm_error(ctx, "Manage Channels"))
            return
        try:
            overwrite = target.overwrites_for(ctx.guild.default_role)
            if overwrite.send_messages is None or overwrite.send_messages is True:
                await self._reply(ctx, embed=error_embed(desc="Channel is not locked."))
                return
            overwrite.send_messages = None
            await target.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(
                title="\U0001F513 Channel Unlocked",
                color=0xFFAA33,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Channel", value=target.mention, inline=True)
            embed.add_field(name="Actor", value=ctx.author.mention, inline=True)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("unlock failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to unlock channel"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChannelLock(bot))
