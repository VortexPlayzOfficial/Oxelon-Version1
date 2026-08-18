import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from cogs.prefix import prefixes

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DEFAULT_PREFIX = "!"

if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is not set.")


# ============================================================
# EXTENSIONS
# ============================================================

EXTENSIONS = [
    "cogs.hello",
    "cogs.warn",
    "cogs.reactions",
    "cogs.help",
    "cogs.kick",
    "cogs.prefix",
    "cogs.ban",
    "cogs.ping",
    "cogs.botinfo",
    "cogs.purge",
    "cogs.premium",
    "cogs.customsettings",
    "cogs.technician",
    "cogs.promotion"
]


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

log = logging.getLogger("Oxelon")


# ============================================================
# PREFIX SYSTEM
# ============================================================

async def get_prefix(bot, message):
    """
    Returns ONLY the currently configured prefix
    for the guild.

    DMs always use the default prefix.
    """

    if message.guild is None:
        return DEFAULT_PREFIX

    guild_id = str(message.guild.id)

    # Get the saved prefix.
    prefix = prefixes.get(guild_id, DEFAULT_PREFIX)

    # Make sure we ALWAYS return a single prefix.
    if not isinstance(prefix, str) or not prefix:
        return DEFAULT_PREFIX

    return prefix


# ============================================================
# INTENTS
# ============================================================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True


# ============================================================
# BOT
# ============================================================

bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    case_insensitive=True,
    help_command=None,
)


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    log.info("=" * 50)
    log.info("Oxelon is online!")
    log.info("Logged in as: %s", bot.user)
    log.info("Bot ID: %s", bot.user.id)
    log.info("Guilds: %s", len(bot.guilds))
    log.info("Commands loaded: %s", len(bot.commands))
    log.info("=" * 50)


# ============================================================
# COMMAND ERRORS
# ============================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(
            f"❌ Missing required argument: `{error.param.name}`"
        )
        return

    if isinstance(error, commands.BadArgument):
        await ctx.reply(
            "❌ One or more arguments are invalid."
        )
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.reply(
            "❌ You don't have permission to use this command."
        )
        return

    if isinstance(error, commands.BotMissingPermissions):
        await ctx.reply(
            "❌ I don't have the permissions required to do that."
        )
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(
            f"⏳ Please wait **{error.retry_after:.1f}s** before using this command again."
        )
        return

    if isinstance(error, commands.CheckFailure):
        return

    log.exception(
        "Error while running command '%s'",
        ctx.command,
        exc_info=error
    )

    try:
        await ctx.reply(
            "❌ An unexpected error occurred while running this command."
        )
    except discord.HTTPException:
        pass


# ============================================================
# GLOBAL COMMAND CHECK
# ============================================================

@bot.check
async def global_command_check(ctx):
    return True


# ============================================================
# LOAD EXTENSIONS
# ============================================================

async def load_extensions():

    loaded = 0
    failed = 0

    log.info("Loading extensions...")

    for extension in EXTENSIONS:

        try:

            await bot.load_extension(extension)

            loaded += 1

            log.info(
                "Loaded: %s",
                extension
            )

        except commands.ExtensionAlreadyLoaded:

            log.warning(
                "Already loaded: %s",
                extension
            )

        except commands.ExtensionNotFound:

            failed += 1

            log.error(
                "Extension not found: %s",
                extension
            )

        except commands.NoEntryPointError:

            failed += 1

            log.error(
                "Missing setup function: %s",
                extension
            )

        except Exception as error:

            failed += 1

            log.exception(
                "Failed to load %s: %s",
                extension,
                error
            )

    log.info(
        "Extensions loaded: %s | Failed: %s",
        loaded,
        failed
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    await load_extensions()

    try:

        log.info("Starting Oxelon...")

        await bot.start(TOKEN)

    except discord.LoginFailure:

        log.critical(
            "Invalid Discord bot token."
        )

    finally:

        if not bot.is_closed():
            await bot.close()


# ============================================================
# START BOT
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        log.info("Bot stopped.")