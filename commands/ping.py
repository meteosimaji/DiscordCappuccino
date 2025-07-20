from discord.ext import commands

class Ping(commands.Cog):
    """Simple ping command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Responds with 'Pong!'")
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send('Pong!')


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Ping(bot))
