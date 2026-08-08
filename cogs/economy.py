import random
import time
import discord
from discord import app_commands
from discord.ext import commands

# ==========================================
# 🌟 HIGH-LOW MINI-GAME UI (Pancake Style)
# ==========================================
class HighLowView(discord.ui.View):
    def __init__(self, user_id: int, bet: int, hint_number: int, bot):
        super().__init__(timeout=30.0)
        self.user_id = user_id
        self.bet = bet
        self.hint_number = hint_number
        self.bot = bot
        self.secret_number = random.randint(1, 100)
        self.chosen = False

    async def handle_choice(self, interaction: discord.Interaction, choice: str):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your game! Start your own with `/highlow`.", ephemeral=True)
            return

        if self.chosen:
            return

        self.chosen = True
        for child in self.children:
            child.disabled = True

        won = False
        if choice == "higher" and self.secret_number > self.hint_number:
            won = True
        elif choice == "lower" and self.secret_number < self.hint_number:
            won = True
        elif choice == "jackpot" and self.secret_number == self.hint_number:
            won = True

        if won:
            multiplier = 10 if choice == "jackpot" else 2
            winnings = self.bet * multiplier
            
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one(
                    {"_id": str(self.user_id)},
                    {"$inc": {"crystals": winnings - self.bet}},
                    upsert=True
                )
            
            embed = discord.Embed(
                title="📈 High-Low Results: VICTORY!", 
                description=f"The secret number was **{self.secret_number}**!\n\nYou guessed **{choice.upper()}** and won ✨ **{winnings} Crystals**!", 
                color=discord.Color.teal()
            )
        else:
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one(
                    {"_id": str(self.user_id)},
                    {"$inc": {"crystals": -self.bet}},
                    upsert=True
                )
                
            embed = discord.Embed(
                title="📉 High-Low Results: DEFEAT!", 
                description=f"The secret number was **{self.secret_number}**!\n\nYou guessed **{choice.upper()}** and lost your bet of ✨ **{self.bet} Crystals**.", 
                color=discord.Color.red()
            )

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Higher", style=discord.ButtonStyle.success, emoji="⬆️")
    async def btn_higher(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "higher")

    @discord.ui.button(label="Jackpot", style=discord.ButtonStyle.primary, emoji="🎯")
    async def btn_jackpot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "jackpot")

    @discord.ui.button(label="Lower", style=discord.ButtonStyle.danger, emoji="⬇️")
    async def btn_lower(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "lower")


# ==========================================
# 🌟 INTERACTIVE EXPEDITION UI
# ==========================================
class ExpeditionView(discord.ui.View):
    def __init__(self, user_id: int, bot):
        super().__init__(timeout=30.0) 
        self.user_id = user_id
        self.bot = bot
        self.chosen = False

    async def handle_choice(self, interaction: discord.Interaction, choice_type: str):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your expedition! Start your own with `/play`.", ephemeral=True)
            return

        if self.chosen:
            return

        self.chosen = True
        
        for child in self.children:
            child.disabled = True

        events = {
            "caverns": [
                {"text": "⛏️ You mined deep into an abandoned mineshaft and discovered rare crystals!", "crystals": random.randint(40, 80), "color": discord.Color.teal()},
                {"text": "⛏️ Your pickaxe broke on some bedrock. You returned empty-handed.", "crystals": 0, "color": discord.Color.light_grey()},
                {"text": "⛏️ You stumbled upon a glowing Sky-Blue Crystal Cavern! The energy here is immense.", "crystals": random.randint(150, 250), "color": discord.Color.teal()}
            ],
            "ruins": [
                {"text": "🏛️ You explored an old rival outpost and secured some abandoned treasury supplies.", "crystals": random.randint(50, 100), "color": discord.Color.green()},
                {"text": "🏛️ You triggered a harmless tripwire! A net dropped on you, delaying your search. You found nothing.", "crystals": 0, "color": discord.Color.orange()},
                {"text": "🏛️ Jackpot! You unearthed a hidden relic of the Faceless Dragon. The Eternal treasury will be pleased!", "crystals": random.randint(200, 350), "color": discord.Color.gold()}
            ],
            "wilderness": [
                {"text": "🌲 You foraged in a server wilderness and found some scattered crystal fragments.", "crystals": random.randint(20, 50), "color": discord.Color.dark_green()},
                {"text": "🌲 You got lost in a dense forest and spent the whole day just finding your way back to base.", "crystals": 0, "color": discord.Color.dark_grey()},
                {"text": "🌲 A wandering merchant traded you a pouch of crystals for your travel rations!", "crystals": random.randint(80, 150), "color": discord.Color.purple()}
            ]
        }

        scenario = random.choice(events[choice_type])
        reward = scenario["crystals"]
        
        if reward > 0 and self.bot.profiles is not None:
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
# MAIN ECONOMY COG
# ==========================================
class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_or_create_profile(self, user_id: int) -> dict:
        default_profile = {
            "_id": str(user_id), 
            "crystals": 0, 
            "last_hunt": 0, 
            "last_expedition": 0,
            "last_work": 0,
            "last_daily": 0,
            "last_crime": 0,
            "daily_streak": 0
        }

        if self.bot.profiles is None:
            return default_profile
            
        profile = await self.bot.profiles.find_one({"_id": str(user_id)})
        if not profile:
            await self.bot.profiles.insert_one(default_profile)
            return default_profile
        return profile

    @app_commands.command(name="profile", description="Check your Eternal faction member card")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        joined_at = user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown"
        
        profile = await self._get_or_create_profile(user.id)
        crystals = profile.get("crystals", 0)
        streak = profile.get("daily_streak", 0)
        
        embed = discord.Embed(title=f"⚔️ Eternal Member Profile: {user.name}", color=discord.Color.teal())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Dragon Crystals", value=f"✨ `{crystals}` Crystals", inline=True)
        embed.add_field(name="Daily Streak", value=f"🔥 `{streak}` Days", inline=True)
        embed.add_field(name="Arrival Date", value=f"📅 {joined_at}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="leaderboard", description="View the top dragon crystal hoarders in Eternal!")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.bot.profiles is None:
            await interaction.followup.send("❌ Database connection is currently unavailable.", ephemeral=True)
            return

        try:
            cursor = self.bot.profiles.find().sort("crystals", -1).limit(10)
            top_users = await cursor.to_list(length=10)

            if not top_users:
                await interaction.followup.send("📜 *No crystal hoarders found in the faction database yet!*")
                return

            embed = discord.Embed(
                title="🏆 Eternal Faction Leaderboard",
                color=discord.Color.gold()
            )

            leaderboard_text = ""
            for index, user_data in enumerate(top_users, start=1):
                user_id = user_data.get("_id")
                crystals = user_data.get("crystals", 0)
                rank_str = ["🥇", "🥈", "🥉"][index - 1] if index <= 3 else f"`#{index}`"
                leaderboard_text += f"{rank_str} <@{user_id}> — ✨ **{crystals:,}**\n"

            embed.description = leaderboard_text
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send("❌ *An error occurred while loading the ranks.*", ephemeral=True)

    # ==========================================
    # 💰 CORE ECONOMY (Daily & Work)
    # ==========================================
    @app_commands.command(name="daily", description="Claim your daily faction rations and crystals!")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        
        profile = await self._get_or_create_profile(user_id)
        last_daily = profile.get("last_daily", 0)
        streak = profile.get("daily_streak", 0)
        
        time_since_last = current_time - last_daily
        
        if time_since_last < 86400 and last_daily != 0:
            remaining = int((86400 - time_since_last) // 3600)
            remaining_mins = int(((86400 - time_since_last) % 3600) // 60)
            await interaction.followup.send(f"⏳ You have already claimed your daily rations! Come back in `{remaining}h {remaining_mins}m`.")
            return

        if time_since_last > 172800 and last_daily != 0:
            streak = 0
            
        streak += 1
        base_reward = 100
        streak_bonus = min(streak * 10, 200)
        total_reward = base_reward + streak_bonus

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {
                    "$inc": {"crystals": total_reward},
                    "$set": {"last_daily": current_time, "daily_streak": streak}
                },
                upsert=True
            )

        embed = discord.Embed(
            title="🎁 Daily Faction Rations Claimed!",
            description=f"You received your daily allowance of **✨ {total_reward} Crystals**!",
            color=discord.Color.teal()
        )
        embed.add_field(name="Base Reward", value=f"✨ {base_reward}", inline=True)
        embed.add_field(name="Streak Bonus", value=f"✨ +{streak_bonus}", inline=True)
        embed.add_field(name="Current Streak", value=f"🔥 {streak} Days", inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="work", description="Complete a quick task for the Eternal faction to earn crystals.")
    async def work(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        
        profile = await self._get_or_create_profile(user_id)
        last_work = profile.get("last_work", 0)
        
        cooldown = 600 
        if current_time - last_work < cooldown:
            remaining_mins = int((cooldown - (current_time - last_work)) // 60)
            remaining_secs = int((cooldown - (current_time - last_work)) % 60)
            await interaction.followup.send(f"🛡️ You are still recovering from your last shift. Wait `{remaining_mins}m {remaining_secs}s`.")
            return

        reward = random.randint(25, 65)
        if self.bot.profiles is not None:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {"$inc": {"crystals": reward}, "$set": {"last_work": current_time}},
                upsert=True
            )

        jobs = [
            f"🧱 You helped construct a massive new wing of the base on a server. You earned ✨ **{reward} Crystals**.",
            f"🐲 You fed and cleaned the scales of the Faceless Dragon statue. The faction pays you ✨ **{reward} Crystals**.",
            f"⛏️ You spent the shift strip-mining in the Minetest caves and found ✨ **{reward} Crystals**.",
            f"⚔️ You successfully defended the perimeter from a rogue mob attack. You were rewarded ✨ **{reward} Crystals**."
        ]
        
        await interaction.followup.send(random.choice(jobs))

    # ==========================================
    # 🦹 PLAYER INTERACTION & CRIME
    # ==========================================
    @app_commands.command(name="give", description="Transfer your Dragon Crystals to another faction member.")
    @app_commands.describe(member="The member receiving the crystals", amount="Amount to transfer")
    async def give(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await interaction.response.defer()
        sender_id = interaction.user.id
        receiver_id = member.id

        if sender_id == receiver_id:
            await interaction.followup.send("❌ You cannot give crystals to yourself!")
            return
            
        if member.bot:
            await interaction.followup.send("❌ Bots have no need for mortal currencies.")
            return

        if amount <= 0:
            await interaction.followup.send("❌ You must give at least `1 Crystal`.")
            return

        sender_profile = await self._get_or_create_profile(sender_id)
        sender_balance = sender_profile.get("crystals", 0)

        if sender_balance < amount:
            await interaction.followup.send(f"❌ You lack the funds! You only have `{sender_balance}` Crystals.")
            return

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one(
                {"_id": str(sender_id)},
                {"$inc": {"crystals": -amount}},
                upsert=True
            )
            await self.bot.profiles.update_one(
                {"_id": str(receiver_id)},
                {"$inc": {"crystals": amount}},
                upsert=True
            )

        embed = discord.Embed(
            title="💸 Crystals Transferred!",
            description=f"**{interaction.user.display_name}** generously gifted ✨ **{amount} Crystals** to {member.mention}!",
            color=discord.Color.green()
        )
        await interaction.followup.send(content=member.mention, embed=embed)

    @app_commands.command(name="crime", description="Commit a risky crime for a massive payout.")
    async def crime(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        
        profile = await self._get_or_create_profile(user_id)
        last_crime = profile.get("last_crime", 0)
        current_balance = profile.get("crystals", 0)
        
        cooldown = 2700 
        if current_time - last_crime < cooldown:
            remaining_mins = int((cooldown - (current_time - last_crime)) // 60)
            await interaction.followup.send(f"🚓 The heat is too high. Wait `{remaining_mins} minutes` before committing another crime.")
            return

        if current_balance < 100:
            await interaction.followup.send("❌ You need at least `100 Crystals` to cover potential fines before attempting a crime!")
            return

        success = random.random() < 0.45

        if success:
            reward = random.randint(150, 400)
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one(
                    {"_id": str(user_id)},
                    {"$inc": {"crystals": reward}, "$set": {"last_crime": current_time}},
                    upsert=True
                )
                
            scenarios = [
                f"💻 You hacked into a rival faction's database and stole their crystal coordinates! Earned ✨ **{reward}**.",
                f"🏴‍☠️ You successfully smuggled illegal redstone components past the server admins. Paid ✨ **{reward}**.",
                f"🐉 You siphoned raw energy from the Faceless Dragon statue and sold it on the black market for ✨ **{reward}**."
            ]
            embed = discord.Embed(title="💰 Crime Pays!", description=random.choice(scenarios), color=discord.Color.green())
            await interaction.followup.send(embed=embed)
        else:
            fine = random.randint(100, 250)
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one(
                    {"_id": str(user_id)},
                    {"$inc": {"crystals": -fine}, "$set": {"last_crime": current_time}},
                    upsert=True
                )

            scenarios = [
                f"🚨 A server admin caught you griefing! You were fined ✨ **{fine}**.",
                f"💥 The contraband TNT you were smuggling exploded in your inventory. Lost ✨ **{fine}** in damages.",
                f"🚓 The Eternal guards caught you trespassing in the treasury. Fined ✨ **{fine}**."
            ]
            embed = discord.Embed(title="🚔 Caught Red-Handed!", description=random.choice(scenarios), color=discord.Color.red())
            await interaction.followup.send(embed=embed)

    # ==========================================
    # 🎲 FACTION MINI-GAMES
    # ==========================================
    @app_commands.command(name="highlow", description="Gamble crystals! Guess if the secret number is Higher or Lower.")
    @app_commands.describe(bet="Amount of crystals to bet")
    async def highlow(self, interaction: discord.Interaction, bet: int):
        await interaction.response.defer()
        user_id = interaction.user.id
        
        profile = await self._get_or_create_profile(user_id)
        current_balance = profile.get("crystals", 0)
        
        if bet < 10:
            await interaction.followup.send("❌ The minimum bet for High-Low is `10 Crystals`.")
            return
        if current_balance < bet:
            await interaction.followup.send(f"❌ You don't have enough! You only possess `{current_balance}` Crystals.")
            return

        hint_number = random.randint(10, 90)
        
        embed = discord.Embed(
            title="🎲 High-Low Mini-game",
            description=(
                f"I have chosen a secret number between 1 and 100.\n\n"
                f"The hint number is: **{hint_number}**\n\n"
                f"Is the secret number **Higher** or **Lower** than the hint? (Or risk it all on an exact Jackpot match?)"
            ),
            color=discord.Color.teal()
        )
        
        view = HighLowView(user_id, bet, hint_number, self.bot)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="play", description="Embark on an interactive journey to find Crystals!")
    async def play(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        
        profile = await self._get_or_create_profile(user_id)
        last_expedition = profile.get("last_expedition", 0)
        
        cooldown_duration = 3600 
        if current_time - last_expedition < cooldown_duration:
            remaining = cooldown_duration - (current_time - last_expedition)
            remaining_mins = int(remaining // 60)
            await interaction.followup.send(f"⛺ You are resting. You can launch the next expedition in `{remaining_mins} minutes`.")
            return

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {"$set": {"last_expedition": current_time}},
                upsert=True
            )

        embed = discord.Embed(
            title="⚔️ Choose Your Expedition Path",
            description=(
                "**Where will you go?**\n"
                "⛏️ **Deep Caverns:** High risk, high reward.\n"
                "🏛️ **Ancient Ruins:** Explore forgotten monuments.\n"
                "🌲 **Wilderness:** Steady, modest finds.\n\n"
                "*You have 30 seconds to decide...*"
            ),
            color=discord.Color.dark_theme()
        )
        
        view = ExpeditionView(interaction.user.id, self.bot)
        await interaction.followup.send(embed=embed, view=view)

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
            
        if self.bot.profiles is not None:
            await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -cost}}, upsert=True)
            
        items = ["🐉", "💎", "⚔️", "🔥", "🍉"]
        slot1, slot2, slot3 = random.choice(items), random.choice(items), random.choice(items)
        embed = discord.Embed(title="🎰 Eternal DRAGON SLOTS 🎰", color=discord.Color.gold())
        embed.description = f"\n> **[ {slot1} | {slot2} | {slot3} ]**\n"
        
        if slot1 == slot2 == slot3:
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": 150}}, upsert=True)
            embed.add_field(name="🎉 JACKPOT!!! 🎉", value="Matched! Won 150 Crystals!")
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": 30}}, upsert=True)
            embed.add_field(name="✨ Small Win! ✨", value="Two matched! Won 30 Crystals!")
        else:
            embed.add_field(name="💀 No Match!", value="Lost 10 Crystals.")
        await interaction.followup.send(embed=embed)

    # ==========================================
    # 🛡️ ADMIN REWARD COMMANDS
    # ==========================================
    @app_commands.command(name="give_everyone", description="Admin: Bestow Dragon Crystals upon the entire faction.")
    @app_commands.describe(amount="Amount of crystals")
    async def give_everyone(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)

        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ You lack the authority.", ephemeral=True)
            return

        if amount <= 0:
            return await interaction.followup.send("❌ Amount must be greater than 0!", ephemeral=True)

        if self.bot.profiles is not None:
            await self.bot.profiles.update_many({}, {"$inc": {"crystals": amount}}, upsert=True)

        embed = discord.Embed(
            title="🔥 THE DRAGON HAS SPOKEN! 🔥",
            description=f"**@everyone**\n\nI have bestowed **✨ {amount} Dragon Crystals** upon every soul in this realm.",
            color=discord.Color.red() 
        )
        await interaction.channel.send(content="@everyone", embed=embed)
        await interaction.followup.send(f"✅ Distributed {amount} crystals to everyone.", ephemeral=True)

    @app_commands.command(name="give_player", description="Admin: Bestow Dragon Crystals upon a specific soul.")
    @app_commands.describe(member="The player", amount="Amount of crystals")
    async def give_player(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await interaction.response.defer(ephemeral=True)

        if not interaction.user.guild_permissions.administrator:
            return await interaction.followup.send("❌ You lack the authority.", ephemeral=True)

        if amount <= 0:
            return await interaction.followup.send("❌ Amount must be greater than 0!", ephemeral=True)

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one({"_id": str(member.id)}, {"$inc": {"crystals": amount}}, upsert=True)

        embed = discord.Embed(
            title="🔥 A DRAGON'S BLESSING! 🔥",
            description=f"Hear me, {member.mention}!\n\nI bestow upon you **✨ {amount} Dragon Crystals**.",
            color=discord.Color.red() 
        )
        await interaction.channel.send(content=member.mention, embed=embed)
        await interaction.followup.send(f"✅ Distributed {amount} crystals to {member.display_name}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
