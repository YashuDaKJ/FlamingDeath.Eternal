import random
import time
import discord
from discord import app_commands
from discord.ext import commands

# ==========================================
# 🌟 INTERACTIVE EXPEDITION UI (NEW GAME)
# ==========================================
class ExpeditionView(discord.ui.View):
    def __init__(self, user_id: int, bot):
        super().__init__(timeout=30.0) # Player has 30 seconds to choose
        self.user_id = user_id
        self.bot = bot
        self.chosen = False

    async def handle_choice(self, interaction: discord.Interaction, choice_type: str):
        # Prevent other users from clicking the buttons
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your expedition! Start your own with `/expedition`.", ephemeral=True)
            return

        self.chosen = True
        # Disable all buttons after a choice is made
        for child in self.children:
            child.disabled = True

        # Custom Lore for ETERNAL Faction
        events = {
            "caverns": [
                {"text": "⛏️ You mined deep into an abandoned mineshaft and discovered rare crystals!", "crystals": random.randint(40, 80), "color": discord.Color.blue()},
                {"text": "⛏️ Your pickaxe broke on some bedrock. You returned empty-handed.", "crystals": 0, "color": discord.Color.light_grey()},
                {"text": "⛏️ You stumbled upon a glowing Sky-Blue Crystal Cavern! The energy here is immense.", "crystals": random.randint(150, 250), "color": discord.Color.teal()}
            ],
            "ruins": [
                {"text": "🏛️ You explored an old rival outpost and secured some abandoned treasury supplies.", "crystals": random.randint(50, 100), "color": discord.Color.green()},
                {"text": "🏛️ You triggered a harmless tripwire! A net dropped on you, delaying your search. You found nothing.", "crystals": 0, "color": discord.Color.orange()},
                {"text": "🏛️ Jackpot! You unearthed a hidden relic of the Faceless Dragon. The ETERNAL treasury will be pleased!", "crystals": random.randint(200, 350), "color": discord.Color.gold()}
            ],
            "wilderness": [
                {"text": "🌲 You foraged in the SquareOne wilderness and found some scattered crystal fragments.", "crystals": random.randint(20, 50), "color": discord.Color.dark_green()},
                {"text": "🌲 You got lost in a dense forest and spent the whole day just finding your way back to base.", "crystals": 0, "color": discord.Color.dark_grey()},
                {"text": "🌲 A wandering merchant traded you a pouch of crystals for your travel rations!", "crystals": random.randint(80, 150), "color": discord.Color.purple()}
            ]
        }

        scenario = random.choice(events[choice_type])
        reward = scenario["crystals"]
        
        # Add crystals to the database if the player won
        if reward > 0 and self.bot.profiles:
            await self.bot.profiles.update_one(
                {"_id": str(interaction.user.id)},
                {"$inc": {"crystals": reward}},
                upsert=True
            )
            
        embed = discord.Embed(
            title="🗺️ Expedition Concluded", 
            description=scenario["text"], 
            color=scenario["color"]
        )
        
        if reward > 0:
            embed.add_field(name="Loot Secured", value=f"✨ **+{reward}** Crystals")
        else:
            embed.add_field(name="Loot Secured", value="None this time.")

        await interaction.response.edit_message(embed=embed, view=self)

    # --- BUTTON DEFINITIONS ---
    @discord.ui.button(label="Deep Caverns", style=discord.ButtonStyle.primary, emoji="⛏️")
    async def btn_caverns(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "caverns")

    @discord.ui.button(label="Ancient Ruins", style=discord.ButtonStyle.danger, emoji="🏛️")
    async def btn_ruins(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "ruins")

    @discord.ui.button(label="Wilderness", style=discord.ButtonStyle.success, emoji="🌲")
    async def btn_wilderness(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "wilderness")


# ==========================================
# MAIN ECONOMY COG (YOUR EXISTING CODE)
# ==========================================
class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_or_create_profile(self, user_id: int) -> dict:
        """Fetches or initializes user profile in MongoDB."""
        if not self.bot.profiles:
            return {"_id": str(user_id), "shards": 0, "crystals": 0, "last_hunt": 0, "last_expedition": 0}
            
        profile = await self.bot.profiles.find_one({"_id": str(user_id)})
        if not profile:
            profile = {
                "_id": str(user_id),
                "shards": 0,
                "crystals": 0,
                "last_hunt": 0,
                "last_expedition": 0
            }
            await self.bot.profiles.insert_one(profile)
        return profile

    @app_commands.command(name="profile", description="Check your ETERNAL faction member card")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        joined_at = user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown"
        
        profile = await self._get_or_create_profile(user.id)
        crystals = profile.get("crystals", 0)
        
        embed = discord.Embed(title=f"⚔️ ETERNAL Member Profile: {user.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Faction Standing", value="**Loyal Member** 🛡️", inline=True)
        embed.add_field(name="Dragon Crystals", value=f"✨ `{crystals}` Crystals", inline=True)
        embed.add_field(name="Arrival Date", value=f"📅 {joined_at}", inline=False)
        # === SAFETY: Command feedback strictly within server channels ===
        await interaction.followup.send(embed=embed)
        # === END SAFETY ===

    # ==========================================
    # 🌟 NEW EXPEDITION COMMAND
    # ==========================================
    @app_commands.command(name="expedition", description="Embark on an interactive journey to find Crystals!")
    async def expedition(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        
        profile = await self._get_or_create_profile(user_id)
        last_expedition = profile.get("last_expedition", 0)
        
        # 2 Hour Cooldown for Expedition (Bigger rewards than hunt, so longer cooldown)
        cooldown_duration = 7200 
        if current_time - last_expedition < cooldown_duration:
            remaining = cooldown_duration - (current_time - last_expedition)
            remaining_mins = int(remaining // 60)
            await interaction.followup.send(f"⛺ You are resting from your last journey. You can launch the next expedition in `{remaining_mins} minutes`.")
            return

        # Update cooldown timestamp in DB
        if self.bot.profiles:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {"$set": {"last_expedition": current_time}},
                upsert=True
            )

        embed = discord.Embed(
            title="⚔️ Choose Your Expedition Path",
            description=(
                "You are leaving the safety of the ETERNAL base to hunt for resources.\n\n"
                "**Where will you go?**\n"
                "⛏️ **Deep Caverns:** High risk, high reward crystal mining.\n"
                "🏛️ **Ancient Ruins:** Explore forgotten monuments and outposts.\n"
                "🌲 **Wilderness:** A safer surface route with steady, modest finds.\n\n"
                "*You have 30 seconds to decide...*"
            ),
            color=discord.Color.dark_theme()
        )
        
        view = ExpeditionView(interaction.user.id, self.bot)
        await interaction.followup.send(embed=embed, view=view)


    # ==========================================
    # ORIGINAL COMMANDS (UNCHANGED)
    # ==========================================
    @app_commands.command(name="hunt", description="Go out on a dynamic dragon hunt to collect crystals!")
    async def hunt(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        
        profile = await self._get_or_create_profile(user_id)
        last_hunt = profile.get("last_hunt", 0)
        
        cooldown_duration = 3600  # 1 hour
        if current_time - last_hunt < cooldown_duration:
            remaining = cooldown_duration - (current_time - last_hunt)
            remaining_mins = int(remaining // 60)
            # === SAFETY: All responses sent via interaction (server channel safe) ===
            await interaction.followup.send(f"🔥 *Growls...* You are exhausted! Wait `{remaining_mins} more minutes`.")
            # === END SAFETY ===
            return
            
        crystals_found = random.randint(15, 50)
        
        if self.bot.profiles:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {
                    "$inc": {"crystals": crystals_found},
                    "$set": {"last_hunt": current_time}
                }
            )
            
        scenarios = [
            f"🐉 You flew into the sky with FlamingDeath and raided an enemy base! Found **{crystals_found}** Crystals! 🔥",
            f"⚔️ You cleared out rogue monsters threatening ETERNAL. Earned **{crystals_found}** Crystals!",
            f"💎 You discovered a hidden crystalline cave! Extracted **{crystals_found}** Crystals!"
        ]
        await interaction.followup.send(random.choice(scenarios))

    @app_commands.command(name="coinflip", description="Bet your crystals on a coin toss!")
    @app_commands.choices(choice=[app_commands.Choice(name="Heads", value="heads"), app_commands.Choice(name="Tails", value="tails")])
    async def coinflip(self, interaction: discord.Interaction, choice: app_commands.Choice[str], bet: int):
        await interaction.response.defer()
        user_id = interaction.user.id
        
        profile = await self._get_or_create_profile(user_id)
        current_balance = profile.get("crystals", 0)
        
        if bet <= 0:
            await interaction.followup.send("🔥 *Grrr...* Bet at least `1 Crystal`!")
            return
        if current_balance < bet:
            await interaction.followup.send(f"🔥 *Growls...* You only have `{current_balance}` Crystals!")
            return
            
        result = random.choice(["heads", "tails"])
        if choice.value == result:
            if self.bot.profiles:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": bet}})
            await interaction.followup.send(f"🪙 **Coinflip:** It's **{result.upper()}**! 🎉 You win **{bet}** Crystals!")
        else:
            if self.bot.profiles:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -bet}})
            await interaction.followup.send(f"🪙 **Coinflip:** It's **{result.upper()}**. 💀 You lost **{bet}** Crystals.")

    @app_commands.command(name="slots", description="Play the Dragon Slot Machine! (Cost: 10 Crystals)")
    async def slots(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        
        profile = await self._get_or_create_profile(user_id)
        current_balance = profile.get("crystals", 0)
        cost = 10
        
        if current_balance < cost:
            await interaction.followup.send(f"🔥 You only have `{current_balance}` Crystals.")
            return
            
        if self.bot.profiles:
            await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -cost}})
            
        items = ["🐉", "💎", "⚔️", "🔥", "🍉"]
        slot1, slot2, slot3 = random.choice(items), random.choice(items), random.choice(items)
        embed = discord.Embed(title="🎰 ETERNAL DRAGON SLOTS 🎰", color=discord.Color.gold())
        embed.description = f"\n> **[ {slot1} | {slot2} | {slot3} ]**\n"
        
        if slot1 == slot2 == slot3:
            if self.bot.profiles:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": 150}})
            embed.add_field(name="🎉 JACKPOT!!! 🎉", value="Matched! Won 150 Crystals!")
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            if self.bot.profiles:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": 30}})
            embed.add_field(name="✨ Small Win! ✨", value="Two matched! Won 30 Crystals!")
        else:
            embed.add_field(name="💀 No Match!", value="Lost 10 Crystals.")
        # === SAFETY: All command output stays in server channels via interaction ===
        await interaction.followup.send(embed=embed)
        # === END SAFETY ===

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
                 
