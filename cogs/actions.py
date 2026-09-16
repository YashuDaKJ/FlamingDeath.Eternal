import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

FALLBACK_GIF = "https://media.tenor.com/gbf398P3xTEAAAAC/hug-anime.gif"

# Mapping ALL actions to nekos.best API endpoints
NEKOS_ACTIONS = {
    # Original Base Actions
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
    # New FlamingDeath Actions
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
            async with self.session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        return results[0].get("url", FALLBACK_GIF)
        except Exception as e:
            print(f"⚠️ Nekos API Error for '{category}': {e}", flush=True)

        return FALLBACK_GIF

    # FlamingDeath Announcer Personality Dialogues for ALL commands
    FLAMINGDEATH_TEXTS = {
        # Base Commands
        "hug": lambda a, t: f"🤗 **[FlamingDeath Broadcast]** {a.mention} hugged aww {t.mention if t else 'everyone'}! Pretty friends!",
        "punch": lambda a, t: f"👊 **[FlamingDeath Broadcast]** FATAL BLOW! oww that hurt for sure 😵 {a.mention} punched {t.mention if t else 'the air'} into another dimension!",
        "pat": lambda a, t: f"🖐️ **[FlamingDeath Broadcast]** {a.mention} is patting {t.mention if t else 'someone\\'s'} head! Cute!",
        "slap": lambda a, t: f"👋 **[FlamingDeath Broadcast]** OOF! {a.mention} slapped the soul out of {t.mention if t else 'chat'}!",
        "highfive": lambda a, t: f"🙌 **[FlamingDeath Broadcast]** EPIC COLLAB! {a.mention} high-fived {t.mention if t else 'themselves'} with high energy!",
        "yeet": lambda a, t: f"💨 **[FlamingDeath Broadcast]** YEET! {a.mention} threw {t.mention if t else 'everyone'} out of the server orbit!",
        "dodge": lambda a, t: f"⚡ **[FlamingDeath Broadcast]** MATRIX MOVES! {a.mention} effortlessly dodged {t.mention if t else 'the incoming attacks'}!",
        "aura": lambda a, t: f"✨ **[FlamingDeath Broadcast]** OVERWHELMING POWER! {a.mention} flexed their aura on {t.mention if t else 'the entire server 😎'}!",
        "flex": lambda a, t: f"💪 **[FlamingDeath Broadcast]** {a.mention} is flexing on {t.mention if t else 'all the mortals'}! Pure intimidation!",
        "annoying": lambda a, t: f"🤪 **[FlamingDeath Broadcast]** {a.mention} is bored and annoying poor {t.mention if t else 'chat'}! The patience is breaking!",
        "rizz": lambda a, t: f"😏 **[FlamingDeath Broadcast]** LIGHTSPEED RIZZ! {a.mention} left {t.mention if t else 'the server'} oww they like them soo much 💀!",
        "hello": lambda a, t: f"👋 **[FlamingDeath Broadcast]** {a.mention} screamed HELLO at {t.mention if t else 'everyone'}! Welcome!",
        
        # New Commands
        "goodmorning": lambda a, t: f"☀️ **[FlamingDeath Broadcast]** Announcing sunrise! {a.mention} dumped a bucket of sunshine on {t.mention if t else 'the entire chat'}! WAKE UP!",
        "goodnight": lambda a, t: f"🌙 **[FlamingDeath Broadcast]** Lights out! {a.mention} tucked {t.mention if t else 'everyone'} into bed with a high lullaby. Sleep tight!",
        "feed": lambda a, t: f"🥐 **[FlamingDeath Broadcast]** Emergency fueling! {a.mention} is force-feeding tasty anime snacks to {t.mention if t else 'the server'}!",
        "tickle": lambda a, t: f"🤭 **[FlamingDeath Broadcast]** Interrogation mode activated! {a.mention} is tickling {t.mention if t else 'random members'} until they surrender!",
        "stare": lambda a, t: f"👁️_👁️ **[FlamingDeath Broadcast]** Awkward silence... {a.mention} is staring through {t.mention if t else 'the chat\\'s'} soul. Explain yourselves!",
        "glare": lambda a, t: f"😠 **[FlamingDeath Broadcast]** Danger alert! {a.mention} just hit {t.mention if t else 'the whole channel'} with a deadly GLARE! Run!",
        "bonk": lambda a, t: f"🔨 **[FlamingDeath Broadcast]** BONK! {a.mention} struck {t.mention if t else 'the general chat'} with the Legendary Hammer!",
        "kick": lambda a, t: f"🦶 **[FlamingDeath Broadcast]** BOOM! {a.mention} kicked {t.mention if t else 'an imaginary target'} straight through the server wall!",
        "nuke": lambda a, t: f"💥 **[FlamingDeath Broadcast]** TACTICAL NUKE INBOUND! {a.mention} wiped out {t.mention if t else 'the battlefield'} with 1000-megaton energy!",
    }

    async def execute_action(
        self,
        channel_or_ctx,
        author: discord.User | discord.Member,
        action: str,
        target: discord.Member | None = None,
        is_interaction: bool = False,
    ):
        act_key = action.lower()
        gif_url = await self.get_anime_gif(act_key)

        text_fn = self.FLAMINGDEATH_TEXTS.get(
            act_key,
            lambda a, t: (
                f"🔥 **[FlamingDeath]** {a.mention} unleashed {act_key} on"
                f" {t.mention if t else 'chat'}!"
            ),
        )
        text = text_fn(author, target)

        embed = discord.Embed(
            description=text, color=discord.Color.from_rgb(255, 69, 0)
        )
        embed.set_image(url=gif_url)
        embed.set_footer(
            text="FlamingDeath Action Protocol", icon_url=author.display_avatar.url
        )

        if is_interaction:
            await channel_or_ctx.followup.send(embed=embed)
        elif isinstance(channel_or_ctx, commands.Context):
            await channel_or_ctx.send(embed=embed)
        else:
            await channel_or_ctx.send(embed=embed)

    # 1. DIRECT TEXT LISTENER (e.g., "flamy kick @user" or "FLAMY NUKE")
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.strip()
        parts = content.split()

        if not parts:
            return

        first_word = parts[0].lower()

        # Check if first word is 'flamy' (without prefix)
        if first_word == "flamy" and len(parts) >= 2:
            action = parts[1].lower()
            if action in NEKOS_ACTIONS:
                target = message.mentions[0] if message.mentions else None
                await self.execute_action(
                    message.channel, message.author, action, target
                )

    # 2. PREFIX COMMAND GROUP (!flamy)
    @commands.group(
        name="flamy", invoke_without_command=True, case_insensitive=True
    )
    async def flamy_prefix(self, ctx: commands.Context):
        actions_list = "|".join(NEKOS_ACTIONS.keys())
        await ctx.send(f"🔥 **[FlamingDeath]** Available actions:\n`{actions_list}`")

    # Generating Prefix Commands Dynamically
    for action_name in NEKOS_ACTIONS.keys():
        @flamy_prefix.command(name=action_name)
        async def prefix_cmd(self, ctx, target: discord.Member | None = None, _action=action_name):
            await self.execute_action(ctx, ctx.author, _action, target)


# 3. SLASH COMMANDS GROUP (/flamy)
class FlamySlashGroup(app_commands.Group):
    def __init__(self, cog: ActionsCog):
        super().__init__(
            name="flamy", description="FlamingDeath Action Commands"
        )
        self.cog = cog

    # Manually defining slash commands due to discord.py limitations on dynamic app_commands
    @app_commands.command(name="hug", description="[FlamingDeath] 🤗 hug someone!")
    async def s_hug(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "hug", target, True)

    @app_commands.command(name="punch", description="[FlamingDeath] 👊 Fatal punch!")
    async def s_punch(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "punch", target, True)

    @app_commands.command(name="pat", description="[FlamingDeath] 😗 pat someone!")
    async def s_pat(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "pat", target, True)

    @app_commands.command(name="slap", description="[FlamingDeath] 💀 Slap the soul out of someone!")
    async def s_slap(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "slap", target, True)

    @app_commands.command(name="highfive", description="[FlamingDeath] 🙌 Epic highfive!")
    async def s_highfive(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "highfive", target, True)

    @app_commands.command(name="yeet", description="[FlamingDeath] ⏏️ Yeet someone into orbit!")
    async def s_yeet(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "yeet", target, True)

    @app_commands.command(name="dodge", description="[FlamingDeath] 💨 Matrix dodge!")
    async def s_dodge(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "dodge", target, True)

    @app_commands.command(name="aura", description="[FlamingDeath] 😏 Flex your overwhelming aura!")
    async def s_aura(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "aura", target, True)

    @app_commands.command(name="flex", description="[FlamingDeath] 🤟 flex!")
    async def s_flex(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "flex", target, True)

    @app_commands.command(name="annoying", description="[FlamingDeath] 😝 Be relentlessly annoying!")
    async def s_annoying(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "annoying", target, True)

    @app_commands.command(name="rizz", description="[FlamingDeath] 😘 Deploy lightspeed rizz!")
    async def s_rizz(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "rizz", target, True)

    @app_commands.command(name="hello", description="[FlamingDeath] 👋 Scream HELLO at someone!")
    async def s_hello(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "hello", target, True)

    @app_commands.command(name="goodmorning", description="[FlamingDeath] 🌄 Announce sunrise!")
    async def s_goodmorning(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "goodmorning", target, True)

    @app_commands.command(name="goodnight", description="[FlamingDeath] 💤 Lights out!")
    async def s_goodnight(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "goodnight", target, True)

    @app_commands.command(name="feed", description="[FlamingDeath] 🥪 Emergency fueling!")
    async def s_feed(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "feed", target, True)

    @app_commands.command(name="tickle", description="[FlamingDeath] 🤣 Interrogation tickle!")
    async def s_tickle(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "tickle", target, True)

    @app_commands.command(name="stare", description="[FlamingDeath] 🤨 Awkward stare!")
    async def s_stare(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "stare", target, True)

    @app_commands.command(name="glare", description="[FlamingDeath] ☺️ Deadly glare!")
    async def s_glare(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "glare", target, True)

    @app_commands.command(name="bonk", description="[FlamingDeath] 🔨 Legendary bonk!")
    async def s_bonk(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "bonk", target, True)

    @app_commands.command(name="kick", description="[FlamingDeath] 🦶 Boom! Kick them!")
    async def s_kick(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "kick", target, True)

    @app_commands.command(name="nuke", description="[FlamingDeath] ☢️ Tactical nuke!")
    async def s_nuke(self, interaction: discord.Interaction, target: discord.Member | None = None):
        await interaction.response.defer(); await self.cog.execute_action(interaction, interaction.user, "nuke", target, True)


async def setup(bot):
    cog = ActionsCog(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(FlamySlashGroup(cog))
    
