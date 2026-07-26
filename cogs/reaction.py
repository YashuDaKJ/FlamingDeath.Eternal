import discord
from discord.ext import commands

class ReactionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if "nice" in message.content.lower():
            try:
                await message.add_reaction("🔥")
            except Exception as e:
                print(f"Reaction Error: {e}")

async def setup(bot):
    await bot.add_cog(ReactionCog(bot))
