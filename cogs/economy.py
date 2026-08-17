import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select, Button
import random
import time
import ast
import operator

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
# 1b. SELF-ASSIGNABLE ROLE SELECT VIEW
# ==========================================

class SelfRoleSelect(Select):
    def __init__(self, roles: list):
        options = [
            discord.SelectOption(label=role.name[:100], value=str(role.id), emoji="🏷️")
            for role in roles[:25]
        ]
        super().__init__(placeholder="Choose a role to toggle...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)
        if role is None:
            await interaction.response.send_message("❌ That role no longer exists.", ephemeral=True)
            return

        member = interaction.user
        if role in member.roles:
            await member.remove_roles(role, reason="Self-role toggle via Flamy Oracle")
            await interaction.response.send_message(f"➖ Removed **{role.name}** from your wings.", ephemeral=True)
        else:
            await member.add_roles(role, reason="Self-role toggle via Flamy Oracle")
            await interaction.response.send_message(f"➕ Added **{role.name}** to your wings.", ephemeral=True)


class SelfRoleView(View):
    def __init__(self, roles: list):
        super().__init__(timeout=180)
        self.add_item(SelfRoleSelect(roles))


# ==========================================
# 2. MAIN ECONOMY & ORACLE COG
# ==========================================

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldowns = {}

    async def _get_or_create_profile(self, user_id: int) -> dict:
        default_profile = {
            "_id": str(user_id),
            "crystals": 0,
            "vault": 0,
            "xp": 0,
            "inventory": [],
            "last_work": 0,
            "last_daily": 0,
            "last_crime": 0,
            "last_fish": 0,
            "daily_streak": 0
        }
        if self.bot.profiles is None:
            return default_profile
        profile = await self.bot.profiles.find_one({"_id": str(user_id)})
        if not profile:
            await self.bot.profiles.insert_one(default_profile)
            return default_profile
        return profile

    async def _get_guild_config(self, guild_id: int) -> dict:
        default_config = {
            "_id": str(guild_id),
            "xp_min": 5,
            "xp_max": 15,
            "xp_cooldown": 60,
            "rank_roles": {},
            "self_roles": [],
            "event_roles": {}
        }
        configs = getattr(self.bot, "guild_configs", None)
        if configs is None:
            return default_config
        config = await configs.find_one({"_id": str(guild_id)})
        if not config:
            await configs.insert_one(default_config)
            return default_config
        return config

    @staticmethod
    def calculate_level(xp: int) -> int:
        return int(xp // 500)

    @staticmethod
    def xp_for_level(level: int) -> int:
        return (level + 1) * 500

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
            if custom_id == "btn_gold":
                await interaction.response.send_message("💡 Quick Tip: Use `/profile` to view your full card!", ephemeral=True)
            elif custom_id == "btn_profile":
                await interaction.response.send_message("💡 Quick Tip: Use `/profile` to view your full card!", ephemeral=True)
            elif custom_id == "btn_daily":
                await interaction.response.send_message("🎁 Claim your daily rewards using `/daily`!", ephemeral=True)
            elif custom_id == "btn_work":
                await interaction.response.send_message("💼 Start your shift using `/work`!", ephemeral=True)
            elif custom_id == "btn_market":
                await interaction.response.send_message("🛒 Browse the market using `/shop`!", ephemeral=True)
            elif custom_id == "btn_inv":
                await interaction.response.send_message("🎒 Check your bag using `/inventory`!", ephemeral=True)
            elif custom_id == "btn_vault":
                await interaction.response.send_message("🏦 Manage your savings using `/vault balance`, `/vault deposit` or `/vault withdraw`!", ephemeral=True)

            # Games Routing
            elif custom_id == "btn_slots":
                await interaction.response.send_message("🎰 Play dragon slots using `/slots`!", ephemeral=True)
            elif custom_id == "btn_crime":
                await interaction.response.send_message("🪓 Attempt a risky crime using `/crime`!", ephemeral=True)
            elif custom_id == "btn_roll":
                await interaction.response.send_message("🪙 Try your luck using `/roll`!", ephemeral=True)
            elif custom_id == "btn_cards":
                await interaction.response.send_message("🎴 Draw against Flamy using `/cards`!", ephemeral=True)
            elif custom_id == "btn_fish":
                await interaction.response.send_message("🎣 Cast your line using `/fish`!", ephemeral=True)
            elif custom_id == "btn_highlow":
                await interaction.response.send_message("🎯 Guess the number using `/highlow`!", ephemeral=True)

            # Rank/XP Routing
            elif custom_id == "btn_rank":
                await interaction.response.send_message("🎖️ Check your standing using `/rank`!", ephemeral=True)
            elif custom_id == "btn_lb":
                await interaction.response.send_message("🏆 View top players using `/leaderboard`!", ephemeral=True)
            elif custom_id == "btn_rankroles":
                await interaction.response.send_message("🏅 View or configure rewards using `/rankroles list` (admins can use `/rankroles set`)!", ephemeral=True)
            elif custom_id == "btn_xpsettings":
                await interaction.response.send_message("⚙️ Admins can tune XP gain using `/xpsettings`!", ephemeral=True)

            # Roles Routing
            elif custom_id == "btn_wings":
                await interaction.response.send_message("📜 View your roles using `/wings`!", ephemeral=True)
            elif custom_id == "btn_roleselect":
                await interaction.response.send_message("🎖️ Open the role picker using `/roleselect`!", ephemeral=True)
            elif custom_id == "btn_claimrole":
                await interaction.response.send_message("🎁 Claim an event role using `/claimrole <code>`!", ephemeral=True)

            # Utility Routing
            elif custom_id == "btn_facstats":
                await interaction.response.send_message("📊 View server stats using `/facstats`!", ephemeral=True)
            elif custom_id == "btn_avatar":
                await interaction.response.send_message("🖼️ View avatars using `/avatar`!", ephemeral=True)
            elif custom_id == "btn_ping":
                await interaction.response.send_message("📶 Check latency using `/ping`!", ephemeral=True)

            # Fun Routing
            elif custom_id == "btn_ai_ask":
                await interaction.response.send_message("🤖 Mention the bot or chat directly in the designated AI channel!", ephemeral=True)
            elif custom_id == "btn_roast":
                await interaction.response.send_message("🔥 Roast a friend using `/roast <member>`!", ephemeral=True)
            elif custom_id == "btn_match":
                await interaction.response.send_message("💕 Test your compatibility using `/match <member>`!", ephemeral=True)
            elif custom_id == "btn_calc":
                await interaction.response.send_message("🧮 Crunch numbers using `/calc <expression>`!", ephemeral=True)
                

    @app_commands.command(name="profile", description="Check your Eternal faction member card")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        joined_at = user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown"
        profile = await self._get_or_create_profile(user.id)
        level = self.calculate_level(profile.get("xp", 0))

        embed = discord.Embed(title=f"⚔️ Eternal Member Profile: {user.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Dragon Crystals", value=f"✨ `{profile.get('crystals', 0)}` Crystals", inline=True)
        embed.add_field(name="Vault Savings", value=f"🏦 `{profile.get('vault', 0)}` Crystals", inline=True)
        embed.add_field(name="Daily Streak", value=f"🔥 `{profile.get('daily_streak', 0)}` Days", inline=True)
        embed.add_field(name="Faction Level", value=f"📈 Level `{level}`", inline=True)
        embed.add_field(name="Total XP", value=f"⭐ `{profile.get('xp', 0)}` XP", inline=True)
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

    # ==========================================
    # MARKET / SHOP SYSTEM
    # ==========================================

    @app_commands.command(name="shop", description="Browse items and perks available in the Eternal Market")
    async def shop(self, interaction: discord.Interaction):
        await interaction.response.defer()

        embed = discord.Embed(
            title="🛒 Eternal Faction Market",
            description="Use `/buy <item_id>` to purchase items using your Dragon Crystals!",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="1. 🛡️ Dragon Guard Role (`guard`)",
            value="Price: ✨ **500 Crystals**\n*Claim the honorable Dragon Guard rank in the server.*",
            inline=False
        )
        embed.add_field(
            name="2. 🔥 Flame Aura Role (`aura`)",
            value="Price: ✨ **1,500 Crystals**\n*Show off a glowing fiery title in member lists.*",
            inline=False
        )
        embed.add_field(
            name="3. ⚡ Double XP Boost (`xpboost`)",
            value="Price: ✨ **800 Crystals**\n*Receive a temporary XP multiplier for faction activities.*",
            inline=False
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="buy", description="Purchase an item from the Eternal shop")
    @app_commands.describe(item_id="The ID of the item you want to buy (e.g., guard, aura, xpboost)")
    async def buy(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.defer()

        items_catalog = {
            "guard": {"name": "Dragon Guard Role", "price": 500},
            "aura": {"name": "Flame Aura Role", "price": 1500},
            "xpboost": {"name": "Double XP Boost", "price": 800}
        }

        key = item_id.lower().strip()
        if key not in items_catalog:
            await interaction.followup.send("❌ Item not found! Use `/shop` to view valid item IDs.")
            return

        item = items_catalog[key]
        user_id = interaction.user.id
        profile = await self._get_or_create_profile(user_id)

        if profile.get("crystals", 0) < item["price"]:
            await interaction.followup.send(f"❌ You need ✨ **{item['price']} Crystals** to buy `{item['name']}`, but you only have ✨ `{profile.get('crystals', 0)}`.")
            return

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {
                    "$inc": {"crystals": -item["price"]},
                    "$push": {"inventory": item["name"]}
                },
                upsert=True
            )

        embed = discord.Embed(
            title="🎉 Purchase Successful!",
            description=f"You bought **{item['name']}** for ✨ **{item['price']} Crystals**!\nCheck your collection anytime with `/inventory`.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="inventory", description="View the items you have purchased from the Eternal Market")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        profile = await self._get_or_create_profile(interaction.user.id)
        items = profile.get("inventory", [])

        embed = discord.Embed(title=f"🎒 {interaction.user.name}'s Inventory", color=discord.Color.dark_gold())
        if not items:
            embed.description = "📦 *Your bag is empty. Visit `/shop` to purchase items!*"
        else:
            counts = {}
            for item in items:
                counts[item] = counts.get(item, 0) + 1
            lines = [f"• **{name}** x{qty}" for name, qty in counts.items()]
            embed.description = "\n".join(lines)
        await interaction.followup.send(embed=embed)

# ==========================================
    # VAULT / SAVINGS SYSTEM
    # ==========================================

    vault_group = app_commands.Group(name="vault", description="Manage your crystal savings vault")

    @vault_group.command(name="balance", description="Check how many crystals you have saved in your vault")
    async def vault_balance(self, interaction: discord.Interaction):
        await interaction.response.defer()
        profile = await self._get_or_create_profile(interaction.user.id)
        embed = discord.Embed(
            title="🏦 Eternal Vault",
            description=f"Wallet: ✨ **{profile.get('crystals', 0):,}**\nVault: 🏦 **{profile.get('vault', 0):,}**",
            color=discord.Color.teal()
        )
        await interaction.followup.send(embed=embed)

    @vault_group.command(name="deposit", description="Move crystals from your wallet into your protected vault")
    @app_commands.describe(amount="Amount of crystals to deposit")
    async def vault_deposit(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer()
        if amount <= 0:
            await interaction.followup.send("❌ Enter an amount greater than 0.")
            return

        user_id = interaction.user.id
        profile = await self._get_or_create_profile(user_id)
        if profile.get("crystals", 0) < amount:
            await interaction.followup.send("❌ You don't have that many crystals in your wallet.")
            return

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {"$inc": {"crystals": -amount, "vault": amount}},
                upsert=True
            )
        await interaction.followup.send(f"🏦 Deposited ✨ **{amount:,} Crystals** into your vault.")

    @vault_group.command(name="withdraw", description="Move crystals from your vault back into your wallet")
    @app_commands.describe(amount="Amount of crystals to withdraw")
    async def vault_withdraw(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer()
        if amount <= 0:
            await interaction.followup.send("❌ Enter an amount greater than 0.")
            return

        user_id = interaction.user.id
        profile = await self._get_or_create_profile(user_id)
        if profile.get("vault", 0) < amount:
            await interaction.followup.send("❌ You don't have that many crystals stored in your vault.")
            return

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {"$inc": {"crystals": amount, "vault": -amount}},
                upsert=True
            )
        await interaction.followup.send(f"💳 Withdrew ✨ **{amount:,} Crystals** from your vault.")

    # ==========================================
    # ADDITIONAL LAIR MINI-GAMES
    # ==========================================

    @app_commands.command(name="roll", description="Bet crystals and guess the number the dragon die will land on (1-6)")
    @app_commands.describe(bet="Amount of crystals to wager", guess="Your guess, from 1 to 6")
    async def roll(self, interaction: discord.Interaction, bet: int, guess: app_commands.Range[int, 1, 6]):
        await interaction.response.defer()
        user_id = interaction.user.id
        if bet <= 0:
            await interaction.followup.send("❌ Your bet must be greater than 0.")
            return

        profile = await self._get_or_create_profile(user_id)
        if profile.get("crystals", 0) < bet:
            await interaction.followup.send("❌ You don't have enough crystals for that bet.")
            return

        result = random.randint(1, 6)
        dice_faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        embed = discord.Embed(title="🪙 Flame Roll", description=f"The die tumbles... {dice_faces[result - 1]} **{result}**!", color=discord.Color.orange())

        if guess == result:
            winnings = bet * 5
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": winnings}}, upsert=True)
            embed.add_field(name="🎉 Perfect Guess!", value=f"You won ✨ **{winnings:,} Crystals**!")
        else:
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -bet}}, upsert=True)
            embed.add_field(name="💀 Missed It!", value=f"You lost ✨ **{bet:,} Crystals**.")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="cards", description="Draw a card against Flamy the dragon, highest card wins!")
    @app_commands.describe(bet="Amount of crystals to wager")
    async def cards(self, interaction: discord.Interaction, bet: int):
        await interaction.response.defer()
        user_id = interaction.user.id
        if bet <= 0:
            await interaction.followup.send("❌ Your bet must be greater than 0.")
            return

        profile = await self._get_or_create_profile(user_id)
        if profile.get("crystals", 0) < bet:
            await interaction.followup.send("❌ You don't have enough crystals for that bet.")
            return

        face_names = {1: "A", 11: "J", 12: "Q", 13: "K"}
        player_card = random.randint(1, 13)
        dragon_card = random.randint(1, 13)
        player_label = face_names.get(player_card, str(player_card))
        dragon_label = face_names.get(dragon_card, str(dragon_card))

        embed = discord.Embed(title="🎴 Flame Cards", description=f"Your card: **{player_label}**\nFlamy's card: **{dragon_label}**", color=discord.Color.purple())

        if player_card == dragon_card:
            embed.add_field(name="🤝 Push!", value="It's a tie. Your bet has been returned.")
        elif player_card > dragon_card:
            winnings = bet * 2
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": winnings}}, upsert=True)
            embed.add_field(name="🎉 You Win!", value=f"You won ✨ **{winnings:,} Crystals**!")
        else:
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -bet}}, upsert=True)
            embed.add_field(name="💀 Flamy Wins!", value=f"You lost ✨ **{bet:,} Crystals**.")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="fish", description="Cast your line into the River of Embers for a chance at rare rewards")
    async def fish(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        current_time = int(time.time())
        profile = await self._get_or_create_profile(user_id)

        if current_time - profile.get("last_fish", 0) < 900:
            remaining_mins = int((900 - (current_time - profile.get("last_fish", 0))) // 60)
            await interaction.followup.send(f"🎣 Your line is still cast. Wait `{remaining_mins} minutes`.")
            return

        roll_value = random.random()
        if roll_value < 0.05:
            catch, reward = "🐉 Baby Dragon Eel (LEGENDARY)", random.randint(400, 700)
        elif roll_value < 0.20:
            catch, reward = "🐡 Ember Pufferfish (RARE)", random.randint(150, 300)
        elif roll_value < 0.55:
            catch, reward = "🐟 River Trout", random.randint(40, 100)
        elif roll_value < 0.85:
            catch, reward = "🥾 Old Boot", random.randint(5, 20)
        else:
            catch, reward = None, 0

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": reward}, "$set": {"last_fish": current_time}}, upsert=True)

        if catch is None:
            await interaction.followup.send("🎣 The line stayed still... nothing bit this time.")
        else:
            await interaction.followup.send(f"🎣 You reeled in a **{catch}**! Sold for ✨ **{reward} Crystals**.")

    @app_commands.command(name="highlow", description="Bet crystals and guess if the next number will be higher or lower")
    @app_commands.describe(bet="Amount of crystals to wager", guess="Will the next number be higher or lower?")
    @app_commands.choices(guess=[
        app_commands.Choice(name="Higher", value="higher"),
        app_commands.Choice(name="Lower", value="lower"),
    ])
    async def highlow(self, interaction: discord.Interaction, bet: int, guess: app_commands.Choice[str]):
        await interaction.response.defer()
        user_id = interaction.user.id
        if bet <= 0:
            await interaction.followup.send("❌ Your bet must be greater than 0.")
            return

        profile = await self._get_or_create_profile(user_id)
        if profile.get("crystals", 0) < bet:
            await interaction.followup.send("❌ You don't have enough crystals for that bet.")
            return

        start_num = random.randint(10, 90)
        next_num = random.randint(1, 100)
        while next_num == start_num:
            next_num = random.randint(1, 100)

        correct = (guess.value == "higher" and next_num > start_num) or (guess.value == "lower" and next_num < start_num)
        embed = discord.Embed(title="🎯 High-Low", description=f"Starting number: **{start_num}**\nNext number: **{next_num}**", color=discord.Color.blue())

        if correct:
            winnings = bet * 2
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": winnings}}, upsert=True)
            embed.add_field(name="🎉 Correct!", value=f"You won ✨ **{winnings:,} Crystals**!")
        else:
            if self.bot.profiles is not None:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -bet}}, upsert=True)
            embed.add_field(name="💀 Wrong!", value=f"You lost ✨ **{bet:,} Crystals**.")
        await interaction.followup.send(embed=embed)

# ==========================================
    # XP & RANK SYSTEM
    # ==========================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        config = await self._get_guild_config(message.guild.id)
        cooldown = config.get("xp_cooldown", 60)
        key = (message.guild.id, message.author.id)
        current_time = time.time()
        last_gain = self.xp_cooldowns.get(key, 0)
        if current_time - last_gain < cooldown:
            return
        self.xp_cooldowns[key] = current_time

        profile = await self._get_or_create_profile(message.author.id)
        gained = random.randint(config.get("xp_min", 5), config.get("xp_max", 15))
        old_level = self.calculate_level(profile.get("xp", 0))
        new_xp = profile.get("xp", 0) + gained
        new_level = self.calculate_level(new_xp)

        if self.bot.profiles is not None:
            await self.bot.profiles.update_one({"_id": str(message.author.id)}, {"$inc": {"xp": gained}}, upsert=True)

        if new_level > old_level:
            try:
                await message.channel.send(f"📈 {message.author.mention} climbed to **Level {new_level}**!")
            except discord.HTTPException:
                pass

            rank_roles = config.get("rank_roles", {})
            role_id = rank_roles.get(str(new_level))
            if role_id:
                role = message.guild.get_role(int(role_id))
                if role:
                    try:
                        await message.author.add_roles(role, reason="Rank role reward")
                    except discord.HTTPException:
                        pass

    @app_commands.command(name="rank", description="View your current XP and faction level")
    async def rank(self, interaction: discord.Interaction):
        await interaction.response.defer()
        profile = await self._get_or_create_profile(interaction.user.id)
        xp = profile.get("xp", 0)
        level = self.calculate_level(xp)
        next_level_xp = self.xp_for_level(level)
        progress = xp - (level * 500)

        embed = discord.Embed(title=f"🎖️ {interaction.user.name}'s Rank", color=discord.Color.blurple())
        embed.add_field(name="Level", value=f"📈 `{level}`", inline=True)
        embed.add_field(name="Total XP", value=f"⭐ `{xp}`", inline=True)
        embed.add_field(name="Progress", value=f"`{progress}/500` to Level `{level + 1}` (needs `{next_level_xp}` total XP)", inline=False)
        await interaction.followup.send(embed=embed)

    rankroles_group = app_commands.Group(name="rankroles", description="Configure roles automatically awarded at certain levels")

    @rankroles_group.command(name="set", description="Assign a role reward for reaching a specific level (Admin only)")
    @app_commands.describe(level="The level required", role="The role to award")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rankroles_set(self, interaction: discord.Interaction, level: int, role: discord.Role):
        configs = getattr(self.bot, "guild_configs", None)
        if configs is None:
            await interaction.response.send_message("❌ Rank role storage is currently unavailable.", ephemeral=True)
            return
        await configs.update_one({"_id": str(interaction.guild.id)}, {"$set": {f"rank_roles.{level}": str(role.id)}}, upsert=True)
        await interaction.response.send_message(f"✅ Members will now receive **{role.name}** upon reaching Level `{level}`.", ephemeral=True)

    @rankroles_group.command(name="list", description="View all configured rank role rewards")
    async def rankroles_list(self, interaction: discord.Interaction):
        await interaction.response.defer()
        config = await self._get_guild_config(interaction.guild.id)
        rank_roles = config.get("rank_roles", {})

        embed = discord.Embed(title="🏅 Rank Role Rewards", color=discord.Color.dark_teal())
        if not rank_roles:
            embed.description = "📜 *No rank roles have been configured yet.*"
        else:
            lines = []
            for level, role_id in sorted(rank_roles.items(), key=lambda pair: int(pair[0])):
                role = interaction.guild.get_role(int(role_id))
                role_name = role.name if role else "*(deleted role)*"
                lines.append(f"Level `{level}` → **{role_name}**")
            embed.description = "\n".join(lines)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="xpsettings", description="Configure how much XP members earn per message (Admin only)")
    @app_commands.describe(xp_min="Minimum XP per message", xp_max="Maximum XP per message", cooldown_seconds="Seconds between XP gains per member")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def xpsettings(self, interaction: discord.Interaction, xp_min: int, xp_max: int, cooldown_seconds: int):
        if xp_min <= 0 or xp_max <= 0 or xp_min > xp_max or cooldown_seconds < 0:
            await interaction.response.send_message("❌ Please provide valid values (xp_min ≤ xp_max, both positive).", ephemeral=True)
            return

        configs = getattr(self.bot, "guild_configs", None)
        if configs is None:
            await interaction.response.send_message("❌ Settings storage is currently unavailable.", ephemeral=True)
            return

        await configs.update_one(
            {"_id": str(interaction.guild.id)},
            {"$set": {"xp_min": xp_min, "xp_max": xp_max, "xp_cooldown": cooldown_seconds}},
            upsert=True
        )
        await interaction.response.send_message(
            f"⚙️ XP settings updated: **{xp_min}-{xp_max} XP** per message, **{cooldown_seconds}s** cooldown.",
            ephemeral=True
        )

    # ==========================================
    # ROLES MANAGEMENT
    # ==========================================

    @app_commands.command(name="wings", description="Check the roles (wings) you currently hold in the faction")
    async def wings(self, interaction: discord.Interaction):
        await interaction.response.defer()
        member = interaction.user
        roles = [role.mention for role in reversed(member.roles) if role.name != "@everyone"]

        embed = discord.Embed(title=f"📜 {member.name}'s Wings", color=discord.Color.dark_purple())
        embed.description = ", ".join(roles) if roles else "*You currently hold no faction roles.*"
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="roleselect", description="Configure or open the self-assignable role picker")
    async def roleselect(self, interaction: discord.Interaction):
        await interaction.response.defer()
        config = await self._get_guild_config(interaction.guild.id)
        role_ids = config.get("self_roles", [])
        roles = [interaction.guild.get_role(int(rid)) for rid in role_ids]
        roles = [r for r in roles if r is not None]

        if not roles:
            await interaction.followup.send("🎖️ No self-assignable roles have been configured yet. Ask an admin to use `/addselfrole`.")
            return

        embed = discord.Embed(title="🎖️ Faction Role Picker", description="Select a role below to add or remove it.", color=discord.Color.blue())
        await interaction.followup.send(embed=embed, view=SelfRoleView(roles))

    @app_commands.command(name="addselfrole", description="Add a role to the self-assignable role picker (Admin only)")
    @app_commands.describe(role="The role to make self-assignable")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addselfrole(self, interaction: discord.Interaction, role: discord.Role):
        configs = getattr(self.bot, "guild_configs", None)
        if configs is None:
            await interaction.response.send_message("❌ Role storage is currently unavailable.", ephemeral=True)
            return
        await configs.update_one({"_id": str(interaction.guild.id)}, {"$addToSet": {"self_roles": str(role.id)}}, upsert=True)
        await interaction.response.send_message(f"✅ **{role.name}** is now available in `/roleselect`.", ephemeral=True)

    @app_commands.command(name="setclaimrole", description="Register a claimable event role and its secret code (Admin only)")
    @app_commands.describe(code="The word members must type to claim the role", role="The role to grant")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def setclaimrole(self, interaction: discord.Interaction, code: str, role: discord.Role):
        configs = getattr(self.bot, "guild_configs", None)
        if configs is None:
            await interaction.response.send_message("❌ Role storage is currently unavailable.", ephemeral=True)
            return
        await configs.update_one(
            {"_id": str(interaction.guild.id)},
            {"$set": {f"event_roles.{code.lower().strip()}": str(role.id)}},
            upsert=True
        )
        await interaction.response.send_message(f"✅ Members can now claim **{role.name}** using `/claimrole {code}`.", ephemeral=True)

    @app_commands.command(name="claimrole", description="Claim a limited-time event role using its code word")
    @app_commands.describe(code="The event code word")
    async def claimrole(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer(ephemeral=True)
        config = await self._get_guild_config(interaction.guild.id)
        event_roles = config.get("event_roles", {})
        role_id = event_roles.get(code.lower().strip())

        if not role_id:
            await interaction.followup.send("❌ That code doesn't match any active event role.")
            return

        role = interaction.guild.get_role(int(role_id))
        if role is None:
            await interaction.followup.send("❌ That event role no longer exists.")
            return

        if role in interaction.user.roles:
            await interaction.followup.send(f"🔥 You already hold **{role.name}**!")
            return

        try:
            await interaction.user.add_roles(role, reason="Event role claimed")
            await interaction.followup.send(f"🎁 You claimed the **{role.name}** role!")
        except discord.HTTPException:
            await interaction.followup.send("❌ I couldn't assign that role. Please contact a moderator.")

    # ==========================================
    # UTILITY & INFO
    # ==========================================

    @app_commands.command(name="facstats", description="View general statistics about the Eternal faction server")
    async def facstats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild = interaction.guild
        bots = sum(1 for member in guild.members if member.bot)
        humans = guild.member_count - bots

        embed = discord.Embed(title=f"📊 {guild.name} Faction Stats", color=discord.Color.dark_blue())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="👤 Members", value=f"`{humans}`", inline=True)
        embed.add_field(name="🤖 Bots", value=f"`{bots}`", inline=True)
        embed.add_field(name="📁 Channels", value=f"`{len(guild.channels)}`", inline=True)
        embed.add_field(name="🏷️ Roles", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(name="💎 Boosts", value=f"`{guild.premium_subscription_count}`", inline=True)
        embed.add_field(name="📅 Created", value=f"{guild.created_at.strftime('%Y-%m-%d')}", inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="avatar", description="View a member's avatar")
    @app_commands.describe(member="The member whose avatar you want to see (defaults to yourself)")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()
        target = member or interaction.user
        embed = discord.Embed(title=f"🖼️ {target.name}'s Avatar", color=discord.Color.blue())
        embed.set_image(url=target.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ping", description="Check Flamy's response latency")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        embed = discord.Embed(title="📶 Flamy Ping", description=f"Pong! Latency: `{latency_ms}ms`", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    # ==========================================
    # FLAMY AI & FUN
    # ==========================================

    ROAST_LINES = [
        "you bring everyone so much joy... when you leave the call.",
        "you're like a cloud — when you disappear, it's a beautiful day.",
        "you're the reason the Dragon statue has trust issues.",
        "even the slot machine feels bad taking your crystals.",
        "you have the confidence of a jackpot and the luck of a fine.",
        "somewhere, a coin is flipping just to avoid landing on your side.",
    ]

    @app_commands.command(name="roast", description="Get playfully roasted by Flamy (all in good fun!)")
    @app_commands.describe(member="The member to roast (defaults to yourself)")
    async def roast(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        line = random.choice(self.ROAST_LINES)
        await interaction.response.send_message(f"🔥 {target.mention}, {line}")

    @app_commands.command(name="match", description="Test your compatibility with another faction member")
    @app_commands.describe(member="The member to test compatibility with")
    async def match(self, interaction: discord.Interaction, member: discord.Member):
        ids = sorted([interaction.user.id, member.id])
        seed_value = ids[0] * 31 + ids[1]
        rng = random.Random(seed_value)
        percent = rng.randint(1, 100)

        if percent >= 85:
            verdict = "🔥 A legendary bond! You two are basically faction royalty."
        elif percent >= 60:
            verdict = "💖 A strong connection! Great teamwork potential."
        elif percent >= 35:
            verdict = "🤝 Decent compatibility — could go either way."
        else:
            verdict = "🧊 Rocky start... but even rivals can become allies!"

        embed = discord.Embed(
            title="💕 Flamy Match",
            description=f"{interaction.user.mention} ❤️ {member.mention}\n\n**Compatibility: {percent}%**\n{verdict}",
            color=discord.Color.magenta()
        )
        await interaction.response.send_message(embed=embed)

    _ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def _safe_eval(cls, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numbers are allowed.")
        if isinstance(node, ast.BinOp) and type(node.op) in cls._ALLOWED_OPERATORS:
            return cls._ALLOWED_OPERATORS[type(node.op)](cls._safe_eval(node.left), cls._safe_eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls._ALLOWED_OPERATORS:
            return cls._ALLOWED_OPERATORS[type(node.op)](cls._safe_eval(node.operand))
        raise ValueError("Only basic arithmetic (+ - * / % **) is allowed.")

    @app_commands.command(name="calc", description="Evaluate a quick math expression")
    @app_commands.describe(expression="A math expression, e.g. (12 + 8) * 3 / 2")
    async def calc(self, interaction: discord.Interaction, expression: str):
        try:
            tree = ast.parse(expression, mode="eval")
            result = self._safe_eval(tree.body)
            embed = discord.Embed(title="🧮 Quick Calc", description=f"`{expression}` = **{result}**", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
        except (ValueError, ZeroDivisionError, SyntaxError, TypeError):
            await interaction.response.send_message("❌ That doesn't look like a valid math expression. Try something like `(12 + 8) * 3 / 2`.", ephemeral=True)

async def setup(bot):
    cog = EconomyCog(bot)
    bot.tree.add_command(cog.vault_group)
    bot.tree.add_command(cog.rankroles_group)
    await bot.add_cog(cog)
    
