import discord
from discord.ext import commands
from discord import app_commands
import random
import time
import os
import aiohttp

FALLBACK_GIF = "https://media.tenor.com/gbf398P3xTEAAAAC/hug-anime.gif"

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

CACHE_TTL_SECONDS = 30 * 60  # 30 minutes

# Updated queries for 100% anime style and dramatic action effects
ACTION_QUERIES = {
    "hug": "anime hug wholesome",
    "punch": "anime punch action",
    "pat": "anime head pat cute",
    "slap": "anime slap dramatic",
    "doom": "anime ultimate attack explosion",
    "burn": "anime fire flame attack",
    "blast": "anime explosion blast",
    "highfive": "anime high five team",
    "cake": "anime cake smash face",
    "spray": "anime water spray party",
    "pie": "anime pie face comedy",
}


class ActionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None
        self._cache: dict[str, tuple[float, list[str]]] = {}

    async def cog_load(self):
        self.session = aiohttp.ClientSession()
        if not GIPHY_API_KEY:
            print("⚠️ GIPHY_API_KEY not set — all GIF commands will use the static fallback.", flush=True)

    async def cog_unload(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def _fetch_batch(self, action: str) -> list[str]:
        query = ACTION_QUERIES.get(action, f"anime {action}")
        try:
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "api_key": GIPHY_API_KEY,
                "q": query,
                "limit": 25,
                "rating": "pg-13",
            }
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    print(f"⚠️ Giphy API returned {resp.status} for '{query}'", flush=True)
                    return []
                data = await resp.json()
                results = data.get("data", [])
                urls = []
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
            print(f"⚠️ Giphy fetch failed for '{query}': {e}", flush=True)
            return []

    async def get_gif(self, action: str) -> str:
        if not GIPHY_API_KEY:
            return FALLBACK_GIF

        now = time.time()
        cached = self._cache.get(action)

        if cached and (now - cached[0]) < CACHE_TTL_SECONDS and cached[1]:
            return random.choice(cached[1])

        urls = await self._fetch_batch(action)
        if urls:
            self._cache[action] = (now, urls)
            return random.choice(urls)

        if cached and cached[1]:
            return random.choice(cached[1])
        return FALLBACK_GIF

    ACTION_TEXTS = {
        'doom': lambda author, target: f"🚀💥 {author.mention} launched a missile strike and DOOMED {target.mention}!",
        'burn': lambda author, target: f"🔥 {author.mention} set {target.mention} on fire with a flamethrower!",
        'blast': lambda author, target: f"💣💥 {author.mention} triggered an explosive blast on {target.mention}!",
        'spray': lambda author, target: f"🎉 {author.mention} sprayed party foam all over {target.mention}!",
        'cake': lambda author, target: f"🎂 {author.mention} smashed a cake on {target.mention}'s face!",
        'pie': lambda author, target: f"🥧 {author.mention} threw a cream pie at {target.mention}!",
    }

    async def perform_action(self, interaction: discord.Interaction, action: str, target: discord.Member):
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't do that to yourself!", ephemeral=True)
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
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)

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

    @app_commands.command(name="doom", description="Launch a devastating doom attack!")
    async def doom(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "doom", target)

    @app_commands.command(name="burn", description="Set someone on fire with a flamethrower!")
    async def burn(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "burn", target)

    @app_commands.command(name="blast", description="Trigger an explosive blast!")
    async def blast(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "blast", target)

    @app_commands.command(name="highfive", description="Give someone a high five!")
    async def highfive(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "highfive", target)

    @app_commands.command(name="cake", description="Smash a birthday cake on someone's face!")
    async def cake(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "cake", target)

    @app_commands.command(name="spray", description="Spray party foam all over someone!")
    async def spray(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "spray", target)

    @app_commands.command(name="pie", description="Throw a cream pie at someone!")
    async def pie(self, interaction: discord.Interaction, target: discord.Member):
        await self.perform_action(interaction, "pie", target)


async def setup(bot):
    await bot.add_cog(ActionsCog(bot))
                      
