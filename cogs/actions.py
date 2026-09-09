import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp
import asyncio

# Complete 110 GIFs Dictionary (Single File Architecture)
ACTION_GIFS = {
    "hug": [
        "https://media.giphy.com/media/l2QDM9Jnim1YV55YA/giphy.gif",
        "https://media.giphy.com/media/109A5G32DYSRqg/giphy.gif",
        "https://media.giphy.com/media/od5H3LnMhdWOoXZnGZ/giphy.gif",
        "https://media.giphy.com/media/u9BxFE6NoG0es/giphy.gif",
        "https://media.giphy.com/media/aD1fI3UU638yY/giphy.gif",
        "https://media.giphy.com/media/3M4NpbLCTxBqU/giphy.gif",
        "https://media.giphy.com/media/G3va3f9E3A9vu/giphy.gif",
        "https://media.giphy.com/media/wnm0fL2M2O69q/giphy.gif",
        "https://media.giphy.com/media/sv2KVORze4t2w/giphy.gif",
        "https://media.giphy.com/media/K9IbsI180Q8py/giphy.gif"
    ],
    "punch": [
        "https://media.giphy.com/media/11tTNkKOscJG6Y/giphy.gif",
        "https://media.giphy.com/media/LwsCiZPppEiOI/giphy.gif",
        "https://media.giphy.com/media/YoB1eEFB6FZv4yCiFi/giphy.gif",
        "https://media.giphy.com/media/mEtSQlx3yvCAC/giphy.gif",
        "https://media.giphy.com/media/D12Xs2L3C132g/giphy.gif",
        "https://media.giphy.com/media/arbUCELLW718A/giphy.gif",
        "https://media.giphy.com/media/u8x3C55S1yS3K/giphy.gif",
        "https://media.giphy.com/media/AThUu38AmeZxL2S2qU/giphy.gif",
        "https://media.giphy.com/media/3pLOOnO1lB5XG/giphy.gif",
        "https://media.giphy.com/media/EUnAbl8B91OFi/giphy.gif"
    ],
    "pat": [
        "https://media.giphy.com/media/N0CIxcyHCsAFG/giphy.gif",
        "https://media.giphy.com/media/L2z7dnOduqEow/giphy.gif",
        "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif",
        "https://media.giphy.com/media/5tmRHw4oH85vNJ0FIsu/giphy.gif",
        "https://media.giphy.com/media/4HP0ddZnNVvKU/giphy.gif",
        "https://media.giphy.com/media/Ye3dev423L92U/giphy.gif",
        "https://media.giphy.com/media/109mX58yPz2328/giphy.gif",
        "https://media.giphy.com/media/8vQSQ3cNXuDGo/giphy.gif",
        "https://media.giphy.com/media/3o84stPdtAAn9z2p4A/giphy.gif",
        "https://media.giphy.com/media/e1P0S4O5L3vC/giphy.gif"
    ],
    "slap": [
        "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
        "https://media.giphy.com/media/j1qqM6Myb8m08/giphy.gif",
        "https://media.giphy.com/media/Zau0yRL15t84w/giphy.gif",
        "https://media.giphy.com/media/m6ETA8A8a3I52/giphy.gif",
        "https://media.giphy.com/media/vOUU9f4f1m1L1XN2lE/giphy.gif",
        "https://media.giphy.com/media/IYAntiG1tnoli/giphy.gif",
        "https://media.giphy.com/media/KKaCYAbceuSkU/giphy.gif",
        "https://media.giphy.com/media/XDRoTw2mFZrlEUM2XY/giphy.gif",
        "https://media.giphy.com/media/3XlEk2L3A184/giphy.gif",
        "https://media.giphy.com/media/WLXO8OZEgMJKw/giphy.gif"
    ],
    "doom": [
        "https://media.giphy.com/media/3o6Ztn39rB7S3mR2cE/giphy.gif",
        "https://media.giphy.com/media/xT9Igk31LOfiP35q2A/giphy.gif",
        "https://media.giphy.com/media/eK12uCsrVKxA4/giphy.gif",
        "https://media.giphy.com/media/wA6a5O3I7Xrq8/giphy.gif",
        "https://media.giphy.com/media/3o7TKL843E6iM3L5nO/giphy.gif",
        "https://media.giphy.com/media/AThUu38AmeZxL2S2qU/giphy.gif",
        "https://media.giphy.com/media/3pLOOnO1lB5XG/giphy.gif",
        "https://media.giphy.com/media/EUnAbl8B91OFi/giphy.gif",
        "https://media.giphy.com/media/Ye3dev423L92U/giphy.gif",
        "https://media.giphy.com/media/109mX58yPz2328/giphy.gif"
    ],
    "burn": [
        "https://media.giphy.com/media/xU1spRleSWalU2fX60/giphy.gif",
        "https://media.giphy.com/media/P7JmDW7IkB7TW/giphy.gif",
        "https://media.giphy.com/media/3o72FfM5HJydzaM6B2/giphy.gif",
        "https://media.giphy.com/media/5nsiFjdgylfK3csZ5E/giphy.gif",
        "https://media.giphy.com/media/Lopx9eUi34rbq/giphy.gif",
        "https://media.giphy.com/media/nrXif4YjgX9sI/giphy.gif",
        "https://media.giphy.com/media/iH2IldJRghWXNEJ43C/giphy.gif",
        "https://media.giphy.com/media/YoB1eEFB6FZv4yCiFi/giphy.gif",
        "https://media.giphy.com/media/wA6a5O3I7Xrq8/giphy.gif",
        "https://media.giphy.com/media/EUnAbl8B91OFi/giphy.gif"
    ],
    "blast": [
        "https://media.giphy.com/media/ceHKRKMR6Ojao/giphy.gif",
        "https://media.giphy.com/media/oe3333B3X85BS/giphy.gif",
        "https://media.giphy.com/media/XUFPGrX5Zis6Y/giphy.gif",
        "https://media.giphy.com/media/3o6Ztn39rB7S3mR2cE/giphy.gif",
        "https://media.giphy.com/media/xT9Igk31LOfiP35q2A/giphy.gif",
        "https://media.giphy.com/media/eK12uCsrVKxA4/giphy.gif",
        "https://media.giphy.com/media/wA6a5O3I7Xrq8/giphy.gif",
        "https://media.giphy.com/media/3o7TKL843E6iM3L5nO/giphy.gif",
        "https://media.giphy.com/media/AThUu38AmeZxL2S2qU/giphy.gif",
        "https://media.giphy.com/media/3pLOOnO1lB5XG/giphy.gif"
    ],
    "highfive": [
        "https://media.giphy.com/media/aD1fI3UU638yY/giphy.gif",
        "https://media.giphy.com/media/3M4NpbLCTxBqU/giphy.gif",
        "https://media.giphy.com/media/G3va3f9E3A9vu/giphy.gif",
        "https://media.giphy.com/media/wnm0fL2M2O69q/giphy.gif",
        "https://media.giphy.com/media/sv2KVORze4t2w/giphy.gif",
        "https://media.giphy.com/media/K9IbsI180Q8py/giphy.gif",
        "https://media.giphy.com/media/l2QDM9Jnim1YV55YA/giphy.gif",
        "https://media.giphy.com/media/109A5G32DYSRqg/giphy.gif",
        "https://media.giphy.com/media/od5H3LnMhdWOoXZnGZ/giphy.gif",
        "https://media.giphy.com/media/u9BxFE6NoG0es/giphy.gif"
    ],
    "cake": [
        "https://media.giphy.com/media/13n8txR8c9Z3N6/giphy.gif",
        "https://media.giphy.com/media/cK8aBwW7hX78c/giphy.gif",
        "https://media.giphy.com/media/xT0xeQ9HQw8Pj46Ebm/giphy.gif",
        "https://media.giphy.com/media/26ufc0OcE3C6wTzRS/giphy.gif",
        "https://media.giphy.com/media/3oEhmI1YziLzX0mRkk/giphy.gif",
        "https://media.giphy.com/media/LwK4O2JzTIfxK/giphy.gif",
        "https://media.giphy.com/media/3o7WTDH9gYo71TurPq/giphy.gif",
        "https://media.giphy.com/media/5wWf7HapU72P203T3X4/giphy.gif",
        "https://media.giphy.com/media/l0HlJ764Cq3gC9Zyo/giphy.gif",
        "https://media.giphy.com/media/xUPGcMZwkJ2XWb020U/giphy.gif"
    ],
    "spray": [
        "https://media.giphy.com/media/3oKIPoZniJ2hq8IItG/giphy.gif",
        "https://media.giphy.com/media/l0HlGVD6zwwK768nu/giphy.gif",
        "https://media.giphy.com/media/3o7aD2saal6gCGWYAQ/giphy.gif",
        "https://media.giphy.com/media/xUPGcq17EmWAmSYzxK/giphy.gif",
        "https://media.giphy.com/media/26FPCXdkvDbKBbgOI/giphy.gif",
        "https://media.giphy.com/media/3oriNU06XSVW7ow3T2/giphy.gif",
        "https://media.giphy.com/media/l41YkFIiBxQdRlKI8/giphy.gif",
        "https://media.giphy.com/media/3o7aTskHEU61D02Ahy/giphy.gif",
        "https://media.giphy.com/media/xT4uQaz24xgfsLE0kU/giphy.gif",
        "https://media.giphy.com/media/l2JHQh6O5Qh2cIfM4/giphy.gif"
    ],
    "pie": [
        "https://media.giphy.com/media/3o6Zt6bK1wD59a8u2Q/giphy.gif",
        "https://media.giphy.com/media/l2Sqe1E42QC7BTYWY/giphy.gif",
        "https://media.giphy.com/media/26FPO1Z6gK9K0oMDK/giphy.gif",
        "https://media.giphy.com/media/3oriOaeTzC2o3O15n2/giphy.gif",
        "https://media.giphy.com/media/xT0BKhz4h9wHqM9LUI/giphy.gif",
        "https://media.giphy.com/media/l0MYKz5r0K0V0pXoI/giphy.gif",
        "https://media.giphy.com/media/3oKIPzO6I0Y6sVb7uE/giphy.gif",
        "https://media.giphy.com/media/26BGIqUMlwcqwFPUY/giphy.gif",
        "https://media.giphy.com/media/3o7aDdz5c5U0sR5EaY/giphy.gif",
        "https://media.giphy.com/media/l2JdUKyOBy2r2FhXa/giphy.gif"
    ]
}

# Guaranteed-working fallback if every candidate in a category turns out dead
FALLBACK_GIF = "https://media.tenor.com/gbf398P3xTEAAAAC/hug-anime.gif"


class ActionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._validate_session: aiohttp.ClientSession | None = None
        # Cache of URL -> bool so we don't re-check the same link every time
        self._link_status_cache: dict[str, bool] = {}

    async def cog_load(self):
        self._validate_session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self._validate_session and not self._validate_session.closed:
            await self._validate_session.close()

    async def _is_link_alive(self, url: str) -> bool:
        """Quick HEAD check (with GET fallback) so we never send a dead GIF link."""
        if url in self._link_status_cache:
            return self._link_status_cache[url]

        alive = False
        try:
            async with self._validate_session.head(url, timeout=aiohttp.ClientTimeout(total=3), allow_redirects=True) as resp:
                content_type = resp.headers.get("Content-Type", "")
                alive = resp.status == 200 and content_type.startswith("image")
        except Exception:
            # Some CDNs don't support HEAD properly — fall back to a light GET
            try:
                async with self._validate_session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                    content_type = resp.headers.get("Content-Type", "")
                    alive = resp.status == 200 and content_type.startswith("image")
            except Exception:
                alive = False

        self._link_status_cache[url] = alive
        return alive

    async def _pick_working_gif(self, action: str) -> str:
        """Shuffle the category's GIFs and return the first one that's actually alive."""
        candidates = ACTION_GIFS.get(action, [])
        if not candidates:
            return FALLBACK_GIF

        shuffled = candidates.copy()
        random.shuffle(shuffled)

        # Try up to 4 candidates before giving up and using the fallback —
        # keeps latency bounded even if several links in a row are dead.
        for url in shuffled[:4]:
            if await self._is_link_alive(url):
                return url

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

        act_key = action.lower()

        # Defer since the link-validation HEAD/GET check can take a moment
        # and we don't want to risk missing Discord's 3s interaction window.
        await interaction.response.defer()

        selected_gif = await self._pick_working_gif(act_key)

        if act_key in self.ACTION_TEXTS:
            text = self.ACTION_TEXTS[act_key](interaction.user, target)
        else:
            text = f"{interaction.user.mention} {act_key}ed {target.mention}!"

        embed = discord.Embed(description=text, color=discord.Color.teal())
        embed.set_image(url=selected_gif)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)

    # Command Definitions
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
