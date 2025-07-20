import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    """Display information about the current server."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="server", description="Show server info")
    async def server(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server")
            return
        embed = discord.Embed(title=f"Server: {guild.name}")
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        embed.add_field(name="ID", value=str(guild.id), inline=False)
        embed.add_field(name="Members", value=str(guild.member_count), inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ServerInfo(bot))
