import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select, Button
import random
import time

# ==========================================
# 1. INTERACTIVE ORACLE DASHBOARD (UI VIEWS)
# ==========================================

class DynamicCategoryButtons(View):
    def __init__(self, category: str):
        super().__init__(timeout=180)
        self.category = category
        self._build_buttons()

    def _build_buttons(self):
        # 1. Treasury & Economy
        if self.category == "Treasury & Economy":
            self.add_item(Button(label="Check Gold", style=discord.ButtonStyle.primary, custom_id="btn_gold", emoji="💳"))
            self.add_item(Button(label="Daily Loot", style=discord.ButtonStyle.success, custom_id="btn_daily", emoji="🎁"))
            self.add_item(Button(label="Work Quest", style=discord.ButtonStyle.secondary, custom_id="btn_work", emoji="💼"))
            self.add_item(Button(label="Flamy Market", style=discord.ButtonStyle.secondary, custom_id="btn_market", emoji="🛒"))
            self.add_item(Button(label="Inventory", style=discord.ButtonStyle.secondary, custom_id="btn_inv", emoji="🎒"))
            self.add_item(Button(label="Vault Deposit", style=discord.ButtonStyle.secondary, custom_id="btn_vault", emoji="🏦"))
            
        # 2. Lair Challenges
        elif self.category == "Lair Mini-Games":
            self.add_item(Button(label="Flame Roll", style=discord.ButtonStyle.primary, custom_id="btn_roll", emoji="🪙"))
            self.add_item(Button(label="Slot Blaze", style=discord.ButtonStyle.danger, custom_id="btn_slots", emoji="🎰"))
            self.add_item(Button(label="Flame Cards", style=discord.ButtonStyle.primary, custom_id="btn_cards", emoji="🎴"))
            self.add_item(Button(label="River Fish", style=discord.ButtonStyle.success, custom_id="btn_fish", emoji="🎣"))
            self.add_item(Button(label="High-Low", style=discord.ButtonStyle.secondary, custom_id="btn_highlow", emoji="🎯"))
            self.add_item(Button(label="Crime Risk", style=discord.ButtonStyle.danger, custom_id="btn_crime", emoji="🪓"))

        # 3. XP & Rank System
        elif self.category == "XP & Rank System":
            self.add_item(Button(label="View Rank", style=discord.ButtonStyle.primary, custom_id="btn_rank", emoji="🎖️"))
            self.add_item(Button(label="Leaderboard", style=discord.ButtonStyle.success, custom_id="btn_lb", emoji="🏆"))
            self.add_item(Button(label="Rank Roles", style=discord.ButtonStyle.secondary, custom_id="btn_rankroles", emoji="🏅"))
            self.add_item(Button(label="XP Settings", style=discord.ButtonStyle.secondary, custom_id="btn_xpsettings", emoji="⚙️"))

        # 4. Roles Management
        elif self.category == "Roles Management":
            self.add_item(Button(label="Check Wings", style=discord.ButtonStyle.secondary, custom_id="btn_wings", emoji="📜"))
            self.add_item(Button(label="Select Role", style=discord.ButtonStyle.primary, custom_id="btn_roleselect", emoji="🎖️"))
            self.add_item(Button(label="Claim Event Role", style=discord.ButtonStyle.success, custom_id="btn_claimrole", emoji="🎁"))

        # 5. Utility & Info
        elif self.category == "Utility & Info":
            self.add_item(Button(label="Profile & Stats", style=discord.ButtonStyle.primary, custom_id="btn_profile", emoji="👤"))
            self.add_item(Button(label="Faction Stats", style=discord.ButtonStyle.secondary, custom_id="btn_facstats", emoji="📊"))
            self.add_item(Button(label="Avatar", style=discord.ButtonStyle.secondary, custom_id="btn_avatar", emoji="🖼️"))
            self.add_item(Button(label="Flamy Ping", style=discord.ButtonStyle.primary, custom_id="btn_ping", emoji="📶"))

        # 6. Flamy AI Chat & Fun
        elif self.category == "Flamy AI & Fun":
            self.add_item(Button(label="Ask Flamy AI", style=discord.ButtonStyle.primary, custom_id="btn_ai_ask", emoji="🤖"))
            self.add_item(Button(label="Flame Roast", style=discord.ButtonStyle.danger, custom_id="btn_roast", emoji="🔥"))
            self.add_item(Button(label="Flamy Match", style=discord.ButtonStyle.success, custom_id="btn_match", emoji="💕"))
            self.add_item(Button(label="Quick Calc", style=discord.ButtonStyle.secondary, custom_id="btn_calc", emoji="🧮"))

class OracleSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Treasury & Economy", emoji="💰", description="Gold, Vault, Market & Daily Loot"),
            discord.SelectOption(label="Lair Mini-Games", emoji="🎲", description="Slots, Cards, Roll & Trivia"),
            discord.SelectOption(label="XP & Rank System", emoji="📈", description="Rank, Leaderboards & XP Settings"),
            discord.SelectOption(label="Roles Management", emoji="🛡️", description="Assign & Claim Faction Roles"),
            discord.SelectOption(label="Utility & Info", emoji="⚙️", description="Server Stats, Ping & Profile"),
            discord.SelectOption(label="Flamy AI & Fun", emoji="🔥", description="Ask Gemini AI, Roasts & Fun Tools"),
        ]
        super().__init__(placeholder="Choose a category to open controls...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = discord.Embed(
            title=f"🔥 Flamy Control Panel | {category}",
            color=discord.Color.dark_theme()
        )
        
        if category == "Treasury & Economy":
            embed.description = "Select an action below to manage your crystal hoard, claim rewards, or trade."
        elif category == "Lair Mini-Games":
            embed.description = "Choose a mini-game to risk your crystals and win big rewards!"
        elif category == "XP & Rank System":
            embed.description = "Track your standing within the Eternal faction."
        elif category == "Roles Management":
            embed.description = "Manage your wings and specialized faction roles."
        elif category == "Utility & Info":
            embed.description = "Access essential server information and member stats."
        elif category == "Flamy AI & Fun":
            embed.description = "Interact with Flamy's AI engine for answers and entertainment."

        view = DynamicCategoryButtons(category)
        await interaction.response.edit_message(embed=embed, view=view)

    
class OracleDashboardView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(OracleSelect())

# ==========================================
# 2. MAIN ECONOMY & ORACLE COG
# ==========================================

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_or_create_profile(self, user_id: int) -> dict:
        default_profile = {
            "_id": str(user_id), 
            "crystals": 0, 
            "last_work": 0,
            "last_daily": 0,
            "last_crime": 0,
            "daily_streak": 0
        }
        if self.bot.profiles is None: return default_profile
        profile = await self.bot.profiles.find_one({"_id": str(user_id)})
        if not profile:
            await self.bot.profiles.insert_one(default_profile)
            return default_profile
        return profile

    @app_commands.command(name="flamy-oracle", description="Open the main interactive UI control dashboard")
    async def flamy_oracle(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🐉 Eternal Faction Control Dashboard",
            description="Select a category from the drop-down menu below to access Flamy's features seamlessly.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=OracleDashboardView())

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id")
            
            # Treasury Routing
            if custom_id in ["btn_gold", "btn_profile"]:
                await interaction.response.send_message("💡 Quick Tip: Use `/profile` to view your full card!", ephemeral=True)
            elif custom_id == "btn_daily":
                await interaction.response.send_message("🎁 Claim your daily rewards using `/daily`!", ephemeral=True)
            elif custom_id == "btn_work":
                await interaction.response.send_message("💼 Start your shift using `/work`!", ephemeral=True)
            
            # Games Routing
            elif custom_id == "btn_slots":
                await interaction.response.send_message("🎰 Play dragon slots using `/slots`!", ephemeral=True)
            elif custom_id == "btn_crime":
                await interaction.response.send_message("🪓 Attempt a risky crime using `/crime`!", ephemeral=True)
            
            # Info Routing
            elif custom_id == "btn_lb":
                await interaction.response.send_message("🏆 View top players using `/leaderboard`!", ephemeral=True)
            elif custom_id == "btn_ai_ask":
                await interaction.response.send_message("🤖 Mention the bot or chat directly in the designated AI channel!", ephemeral=True)
            
            # Placeholder for unlinked buttons
            elif custom_id in ["btn_market", "btn_inv", "btn_vault", "btn_roll", "btn_cards", "btn_fish", "btn_highlow", "btn_rank", "btn_rankroles", "btn_xpsettings", "btn_wings", "btn_roleselect", "btn_claimrole", "btn_facstats", "btn_avatar", "btn_ping", "btn_roast", "btn_match", "btn_calc"]:
                await interaction.response.send_message("🚧 **This feature is currently under construction for the Eternal faction!** Check back soon.", ephemeral=True)

    @app_commands.command(name="profile", description="Check your Eternal faction member card")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        joined_at = user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown"
        profile = await self._get_or_create_profile(user.id)
        
        embed = discord.Embed(title=f"⚔️ Eternal Member Profile: {user.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Dragon Crystals", value=f"✨ `{profile.get('crystals', 0)}` Crystals", inline=True)
        embed.add_field(name="Daily Streak", value=f"🔥 `{profile.get('daily_streak', 0)}` Days", inline=True)
        embed.add_field(name="Arrival Date", value=f"📅 {joined_at}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="daily", description="Claim your daily faction rations and crystals!")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        profile = await self._get_or_create_profile(user_id)
        
        last_daily = profile.get("last_daily", 0)
        time_since_last = current_time - last_daily
        
        if time_since_last < 86400 and last_daily != 0:
            remaining = int((86400 - time_since_last) // 3600)
            remaining_mins = int(((86400 - time_since_last) % 3600) // 60)
            await interaction.followup.send(f"⏳ You have already claimed your daily rations! Come back in `{remaining}h {remaining_mins}m`.")
            return

        streak = profile.get("daily_streak", 0) if time_since_last <= 172800 else 0
        streak += 1
        total_reward = 100 + min(streak * 10, 200)

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {"$inc": {"crystals": total_reward}, "$set": {"last_daily": current_time, "daily_streak": streak}},
                upsert=True
            )
        embed = discord.Embed(title="🎁 Daily Faction Rations Claimed!", description=f"You received **✨ {total_reward} Crystals**!\nCurrent Streak: 🔥 `{streak}` Days", color=discord.Color.green())
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="work", description="Complete a quick task for the Eternal faction to earn crystals.")
    async def work(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        profile = await self._get_or_create_profile(user_id)
        
        if current_time - profile.get("last_work", 0) < 600:
            remaining_mins = int((600 - (current_time - profile.get("last_work", 0))) // 60)
            await interaction.followup.send(f"🛡️ You are resting. Wait `{remaining_mins} minutes`.")
            return

        reward = random.randint(25, 65)
        if self.bot.profiles is not None:
            await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": reward}, "$set": {"last_work": current_time}}, upsert=True)

        jobs = [
            f"🧱 You helped construct a massive new wing of the base. Earned ✨ **{reward} Crystals**.",
            f"🐲 You polished the scales of the Dragon statue. Earned ✨ **{reward} Crystals**.",
            f"⛏️ You spent the shift strip-mining in the caves. Earned ✨ **{reward} Crystals**."
        ]
        await interaction.followup.send(random.choice(jobs))

    @app_commands.command(name="crime", description="Commit a risky crime for a massive payout.")
    async def crime(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        profile = await self._get_or_create_profile(user_id)
        
        if current_time - profile.get("last_crime", 0) < 2700:
            await interaction.followup.send("🚓 The heat is too high. Try again later.")
            return

        if random.random() < 0.45:
            reward = random.randint(150, 400)
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": reward}, "$set": {"last_crime": current_time}}, upsert=True)
            await interaction.followup.send(f"💰 **Crime Pays!** Stole ✨ **{reward} Crystals**!")
        else:
            fine = random.randint(100, 250)
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -fine}, "$set": {"last_crime": current_time}}, upsert=True)
            await interaction.followup.send(f"🚨 **Caught!** You were fined ✨ **{fine} Crystals**.")

    @app_commands.command(name="slots", description="Play the Dragon Slot Machine!")
    async def slots(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        profile = await self._get_or_create_profile(user_id)
        
        if profile.get("crystals", 0) < 10:
            await interaction.followup.send("🔥 You need at least 10 Crystals to play.")
            return
            
        if self.bot.profiles is not None:
            await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -10}}, upsert=True)
            
        items = ["🐉", "💎", "⚔️", "🔥", "🍉"]
        s1, s2, s3 = random.choice(items), random.choice(items), random.choice(items)
        embed = discord.Embed(title="🎰 Eternal DRAGON SLOTS 🎰", description=f"\n> **[ {s1} | {s2} | {s3} ]**\n", color=discord.Color.blue())
        
        if s1 == s2 == s3:
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": 150}}, upsert=True)
            embed.add_field(name="🎉 JACKPOT!", value="Won 150 Crystals!")
        elif s1 == s2 or s2 == s3 or s1 == s3:
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": 30}}, upsert=True)
            embed.add_field(name="✨ Small Win!", value="Won 30 Crystals!")
        else:
            embed.add_field(name="💀 No Match!", value="Lost 10 Crystals.")
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
            embed = discord.Embed(title="🏆 Eternal Faction Leaderboard", color=discord.Color.gold())
            
            leaderboard_text = ""
            for index, user_data in enumerate(top_users, start=1):
                user_id = user_data.get("_id")
                crystals = user_data.get("crystals", 0)
                rank_str = ["🥇", "🥈", "🥉"][index - 1] if index <= 3 else f"`#{index}`"
                leaderboard_text += f"{rank_str} <@{user_id}> — ✨ **{crystals:,}**\n"

            embed.description = leaderboard_text or "📜 *No crystal hoarders found in the faction database yet!*"
            await interaction.followup.send(embed=embed)
        except Exception:
            await interaction.followup.send("❌ *An error occurred while loading the ranks.*", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
        
