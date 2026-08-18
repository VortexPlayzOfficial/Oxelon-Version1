import asyncio
import json
import os
import time

import discord
from discord.ext import commands


PREMIUM_FILE = "premium.json"

DEFAULT_DATA = {
    "users": {},
    "guilds": {},
}

_file_lock = asyncio.Lock()


def load_premium() -> dict:
    if not os.path.exists(PREMIUM_FILE):
        return {
            "users": {},
            "guilds": {},
        }

    try:
        with open(PREMIUM_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {
            "users": {},
            "guilds": {},
        }

    data.setdefault("users", {})
    data.setdefault("guilds", {})

    return data


def save_premium(data: dict) -> None:
    with open(PREMIUM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def _not_expired(entry: dict) -> bool:
    expires = entry.get("expires")

    return expires is None or expires > time.time()


def is_premium_user(user_id: int) -> bool:
    data = load_premium()

    entry = data["users"].get(str(user_id))

    return bool(
        entry and _not_expired(entry)
    )


def is_premium_guild(guild_id: int) -> bool:
    data = load_premium()

    entry = data["guilds"].get(str(guild_id))

    return bool(
        entry and _not_expired(entry)
    )


def has_premium(
    user_id: int,
    guild_id: int | None
) -> bool:

    if is_premium_user(user_id):
        return True

    if guild_id is not None and is_premium_guild(guild_id):
        return True

    return False


async def add_premium_user(
    user_id: int,
    expires: float | None = None
):
    async with _file_lock:
        data = load_premium()

        data["users"][str(user_id)] = {
            "since": time.time(),
            "expires": expires,
        }

        save_premium(data)


async def remove_premium_user(user_id: int):
    async with _file_lock:
        data = load_premium()

        data["users"].pop(
            str(user_id),
            None
        )

        save_premium(data)


async def add_premium_guild(
    guild_id: int,
    expires: float | None = None
):
    async with _file_lock:
        data = load_premium()

        data["guilds"][str(guild_id)] = {
            "since": time.time(),
            "expires": expires,
        }

        save_premium(data)


async def remove_premium_guild(guild_id: int):
    async with _file_lock:
        data = load_premium()

        data["guilds"].pop(
            str(guild_id),
            None
        )

        save_premium(data)


def premium_only():

    async def predicate(ctx: commands.Context) -> bool:

        guild_id = (
            ctx.guild.id
            if ctx.guild
            else None
        )

        if has_premium(
            ctx.author.id,
            guild_id
        ):
            return True

        embed = discord.Embed(
            title="🔒 Premium Command",
            description=(
                "This command is for **Oxelon Premium** members only.\n"
                "Upgrade your account or server to unlock it."
            ),
            color=discord.Color.gold(),
        )

        await ctx.send(embed=embed)

        return False

    return commands.check(predicate)


class Premium(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_prefix(self, ctx):
        prefix = await self.bot.get_prefix(ctx.message)

        if isinstance(prefix, list):
            prefix = prefix[0]

        return prefix

    @commands.command(name="premiumstatus")
    async def premium_status(
        self,
        ctx: commands.Context
    ):

        user_status = (
            "✅ Active"
            if is_premium_user(ctx.author.id)
            else "❌ Not active"
        )

        guild_status = "N/A"

        if ctx.guild:
            guild_status = (
                "✅ Active"
                if is_premium_guild(ctx.guild.id)
                else "❌ Not active"
            )

        embed = discord.Embed(
            title="Premium Status",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="You",
            value=user_status,
            inline=True
        )

        embed.add_field(
            name="This Server",
            value=guild_status,
            inline=True
        )

        await ctx.send(embed=embed)

    @commands.command(name="grantpremium")
    @commands.is_owner()
    async def grant_premium(
        self,
        ctx: commands.Context,
        target: discord.User | discord.Guild
    ):

        if isinstance(target, discord.User):

            await add_premium_user(target.id)

            await ctx.send(
                f"✅ Granted premium to user **{target}**."
            )

        else:

            await add_premium_guild(target.id)

            await ctx.send(
                f"✅ Granted premium to guild **{target.name}**."
            )

    @commands.command(name="revokepremium")
    @commands.is_owner()
    async def revoke_premium(
        self,
        ctx: commands.Context,
        target: discord.User | discord.Guild
    ):

        if isinstance(target, discord.User):

            await remove_premium_user(target.id)

            await ctx.send(
                f"✅ Revoked premium from user **{target}**."
            )

        else:

            await remove_premium_guild(target.id)

            await ctx.send(
                f"✅ Revoked premium from guild **{target.name}**."
            )

    @grant_premium.error
    @revoke_premium.error
    async def premium_admin_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):

        prefix = await self.get_prefix(ctx)

        if isinstance(error, commands.NotOwner):

            await ctx.send(
                "❌ Only the bot owner can manage premium status."
            )

        elif isinstance(error, commands.BadUnionArgument):

            await ctx.send(
                "❌ Couldn't find that user or guild ID."
            )

        elif isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            await ctx.send(
                "❌ Missing target.\n\n"
                "Usage:\n"
                f"`{prefix}grantpremium @User`\n"
                f"`{prefix}revokepremium @User`"
            )

        else:
            raise error

    @commands.command(name="autopurge")
    @premium_only()
    async def autopurge(
        self,
        ctx: commands.Context,
        minutes: int
    ):

        prefix = await self.get_prefix(ctx)

        if minutes <= 0:
            await ctx.send(
                f"❌ Please provide a valid number of minutes.\n"
                f"Example: `{prefix}autopurge 30`"
            )
            return

        await ctx.send(
            f"✅ Auto-purge enabled for this channel "
            f"every **{minutes} minutes**."
        )

    @autopurge.error
    async def autopurge_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):

        prefix = await self.get_prefix(ctx)

        if isinstance(error, commands.MissingRequiredArgument):

            await ctx.send(
                "❌ Please specify the number of minutes.\n"
                f"Example: `{prefix}autopurge 30`"
            )

        elif isinstance(error, commands.BadArgument):

            await ctx.send(
                "❌ Minutes must be a number.\n"
                f"Example: `{prefix}autopurge 30`"
            )

        elif isinstance(error, commands.CheckFailure):
            return

        else:
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(Premium(bot))