import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

log = logging.getLogger(__name__)


class React(commands.Cog):
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

    @commands.hybrid_command(name="react", description="Add a reaction to a message")
    async def react(self, ctx: commands.Context, message_id: int, emoji: str) -> None:
        if not isinstance(ctx.channel, discord.TextChannel):
            await self._reply(ctx, embed=error_embed(desc="Run in a text channel."))
            return
        try:
            msg = await ctx.channel.fetch_message(message_id)
            await msg.add_reaction(emoji)
            embed = discord.Embed(
                title="\u2705 Reaction Added",
                color=0xFFAA33,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Message", value=f"[Jump]({msg.jump_url})", inline=False)
            embed.add_field(name="Emoji", value=emoji, inline=True)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("react failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to add reaction"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(React(bot))
