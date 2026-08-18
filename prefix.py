import json
import os

from discord.ext import commands


PREFIX_FILE = "prefixes.json"
DEFAULT_PREFIX = "!"

prefixes = {}


# ============================================================
# LOAD PREFIXES
# ============================================================

def load_prefixes():
    global prefixes

    if not os.path.exists(PREFIX_FILE):
        prefixes = {}
        return

    try:
        with open(PREFIX_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Make sure the file contains a dictionary
        if isinstance(data, dict):
            prefixes = data
        else:
            prefixes = {}

    except (json.JSONDecodeError, OSError):
        prefixes = {}


# ============================================================
# SAVE PREFIXES
# ============================================================

def save_prefixes():
    try:
        with open(PREFIX_FILE, "w", encoding="utf-8") as file:
            json.dump(
                prefixes,
                file,
                indent=4
            )

    except OSError:
        pass


# Load saved prefixes when the cog starts
load_prefixes()


# ============================================================
# PREFIX COG
# ============================================================

class Prefix(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------------
    # SET PREFIX
    # --------------------------------------------------------

    @commands.command(name="prefixset")
    @commands.has_guild_permissions(manage_guild=True)
    async def prefixset(self, ctx, new_prefix: str):

        # Server-only
        if ctx.guild is None:
            await ctx.reply(
                "❌ This command can only be used in a server."
            )
            return

        # No spaces
        if " " in new_prefix:
            await ctx.reply(
                "❌ Your prefix cannot contain spaces."
            )
            return

        # Prefix length
        if len(new_prefix) > 5:
            await ctx.reply(
                "❌ Your prefix cannot be longer than 5 characters."
            )
            return

        # Prefix cannot be empty
        if not new_prefix:
            await ctx.reply(
                "❌ You must provide a prefix."
            )
            return

        guild_id = str(ctx.guild.id)

        # IMPORTANT:
        # Replace the old prefix completely.
        prefixes[guild_id] = new_prefix

        save_prefixes()

        await ctx.reply(
            f"✅ Server prefix changed to `{new_prefix}`"
        )

    # --------------------------------------------------------
    # SHOW PREFIX
    # --------------------------------------------------------

    @commands.command(name="prefix")
    async def prefix(self, ctx):

        if ctx.guild is None:
            await ctx.reply(
                f"🔧 The default prefix is `{DEFAULT_PREFIX}`"
            )
            return

        guild_id = str(ctx.guild.id)

        current_prefix = prefixes.get(
            guild_id,
            DEFAULT_PREFIX
        )

        await ctx.reply(
            f"🔧 The current server prefix is `{current_prefix}`"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Prefix(bot))