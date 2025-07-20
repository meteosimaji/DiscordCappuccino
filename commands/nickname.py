import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

log = logging.getLogger(__name__)


class Nickname(commands.Cog):
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

    @commands.hybrid_command(name="nickname", description="Change a member's nickname")
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx: commands.Context, member: discord.Member, *, new_nick: str) -> None:
        if not ctx.guild:
            await self._reply(ctx, embed=error_embed(desc="Run this in a server."))
            return
        if not ctx.author.guild_permissions.manage_nicknames:
            await self._reply(ctx, embed=error_embed(desc="You lack the required permission: Manage Nicknames"))
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await self._reply(ctx, embed=error_embed(desc="You cannot modify this member."))
            return
        try:
            if new_nick in {"-", "reset"}:
                new_nick = None
            await member.edit(nick=new_nick, reason=f"By {ctx.author}")
            embed = discord.Embed(
                title="\u270F\ufe0f Nickname Updated",
                color=0xFFAA33,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Member", value=member.mention, inline=True)
            embed.add_field(name="New Nick", value=new_nick or "None", inline=True)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("nickname failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to change nickname"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Nickname(bot))
