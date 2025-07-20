import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed, sanitize

log = logging.getLogger(__name__)


class Say(commands.Cog):
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

    @commands.hybrid_command(name="say", description="Have the bot repeat your message")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx: commands.Context, *, message: str, as_embed: bool = False) -> None:
        text = sanitize(message)
        try:
            if as_embed:
                if len(text) > 1800:
                    await self._reply(ctx, embed=error_embed(desc="Message too long for embed."))
                    return
                embed = discord.Embed(
                    title="\U0001F4AC Say",
                    description=text,
                    color=0x42A5F5,
                    timestamp=datetime.utcnow(),
                )
                embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
                await self._reply(ctx, embed=embed)
            else:
                if len(text) > 2000:
                    await self._reply(ctx, embed=error_embed(desc="Message too long."))
                    return
                await self._reply(ctx, content=text)
        except Exception:
            log.exception("say failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to send message"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Say(bot))
