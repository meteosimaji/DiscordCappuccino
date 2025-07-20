import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

log = logging.getLogger(__name__)


class ServerIcon(commands.Cog):
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

    @commands.hybrid_command(name="servericon", description="Show the server's icon")
    async def servericon(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        if guild is None:
            await self._reply(ctx, embed=error_embed(desc="Run this in a server."))
            return
        if not guild.icon:
            await self._reply(ctx, embed=error_embed(desc="This server has no icon."))
            return
        try:
            asset = guild.icon.replace(size=1024)
            formats = [f"[{fmt}]({asset.replace(format=fmt)})" for fmt in ("png", "webp", "jpg")]
            if asset.is_animated():
                formats.append(f"[gif]({asset.replace(format='gif')})")
            embed = discord.Embed(
                title=f"\U0001F5BC Server Icon – {guild.name}",
                description=" | ".join(formats),
                color=0x42A5F5,
                timestamp=datetime.utcnow(),
            )
            embed.set_image(url=asset)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("servericon failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to fetch icon"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ServerIcon(bot))
