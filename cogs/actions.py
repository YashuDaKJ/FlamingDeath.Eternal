import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp

# Fallback link in case Network API fails
FALLBACK_GIF = "https://media.tenor.com/gbf398P3xTEAAAAC/hug-anime.gif"

# Mapping Discord action names to nekos.best API endpoints
NEKOS_ACTIONS = {
    "hug": "hug",
    "punch": "punch",
    "pat": "pat",
    "slap": "slap",
    "highfive": "highfive",
    "yeet": "yeet",
    "dodge": "dodge",
    "aura": "shoot",       # High power energy/aura alternative
    "flex": "bored",       # Playful flex alternative
    "annoying": "poke",    # Poke / annoying action
    "rizz": "smug",        # Smug anime expression for rizz
    "hello": "wave",       # Waving hello
}


class ActionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_anime_gif(self, action: str) -> str:
        """Fetch a guaranteed high-quality anime GIF from nekos.best API."""
        category = NEKOS_ACTIONS.get(action.lower(), "hug")
        url = f"https://nekos.best/api/v2/{category}"
        
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        return results[0].get("url", FALLBACK_GIF)
        except Exception as e:
            print(f"⚠️ Nekos API Request Error for '{category}': {e}", flush=True)

        return FALLBACK_GIF

    ACTION_TEXTS = {
        'yeet': lambda author, target: f"💨 {author.mention} YEETED {target.mention} into the stratosphere!",
        'dodge': lambda author, target: f"⚡ {author.mention} effortlessly DODGED {target.mention}'s attack with Ultra Instinct!",
        'aura': lambda author, target: f"✨ {author.mention} unleashed an overwhelming anime AURA in front of {target.mention}!",
        'flex': lambda author, target: f"💪 {author.mention} FLEXED their supreme power on {target.mention}!",
        'annoying': lambda author, target: f"🤪 {author.mention} is continuously ANNOYING {target.mention}!",
        'rizz': lambda author, target: f"😏 {author.mention} deployed lightspeed ANIME RIZZ on {target.mention}!",
        'hello': lambda author, target: f"👋 {author.mention} gave a sweet anime HELLO wave to {target.mention}!",
    }

    async def perform_action(self, interaction: discord.Interaction, action: str, target: discord.Member):
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't perform this action on yourself!", ephemeral=True)
            return

        # Defer interaction to avoid 3-second timeout limits
        await interaction.response.defer()
        act_key = action.lower()

        selected_gif = await self.get_anime_gif(act_key)

        if act_key in self.ACTION_TEXTS:
            text = self.ACTION_TEXTS[act_key](interaction.user, target)
        else:
            text = f"{interaction.user.mention} {act_key}ed {target.mention}!"

        embed = discord.Embed(description=text, color=discord.Color.teal())
        embed.set_image(url=selected_gif)
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.followup.send(embed=embed)

    # Anime Slash Commands
    @app_commands.command(name="hug", description="Give someone a warm hug!")
    async def hug(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "hug", target)

    @app_commands.command(name="punch", description="Punch someone!")
    async def punch(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "punch", target)

    @app_commands.command(name="pat", description="Pat someone on the head")
    async def pat(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "pat", target)

    @app_commands.command(name="slap", description="Slap someone!")
    async def slap(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "slap", target)

    @app_commands.command(name="highfive", description="Give someone a high five!")
    async def highfive(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "highfive", target)

    @app_commands.command(name="yeet", description="Yeet someone into orbit!")
    async def yeet(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "yeet", target)

    @app_commands.command(name="dodge", description="Dodge an incoming attack!")
    async def dodge(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "dodge", target)

    @app_commands.command(name="aura", description="Flex your overwhelming aura!")
    async def aura(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "aura", target)

    @app_commands.command(name="flex", description="Flex your power on someone!")
    async def flex(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "flex", target)

    @app_commands.command(name="annoying", description="Be annoying to someone!")
    async def annoying(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "annoying", target)

    @app_commands.command(name="rizz", description="Use your ultimate rizz!")
    async def rizz(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "rizz", target)

    @app_commands.command(name="hello", description="Wave hello!")
    async def hello(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "hello", target)


async def setup(bot):
    await bot.add_cog(ActionsCog(bot))
    
