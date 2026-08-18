import discord
from discord.ext import commands


class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):

        if amount < 1:
            await ctx.reply(
                "❌ You must specify an amount greater than 0."
            )
            return

        deleted = await ctx.channel.purge(
            limit=amount + 1
        )

        confirmation = await ctx.send(
            f"🧹 Purged **{len(deleted) - 1}** message(s)."
        )

        await confirmation.delete(delay=5)

    @purge.error
    async def purge_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "❌ You need **Manage Messages** permission to use this command."
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(
                "❌ I need **Manage Messages** permission to purge messages."
            )
            return

        if isinstance(error, commands.MissingRequiredArgument):
            prefix = await self.bot.get_prefix(ctx.message)

            if isinstance(prefix, list):
                prefix = prefix[0]

            await ctx.reply(
                f"❌ Usage: `{prefix}purge <amount>`"
            )
            return

        if isinstance(error, commands.BadArgument):
            prefix = await self.bot.get_prefix(ctx.message)

            if isinstance(prefix, list):
                prefix = prefix[0]

            await ctx.reply(
                f"❌ Please provide a valid number.\n"
                f"Example: `{prefix}purge 10`"
            )
            return

        raise error


async def setup(bot):
    await bot.add_cog(Purge(bot))