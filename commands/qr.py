import asyncio
import os
import tempfile
import discord
from discord.ext import commands

class QR(commands.Cog):
    """Generate a QR code from text."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="qr", description="Generate QR code")
    async def qr(self, ctx: commands.Context, *, text: str) -> None:
        text = text.strip()
        if not text:
            await ctx.send("Provide text to encode")
            return
        try:
            import qrcode
        except ModuleNotFoundError:
            await ctx.send("qrcode module not installed. `pip install qrcode`")
            return
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        path = tmp.name
        tmp.close()
        await asyncio.to_thread(img.save, path)
        try:
            await ctx.send(file=discord.File(path))
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QR(bot))
