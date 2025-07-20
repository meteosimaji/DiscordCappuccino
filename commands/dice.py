import random
import re
from discord.ext import commands

class Dice(commands.Cog):
    """Roll dice like 2d6 or d20."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="dice", description="Roll dice in NdM format")
    async def dice(self, ctx: commands.Context, nota: str) -> None:
        m = re.fullmatch(r"(\d*)d(\d+)", nota, re.I)
        if not m:
            await ctx.send("Format is XdY e.g. 2d6, d20")
            return
        count = int(m.group(1)) if m.group(1) else 1
        sides = int(m.group(2))
        if not (1 <= count <= 100):
            await ctx.send("Dice count must be 1-100")
            return
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        txt = ", ".join(map(str, rolls))
        await ctx.send(f"🎲 {nota} → {txt} [total {total}]")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dice(bot))
