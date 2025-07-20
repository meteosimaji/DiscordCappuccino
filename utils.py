import discord


def humanize_delta(seconds: float) -> str:
    seconds = int(seconds)
    units = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    parts = []
    for suffix, size in units:
        value, seconds = divmod(seconds, size)
        if value:
            parts.append(f"{value}{suffix}")
    return " ".join(parts) if parts else "0s"


def error_embed(title: str = "\u26A0\ufe0f Error", desc: str = "Something went wrong.") -> discord.Embed:
    return discord.Embed(title=title, description=desc, color=0xFF0000)


def sanitize(text: str) -> str:
    return text.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")


def chunk_string(items, sep: str = ", ", max_len: int = 1000) -> list[str]:
    """Split items into chunks not exceeding ``max_len`` characters."""
    chunks: list[str] = []
    buf = ""
    for it in items:
        token = str(it)
        token_len = len(token) if not buf else len(sep) + len(token)
        if not buf:
            buf = token
        elif len(buf) + token_len <= max_len:
            buf += sep + token
        else:
            chunks.append(buf)
            buf = token
    if buf:
        chunks.append(buf)
    return chunks
