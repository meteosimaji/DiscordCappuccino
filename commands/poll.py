import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed, sanitize

log = logging.getLogger(__name__)


class Poll(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _reply(self, ctx: commands.Context, **kwargs):
        if ctx.interaction:
            if ctx.interaction.response.is_done():
                return await ctx.interaction.followup.send(**kwargs)
            else:
                return await ctx.interaction.response.send_message(**kwargs)
        else:
            return await ctx.send(**kwargs)

    @commands.hybrid_command(name="poll", description="Create a simple reaction poll")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def poll(self, ctx: commands.Context, question: str, option1: str, option2: str, option3: str | None = None, option4: str | None = None) -> None:
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        if len(options) < 2 or len(options) > 4:
            await self._reply(ctx, embed=error_embed(desc="Provide between 2 and 4 options."))
            return
        for opt in options:
            if len(opt) > 100:
                await self._reply(ctx, embed=error_embed(desc="Options must be under 100 characters."))
                return
        try:
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            embed = discord.Embed(
                title="\U0001F4CA Poll",
                description=sanitize(question),
                color=0x42A5F5,
                timestamp=datetime.utcnow(),
            )
            for idx, opt in enumerate(options, start=1):
                embed.add_field(name=f"{emojis[idx-1]}", value=sanitize(opt), inline=False)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            message = await self._reply(ctx, embed=embed)
            if isinstance(message, (discord.Message, discord.InteractionMessage)):
                target_message = message
            else:
                return
            for idx in range(len(options)):
                try:
                    await target_message.add_reaction(emojis[idx])
                except Exception:
                    pass
        except Exception:
            log.exception("poll failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to create poll"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Poll(bot))
