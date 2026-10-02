import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

FALLBACK_GIF = "https://media.tenor.com/gbf398P3xTEAAAAC/hug-anime.gif"

# Static fallback used only if the live /endpoints fetch fails at startup
# (e.g. nekos.best is briefly down when the bot boots). Once the live
# fetch succeeds this is replaced with the real, full category list.
STATIC_FALLBACK_CATEGORIES = {
    "hug": "gif", "punch": "gif", "pat": "gif", "slap": "gif", "highfive": "gif",
    "yeet": "gif", "dodge": "gif", "shoot": "gif", "bored": "gif", "poke": "gif",
    "smug": "gif", "wave": "gif", "sleep": "gif", "feed": "gif", "tickle": "gif",
    "stare": "gif", "bonk": "gif", "kick": "gif",
}

# Hand-written flavor text for the "signature" FlamingDeath actions.
# Anything NOT in this dict (i.e. every other live nekos.best category)
# gets an auto-generated generic line instead — see _default_text().
FLAMINGDEATH_TEXTS = {
    "hug": lambda a, t: f"🤗 **[FlamingDeath Broadcast]** {a.mention} hugged aww {t.mention if t else 'everyone'}! Pretty friends!",
    "punch": lambda a, t: f"👊 **[FlamingDeath Broadcast]** FATAL BLOW! oww that hurt for sure 😵 {a.mention} punched {t.mention if t else 'the air'} into another dimension!",
    "pat": lambda a, t: f"🖐️ **[FlamingDeath Broadcast]** {a.mention} is patting {t.mention if t else 'someone' + chr(39) + 's'} head! Cute!",
    "slap": lambda a, t: f"👋 **[FlamingDeath Broadcast]** OOF! {a.mention} slapped the soul out of {t.mention if t else 'chat'}!",
    "highfive": lambda a, t: f"🙌 **[FlamingDeath Broadcast]** EPIC COLLAB! {a.mention} high-fived {t.mention if t else 'themselves'} with high energy!",
    "yeet": lambda a, t: f"💨 **[FlamingDeath Broadcast]** YEET! {a.mention} threw {t.mention if t else 'everyone'} out of the server orbit!",
    "dodge": lambda a, t: f"⚡ **[FlamingDeath Broadcast]** MATRIX MOVES! {a.mention} effortlessly dodged {t.mention if t else 'the incoming attacks'}!",
    "shoot": lambda a, t: f"✨ **[FlamingDeath Broadcast]** OVERWHELMING POWER! {a.mention} flexed their aura on {t.mention if t else 'the entire server 😎'}!",
    "bored": lambda a, t: f"💪 **[FlamingDeath Broadcast]** {a.mention} is flexing on {t.mention if t else 'all the mortals'}! Pure intimidation!",
    "poke": lambda a, t: f"🤪 **[FlamingDeath Broadcast]** {a.mention} is bored and annoying poor {t.mention if t else 'chat'}! The patience is breaking!",
    "smug": lambda a, t: f"😏 **[FlamingDeath Broadcast]** LIGHTSPEED RIZZ! {a.mention} left {t.mention if t else 'the server'} oww they like them soo much 💀!",
    "wave": lambda a, t: f"👋 **[FlamingDeath Broadcast]** {a.mention} screamed HELLO at {t.mention if t else 'everyone'}! Welcome!",
    "sleep": lambda a, t: f"🌙 **[FlamingDeath Broadcast]** Lights out! {a.mention} tucked {t.mention if t else 'everyone'} into bed with a high lullaby. Sleep tight!",
    "feed": lambda a, t: f"🥐 **[FlamingDeath Broadcast]** Emergency fueling! {a.mention} is force-feeding tasty anime snacks to {t.mention if t else 'the server'}!",
    "tickle": lambda a, t: f"🤭 **[FlamingDeath Broadcast]** Interrogation mode activated! {a.mention} is tickling {t.mention if t else 'random members'} until they surrender!",
    "stare": lambda a, t: f"👁️_👁️ **[FlamingDeath Broadcast]** Awkward silence... {a.mention} is staring through {t.mention if t else 'the chat' + chr(39) + 's'} soul. Explain yourselves!",
    "bonk": lambda a, t: f"🔨 **[FlamingDeath Broadcast]** BONK! {a.mention} struck {t.mention if t else 'the general chat'} with the Legendary Hammer!",
    "kick": lambda a, t: f"🦶 **[FlamingDeath Broadcast]** BOOM! {a.mention} kicked {t.mention if t else 'an imaginary target'} straight through the server wall!",
}

# Friendlier display names for categories whose raw API name reads oddly
# in a generated sentence (e.g. "kabedon" -> still "kabedon", fine as-is;
# this is only for the handful that need it).
DISPLAY_NAME_OVERRIDES = {
    "blowkiss": "blow a kiss to",
    "handhold": "hold hands with",
    "handshake": "shake hands with",
    "facepalm": "facepalm at",
}


def _default_text(category: str):
    verb = DISPLAY_NAME_OVERRIDES.get(category, category)
    return lambda a, t: f"🔥 **[FlamingDeath Broadcast]** {a.mention} used **{verb}** on {t.mention if t else 'everyone'}!"


class ActionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None
        # category_name -> "gif" or "png"
        self.categories: dict[str, str] = {}

    # Total top-level slash commands this cog will register. Your bot had
    # 58 synced commands before this cog; replacing the old 21-command
    # version with this budget nets ~77 total, leaving ~23 headroom under
    # Discord's hard 100-global-command cap. Raise this later if you free
    # up budget elsewhere, but check your !sync number again first.
    SLASH_BUDGET = 40

    # These get first priority for a slash slot (familiar names, custom
    # flavor text). Remaining budget slots are filled from whatever other
    # live categories come back from nekos.best, alphabetically.
    PRIORITY_CATEGORIES = [
        "hug", "punch", "pat", "slap", "highfive", "yeet", "dodge",
        "shoot", "bored", "poke", "smug", "wave", "sleep", "feed",
        "tickle", "stare", "bonk", "kick",
    ]

    async def cog_load(self):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "FlamingDeathBot/1.0 (Discord action commands)"}
        )
        await self._load_categories()
        self._register_prefix_group()
        self._registered_slash_names: list[str] = []
        self._register_slash_commands()

    def _register_slash_commands(self):
        chosen: list[str] = []
        for cat in self.PRIORITY_CATEGORIES:
            if cat in self.categories and cat not in chosen:
                chosen.append(cat)
                if len(chosen) >= self.SLASH_BUDGET:
                    break

        if len(chosen) < self.SLASH_BUDGET:
            for cat in sorted(self.categories.keys()):
                if cat not in chosen:
                    chosen.append(cat)
                    if len(chosen) >= self.SLASH_BUDGET:
                        break

        for category in chosen:
            self._add_dynamic_slash(category)

        print(f"🔥 Registered {len(chosen)} slash commands out of {len(self.categories)} live categories "
              f"({len(self.categories) - len(chosen)} more available via !flamy / text-trigger only).", flush=True)

    def _add_dynamic_slash(self, category: str):
        async def _callback(interaction: discord.Interaction, target: discord.Member | None = None):
            await interaction.response.defer()
            await self._send_action(interaction.followup.send, interaction.user, category, target)

        _callback.__name__ = category
        verb = DISPLAY_NAME_OVERRIDES.get(category, category)
        cmd = app_commands.Command(
            name=category,
            description=f"[FlamingDeath] {verb} someone!",
            callback=_callback,
        )
        self.bot.tree.add_command(cmd)
        self._registered_slash_names.append(category)

    async def cog_unload(self):
        for name in getattr(self, "_registered_slash_names", []):
            self.bot.tree.remove_command(name)
        if self.session and not self.session.closed:
            await self.session.close()

    async def _load_categories(self):
        """Fetch the live, current category list straight from nekos.best."""
        try:
            async with self.session.get(
                "https://nekos.best/api/v2/endpoints",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Only "gif" categories make sense as a targeted action;
                    # png categories (neko, waifu, husbando, kitsune) are
                    # standalone images, not something you "do" to someone.
                    self.categories = {
                        name: info.get("format", "gif")
                        for name, info in data.items()
                        if info.get("format") == "gif"
                    }
                    print(f"🔥 Loaded {len(self.categories)} live nekos.best gif categories.", flush=True)
                    return
        except Exception as e:
            print(f"⚠️ Failed to fetch nekos.best /endpoints: {e}", flush=True)

        print("⚠️ Falling back to static category list.", flush=True)
        self.categories = STATIC_FALLBACK_CATEGORIES

    async def get_anime_gif(self, category: str) -> str:
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

    def _text_for(self, category: str):
        return FLAMINGDEATH_TEXTS.get(category, _default_text(category))

    async def _send_action(self, destination_send, author: discord.abc.User, category: str, target: discord.Member | None):
        gif_url = await self.get_anime_gif(category)
        text = self._text_for(category)(author, target)

        embed = discord.Embed(description=text, color=discord.Color.from_rgb(255, 69, 0))
        embed.set_image(url=gif_url)
        embed.set_footer(text="FlamingDeath Action Protocol", icon_url=author.display_avatar.url)
        await destination_send(embed=embed)

    # ==========================================
    # TEXT TRIGGER: "flamy <action> @user" — unlimited, covers every live category
    # ==========================================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        parts = message.content.strip().split()
        if len(parts) >= 2 and parts[0].lower() == "flamy":
            action = parts[1].lower()
            if action in self.categories:
                target = message.mentions[0] if message.mentions else None
                await self._send_action(message.channel.send, message.author, action, target)

    # ==========================================
    # PREFIX COMMANDS: "!flamy <action> @user" — unlimited, dynamically built
    # from the live category list. Registered in cog_load, not via a
    # fragile class-body loop.
    # ==========================================
    def _register_prefix_group(self):
        group = commands.Group(name="flamy", invoke_without_command=True, case_insensitive=True)

        async def flamy_root(ctx: commands.Context):
            names = ", ".join(sorted(self.categories.keys()))
            await ctx.send(f"🔥 **[FlamingDeath]** Available actions ({len(self.categories)}):\n`{names}`")

        group.callback = flamy_root

        def make_subcommand(category: str):
            async def _cmd(ctx: commands.Context, target: discord.Member | None = None):
                await self._send_action(ctx.send, ctx.author, category, target)
            _cmd.__name__ = f"flamy_{category}"
            return group.command(name=category)(_cmd)

        for category in self.categories:
            make_subcommand(category)

        self.bot.add_command(group)


async def setup(bot):
    await bot.add_cog(ActionsCog(bot))
