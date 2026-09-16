import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

FALLBACK_GIF = "https://media.tenor.com/gbf398P3xTEAAAAC/hug-anime.gif"

# Mapping ALL actions to nekos.best API endpoints
NEKOS_ACTIONS = {
    "hug": "hug",
    "punch": "punch",
    "pat": "pat",
    "slap": "slap",
    "highfive": "highfive",
    "yeet": "yeet",
    "dodge": "dodge",
    "aura": "shoot",
    "flex": "bored",
    "annoying": "poke",
    "rizz": "smug",
    "hello": "wave",
    "goodmorning": "wave",
    "goodnight": "sleep",
    "feed": "feed",
    "tickle": "tickle",
    "stare": "stare",
    "glare": "stare",
    "bonk": "punch",
    "kick": "kick",
    "nuke": "shoot",
}

FLAMINGDEATH_TEXTS = {
    "hug": lambda a, t: f"🤗 **[FlamingDeath Broadcast]** {a.mention} hugged aww {t.mention if t else 'everyone'}! Pretty friends!",
    "punch": lambda a, t: f"👊 **[FlamingDeath Broadcast]** FATAL BLOW! oww that hurt for sure 😵 {a.mention} punched {t.mention if t else 'the air'} into another dimension!",
    "pat": lambda a, t: f"🖐️ **[FlamingDeath Broadcast]** {a.mention} is patting {t.mention if t else 'someone' + chr(39) + 's'} head! Cute!",
    "slap": lambda a, t: f"👋 **[FlamingDeath Broadcast]** OOF! {a.mention} slapped the soul out of {t.mention if t else 'chat'}!",
    "highfive": lambda a, t: f"🙌 **[FlamingDeath Broadcast]** EPIC COLLAB! {a.mention} high-fived {t.mention if t else 'themselves'} with high energy!",
    "yeet": lambda a, t: f"💨 **[FlamingDeath Broadcast]** YEET! {a.mention} threw {t.mention if t else 'everyone'} out of the server orbit!",
    "dodge": lambda a, t: f"⚡ **[FlamingDeath Broadcast]** MATRIX MOVES! {a.mention} effortlessly dodged {t.mention if t else 'the incoming attacks'}!",
    "aura": lambda a, t: f"✨ **[FlamingDeath Broadcast]** OVERWHELMING POWER! {a.mention} flexed their aura on {t.mention if t else 'the entire server 😎'}!",
    "flex": lambda a, t: f"💪 **[FlamingDeath Broadcast]** {a.mention} is flexing on {t.mention if t else 'all the mortals'}! Pure intimidation!",
    "annoying": lambda a, t: f"🤪 **[FlamingDeath Broadcast]** {a.mention} is bored and annoying poor {t.mention if t else 'chat'}! The patience is breaking!",
    "rizz": lambda a, t: f"😏 **[FlamingDeath Broadcast]** LIGHTSPEED RIZZ! {a.mention} left {t.mention if t else 'the server'} oww they like them soo much 💀!",
    "hello": lambda a, t: f"👋 **[FlamingDeath Broadcast]** {a.mention} screamed HELLO at {t.mention if t else 'everyone'}! Welcome!",
    "goodmorning": lambda a, t: f"☀️ **[FlamingDeath Broadcast]** Announcing sunrise! {a.mention} dumped a bucket of sunshine on {t.mention if t else 'the entire chat'}! WAKE UP!",
    "goodnight": lambda a, t: f"🌙 **[FlamingDeath Broadcast]** Lights out! {a.mention} tucked {t.mention if t else 'everyone'} into bed with a high lullaby. Sleep tight!",
    "feed": lambda a, t: f"🥐 **[FlamingDeath Broadcast]** Emergency fueling! {a.mention} is force-feeding tasty anime snacks to {t.mention if t else 'the server'}!",
    "tickle": lambda a, t: f"🤭 **[FlamingDeath Broadcast]** Interrogation mode activated! {a.mention} is tickling {t.mention if t else 'random members'} until they surrender!",
    "stare": lambda a, t: f"👁️_👁️ **[FlamingDeath Broadcast]** Awkward silence... {a.mention} is staring through {t.mention if t else 'the chat' + chr(39) + 's'} soul. Explain yourselves!",
    "glare": lambda a, t: f"😠 **[FlamingDeath Broadcast]** Danger alert! {a.mention} just hit {t.mention if t else 'the whole channel'} with a deadly GLARE! Run!",
    "bonk": lambda a, t: f"🔨 **[FlamingDeath Broadcast]** BONK! {a.mention} struck {t.mention if t else 'the general chat'} with the Legendary Hammer!",
    "kick": lambda a, t: f"🦶 **[FlamingDeath Broadcast]** BOOM! {a.mention} kicked {t.mention if t else 'an imaginary target'} straight through the server wall!",
    "nuke": lambda a, t: f"💥 **[FlamingDeath Broadcast]** TACTICAL NUKE INBOUND! {a.mention} wiped out {t.mention if t else 'the battlefield'} with 1000-megaton energy!",
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
        category = NEKOS_ACTIONS.get(action.lower(), "stare")
        url = f"https://nekos.best/api/v2/{category}"

        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        return results[0].get("url", FALLBACK_GIF)
        except Exception as e:
            print(f"⚠️ Nekos API Error for '{category}': {e}", flush=True)

        return FALLBACK_GIF

    async def execute_action(
        self,
        interaction: discord.Interaction,
        action: str,
        target: discord.Member | None = None,
    ):
        act_key = action.lower()
        gif_url = await self.get_anime_gif(act_key)

        text_fn = FLAMINGDEATH_TEXTS.get(
            act_key,
            lambda a, t: f"🔥 **[FlamingDeath]** {a.mention} unleashed {act_key} on {t.mention if t else 'chat'}!",
        )
        text = text_fn(interaction.user, target)

        embed = discord.Embed(description=text, color=discord.Color.from_rgb(255, 69, 0))
        embed.set_image(url=gif_url)
        embed.set_footer(text="FlamingDeath Action Protocol", icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)

    # Optional text-trigger fallback: "flamy hug @user" works without a slash command
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        parts = message.content.strip().split()
        if len(parts) >= 2 and parts[0].lower() == "flamy":
            action = parts[1].lower()
            if action in NEKOS_ACTIONS:
                target = message.mentions[0] if message.mentions else None
                gif_url = await self.get_anime_gif(action)
                text_fn = FLAMINGDEATH_TEXTS.get(
                    action,
                    lambda a, t: f"🔥 **[FlamingDeath]** {a.mention} unleashed {action} on {t.mention if t else 'chat'}!",
                )
                text = text_fn(message.author, target)
                embed = discord.Embed(description=text, color=discord.Color.from_rgb(255, 69, 0))
                embed.set_image(url=gif_url)
                embed.set_footer(text="FlamingDeath Action Protocol", icon_url=message.author.display_avatar.url)
                await message.channel.send(embed=embed)

    # ==========================================
    # TOP-LEVEL SLASH COMMANDS — /hug, /punch, etc. directly, no group nesting
    # ==========================================
    @app_commands.command(name="hug", description="[FlamingDeath] 🤗 hug someone!")
    async def hug(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "hug", target)

    @app_commands.command(name="punch", description="[FlamingDeath] 👊 Fatal punch!")
    async def punch(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "punch", target)

    @app_commands.command(name="pat", description="[FlamingDeath] 😗 pat someone!")
    async def pat(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "pat", target)

    @app_commands.command(name="slap", description="[FlamingDeath] 💀 Slap the soul out of someone!")
    async def slap(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "slap", target)

    @app_commands.command(name="highfive", description="[FlamingDeath] 🙌 Epic highfive!")
    async def highfive(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "highfive", target)

    @app_commands.command(name="yeet", description="[FlamingDeath] ⏏️ Yeet someone into orbit!")
    async def yeet(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "yeet", target)

    @app_commands.command(name="dodge", description="[FlamingDeath] 💨 Matrix dodge!")
    async def dodge(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "dodge", target)

    @app_commands.command(name="aura", description="[FlamingDeath] 😏 Flex your overwhelming aura!")
    async def aura(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "aura", target)

    @app_commands.command(name="flex", description="[FlamingDeath] 🤟 flex!")
    async def flex(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "flex", target)

    @app_commands.command(name="annoying", description="[FlamingDeath] 😝 Be relentlessly annoying!")
    async def annoying(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "annoying", target)

    @app_commands.command(name="rizz", description="[FlamingDeath] 😘 Deploy lightspeed rizz!")
    async def rizz(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "rizz", target)

    @app_commands.command(name="hello", description="[FlamingDeath] 👋 Scream HELLO at someone!")
    async def hello(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "hello", target)

    @app_commands.command(name="goodmorning", description="[FlamingDeath] 🌄 Announce sunrise!")
    async def goodmorning(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "goodmorning", target)

    @app_commands.command(name="goodnight", description="[FlamingDeath] 💤 Lights out!")
    async def goodnight(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "goodnight", target)

    @app_commands.command(name="feed", description="[FlamingDeath] 🥪 Emergency fueling!")
    async def feed(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "feed", target)

    @app_commands.command(name="tickle", description="[FlamingDeath] 🤣 Interrogation tickle!")
    async def tickle(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "tickle", target)

    @app_commands.command(name="stare", description="[FlamingDeath] 🤨 Awkward stare!")
    async def stare(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "stare", target)

    @app_commands.command(name="glare", description="[FlamingDeath] ☺️ Deadly glare!")
    async def glare(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "glare", target)

    @app_commands.command(name="bonk", description="[FlamingDeath] 🔨 Legendary bonk!")
    async def bonk(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "bonk", target)

    @app_commands.command(name="kick", description="[FlamingDeath] 🦶 Boom! Kick them!")
    async def kick(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "kick", target)

    @app_commands.command(name="nuke", description="[FlamingDeath] ☢️ Tactical nuke!")
    async def nuke(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer()
        await self.execute_action(interaction, "nuke", target)


async def setup(bot):
    await bot.add_cog(ActionsCog(bot))
