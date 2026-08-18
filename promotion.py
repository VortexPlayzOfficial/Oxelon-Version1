import discord
from discord.ext import commands
import random
import string


def generate_promotion_id():
    return "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=10
        )
    )


class Promotion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="promote",
        help="Promote a staff member."
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def promote(
        self,
        ctx,
        member: discord.Member,
        *,
        new_rank: str
    ):
        promotion_id = generate_promotion_id()

        ctx.send(f"{member.mention}")

        embed = discord.Embed(
            title="Staff Promotion",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Staff Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="New Rank",
            value=new_rank,
            inline=False
        )

        embed.add_field(
            name="Promoted By",
            value=ctx.author.mention,
            inline=False
        )

        embed.set_footer(
            text=f"Promotion ID | {promotion_id}"
        )

        await ctx.send(embed=embed)

    @promote.error
    async def promote_error(self, ctx, error):

        prefix = await self.bot.get_prefix(ctx.message)

        if isinstance(prefix, list):
            prefix = prefix[0]

        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "❌ You need **Manage Roles** permission to promote staff."
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(
                "❌ I need permission to send embeds."
            )
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                "**Incorrect format!**\n\n"
                "Use:\n"
                f"`{prefix}promote @Member New Rank`\n\n"
                "Example:\n"
                f"`{prefix}promote @Vortex Senior Moderator`"
            )
            return

        if isinstance(error, commands.MemberNotFound):
            await ctx.reply(
                "❌ I couldn't find that member."
            )
            return

        raise error


async def setup(bot):
    await bot.add_cog(Promotion(bot))