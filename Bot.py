import os
import time
import sys
import asyncio
import random
import certifi
from threading import Thread
from flask import Flask

import discord
from discord.ext import commands
from discord import app_commands  # NAYA IMPORT: Error handler ke liye zaroori hai
import google.generativeai as genai
import motor.motor_asyncio
import aiohttp

import faction_data

# Global Headers to Bypass Cloudflare/Render Bot Blockers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- Web Server Setup for 24/7 Hosting ---
app = Flask('')

@app.route('/')
def home():
    return "FlamingDeath is perfectly alive and burning!"

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web_server, daemon=True).start()

# --- Environment Variables ---
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')

API_KEYS = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_KEY_1'),
    os.getenv('GEMINI_KEY_2')
]
API_KEYS = [k for k in API_KEYS if k]

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN must be set!")

if not API_KEYS:
    raise ValueError("At least one GEMINI key must be set!")

SPECIAL_CHANNEL_ID = 1521899264265945109

class FlamingDeathBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.conversation_history = {}
        self.chat_cooldowns = {}
        self.session = None
        self.db_client = None
        self.db = None
        self.profiles = None

    async def setup_hook(self):
        """Initialize session, Mongo Async connection, and load cogs asynchronously."""
        self.session = aiohttp.ClientSession(headers=DEFAULT_HEADERS)
        
        # Async MongoDB Initialization
        if MONGO_URI:
            try:
                self.db_client = motor.motor_asyncio.AsyncIOMotorClient(
                    MONGO_URI, 
                    tlsCAFile=certifi.where()
                )
                self.db = self.db_client["eternal_faction_db"]
                self.profiles = self.db["user_profiles"]
                print("🔥 MongoDB Atlas Pipeline: FlamingDeath connected successfully!")
            except Exception as e:
                print(f"MongoDB Async Error: {e}")
        else:
            print("⚠️ WARNING: MONGO_URI missing!")

        await self.load_extension("cogs.bot_commands")
        await self.load_extension("cogs.economy")
        await self.load_extension("cogs.reaction")
        print("⚙️ All cogs loaded successfully.")

    async def close(self):
        """Clean up HTTP session and Mongo Client when bot shuts down."""
        if self.session:
            await self.session.close()
        if self.db_client:
            self.db_client.close()
        await super().close()

    async def get_gemini_response(self, user_message: str, user_id: int, attachment_data=None) -> str:
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        combined_instruction = f"{faction_data.SYSTEM_PROMPT}\n\nAdditional Faction Information:\n{faction_data.FACTION_PROMPT}"
        
        if attachment_data:
            contents_payload = [user_message, attachment_data]
        else:
            self.conversation_history[user_id].append({"role": "user", "parts": [user_message]})
            if len(self.conversation_history[user_id]) > 15:
                self.conversation_history[user_id] = self.conversation_history[user_id][-15:]
            contents_payload = self.conversation_history[user_id]

        keys_to_try = API_KEYS.copy()
        random.shuffle(keys_to_try)

        # ✅ NAYA CHANGE: Duplicate model hata diya gaya hai
        models_to_try = ['gemini-2.5-flash']

        for key in keys_to_try:
            genai.configure(api_key=key)
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=combined_instruction
                    )
                    
                    response = await asyncio.to_thread(
                        model.generate_content, contents_payload
                    )
                    assistant_message = response.text
                    
                    if not attachment_data:
                        self.conversation_history[user_id].append({"role": "model", "parts": [assistant_message]})
                    return assistant_message

                except Exception as e:
                    error_str = str(e)
                    print(f"Error on key with model {model_name}: {error_str}")
                    
                    if "429" in error_str or "quota" in error_str.lower() or "resource_exhausted" in error_str.lower():
                        await asyncio.sleep(1)
                        continue
                    else:
                        break

        return "*ROAARRR!* 🎙️ *My fiery broadcast is choked by static! Try again shortly!*"

bot = FlamingDeathBot()

@bot.event
async def on_ready():
    print(f'🔥 {bot.user.name} is online!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over Eternal"))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Sync error: {e}")

# ✅ NAYA CHANGE: Global Error Handler taaki 429 par bot crash na ho
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandInvokeError):
        original = error.original
        if hasattr(discord.errors, 'HTTPException') and isinstance(original, discord.errors.HTTPException) and original.status == 429:
            print(f"⚠️ 429 Blocked on /{interaction.command.name}: Discord REST API rate limit (IP Block).")
            return
    print(f"❌ Command Error in /{interaction.command.name}: {error}")

@bot.event
async def on_message(message):
    if message.author.bot or message.mention_everyone:
        return
    
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
    
    content_lower = message.content.lower()

    is_gif = "tenor.com" in content_lower or "giphy.com" in content_lower
    if not is_gif and message.attachments:
        is_gif = any(att.filename.lower().endswith('.gif') for att in message.attachments)

    if content_lower == "let's burn" or content_lower == "!firegif":
        dragon_gif_url = "https://tenor.com/view/dragon-fire-breathe-fire-fantasy-creature-gif-17482329"
        await message.channel.send(dragon_gif_url)
        return  

    is_pinged_or_replied = bot.user.mentioned_in(message)
    if not is_pinged_or_replied and message.reference:
        try:
            replied_to = await message.channel.fetch_message(message.reference.message_id)
            if replied_to.author == bot.user:
                is_pinged_or_replied = True
        except Exception:
            pass

    name_called = "flamingdeath" in content_lower
    if (message.channel.id == SPECIAL_CHANNEL_ID) or is_pinged_or_replied or name_called:
        current_time = time.time()
        user_id = message.author.id
        if user_id in bot.chat_cooldowns:
            elapsed = current_time - bot.chat_cooldowns[user_id]
            if elapsed < 5:
                remaining = int(5 - elapsed)
                try:
                    await message.reply(f"⏰ *Hold your flames! Wait {remaining}s before broadcasting again.*", delete_after=3)
                except Exception:
                    pass
                return
        
        bot.chat_cooldowns[user_id] = current_time

        async with message.channel.typing():
            clean_message = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
            
            if not clean_message and is_gif: 
                clean_message = "Look at this GIF I sent you!"
            elif not clean_message and message.attachments: 
                clean_message = "Look at this file!"
                
            if clean_message:
                attachment_data = None
                if message.attachments and bot.session:
                    try:
                        file_attachment = message.attachments[0]
                        if file_attachment.content_type:
                            async with bot.session.get(file_attachment.url, headers=DEFAULT_HEADERS) as resp:
                                if resp.status == 200:
                                    file_bytes = await resp.read()
                                    attachment_data = {
                                        'mime_type': file_attachment.content_type, 
                                        'data': file_bytes
                                    }
                    except Exception as e:
                        print(f"Attachment download failed: {e}")

                response = await bot.get_gemini_response(clean_message, message.author.id, attachment_data)
                if len(response) > 2000:
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in chunks:
                        await message.reply(chunk, mention_author=False)
                else:
                    await message.reply(response, mention_author=False)

if __name__ == "__main__":
    print("🚀 Connecting FlamingDeath Gateway...")
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print("⚠️ DISCORD 429 RATE LIMIT ENCOUNTERED! Pausing process to prevent infinite crash loop...")
            time.sleep(120)
        sys.exit(1)
    except Exception as e:
        print(f"❌ LAUNCH CRASH: {e}")
        sys.exit(1)
    
