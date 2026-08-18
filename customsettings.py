import json
import os
import asyncio
import discord
from discord.ext import commands
 
CONFIG_FILE = "guild_configs.json"
 
DEFAULT_CONFIG = {
    "purge_limit": 100,
    "log_channel": None,
    "prefix": "!",
}
 
# Prevents two coroutines from writing to the file at the same time
_file_lock = asyncio.Lock()
 
 
# ---------------------------------------------------------------------------
# Low-level storage helpers
# ---------------------------------------------------------------------------
 
def load_configs() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
 
 
def save_configs(data: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
 
 
def get_guild_config(guild_id: int) -> dict:
    configs = load_configs()
    cfg = configs.get(str(guild_id), {})
    # Fill in any missing keys with defaults (handles new settings added later)
    merged = {**DEFAULT_CONFIG, **cfg}
    return merged
 
 
def set_guild_config(guild_id: int, key: str, value) -> None:
    configs = load_configs()
    guild_id = str(guild_id)
    if guild_id not in configs:
        configs[guild_id] = dict(DEFAULT_CONFIG)
    configs[guild_id][key] = value
    save_configs(configs)
 
 
async def async_set_guild_config(guild_id: int, key: str, value) -> None:
    """Use this from commands to avoid race conditions on concurrent writes."""
    async with _file_lock:
        set_guild_config(guild_id, key, value)
 
 
# ---------------------------------------------------------------------------
# Cog: lets server admins view/edit their own settings
# ---------------------------------------------------------------------------
 
class CustomSettings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
 
    @commands.group(name="config", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def config(self, ctx: commands.Context):
        """Show the current settings for this server."""
        cfg = get_guild_config(ctx.guild.id)
        embed = discord.Embed(
            title=f"Settings for {ctx.guild.name}",
            color=discord.Color.blurple(),
        )
        for key, value in cfg.items():
            embed.add_field(name=key, value=str(value), inline=False)
        embed.set_footer(text="Use !config <setting> <value> to change one.")
        await ctx.send(embed=embed)
 
    @config.command(name="purgelimit")
    @commands.has_permissions(administrator=True)
    async def set_purge_limit(self, ctx: commands.Context, limit: int):
        """Set the max number of messages !purge can delete at once."""
        if limit < 1 or limit > 1000:
            return await ctx.send("Purge limit must be between 1 and 1000.")
        await async_set_guild_config(ctx.guild.id, "purge_limit", limit)
        await ctx.send(f"✅ Purge limit set to **{limit}** for this server.")
 
    @config.command(name="logchannel")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel used for mod-action logs."""
        await async_set_guild_config(ctx.guild.id, "log_channel", channel.id)
        await ctx.send(f"✅ Log channel set to {channel.mention}.")
 
    @config.command(name="prefix")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        """Set a custom command prefix for this server."""
        if len(new_prefix) > 5:
            return await ctx.send("Prefix must be 5 characters or fewer.")
        await async_set_guild_config(ctx.guild.id, "prefix", new_prefix)
        await ctx.send(f"✅ Prefix set to `{new_prefix}` for this server.")
 
    @config.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_config(self, ctx: commands.Context):
        """Reset this server's settings back to defaults."""
        configs = load_configs()
        configs.pop(str(ctx.guild.id), None)
        save_configs(configs)
        await ctx.send("✅ Settings reset to defaults for this server.")
 
    @config.error
    @set_purge_limit.error
    @set_log_channel.error
    @set_prefix.error
    @reset_config.error
    async def config_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need **Administrator** permission to change server settings.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: `{error.param.name}`.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Couldn't parse that value — check the type (channel/number/etc).")
        else:
            raise error
 
 
async def setup(bot: commands.Bot):
    await bot.add_cog(CustomSettings(bot))
 
 
# ---------------------------------------------------------------------------
# Dynamic prefix helper — plug this into your bot's constructor:
#
#   bot = commands.Bot(command_prefix=get_prefix, intents=intents)
# ---------------------------------------------------------------------------
 
async def get_prefix(bot: commands.Bot, message: discord.Message):
    if message.guild is None:
        return commands.when_mentioned_or("!")(bot, message)
    cfg = get_guild_config(message.guild.id)
    return commands.when_mentioned_or(cfg["prefix"])(bot, message)