import logging

import discord
from discord.ext import commands

log = logging.getLogger("bot")


class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(send_messages=True)
    async def warn(
        self,
        ctx: commands.Context,
        member: discord.Member,
        *,
        reason: str = "No reason provided",
    ) -> None:
        if member.id == ctx.author.id:
            await ctx.send("❌ You cannot warn yourself.")
            return

        if member.bot:
            await ctx.send("❌ You cannot warn a bot.")
            return

        dm_sent = True

        try:
            dm_embed = discord.Embed(
                title=f"⚠️ You've been warned in {ctx.guild.name}",
                description=f"**Reason:** {reason}",
                color=discord.Color.orange(),
            )

            dm_embed.set_footer(
                text=f"Warned by {ctx.author}"
            )

            await member.send(embed=dm_embed)

        except discord.Forbidden:
            dm_sent = False

        response = (
            f"⚠️ {member.mention} has been warned. "
            f"Reason: {reason}"
        )

        if not dm_sent:
            response += (
                "\n*(Couldn't DM this user — "
                "they may have DMs disabled.)*"
            )

        await ctx.send(response)

        log.info(
            "%s warned %s in guild %s (%s) — reason: %s",
            ctx.author,
            member,
            ctx.guild.name,
            ctx.guild.id,
            reason,
        )

    @warn.error
    async def warn_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ) -> None:

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ You don't have permission to warn members."
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                "❌ Couldn't find that member."
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            prefix = await self.bot.get_prefix(ctx.message)

            if isinstance(prefix, list):
                prefix = prefix[0]

            await ctx.send(
                f"❌ Usage: `{prefix}warn <member> [reason]`"
            )

        else:
            log.exception(
                "Unexpected error in warn command",
                exc_info=error
            )

            await ctx.send(
                "❌ Something went wrong while warning that member."
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Warn(bot))