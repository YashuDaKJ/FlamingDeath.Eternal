import os
import discord
from discord.ext import commands
import google.generativeai as genai
from threading import Thread
from flask import Flask
import requests
import time  # ⏱️ Perfect loop tracker for chat system cooldowns
import motor.motor_asyncio  # Async MongoDB driver for discord.py

# Import the separated local files
import faction_data
import bot_commands 

app = Flask('')
@app.route('/')
def home(): return "FlamingDeath is perfectly alive and burning!"

def run_web_server():
    port = int(os.getenv("PORT", 7860))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web_server, daemon=True).start()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MONGO_URI = os.getenv('MONGO_URI')  # 🛰️ Linked directly to ClusterEternal variable

if not DISCORD_TOKEN or not GEMINI_API_KEY:
    raise ValueError("DISCORD_TOKEN and GEMINI_API_KEY must be set!")

genai.configure(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Custom Bot Subclass setup to match Eternity's database structural connection
class FlamingDeathBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize Database connection variables
        if not MONGO_URI:
            print("⚠️ WARNING: MONGO_URI environment variable is missing! Database features will fail.")
            self.db_client = None
            self.db = None
            self.profiles = None
        else:
            self.db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
            self.db = self.db_client["eternal_faction_db"]  # Shares the EXACT same DB workspace
            self.profiles = self.db["user_profiles"]         # Synchronized user ledger
            print("🔥 MongoDB Atlas Pipeline: FlamingDeath connected to ClusterEternal successfully!")

bot = FlamingDeathBot()

SPECIAL_CHANNEL_ID = 1521899264265945109
conversation_history = {}

# 🟢 UPGRADE: Local economy/cooldown dictionaries removed! 
# Data queries now leverage self.profiles for permanent persistence across server restarts.

# ⏱️ Chat cooldown tracking array
chat_cooldowns = {}

async def get_gemini_response(user_message: str, user_id: int, attachment_data=None) -> str:
    try:
        if user_id not in conversation_history: 
            conversation_history[user_id] = []
        
        combined_instruction = f"{faction_data.SYSTEM_PROMPT}\n\nAdditional Faction Information:\n{faction_data.FACTION_PROMPT}"
        
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=combined_instruction
        )
        
        if attachment_data:
            response = model.generate_content([user_message, attachment_data])
            return response.text
            
        conversation_history[user_id].append({"role": "user", "parts": [user_message]})
        
        # 📈 OPTIMIZATION: Truncate context BEFORE sending request to guarantee token conservation
        if len(conversation_history[user_id]) > 15: 
            conversation_history[user_id] = conversation_history[user_id][-15:]
            
        response = model.generate_content(conversation_history[user_id])
        assistant_message = response.text
        conversation_history[user_id].append({"role": "model", "parts": [assistant_message]})
        
        return assistant_message
    except Exception as e:
        print(f"Error captured in FlamingDeath Gemini Call: {e}")
        if "429" in str(e) or "quota" in str(e).lower():
            return "*ROAARRR!* 🎙️ *My fiery broadcast is currently choked by static! Let the flames cool down for a moment, darling, and try again shortly!*"
        return f"*ROAARRR!* 🎙️ *An unexpected disturbance in the airwaves! Let us ignite the transmission again shortly.*"

@bot.event
async def on_ready():
    print(f'{bot.user.name} is online!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over Eternal"))
    
    try:
        # Pass the bot client instance cleanly to let commands hook into bot.profiles database paths
        await bot_commands.setup(bot, conversation_history, get_gemini_response)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Sync error: {e}")

@bot.event
async def on_message(message):
    if message.author.bot or message.mention_everyone: return
    
    # 🛡️ ARCHITECTURAL INTERCEPT: Prevent command text patterns from filtering down into the AI generator
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
    
    content_lower = message.content.lower()
    
    if "nice" in content_lower:
        try: await message.add_reaction("🔥")
        except: pass

    is_gif = "tenor.com" in content_lower or "giphy.com" in content_lower
    if not is_gif and message.attachments:
        is_gif = any(att.filename.lower().endswith('.gif') for att in message.attachments)
        
    if is_gif:
        print(f"⚡ [GIF Detected] in channel {message.channel.id} by {message.author}")

    if content_lower == "let's burn" or content_lower == "!firegif":
        dragon_gif_url = "https://tenor.com/view/dragon-fire-breathe-fire-fantasy-creature-gif-17482329"
        await message.channel.send(dragon_gif_url)
        return  

    is_pinged_or_replied = bot.user.mentioned_in(message)
    if not is_pinged_or_replied and message.reference:
        try:
            replied_to = await message.channel.fetch_message(message.reference.message_id)
            if replied_to.author == bot.user: is_pinged_or_replied = True
        except: pass

    name_called = "flamingdeath" in content_lower
    if (message.channel.id == SPECIAL_CHANNEL_ID) or is_pinged_or_replied or name_called:
        
        # ⏱️ IMPLEMENTATION: 5-Second Cooldown Verification Matrix
        current_time = time.time()
        user_id = message.author.id
        if user_id in chat_cooldowns:
            elapsed = current_time - chat_cooldowns[user_id]
            if elapsed < 5:
                remaining = int(5 - elapsed)
                try:
                    await message.reply(f"⏰ *Hold your flames, champion! Wait {remaining}s before broadcasting again.*", delete_after=3)
                except: pass
                return
        
        chat_cooldowns[user_id] = current_time

        async with message.channel.typing():
            clean_message = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
            
            if not clean_message and is_gif: 
                clean_message = "Look at this GIF I sent you!"
            elif not clean_message and message.attachments: 
                clean_message = "Look at this file!"
                
            if clean_message:
                attachment_data = None
                if message.attachments:
                    try:
                        file_attachment = message.attachments[0]
                        if file_attachment.content_type:
                            file_response = requests.get(file_attachment.url)
                            attachment_data = {'mime_type': file_attachment.content_type, 'data': file_response.content}
                    except: pass
                response = await get_gemini_response(clean_message, message.author.id, attachment_data)
                if len(response) > 2000:
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in chunks: await message.reply(chunk, mention_author=False)
                else:
                    await message.reply(response, mention_author=False)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
