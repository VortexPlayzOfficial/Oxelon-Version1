import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        
        if member == ctx.author:
            return await ctx.send("You can't ban yourself.")

        if member == ctx.bot.user:
            return await ctx.send("I can't ban myself.")

        if member == ctx.guild.owner:
            return await ctx.send("You can't ban the server owner.")

       
        staff_perms = ("ban_members", "kick_members", "administrator", "manage_guild")
        if any(getattr(member.guild_permissions, perm) for perm in staff_perms):
            return await ctx.send("You can't ban another staff member.")

        
        if ctx.author != ctx.guild.owner and member.top_role >= ctx.author.top_role:
            return await ctx.send("You can't ban someone with an equal or higher role than you.")

        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("I can't ban this user — my role is too low.")
      

        dm_sent = True
        try:
            dm_embed = discord.Embed(
                title=f" You've been banned from {ctx.guild.name}",
                description=f"**Reason:** {reason}",
                color=discord.Color.dark_red(),
            )
            dm_embed.set_footer(text=f"Banned by {ctx.author}")
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            dm_sent = False

        await member.ban(reason=reason)

        await ctx.send(
            f" {member.mention} has been banned. Reason: {reason}"
            + ("" if dm_sent else "\n*(Couldn't DM this user — they may have DMs disabled.)*")
        )

async def setup(bot):
    await bot.add_cog(Ban(bot))