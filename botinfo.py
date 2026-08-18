import discord
from discord.ext import commands


class BotInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="botinfo")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def botinfo(self, ctx: commands.Context):
        guilds = self.bot.guilds

        # Unique users across every server the bot can see
        unique_users = set()

        for guild in guilds:
            for member in guild.members:
                if not member.bot:
                    unique_users.add(member.id)

        embed = discord.Embed(
            title=f"{self.bot.user.name} Bot Information",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Servers",
            value=f"**{len(guilds):,}**",
            inline=True
        )

        embed.add_field(
            name="Unique Users",
            value=f"**{len(unique_users):,}**",
            inline=True
        )

        embed.add_field(
            name="Total Members",
            value=f"**{sum(guild.member_count or 0 for guild in guilds):,}**",
            inline=True
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(BotInfo(bot))