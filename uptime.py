import discord
from discord.ext import commands
from datetime import datetime, timezone

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now(timezone.utc)

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        """Shows how long the bot has been online."""

        now = datetime.now(timezone.utc)
        uptime = now - self.start_time

        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []

        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")

        parts.append(f"{seconds}s")

        embed = discord.Embed(
            title="Bot Uptime",
            description=f"**Hosted for:** `{', '.join(parts)}`",
            color=discord.Color.blurple()
        )

        embed.set_footer(text="Oxelon Systems")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Uptime(bot))