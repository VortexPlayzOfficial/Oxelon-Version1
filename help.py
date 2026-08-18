import discord
from discord.ext import commands

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = None

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Oxelon - Commands",
            description="Here's everything I can do:",
            color=discord.Color.blurple()
        )
        embed.add_field(name="\u200b", value="** General & Moderation**", inline=False)
        embed.add_field(name="!hello", value="Says hello back to you.", inline=False)
        embed.add_field(name="!warn @user [reason]", value="Warns a member (mod only).", inline=False)
        embed.add_field(name="!kick @user [reason]", value="Kicks a member (mod only).", inline=False)
        embed.add_field(name="!ban @user [reason]", value="Bans a member (mod only).", inline=False)
        embed.add_field(name="!prefix", value="Shows the current prefix. Run !prefixset to change the prefix.", inline=False)
        embed.add_field(name="!ping", value="Pings the bot to make sure it's online.", inline=False)

        embed.add_field(name="\u200b", value="**Server Settings**", inline=False)
        embed.add_field(name="!config", value="Shows this server's current settings.", inline=False)
        embed.add_field(name="!config purgelimit <number>", value="Sets the max messages !purge can delete at once (admin only).", inline=False)
        embed.add_field(name="!config logchannel #channel", value="Sets the channel used for mod-action logs (admin only).", inline=False)
        embed.add_field(name="!config prefix <symbol>", value="Sets a custom prefix for this server (admin only).", inline=False)
        embed.add_field(name="!config reset", value="Resets this server's settings to defaults (admin only).", inline=False)

        embed.add_field(name="\u200b", value="** Premium**", inline=False)
        embed.add_field(name="!premiumstatus", value="Checks your premium status and this server's premium status.", inline=False)
        embed.add_field(name="!autopurge <minutes>", value="Auto-purges the channel on a timer (premium only).", inline=False)

        embed.add_field(name="\u200b", value="**Coming Soon**", inline=False)
        embed.add_field(name="More Commands Soon.", value="We are working on more commands like !mute, !nick, !logs and more.", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomHelp(bot))