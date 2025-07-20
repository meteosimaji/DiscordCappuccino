# -*- coding: utf-8 -*-
"""Discord bot entry point."""
from __future__ import annotations

import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

COMMANDS_PATH = Path(__file__).parent / "commands"


def create_bot(prefix: str) -> commands.Bot:
    """Create bot with minimal intents."""
    intents = discord.Intents.none()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True
    bot = commands.Bot(command_prefix=prefix, intents=intents)

    @bot.event
    async def on_ready() -> None:
        logger.info("Logged in as %s", bot.user)
        try:
            synced = await bot.tree.sync()
            logger.info("Synced %d command(s)", len(synced))
        except Exception:
            logger.exception("Failed to sync commands")

    return bot


def load_extensions(bot: commands.Bot, directory: Path) -> tuple[list[str], list[str]]:
    """Load extensions from the given directory."""
    successes: list[str] = []
    failures: list[str] = []
    pattern = "[A-Za-z0-9_]*.py"
    for file in sorted(directory.glob(pattern)):
        if file.name.startswith("_") or file.name == "__init__.py":
            continue
        ext = f"{directory.name}.{file.stem}"
        try:
            bot.load_extension(ext)
            logger.info("Loaded extension %s", ext)
            successes.append(ext)
        except Exception:
            logger.exception("Failed to load extension %s", ext)
            failures.append(ext)
    return successes, failures


def main() -> None:
    """Bot startup sequence."""
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")
    prefix = os.getenv("BOT_PREFIX", "c!")
    if not token or token.startswith("YOUR_"):
        logger.error("DISCORD_BOT_TOKEN is not set correctly. Please check your .env file.")
        raise SystemExit(1)

    bot = create_bot(prefix)
    successes, failures = load_extensions(bot, COMMANDS_PATH)
    logger.info("Extensions loaded: %d success, %d failed", len(successes), len(failures))
    if failures:
        logger.info("Failed extensions: %s", ", ".join(failures))

    bot.run(token)


if __name__ == "__main__":
    main()
