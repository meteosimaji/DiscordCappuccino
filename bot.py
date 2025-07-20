import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='c!', intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')


# Load commands from commands directory
for filename in os.listdir('./commands'):
    if filename.endswith('.py') and not filename.startswith('_'):
        bot.load_extension(f'commands.{filename[:-3]}')


def main() -> None:
    load_dotenv()
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        raise RuntimeError('DISCORD_BOT_TOKEN environment variable not set')
    bot.run(token)


if __name__ == '__main__':
    main()
