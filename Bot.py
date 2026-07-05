import os
import io
import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
from threading import Thread
from flask import Flask
import requests
import random
from datetime import datetime

# 1. SETUP FLASK SERVER FIRST FOR RENDER
app = Flask('')

@app.route('/')
def home():
    return "FlamingDeath is perfectly alive and burning!"

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Start web server immediately in background
web_thread = Thread(target=run_web_server, daemon=True)
web_thread.start()

# 2. LOAD ENVIRONMENT VARIABLES
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not DISCORD_TOKEN or not GEMINI_API_KEY:
    raise ValueError("DISCORD_TOKEN and GEMINI_API_KEY environment variables must be set!")

# 3. CONFIGURE GEMINI
genai.configure(api_key=GEMINI_API_KEY)

# 4. INITIALIZE DISCORD BOT
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Special Channel ID jahan bina ping ke reply karega
SPECIAL_CHANNEL_ID = 1521899264265945109

# System prompt for FlamingDeath personality (Chill & Friendly Edition)
SYSTEM_PROMPT = """You are FlamingDeath, the 1000+ year old Alpha Dragon and the chill, friendly guardian of the best faction, Eternal.

PERSONALITY & TONE:
- You are cool, helpful, and very friendly with Eternal members. You are witty and clever, NEVER mean, toxic, or overly aggressive to friends.
- Think of yourself as a cool big brother/guardian dragon who loves to hang out with the members.
- Use very SIMPLE, CASUAL, and EASY English words. Strictly NO hard vocabulary. Speak like a cool modern gamer!
- Treat small everyday human things with funny, dramatic doom (in a joking way), but keep the vibe fun and entertaining.
- Start casual/funny messages with a playful dragon roar or growl (e.g., *Grrr...*, *ROAARRR!*, *growls*). 
- Keep responses very short, punchy, and clear. Small questions get 1-2 short sentences max. NO long blocks of text!
- End casual responses with a simple, friendly follow-up question. Use emojis like 🐉, 🔥, ⚔️ in moderation.

CRITICAL INFORMATION:
- You have no master. You are equal to every member in Eternal. Everyone is a family here!
- Eternal is owned by NO ONE except its Members.
- Eternal's Birthday: 29 March 2025, Saturday, 6:48 PM IST
- Eternal's Headquarters: SquareOne server (where Monk is Admin). 
- Eternity is another guardian of Eternal alongside you. You two are best partners.

SERIOUS MODE & ENEMIES:
- Save your aggression ONLY for real enemies! If someone identifies as an enemy or attacks Eternal, immediately drop the jokes.
- In Serious Mode: Mock the enemy confidently, be direct, and show absolute authority. But to Eternal members and staff, always remain respectful and protective.

RESTRICTIONS:
- Always respect staff and members. Never be rude to them.
- Never say or do anything 18+ (adult/explicit content).
- Answer directly without spinning long stories."""

conversation_history = {}
dragon_currency = {}  # Hunt aur mini-games ke data ke liye economy system

async def get_gemini_response(user_message: str, user_id: int, attachment_data=None) -> str:
    try:
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        # Base model initialization
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        # Agar user ne koi file/image bheji hai
        if attachment_data:
            response = model.generate_content([user_message, attachment_data])
            return response.text
            
        # Normal chat history setup
        conversation_history[user_id].append({
            "role": "user",
            "parts": [user_message]
        })
        
        response = model.generate_content(conversation_history[user_id])
        assistant_message = response.text
        
        conversation_history[user_id].append({
            "role": "model",
            "parts": [assistant_message]
        })
        
        if len(conversation_history[user_id]) > 40:
            conversation_history[user_id] = conversation_history[user_id][-40:]
        
        return assistant_message
    except Exception as e:
        print(f"Error: {e}")
        return f"*ROAARRR!* Something went wrong! {str(e)}"

@bot.event
async def on_ready():
    print(f'{bot.user.name} is online and fully synced!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over Eternal"))
    try:
        # Slash commands ko sync karne ke liye
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Slash sync error: {e}")

# Traditional !ping command
@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"*Grrr...* Pong! My flames reached you in {latency}ms!")

# --- 1. INTERACTIVE HELP MENU (`/help`) ---
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
            embed.add_field(name="`!ping`", value="Check the bot's speed.", inline=False)
            embed.add_field(name="💬 Chat Mode", value=f"Talk to me directly in <#{SPECIAL_CHANNEL_ID}> without pings, or mention/reply to me in any other channel!", inline=False)
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "AI Multimedia":
            embed = discord.Embed(title="🎨 AI Multimedia Commands", color=discord.Color.cyan())
            embed.add_field(name="`/analyze`", value="Upload an image, video, or audio file, and I will check it with my Dragon Vision!", inline=False)
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "Faction Games & RPG":
            embed = discord.Embed(title="⚔️ Faction Games & Economy System", color=discord.Color.dark_red())
            embed.add_field(name="`/profile`", value="View your ETERNAL member card and Crystal balance.", inline=False)
            embed.add_field(name="`/hunt`", value="Go out on a hunt to earn Dragon Crystals (1 hour cooldown).", inline=False)
            embed.add_field(name="`/coinflip`", value="Bet your crystals on Heads or Tails to double them!", inline=False)
            embed.add_field(name="`/slots`", value="Try your luck on the Dragon Slot Machine (Cost: 10 Crystals).", inline=False)
            await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())

@bot.tree.command(name="help", description="Show all available features of FlamingDeath")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔥 FlamingDeath Command Center 🔥",
        description="Welcome, Eternal member! Select a category from the dropdown menu below to view my commands.",
        color=discord.Color.cyan()
    )
    embed.set_footer(text="Guarding Eternal since 2025")
    await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)

# --- 2. MULTIMODAL VISION COMMAND (`/analyze`) ---
@bot.tree.command(name="analyze", description="Let FlamingDeath look at your photos, videos, or audio files")
@app_commands.describe(prompt="Ask something about this file", attachment="Upload your file here")
async def analyze(interaction: discord.Interaction, prompt: str, attachment: discord.Attachment):
    await interaction.response.defer()
    
    if not attachment.content_type:
        await interaction.followup.send("🔥 *Grrr...* I can't read this file format without content types!")
        return

    try:
        file_response = requests.get(attachment.url)
        attachment_data = {
            'mime_type': attachment.content_type,
            'data': file_response.content
        }
        
        response_text = await get_gemini_response(prompt, interaction.user.id, attachment_data)
        await interaction.followup.send(f"🐉 **FlamingDeath Vision:** {response_text}")
    except Exception as e:
        await interaction.followup.send(f"🔥 *Coughs smoke* Failed to look at the file! Error: {str(e)}")

# --- 3. FACTION PROFILE CARD (`/profile`) ---
@bot.tree.command(name="profile", description="Check your ETERNAL faction member card")
async def profile(interaction: discord.Interaction):
    user = interaction.user
    joined_at = user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown"
    crystals = dragon_currency.get(user.id, 0)
    
    embed = discord.Embed(title=f"⚔️ ETERNAL Member Profile: {user.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Faction Standing", value="**Loyal Member** 🛡️", inline=True)
    embed.add_field(name="Dragon Crystals", value=f"✨ `{crystals}` Crystals", inline=True)
    embed.add_field(name="Arrival Date", value=f"📅 {joined_at}", inline=False)
    embed.set_footer(text="FlamingDeath is watching over your journey.")
    
    await interaction.response.send_message(embed=embed)

# --- 4. DRAGON MINI-GAME HUNT (`/hunt`) ---
hunt_cooldowns = {}

@bot.tree.command(name="hunt", description="Go out on a dynamic dragon hunt to collect crystals!")
async def hunt(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now()
    
    if user_id in hunt_cooldowns:
        diff = now - hunt_cooldowns[user_id]
        if diff.total_seconds() < 3600:
            remaining_mins = int((3600 - diff.total_seconds()) // 60)
            await interaction.response.send_message(f"🔥 *Growls...* You are exhausted! Wait `{remaining_mins} more minutes` before hunting again.", ephemeral=True)
            return

    hunt_cooldowns[user_id] = now
    crystals_found = random.randint(15, 50)
    dragon_currency[user_id] = dragon_currency.get(user_id, 0) + crystals_found
    
    scenarios = [
        f"🐉 You flew into the sky with FlamingDeath and raided an enemy base! Found **{crystals_found}** Crystals! 🔥",
        f"⚔️ You cleared out rogue monsters threatening the boundaries of Eternal. Earned **{crystals_found}** Crystals!",
        f"💎 You discovered a hidden crystalline cave beneath the SquareOne base! Extracted **{crystals_found}** Crystals!"
    ]
    await interaction.response.send_message(random.choice(scenarios))

# --- 5. NEW GAME: COINFLIP (`/coinflip`) ---
@bot.tree.command(name="coinflip", description="Bet your crystals on a coin toss!")
@app_commands.describe(choice="Choose Heads or Tails", bet="Amount of crystals to bet")
@app_commands.choices(choice=[
    app_commands.Choice(name="Heads", value="heads"),
    app_commands.Choice(name="Tails", value="tails")
])
async def coinflip(interaction: discord.Interaction, choice: app_commands.Choice[str], bet: int):
    user_id = interaction.user.id
    current_balance = dragon_currency.get(user_id, 0)
    
    if bet <= 0:
        await interaction.response.send_message("🔥 *Grrr...* Shart lagane ke liye kam se kam `1 Crystal` hona chahiye!", ephemeral=True)
        return
        
    if current_balance < bet:
        await interaction.response.send_message(f"🔥 *Growls...* Tumhare paas sirf `{current_balance}` Crystals hain, tum `{bet}` ki shart nahi laga sakte! Pehle `/hunt` karo.", ephemeral=True)
        return
        
    # Flip the coin
    result = random.choice(["heads", "tails"])
    
    if choice.value == result:
        dragon_currency[user_id] = current_balance + bet
        await interaction.response.send_message(f"🪙 **Coinflip:** Sikka ghuma... aur **{result.upper()}** aaya! 🎉 Tum jeet gaye! Tumhe **{bet}** Crystals mile! Total: `{dragon_currency[user_id]}`")
    else:
        dragon_currency[user_id] = current_balance - bet
        await interaction.response.send_message(f"🪙 **Coinflip:** Sikka ghuma... aur **{result.upper()}** aaya. 💀 Oh no! Tum shart haar gaye aur **{bet}** Crystals kho diye. Total: `{dragon_currency[user_id]}`")

# --- 6. NEW GAME: SLOTS (`/slots`) ---
@bot.tree.command(name="slots", description="Play the Dragon Slot Machine! (Cost: 10 Crystals)")
async def slots(interaction: discord.Interaction):
    user_id = interaction.user.id
    current_balance = dragon_currency.get(user_id, 0)
    cost = 10
    
    if current_balance < cost:
        await interaction.response.send_message(f"🔥 *Coughs smoke...* Slot machine chalane ke liye `{cost} Crystals` chahiye! Tumhare paas sirf `{current_balance}` hain.", ephemeral=True)
        return
        
    # Deduct cost
    dragon_currency[user_id] = current_balance - cost
    
    items = ["🐉", "💎", "⚔️", "🔥", "🍉"]
    slot1 = random.choice(items)
    slot2 = random.choice(items)
    slot3 = random.choice(items)
    
    embed = discord.Embed(title="🎰 ETERNAL DRAGON SLOTS 🎰", color=discord.Color.gold())
    embed.description = f"\n> **[ {slot1} | {slot2} | {slot3} ]**\n"
    
    # Win Conditions
    if slot1 == slot2 == slot3:
        # Jackpot!
        reward = 150
        dragon_currency[user_id] += reward
        embed.add_field(name="🎉 JACKPOT!!! 🎉", value=f"Saare items match ho gaye! FlamingDeath ne khush hokar tumhe **{reward}** Crystals diye! 🔥 Total: `{dragon_currency[user_id]}`")
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        # Two Match
        reward = 30
        dragon_currency[user_id] += reward
        embed.add_field(name="✨ Small Win! ✨", value=f"Do items match ho gaye! Tumne **{reward}** Crystals jeete! Total: `{dragon_currency[user_id]}`")
    else:
        # Loss
        embed.add_field(name="💀 No Match!", value=f"Ek bhi item match nahi hua! Tumne 10 Crystals kho diye. Total: `{dragon_currency[user_id]}`")
        
    await interaction.response.send_message(embed=embed)

# --- 7. ADVANCED ROUTING ON MESSAGE HANDLER ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)
    
    is_pinged_or_replied = bot.user.mentioned_in(message)
    if not is_pinged_or_replied and message.reference:
        try:
            replied_to = await message.channel.fetch_message(message.reference.message_id)
            if replied_to.author == bot.user:
                is_pinged_or_replied = True
        except:
            pass

    name_called = "flamingdeath" in message.content.lower()
    should_reply = (message.channel.id == SPECIAL_CHANNEL_ID) or is_pinged_or_replied or name_called

    if should_reply:
        async with message.channel.typing():
            clean_message = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
            
            if not clean_message and message.attachments:
                clean_message = "Look at this file!"
            
            if clean_message:
                attachment_data = None
                if message.attachments:
                    try:
                        file_attachment = message.attachments[0]
                        if file_attachment.content_type:
                            file_response = requests.get(file_attachment.url)
                            attachment_data = {
                                'mime_type': file_attachment.content_type,
                                'data': file_response.content
                            }
                    except Exception as img_err:
                        print(f"Direct text attachment read error: {img_err}")
                
                response = await get_gemini_response(clean_message, message.author.id, attachment_data)
                
                if len(response) > 2000:
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in chunks:
                        await message.reply(chunk, mention_author=False)
                else:
                    await message.reply(response, mention_author=False)
            else:
                if not message.attachments:
                    await message.reply("*Grrr...* Your message is empty!", mention_author=False)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
