# DiscordCappuccino

This is a lightweight Discord bot example.  Extensions under `commands/` are loaded dynamically and most functionality is provided via slash commands.  It includes a simple music player and several utility commands.

## Directory layout
```text
DiscordCappuccino/
├─ bot.py
├─ commands/
│  ├─ __init__.py
│  └─ *.py
├─ .env.example
└─ requirements.txt
```

## `.env.example`
```text
DISCORD_BOT_TOKEN=YOUR_TOKEN_HERE
BOT_PREFIX=c!
SUPPORT_SERVER_URL=https://example.com/support
BOT_INVITE_URL=https://example.com/invite
```
Copy this file to `.env` and fill in the actual values.

## Running
1. Prepare Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set `DISCORD_BOT_TOKEN`.
5. Run the bot with `python bot.py`.

## Adding commands
Create `commands/xxx.py` and define a Cog class with `async def setup(bot)` to register it.

```python
from discord.ext import commands

class Example(commands.Cog):
    ...

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Example(bot))
```

## Features
- Music playback from YouTube and other sources (`/play`, `/queue`, `/remove`, `/keep`, `/seek`, `/rewind`, `/forward`, `/stop`)
- Utility commands such as `/ping`, `/uptime`, `/dice`, `/qr`, `/barcode`, `/user`, `/server`, `/purge`

## FAQ
Prefix commands can be disabled by setting `BOT_PREFIX` to an empty string.  If prefix commands do not work, enable the Message Content Intent in the Developer Portal.
