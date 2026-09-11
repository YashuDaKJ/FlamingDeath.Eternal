import discord
from discord.ext import commands
from discord import app_commands
import random
import time
import os
import aiohttp

# Fallback link in case Giphy API fails or key is missing
FALLBACK_GIF = "https://media.tenor.com/gbf398P3xTEAAAAC/hug-anime.gif"

# Environment Variable for Giphy API Key
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

# In-Memory Cache Duration (30 Minutes)
CACHE_TTL_SECONDS = 30 * 60

# Search queries optimized for pure anime action & tropes
ACTION_QUERIES = {
    "hug": "anime hug anime",
    "punch": "anime punch",
    "pat": "anime head pat cute",
    "slap": "anime slap face",
    "highfive": "anime high five",
    "yeet": "anime throw yeet",
    "dodge": "anime dodge attack",
    "aura": "anime power aura",
    "flex": "anime flex",
    "annoying": "anime poke annoying",
    "rizz": "anime rizz",
    "hello": "anime wave hello cute",
}


class ActionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None
        # Internal cache: action_name -> (fetch_timestamp, [list_of_urls])
        self._cache: dict[str, tuple[float, list[str]]] = {}

    async def cog_load(self):
        self.session = aiohttp.ClientSession()
        if not GIPHY_API_KEY:
            print("⚠️ GIPHY_API_KEY is not set! Bot will fallback to static GIF link.", flush=True)

    async def cog_unload(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def _fetch_batch(self, action: str) -> list[str]:
        """Fetch a batch of GIFs for the requested action query from Giphy with strict Anime filtering."""
        query = ACTION_QUERIES.get(action, f"anime {action}")
        try:
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "api_key": GIPHY_API_KEY,
                "q": query,
                "limit": 35,
                "rating": "pg-13",
            }
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    print(f"⚠️ Giphy API returned status {resp.status} for query '{query}'", flush=True)
                    return []
                data = await resp.json()
                results = data.get("data", [])
                urls = []
                for item in results:
                    title = item.get("title", "").lower()
                    slug = item.get("slug", "").lower()
                    
                    # STRICT FILTER: Ensure title/slug contains 'anime'
                    if "anime" in title or "anime" in slug:
                        images = item.get("images", {})
                        candidate = (
                            images.get("downsized", {}).get("url")
                            or images.get("original", {}).get("url")
                        )
                        if candidate:
                            urls.append(candidate)
                
                # If strict filtering returned no results, fall back to unfiltered batch
                if not urls:
                    for item in results:
                        images = item.get("images", {})
                        candidate = (
                            images.get("downsized", {}).get("url")
                            or images.get("original", {}).get("url")
                        )
                        if candidate:
                            urls.append(candidate)

                return urls
        except Exception as e:
            print(f"⚠️ Giphy API request failed for '{query}': {e}", flush=True)
            return []

    async def get_gif(self, action: str) -> str:
        """Retrieve a cached GIF or fetch a new batch and select ONLY from the top 10 results."""
        if not GIPHY_API_KEY:
            return FALLBACK_GIF

        now = time.time()
        cached = self._cache.get(action)

        # Serve from cache (Top 10 only)
        if cached and (now - cached[0]) < CACHE_TTL_SECONDS and cached[1]:
            top_10 = cached[1][:10]
            return random.choice(top_10)

        # Cache expired/empty -> fetch fresh batch
        urls = await self._fetch_batch(action)
        if urls:
            self._cache[action] = (now, urls)
            top_10 = urls[:10]
            return random.choice(top_10)

        # Serve stale cache fallback (Top 10 only)
        if cached and cached[1]:
            top_10 = cached[1][:10]
            return random.choice(top_10)
        return FALLBACK_GIF

    ACTION_TEXTS = {
        'yeet': lambda author, target: f"💨 {author.mention} YEETED {target.mention} into the stratosphere!",
        'dodge': lambda author, target: f"⚡ {author.mention} effortlessly DODGED {target.mention}'s attack with Ultra Instinct!",
        'aura': lambda author, target: f"✨ {author.mention} unleashed an overwhelming AURA in front of {target.mention}!",
        'flex': lambda author, target: f"💪 {author.mention} FLEXED their supreme power on {target.mention}!",
        'annoying': lambda author, target: f"🤪 {author.mention} is continuously ANNOYING {target.mention}!",
        'rizz': lambda author, target: f"😏 {author.mention} deployed lightspeed RIZZ on {target.mention}!",
        'hello': lambda author, target: f"👋 {author.mention} gave a sweet HELLO wave to {target.mention}!",
    }

    async def perform_action(self, interaction: discord.Interaction, action: str, target: discord.Member):
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't perform this action on yourself!", ephemeral=True)
            return

        await interaction.response.defer()
        act_key = action.lower()

        selected_gif = await self.get_gif(act_key)

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
                            
