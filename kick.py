import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
       
        dm_sent = True
        try:
            dm_embed = discord.Embed(
                title=f" You've been kicked from {ctx.guild.name}",
                description=f"**Reason:** {reason}",
                color=discord.Color.red(),
            )
            dm_embed.set_footer(text=f"Kicked by {ctx.author}")
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            dm_sent = False

        await member.kick(reason=reason)

        await ctx.send(
            f" {member.mention} has been kicked. Reason: {reason}"
            + ("" if dm_sent else "\n*(Couldn't DM this user — they may have DMs disabled.)*")
        )

async def setup(bot):
    await bot.add_cog(Kick(bot))