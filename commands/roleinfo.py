import logging
from datetime import datetime

import discord
from discord.ext import commands

from utils import error_embed

log = logging.getLogger(__name__)


class RoleInfo(commands.Cog):
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

    @commands.hybrid_command(name="roleinfo", description="Information about a role")
    async def roleinfo(self, ctx: commands.Context, role: discord.Role) -> None:
        try:
            perms = []
            notable = [
                ("Administrator", role.permissions.administrator),
                ("Manage Messages", role.permissions.manage_messages),
                ("Manage Channels", role.permissions.manage_channels),
                ("Ban Members", role.permissions.ban_members),
                ("Kick Members", role.permissions.kick_members),
            ]
            for name, has in notable:
                if has:
                    perms.append(name)
            embed = discord.Embed(
                title=f"\U0001F396\ufe0f Role Info – {role.name}",
                color=role.color if role.color.value else 0xFFC0CB,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="ID", value=str(role.id), inline=True)
            embed.add_field(name="Created", value=discord.utils.format_dt(role.created_at, "R"), inline=True)
            embed.add_field(name="Position", value=str(role.position), inline=True)
            embed.add_field(name="Color", value=str(role.color), inline=True)
            embed.add_field(name="Members", value=str(len(role.members)), inline=True)
            embed.add_field(name="Mentionable", value=str(role.mentionable), inline=True)
            embed.add_field(name="Hoisted", value=str(role.hoist), inline=True)
            embed.add_field(name="Managed", value=str(role.managed), inline=True)
            embed.add_field(name="Key Perms", value=", ".join(perms) or "None", inline=False)
            embed.set_footer(text="Brewed with love \u2615\ufe0f\u2728")
            await self._reply(ctx, embed=embed)
        except Exception:
            log.exception("roleinfo failed")
            await self._reply(ctx, embed=error_embed(desc="Failed to fetch role info"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RoleInfo(bot))
