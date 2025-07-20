from discord.ext import commands
import discord

class Purge(commands.Cog):
    """Bulk delete messages."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="purge", description="Delete recent messages")
    @discord.app_commands.describe(count="Number of messages to delete (1-100)")
    async def purge(self, ctx: commands.Context, count: int) -> None:
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send("You don't have permission to purge messages.", ephemeral=True)
            return
        count = max(1, min(100, count))
        deleted = await ctx.channel.purge(limit=count)
        await ctx.send(f"Deleted {len(deleted)} messages", delete_after=5)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Purge(bot))
