import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

log = logging.getLogger(__name__)


class UserInfo(commands.Cog):
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

    @commands.hybrid_command(name="userinfo", description="Detailed profile of a user in this guild")
    async def userinfo(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        if ctx.guild is None:
            await self._reply(ctx, embed=error_embed(desc="Run this in a server."))
            return
        target = member or ctx.author
        try:
            fetched = await self.bot.fetch_user(target.id)
            banner = fetched.banner
            embed = discord.Embed(
                title=f"\U0001F464 User Info – {target.display_name}",
                color=0x42A5F5,
                timestamp=datetime.utcnow(),
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            if banner:
                embed.set_image(url=banner.url)
            created = discord.utils.format_dt(target.created_at, "R")
            joined = discord.utils.format_dt(target.joined_at, "R") if target.joined_at else "N/A"
            roles = [r.mention for r in sorted(target.roles, key=lambda r: r.position, reverse=True) if r != ctx.guild.default_role]
            embed.add_field(name="ID", value=str(target.id), inline=True)
            embed.add_field(name="Created", value=created, inline=True)
            embed.add_field(name="Joined", value=joined, inline=True)
            embed.add_field(name="Top Role", value=target.top_role.mention, inline=True)
            embed.add_field(name="Roles", value=", ".join(roles) or "None", inline=False)
            embed.add_field(name="Booster", value="Yes" if target.premium_since else "No", inline=True)
            if target.timed_out_until:
                timeout = discord.utils.format_dt(target.timed_out_until, "R")
                embed.add_field(name="Timeout", value=timeout, inline=True)
            embed.add_field(name="Bot", value="Yes" if target.bot else "No", inline=True)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("userinfo failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to fetch user info"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UserInfo(bot))
