import logging
import time
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands

import io

from utils import error_embed, chunk_string

log = logging.getLogger(__name__)


class ServerInfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _reply(self, ctx: commands.Context, **kwargs) -> None:
        if ctx.interaction:
            if ctx.interaction.response.is_done():
                await ctx.interaction.followup.send(**kwargs)
            else:
                await ctx.interaction.response.send_message(**kwargs)
        else:
            await ctx.send(**kwargs)

    @commands.hybrid_command(
        name="serverinfo",
        description="Display a detailed snapshot of this server.",
    )
    async def serverinfo(
        self,
        ctx: commands.Context,
        show_counts: bool = True,
        show_roles: bool = True,
        collapse_roles: bool = False,
        show_emojis: bool = True,
        show_boosters: bool = True,
    ) -> None:
        guild = ctx.guild
        if guild is None:
            await self._reply(ctx, embed=error_embed(desc="Run this in a server."))
            return
        start = time.perf_counter()
        if ctx.interaction:
            await ctx.interaction.response.defer()
        try:
            humans = sum(1 for m in guild.members if not m.bot)
            bots = guild.member_count - humans
            online = sum(1 for m in guild.members if m.status != discord.Status.offline)
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)
            threads = sum(len(ch.threads) for ch in guild.text_channels)
            emoji_total = len(guild.emojis)
            animated = sum(1 for e in guild.emojis if e.animated)
            static = emoji_total - animated
            boosters: Optional[list[discord.Member]] = guild.premium_subscribers
            ws_latency = self.bot.latency * 1000
            embed = discord.Embed(
                title=f"\U0001F310 Server Info – {guild.name}",
                color=0xFFC0CB,
                timestamp=datetime.utcnow(),
            )
            embed.set_footer(text="Brewed with love ☕️✨")
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            embed.add_field(name="ID", value=guild.id, inline=True)
            embed.add_field(
                name="Created",
                value=f"{discord.utils.format_dt(guild.created_at, 'R')} ({guild.created_at:%Y-%m-%d})",
                inline=True,
            )
            embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
            if show_counts:
                embed.add_field(
                    name="Members",
                    value=f"Total: **{guild.member_count}**\nHumans: {humans} | Bots: {bots}\nOnline: {online}",
                    inline=False,
                )
                embed.add_field(
                    name="Channels",
                    value=f"Text: {text_channels} | Voice: {voice_channels} | Cat: {categories} | Threads: {threads}",
                    inline=False,
                )
                embed.add_field(
                    name="Other",
                    value=f"Boost Lvl: {guild.premium_tier}\nLatency: {ws_latency:.0f} ms",
                    inline=False,
                )
            send_file = None
            if show_roles:
                roles_sorted = [r for r in sorted(guild.roles, key=lambda r: r.position, reverse=True) if r != guild.default_role]
                if collapse_roles:
                    display = ", ".join(r.mention for r in roles_sorted[:10])
                    if len(roles_sorted) > 10:
                        display += " ..."
                    embed.add_field(name=f"Roles ({len(roles_sorted)})", value=display or "None", inline=False)
                else:
                    role_mentions = [r.mention for r in roles_sorted]
                    chunks = chunk_string(role_mentions)
                    if len(roles_sorted) > 200 or sum(len(c) for c in chunks) > 6000:
                        content = "\n".join(f"{r.name} ({r.id})" for r in roles_sorted)
                        send_file = discord.File(io.BytesIO(content.encode("utf-8")), filename="roles.txt")
                        embed.add_field(name=f"Roles ({len(roles_sorted)})", value="All roles included in attached file.", inline=False)
                    else:
                        for idx, part in enumerate(chunks, start=1):
                            title = f"Roles ({idx}/{len(chunks)})" if len(chunks) > 1 else f"Roles ({len(roles_sorted)})"
                            embed.add_field(name=title, value=part, inline=False)
            if show_emojis:
                embed.add_field(
                    name=f"Emojis ({emoji_total})",
                    value=f"Static: {static} | Animated: {animated}" if emoji_total else "None",
                    inline=False,
                )
            if show_boosters and boosters:
                sample = boosters[:10]
                booster_value = " ".join(m.mention for m in sample)
                if len(boosters) > 10:
                    booster_value += f" +{len(boosters) - 10} more"
                embed.add_field(name=f"Boosters ({len(boosters)})", value=booster_value, inline=False)
            api_latency = (time.perf_counter() - start) * 1000
            embed.add_field(name="API", value=f"{api_latency:.0f} ms", inline=False)
            if send_file:
                await self._reply(ctx, embed=embed, file=send_file)
            else:
                await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("serverinfo failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to build server info."))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ServerInfo(bot))
