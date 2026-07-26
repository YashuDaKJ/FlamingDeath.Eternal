import random
import time
import discord
from discord import app_commands
from discord.ext import commands

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_or_create_profile(self, user_id: int) -> dict:
        """Fetches or initializes user profile in MongoDB."""
        if not self.bot.profiles:
            return {"_id": str(user_id), "shards": 0, "crystals": 0, "last_hunt": 0}
            
        profile = await self.bot.profiles.find_one({"_id": str(user_id)})
        if not profile:
            profile = {
                "_id": str(user_id),
                "shards": 0,
                "crystals": 0,
                "last_hunt": 0
            }
            await self.bot.profiles.insert_one(profile)
        return profile

    @app_commands.command(name="profile", description="Check your Eternal faction member card")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        joined_at = user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown"
        
        profile = await self._get_or_create_profile(user.id)
        crystals = profile.get("crystals", 0)
        
        embed = discord.Embed(title=f"⚔️ Eternal Member Profile: {user.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Faction Standing", value="**Loyal Member** 🛡️", inline=True)
        embed.add_field(name="Dragon Crystals", value=f"✨ `{crystals}` Crystals", inline=True)
        embed.add_field(name="Arrival Date", value=f"📅 {joined_at}", inline=False)
        await interaction.followup.send(embed=embed)

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
            await interaction.followup.send(f"🔥 *Growls...* You are exhausted! Wait `{remaining_mins} more minutes`.")
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
            f"⚔️ You cleared out rogue monsters threatening Eternal. Earned **{crystals_found}** Crystals!",
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
        embed = discord.Embed(title="🎰 Eternal DRAGON SLOTS 🎰", color=discord.Color.gold())
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
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
