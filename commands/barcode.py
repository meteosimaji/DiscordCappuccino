import asyncio
import os
import tempfile
import discord
from discord.ext import commands

class Barcode(commands.Cog):
    """Generate a Code128 barcode from text."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="barcode", description="Generate barcode")
    async def barcode(self, ctx: commands.Context, *, text: str) -> None:
        text = text.strip()
        if not text:
            await ctx.send("Provide text to encode")
            return
        try:
            import barcode
            from barcode.writer import ImageWriter
            from barcode.errors import IllegalCharacterError
        except ModuleNotFoundError:
            await ctx.send("python-barcode module not installed. `pip install python-barcode`")
            return
        try:
            code = barcode.get("code128", text, writer=ImageWriter())
        except IllegalCharacterError:
            await ctx.send("Code128 supports ASCII characters only")
            return
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        path = tmp.name
        tmp.close()
        await asyncio.to_thread(code.write, path)
        try:
            await ctx.send(file=discord.File(path))
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Barcode(bot))
