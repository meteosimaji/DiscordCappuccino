import discord
from discord.ext import commands

class UserInfo(commands.Cog):
    """Display basic user information."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="user", description="Show user info")
    async def user(self, ctx: commands.Context, user: discord.User | None = None) -> None:
        target = user or ctx.author
        member = ctx.guild.get_member(target.id) if ctx.guild else None
        embed = discord.Embed(title=f"User: {target}")
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="ID", value=str(target.id), inline=False)
        if member:
            embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UserInfo(bot))
