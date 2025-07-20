"""Discord bot entry point."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
from dotenv import load_dotenv


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger(__name__)

COMMANDS_PATH = Path(__file__).parent / "commands"


class CappuccinoBot(commands.Bot):
    """Bot implementation with async extension loading."""

    def __init__(self, prefix: str) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=prefix, intents=intents)
        tz_name = os.getenv("TIMEZONE", "UTC")
        try:
            self.timezone = ZoneInfo(tz_name)
        except Exception:
            log.warning("Invalid TIMEZONE %s, falling back to UTC", tz_name)
            self.timezone = ZoneInfo("UTC")
        self.launch_time = datetime.now(timezone.utc)

    async def setup_hook(self) -> None:  # type: ignore[override]
        successes, failures = await self.load_all_extensions()
        log.info("Extensions loaded: %d success, %d failed", len(successes), len(failures))
        if failures:
            log.info("Failed extensions: %s", ", ".join(failures))
        synced = await self.tree.sync()
        log.info("Synced %d application command(s)", len(synced))

    async def load_all_extensions(self) -> tuple[list[str], list[str]]:
        """Load every extension under the commands directory."""

        successes: list[str] = []
        failures: list[str] = []
        for file in sorted(COMMANDS_PATH.glob("*.py")):
            if file.name.startswith("_") or file.name == "__init__.py":
                continue
            ext = f"{COMMANDS_PATH.name}.{file.stem}"
            try:
                await self.load_extension(ext)
                log.info("Loaded extension %s", ext)
                successes.append(ext)
            except Exception:
                log.exception("Failed to load extension %s", ext)
                failures.append(ext)
        return successes, failures


def main() -> None:
    """Bot startup sequence."""

    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")
    prefix = os.getenv("BOT_PREFIX", "c!")
    if not token or token.startswith("YOUR_"):
        raise SystemExit("ERROR: valid DISCORD_BOT_TOKEN not set")

    bot = CappuccinoBot(prefix)
    bot.run(token)


if __name__ == "__main__":
    main()

