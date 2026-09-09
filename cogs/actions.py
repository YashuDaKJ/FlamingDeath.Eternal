import discord
from discord.ext import commands
from discord import app_commands
import random
from actions_data import ACTION_GIFS

class ActionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Custom embed texts for each action
    ACTION_TEXTS = {
        'doom': lambda author, target: f"🚀💥 {author.mention} launched a missile/tank strike and DOOMED {target.mention} into oblivion!",
        'burn': lambda author, target: f"🔥 {author.mention} set {target.mention} on fire with a scorching flamethrower attack!",
        'blast': lambda author, target: f"💣💥 {author.mention} triggered an explosive blast and BLEW UP {target.mention}!",
        'spray': lambda author, target: f"🎉 {author.mention} sprayed party foam / silly string all over {target.mention}!",
        'cake': lambda author, target: f"🎂 {author.mention} smashed a birthday cake on {target.mention}'s face!",
        'pie': lambda author, target: f"🥧 {author.mention} threw a cream pie right into {target.mention}'s face!",
    }

    async def perform_action(self, interaction: discord.Interaction, action: str, target: discord.Member):
        """Perform an action on a target member"""
        # Check if target is the author
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't do that to yourself!", ephemeral=True)
            return

        # Get random GIF
        gifs = ACTION_GIFS.get(action.lower(), ["https://placeholder.com/gif.gif"])
        gif_url = random.choice(gifs)

        # Create embed
        embed = discord.Embed(color=discord.Color.cyan())
        embed.set_image(url=gif_url)

        # Set text based on action type
        if action.lower() in self.ACTION_TEXTS:
            text = self.ACTION_TEXTS[action.lower()](interaction.user, target)
        else:
            text = f"{interaction.user.mention} {action}ed {target.mention}!"

        embed.description = text
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hug", description="Give someone a warm hug!")
    @app_commands.describe(target="The person to hug")
    async def hug(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "hug", target)

    @app_commands.command(name="punch", description="Punch someone!")
    @app_commands.describe(target="The person to punch")
    async def punch(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "punch", target)

    @app_commands.command(name="pat", description="Pat someone on the head")
    @app_commands.describe(target="The person to pat")
    async def pat(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "pat", target)

    @app_commands.command(name="slap", description="Slap someone!")
    @app_commands.describe(target="The person to slap")
    async def slap(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "slap", target)

    @app_commands.command(name="doom", description="Launch a devastating doom attack!")
    @app_commands.describe(target="The person to doom")
    async def doom(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "doom", target)

    @app_commands.command(name="burn", description="Set someone on fire with a flamethrower!")
    @app_commands.describe(target="The person to burn")
    async def burn(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "burn", target)

    @app_commands.command(name="blast", description="Trigger an explosive blast!")
    @app_commands.describe(target="The person to blast")
    async def blast(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "blast", target)

    @app_commands.command(name="highfive", description="Give someone a high five!")
    @app_commands.describe(target="The person to high five")
    async def highfive(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "highfive", target)

    @app_commands.command(name="cake", description="Smash a birthday cake on someone's face!")
    @app_commands.describe(target="The person to cake")
    async def cake(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "cake", target)

    @app_commands.command(name="spray", description="Spray party foam all over someone!")
    @app_commands.describe(target="The person to spray")
    async def spray(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "spray", target)

    @app_commands.command(name="pie", description="Throw a cream pie at someone!")
    @app_commands.describe(target="The person to pie")
    async def pie(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "pie", target)

async def setup(bot):
    await bot.add_cog(ActionsCog(bot))
