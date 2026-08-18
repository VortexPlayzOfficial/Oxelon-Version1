import logging

import discord
from discord.ext import commands

log = logging.getLogger("bot")

TRIGGERS = {
    "hello": "👋",
}


class Reactions(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        content = message.content.lower()

        for trigger, emoji in TRIGGERS.items():
            if trigger in content:
                try:
                    await message.add_reaction(emoji)
                except discord.HTTPException:
                    log.warning(
                        "Failed to add reaction %s to message %s",
                        emoji,
                        message.id,
                    )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reactions(bot))