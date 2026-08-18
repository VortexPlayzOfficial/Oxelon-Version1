import discord
from discord.ext import commands

TECHNICAL_CHANNEL_ID = 1539343375273304154
TECHNICAL_ROLE_ID = 1462218835464687617


class Technician(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="technical",
        help="Request assistance from the technical team."
    )
    async def technical(self, ctx, *, request: str):
        parts = [part.strip() for part in request.split("|")]

        if len(parts) != 3:
            prefix = await self.bot.get_prefix(ctx.message)

            if isinstance(prefix, list):
                prefix = prefix[0]

            await ctx.reply(
                "**Incorrect format!**\n\n"
                "Use:\n"
                f"`{prefix}technical Server Name | Server Link | Reason`"
            )
            return

        server_name, server_link, reason = parts

        channel = self.bot.get_channel(TECHNICAL_CHANNEL_ID)

        if channel is None:
            await ctx.reply(
                "I couldn't find the technical support channel."
            )
            return

        technical_role = ctx.guild.get_role(TECHNICAL_ROLE_ID)

        if technical_role is None:
            await ctx.reply(
                "I couldn't find the Technical Team role."
            )
            return

        embed = discord.Embed(
            title="Technical Assistance Requested",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Server Name",
            value=server_name,
            inline=False
        )

        embed.add_field(
            name="Server Link",
            value=server_link,
            inline=False
        )

        embed.add_field(
            name="Reason",
            value=reason,
            inline=False
        )

        embed.add_field(
            name="Requested By",
            value=ctx.author.mention,
            inline=False
        )

        embed.set_footer(
            text="Oxelon Technical Support"
        )

        await channel.send(
            content=technical_role.mention,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                roles=True
            )
        )

        await ctx.reply(
            "**Technical request submitted!**\n"
            "The Technical Team has been notified."
        )


async def setup(bot):
    await bot.add_cog(Technician(bot))