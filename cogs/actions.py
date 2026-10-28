import random

import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

FALLBACK_GIF = "https://media.tenor.com/gbf398P3xTEAAAAC/hug-anime.gif"

# Static fallback used only if the live /endpoints fetch fails at startup
STATIC_FALLBACK_CATEGORIES = {
    "hug": "gif", "punch": "gif", "pat": "gif", "slap": "gif", "highfive": "gif",
    "yeet": "gif", "shoot": "gif", "bored": "gif", "poke": "gif",
    "smug": "gif", "wave": "gif", "sleep": "gif", "feed": "gif", "tickle": "gif",
    "stare": "gif", "bonk": "gif", "kick": "gif",
}

# Custom Command Descriptions for Discord Slash Commands (No "anime" word)
COMMAND_DESCRIPTIONS = {
    "kick": "Kick a target through the server walls!",
    "punch": "Land a fatal punch that sends the target into another dimension!",
    "slap": "Slap the soul out of someone!",
    "bonk": "Strike a member with the Legendary Ban Hammer!",
    "yeet": "Throw someone into outer space orbit!",
    "shoot": "Fire a beam of pure energy at the target!",
    "bite": "Take a quick bite out of someone!",
    "bored": "Show everyone how extremely bored you are!",
    "poke": "Relentlessly poke someone until their patience breaks!",
    "smug": "Show off a smug, confident face!",
    "stare": "Stare awkwardly right through someone's soul!",
    "confused": "Look around in utter confusion!",
    "think": "Ponder deeply about life choices!",
    "shocked": "Show a shocked, jaw-dropping reaction!",
    "facepalm": "Facepalm at someone's hilarious mistake!",
    "yawn": "Yawn dramatically to show you're sleepy!",
    "bleh": "Stick your tongue out playfully!",
    "teehee": "Giggle mischievously!",
    "lurk": "Stalk and watch quietly from the dark shadows!",
    "shrug": "Shrug your shoulders in total indifference!",
    "pout": "Pout with cute anger!",
    "cry": "Burst into emotional tears!",
    "laugh": "Laugh out loud at something funny!",
    "tableflip": "Flip a table in pure rage!",
    "hug": "Give someone an aggressive, wholesome warm hug!",
    "pat": "Gently pat someone on the head!",
    "highfive": "High-five someone with explosive energy!",
    "wave": "Wave hello warmly to the chat!",
    "sleep": "Tuck into bed and fall asleep!",
    "feed": "Force-feed delicious snacks to someone!",
    "tickle": "Tickle someone until they surrender!",
    "smile": "Share a bright and cheerful smile!",
    "peck": "Give a quick, cute peck on the cheek!",
    "wink": "Send a smooth, playful wink!",
    "sip": "Calmly sip a warm drink while watching chat!",
    "blush": "Turn bright red and blush bashfully!",
    "wag": "Wag your tail happily!",
    "nya": "Strike a cute cat pose!",
    "cuddle": "Snuggle up close for warm cuddles!",
    "happy": "Express pure, uninhibited happiness!",
    "carry": "Carry someone in your arms like a hero!",
    "kabedon": "Corner someone against the wall dramatically!",
    "baka": "Call someone a total dummy!",
    "angry": "Show off your furious mood!",
    "spin": "Spin around merrily in circles!",
    "shake": "Shake violently with energy or terror!",
    "run": "Sprint away at full speed!",
    "nod": "Nod your head in clear agreement!",
    "nope": "Shake your head in absolute refusal!",
    "kiss": "Give someone a sweet kiss!",
    "dance": "Bust out some legendary dance moves!",
    "handshake": "Shake hands with respect!",
    "lappillow": "Rest your head gently on someone's lap!",
    "blowkiss": "Blow a loving kiss across the channel!",
    "handhold": "Hold hands warmly with a friend!",
    "salute": "Stand at attention and salute!",
    "thumbsup": "Give a big thumbs up for approval!",
}

def _fmt_target(target: discord.abc.User | None, fallback: str = "everyone") -> str:
    return target.mention if target else fallback

# Randomized funny text variations for each action.
FLAMINGDEATH_TEXTS = {
    "hug": [
        "{a} jumped in with a warm, dramatic hug for {t} and instantly made the room feel way too cozy.",
        "{a} wrapped {t} in a full-body hug and somehow turned chaos into a wholesome moment.",
        "{a} launched a hug ambush on {t} and called it a successful public service.",
    ],
    "punch": [
        "{a} landed a brutal punch on {t} and somehow made it look stylish.",
        "{a} sent {t} flying back with a clean knockout hit and zero mercy.",
        "{a} absolutely walloped {t} like the room was a fighting game and they were the boss battle.",
    ],
    "pat": [
        "{a} gently patted {t}'s head like a calm boss with zero fear and maximum affection.",
        "{a} gave {t} a quick head pat and somehow made it feel like a power move.",
        "{a} tapped {t} on the head and instantly became the most emotionally stable person in the chat.",
    ],
    "slap": [
        "{a} slapped the soul out of {t} and left the room stunned for a full second.",
        "{a} gave {t} a cinematic slap and somehow made it look like a warning shot.",
        "{a} clapped {t} with a dramatic slap and perfectly timed chaos.",
    ],
    "highfive": [
        "{a} high-fived {t} like a total legend and instantly boosted the mood of the whole server.",
        "{a} pulled off a hype-level high-five with {t} and made the room feel like a montage.",
        "{a} and {t} locked hands in a high-five so clean it deserved its own soundtrack.",
    ],
    "yeet": [
        "{a} yeeted {t} clean out of the server orbit and called it a team-building exercise.",
        "{a} launched {t} across the room like they were trying to break the stratosphere.",
        "{a} threw {t} so hard they may need a new timezone after this.",
    ],
    "shoot": [
        "{a} fired a glowing beam at {t} and somehow made the whole channel feel like a movie scene.",
        "{a} blasted {t} with pure energy and walked away like it was nothing.",
        "{a} unleashed a ridiculous laser shot on {t} and called it a clean finish.",
    ],
    "bored": [
        "{a} flexed at {t} with maximum boredom energy and somehow made it intimidating.",
        "{a} went full sleepy flex and still managed to make {t} feel personally attacked.",
        "{a} looked at {t} like they were the problem and the problem was very much not okay.",
    ],
    "poke": [
        "{a} kept poking {t} until even the silence started judging them.",
        "{a} launched a full-on poke assault on {t} and proudly called it a strategy.",
        "{a} poked {t} with absolute confidence and zero concern for boundaries.",
    ],
    "smug": [
        "{a} gave {t} the smuggest look in the room and somehow made it a victory speech.",
        "{a} locked eyes with {t} and smirked like they already won the argument.",
        "{a} leaned in with pure smug energy and made {t} feel personally judged.",
    ],
    "wave": [
        "{a} waved at {t} so enthusiastically it felt like the whole server got a greeting.",
        "{a} gave {t} a warm hello wave and somehow made it a full event.",
        "{a} waved at {t} like they were launching a friendly apocalypse.",
    ],
    "sleep": [
        "{a} tucked {t} into a dramatic bedtime nap and called it mission accomplished.",
        "{a} put {t} to sleep like a bedtime legend with zero shame and full theatrics.",
        "{a} started a sleep routine with {t} and somehow turned bedtime into a villain monologue.",
    ],
    "feed": [
        "{a} force-fed a snack to {t} like a personal chef with zero regard for personal space.",
        "{a} shoved food at {t} and declared it the most important event of the day.",
        "{a} fed {t} with dramatic flair and zero concern for their dietary plan.",
    ],
    "tickle": [
        "{a} started a ruthless tickle attack on {t} and the room immediately became chaos.",
        "{a} tickled {t} until they were laughing so hard the whole chat felt it.",
        "{a} launched a surprise tickle ambush on {t} and called it public service.",
    ],
    "stare": [
        "{a} locked eyes with {t} and somehow made the silence feel more dramatic than the action.",
        "{a} stared straight through {t} like they were reading the entire future in one look.",
        "{a} and {t} got stuck in an awkward stare-off that somehow became the main event.",
    ],
    "bonk": [
        "{a} bonked {t} with the legendary hammer and made the room gasp instantly.",
        "{a} unleashed the ban hammer on {t} and somehow made it feel heroic.",
        "{a} bonked {t} so dramatically even the hammer looked proud.",
    ],
    "kick": [
        "{a} kicked {t} straight through the server wall and called it a clean finish.",
        "{a} booted {t} with full savage energy and instantly made the room cheer.",
        "{a} launched a brutal kick at {t} and somehow made the impact look elegant.",
    ],
}

DISPLAY_NAME_OVERRIDES = {
    "blowkiss": "blow a kiss to",
    "handhold": "hold hands with",
    "handshake": "shake hands with",
    "facepalm": "facepalm at",
}

def _default_text(category: str):
    verb = DISPLAY_NAME_OVERRIDES.get(category, category)
    return lambda a, t: f"🔥 **[FlamingDeath Chaos]** {a.mention} used **{verb}** on {_fmt_target(t, 'everyone')}!"

class ActionRetaliateView(discord.ui.View):
    def __init__(self, cog: "ActionsCog", category: str, original_author: discord.abc.User, target: discord.Member | None):
        super().__init__(timeout=180)
        self.cog = cog
        self.category = category
        self.original_author = original_author
        self.target = target

        label = self._build_button_label(category)
        self.action_button = discord.ui.Button(
            label=label,
            style=discord.ButtonStyle.secondary,
        )
        self.action_button.callback = self._on_click
        self.add_item(self.action_button)

    @staticmethod
    def _build_button_label(category: str) -> str:
        replacements = {
            "hug": "Hug",
            "punch": "Punch",
            "pat": "Pat",
            "slap": "Slap",
            "highfive": "High-Five",
            "yeet": "Yeet",
            "shoot": "Shoot",
            "bored": "Bored",
            "poke": "Poke",
            "smug": "Smug",
            "wave": "Wave",
            "sleep": "Sleep",
            "feed": "Feed",
            "tickle": "Tickle",
            "stare": "Stare",
            "bonk": "Bonk",
            "kick": "Kick",
        }
        name = replacements.get(category, category.replace("_", " ").replace("-", " ").title())
        return f"🔄 {name} Back!"

    def disable_all_items(self):
        for item in self.children:
            item.disabled = True

    async def _on_click(self, interaction: discord.Interaction):
        if self.target is not None and interaction.user != self.target:
            await interaction.response.send_message("⚠️ Only the target can retaliate!", ephemeral=True)
            return

        self.disable_all_items()
        await interaction.response.defer()
        try:
            await interaction.message.edit(view=self)
        except discord.NotFound:
            pass

        await self.cog._send_action(interaction.channel.send, interaction.user, self.category, self.original_author)

class ActionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None
        self.categories: dict[str, str] = {}

    SLASH_BUDGET = 40

    PRIORITY_CATEGORIES = [
        "hug", "punch", "pat", "slap", "highfive", "yeet",
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
        verb = DISPLAY_NAME_OVERRIDES.get(category, category)
        command_desc = COMMAND_DESCRIPTIONS.get(category, f"[FlamingDeath] {verb} someone!")

        async def _callback(interaction: discord.Interaction, target: discord.Member | None = None):
            await interaction.response.defer()
            await self._send_action(interaction.followup.send, interaction.user, category, target)

        _callback.__name__ = category
        cmd = app_commands.Command(
            name=category,
            description=command_desc[:100],
            callback=_callback,
        )
        self.bot.tree.add_command(cmd)
        self._registered_slash_names.append(category)

    async def cog_unload(self):
        for name in getattr(self, "_registered_slash_names", []):
            self.bot.tree.remove_command(name)

        self.bot.remove_command("flamy")

        if self.session and not self.session.closed:
            await self.session.close()

    async def _load_categories(self):
        try:
            async with self.session.get(
                "https://nekos.best/api/v2/endpoints",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
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
        variants = FLAMINGDEATH_TEXTS.get(category)
        if isinstance(variants, list) and variants:
            return lambda a, t: random.choice(variants).format(
                a=a.mention,
                t=_fmt_target(t, "everyone"),
            )
        return _default_text(category)

    async def _send_action(self, destination_send, author: discord.abc.User, category: str, target: discord.Member | None):
        gif_url = await self.get_anime_gif(category)
        text = self._text_for(category)(author, target)

        embed = discord.Embed(description=text, color=discord.Color.from_rgb(255, 69, 0))
        embed.set_image(url=gif_url)
        embed.set_footer(text="FlamingDeath Action Arena", icon_url=author.display_avatar.url)

        view = ActionRetaliateView(self, category, author, target)
        await destination_send(embed=embed, view=view)

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

    def _register_prefix_group(self):
        async def flamy_root(ctx: commands.Context):
            names = ", ".join(sorted(self.categories.keys()))
            await ctx.send(f"🔥 **[FlamingDeath]** Available actions ({len(self.categories)}):\n`{names}`")

        group = commands.Group(flamy_root, name="flamy", invoke_without_command=True, case_insensitive=True)

        def make_subcommand(cat_name: str):
            async def _cmd(ctx: commands.Context, target: discord.Member | None = None):
                await self._send_action(ctx.send, ctx.author, cat_name, target)
            _cmd.__name__ = f"flamy_{cat_name}"
            return commands.Command(_cmd, name=cat_name)

        for category in self.categories:
            group.add_command(make_subcommand(category))

        self.bot.add_command(group)

async def setup(bot):
    await bot.add_cog(ActionsCog(bot))
