from discord.ext import commands

class Ping(commands.Cog):
    """Simple ping command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Responds with 'Pong!'"""
        await ctx.send('Pong!')


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Ping(bot))
