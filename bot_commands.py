import os
import random
import requests
import time
from bs4 import BeautifulSoup

import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import faction_data  # Import the secret data file

SPECIAL_CHANNEL_ID = 1521899264265945109
ADMIN_IDS = [1477528681709830297]

# --- WEB READER HELPER FUNCTION ---
def fetch_web_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Error: Website open nahi ho rahi hai (Status Code issue)."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]): 
            script.extract()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        clean_text = '\n'.join(chunk for chunk in lines if chunk)
        return clean_text[:1500]
    except Exception as e:
        return f"Error: {str(e)}"

# --- INTERACTIVE DROP DOWN UI ---
class HelpDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="General Commands", description="Basic chat and utility features", emoji="🐉"),
            discord.SelectOption(label="AI Multimedia", description="Vision features", emoji="🎨"),
            discord.SelectOption(label="Faction Games & RPG", description="Play games and earn crystals", emoji="⚔️")
        ]
        super().__init__(placeholder="Choose a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "General Commands":
            embed = discord.Embed(title="🐉 General Commands", color=discord.Color.blue())
            embed.add_field(name="`/ping`", value="Check the bot's speed.", inline=False)
            embed.add_field(name="`/ask`", value="Ask FlamingDeath a question from anywhere in the server.", inline=False)
            embed.add_field(name="`/remember`", value="Make the dragon remember faction info in the cloud database.", inline=False)
            embed.add_field(name="`/recall`", value="Ask the dragon to recall remembered info.", inline=False)
            embed.add_field(name="`/readweb`", value="Provide a link and let the dragon read it.", inline=False)
            embed.add_field(name="💬 Chat Mode", value=f"Talk to me directly in <#{SPECIAL_CHANNEL_ID}> without pings!", inline=False)
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "AI Multimedia":
            embed = discord.Embed(title="🎨 AI Multimedia Commands", color=discord.Color.cyan())
            embed.add_field(name="`/analyze`", value="Upload an image, video, or audio file for Dragon Vision!", inline=False)
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "Faction Games & RPG":
            embed = discord.Embed(title="⚔️ Faction Games & Economy System", color=discord.Color.dark_red())
            embed.add_field(name="`/profile`", value="View your Eternal member card and Crystal balance.", inline=False)
            embed.add_field(name="`/hunt`", value="Go out on a hunt to earn Dragon Crystals (1 hour cooldown).", inline=False)
            embed.add_field(name="`/coinflip`", value="Bet your crystals on Heads or Tails!", inline=False)
            embed.add_field(name="`/slots`", value="Try your luck on the Dragon Slot Machine (Cost: 10 Crystals).", inline=False)
            await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())


# ==========================================
# MAIN COMMAND COG ARCHITECTURE
# ==========================================
class FactionBotCommands(commands.Cog):
    def __init__(self, bot, conversation_history, get_gemini_response_func):
        self.bot = bot
        self.conversation_history = conversation_history
        self.get_gemini_response = get_gemini_response_func

    async def _get_or_create_profile(self, user_id: int) -> dict:
        """
        Asynchronous database link. Fetches or initializes a member's global profile.
        Uses the shared field 'crystals' for the FlamingDeath economy system.
        """
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

    @app_commands.command(name='ping', description="Check the operational response latency matrix")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"*Grrr...* Pong! My flames reached you in {latency}ms!")

    @app_commands.command(name="help", description="Show all available features of FlamingDeath")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔥 FlamingDeath Command Center 🔥", description="Welcome, Eternal member! Select a category from the dropdown menu below.", color=discord.Color.cyan())
        embed.set_footer(text="Guarding Eternal since 2025")
        await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)

    @app_commands.command(name="ask", description="Ask FlamingDeath anything, anywhere!")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        try:
            combined_instruction = f"{faction_data.SYSTEM_PROMPT}\n\nAdditional Faction Information:\n{faction_data.FACTION_PROMPT}"
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=combined_instruction)
            
            response = model.generate_content(question)
            answer = response.text
            formatted_response = f"**Your question:** {question}\n\n**Answer:** {answer}"
            if len(formatted_response) > 2000:
                await interaction.followup.send(f"**Your question:** {question}")
                chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
                for chunk in chunks: await interaction.followup.send(f"**Answer (part):** {chunk}")
            else:
                await interaction.followup.send(formatted_response)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                await interaction.followup.send("🔥 *ROAARRR!* My fiery broadcast is currently choked by the static! Let the flames cool down and try again shortly!")
            else:
                await interaction.followup.send(f"🔥 *Grrr...* Error: {str(e)}")

    # 🟢 UPGRADE: /remember and /recall now store custom data in a persistent 'faction_shared_memory' database collection
    @app_commands.command(name="remember", description="Make the Dragon remember a faction detail or rule")
    async def remember(self, interaction: discord.Interaction, topic: str, information: str):
        await interaction.response.defer()
        if self.bot.db:
            memory_coll = self.bot.db["faction_shared_memory"]
            await memory_coll.update_one(
                {"_id": topic.lower()},
                {"$set": {"info": information}},
                upsert=True
            )
        await interaction.followup.send(f"📥 **Memory Updated!** Maine yaad rakh liya hai ki `{topic}` kya hai.")

    @app_commands.command(name="recall", description="Ask the Dragon to recall something it remembered")
    async def recall(self, interaction: discord.Interaction, topic: str):
        await interaction.response.defer()
        info = None
        if self.bot.db:
            memory_coll = self.bot.db["faction_shared_memory"]
            doc = await memory_coll.find_one({"_id": topic.lower()})
            if doc:
                info = doc.get("info")

        if info:
            await interaction.followup.send(f"🧠 **Memory Box:** `{topic}` ke baare mein mujhe ye pata hai:\n> {info}")
        else:
            await interaction.followup.send(f"🔍 Sorry, mujhe `{topic}` ke baare mein kuch yaad nahi hai.")

    @app_commands.command(name="readweb", description="Provide a website URL and let the Dragon read and summarize it")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def readweb(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        web_raw_data = fetch_web_content(url)
        
        if "Error:" in web_raw_data:
            await interaction.followup.send(f"🔥 {web_raw_data}")
            return
            
        try:
            combined_instruction = f"{faction_data.SYSTEM_PROMPT}\n\nAdditional Faction Information:\n{faction_data.FACTION_PROMPT}\n\nTumhe niche di gayi website ke raw content ko read karna hai aur uski ek short, helpful summary faction members ko batani hai."
            model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=combined_instruction)
            
            ai_prompt = f"Website URL: {url}\nWebsite Text to read Content:\n{web_raw_data}"
            response = model.generate_content(ai_prompt)
            summary = response.text
            
            await interaction.followup.send(f"🌐 **Web Reader Report for:** {url}\n\n{summary}")
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                await interaction.followup.send("🔥 *ROAARRR!* My fiery broadcast is currently choked by the static! Let the flames cool down and try again shortly!")
            else:
                await interaction.followup.send(f"🔥 *Coughs smoke* Web read error: {str(e)}")

    @app_commands.command(name="behave", description="Let the Dragon speak and act for you (Admin Only)")
    async def behave(self, interaction: discord.Interaction, script: str):
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("🔥 *Growls...* Only the high keepers can command me!", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            combined_instruction = f"{faction_data.SYSTEM_PROMPT}\n\nAdditional Faction Information:\n{faction_data.FACTION_PROMPT}"
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=combined_instruction)
            
            acting_prompt = f"Act completely as FlamingDeath. Directly generate the final text based on this script: {script}"
            response = model.generate_content(acting_prompt)
            acting_message = response.text
            if acting_message:
                await interaction.channel.send(acting_message)
                await interaction.followup.send("✅ Script executed successfully!", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ No message was generated.", ephemeral=True)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                await interaction.followup.send("🔥 *ROAARRR!* Rate limit hit! Wait a moment.", ephemeral=True)
            else:
                await interaction.followup.send(f"🔥 Acting error: {str(e)}", ephemeral=True)

    @app_commands.command(name="analyze", description="Let FlamingDeath look at your photos, videos, or audio files")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def analyze(self, interaction: discord.Interaction, prompt: str, attachment: discord.Attachment):
        await interaction.response.defer()
        if not attachment.content_type:
            await interaction.followup.send("🔥 *Grrr...* I can't read this file format!")
            return
        try:
            file_response = requests.get(attachment.url)
            attachment_data = {'mime_type': attachment.content_type, 'data': file_response.content}
            response_text = await self.get_gemini_response(prompt, interaction.user.id, attachment_data)
            await interaction.followup.send(f"🐉 **FlamingDeath Vision:** {response_text}")
        except Exception as e:
            await interaction.followup.send(f"🔥 *Coughs smoke* Error: {str(e)}")

    # --- Error Handler for Slash Commands Cooldowns ---
    @ask.error
    @readweb.error
    @analyze.error
    async def command_cooldown_error_handler(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏰ *Hold your horses, warrior! This command is cooling down. Try again in {error.retry_after:.1f}s.*", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(f"🔥 An execution error occurred: {str(error)}", ephemeral=True)

    # ==========================================
    # PERSISTENT ECONOMY & MINI-GAMES SYSTEMS
    # ==========================================

    @app_commands.command(name="profile", description="Check your Eternal faction member card")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        joined_at = user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown"
        
        # Read balance natively from cloud data document
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
        
        # 1-Hour Cooldown Logic = 3600 seconds
        cooldown_duration = 3600
        if current_time - last_hunt < cooldown_duration:
            remaining = cooldown_duration - (current_time - last_hunt)
            remaining_mins = int(remaining // 60)
            await interaction.followup.send(f"🔥 *Growls...* You are exhausted! Wait `{remaining_mins} more minutes`.")
            return
            
        crystals_found = random.randint(15, 50)
        
        if self.bot.profiles:
            # Atomic increase to database balance and save new timestamp
            await self.bot.profiles.update_one(
                {"_id": str(user_id)},
                {
                    "$inc": {"crystals": crystals_found},
                    "$set": {"last_hunt": current_time}
                }
            )
            
        scenarios = [
            f"🐉 You flew into the sky with FlamingDeath and raided an enemy base! Found **{crystals_found}** Crystals! 🔥",
            f"⚔️ You cleared out rogue monsters threatening the boundaries of Eternal. Earned **{crystals_found}** Crystals!",
            f"💎 You discovered a hidden crystalline cave beneath the SquareOne base! Extracted **{crystals_found}** Crystals!"
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
            await interaction.followup.send("🔥 *Grrr...* You must bet at least `1 Crystal`!")
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
            await interaction.followup.send(f"🔥 *Coughs smoke...* You only have `{current_balance}` Crystals.")
            return
            
        # Deduct cost first
        if self.bot.profiles:
            await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": -cost}})
            
        items = ["🐉", "💎", "⚔️", "🔥", "🍉"]
        slot1, slot2, slot3 = random.choice(items), random.choice(items), random.choice(items)
        embed = discord.Embed(title="🎰 Eternal DRAGON SLOTS 🎰", color=discord.Color.gold())
        embed.description = f"\n> **[ {slot1} | {slot2} | {slot3} ]**\n"
        
        if slot1 == slot2 == slot3:
            if self.bot.profiles:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": 150}})
            embed.add_field(name="🎉 JACKPOT!!! 🎉", value=f"Matched! Won 150 Crystals!")
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            if self.bot.profiles:
                await self.bot.profiles.update_one({"_id": str(user_id)}, {"$inc": {"crystals": 30}})
            embed.add_field(name="✨ Small Win! ✨", value=f"Two matched! Won 30 Crystals!")
        else:
            embed.add_field(name="💀 No Match!", value="Lost 10 Crystals.")
        await interaction.followup.send(embed=embed)

async def setup(bot, conversation_history, get_gemini_response_func):
    # Adjusted footprint signatures to cleanly eliminate local parameters
    cog = FactionBotCommands(bot, conversation_history, get_gemini_response_func)
    await bot.add_cog(cog)
            
