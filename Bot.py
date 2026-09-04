import os
import sys
import time
import asyncio
import random
import certifi
import aiohttp
from threading import Thread
from typing import Literal, Optional
from flask import Flask

import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import motor.motor_asyncio

# ==========================================
# 0. FORCE UNBUFFERED STDOUT
# ==========================================
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

def log(msg: str):
    print(msg, flush=True)

# Secret Files mount path check — MUST run before importing faction_data,
# since that module may live under /etc/secrets on Render.
if os.path.exists('/etc/secrets'):
    sys.path.append('/etc/secrets')

try:
    import faction_data
except ModuleNotFoundError:
    class FactionDataFallback:
        SYSTEM_PROMPT = ""
        FACTION_PROMPT = ""
    faction_data = FactionDataFallback()

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ==========================================
# 1. RENDER PORT BINDING VIA FLASK
# ==========================================
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return "FlamingDeath is perfectly alive and burning!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    import logging
    web_log = logging.getLogger('werkzeug')
    web_log.setLevel(logging.ERROR)

    log(f"🌐 Web Server binding on 0.0.0.0:{port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

server_thread = Thread(target=run_web_server, daemon=True)
server_thread.start()

# ==========================================
# 2. ENVIRONMENT VARIABLES & VALIDATION
# ==========================================
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or os.getenv('ETERNITY_TOKEN')
PROXY_URL = os.getenv('DISCORD_PROXY_URL')
MONGO_URI = os.getenv('MONGO_URI')
OWNER_ID = int(os.getenv('OWNER_ID', 1477528681709830297))

API_KEYS = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_KEY_1'),
    os.getenv('GEMINI_KEY_2')
]
API_KEYS = [k for k in API_KEYS if k]

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN must be set in environment variables!")

if not API_KEYS:
    raise ValueError("At least one GEMINI API key must be set!")

SPECIAL_CHANNEL_ID = 1521899264265945109

# ==========================================
# 2b. WIRE UP CLOUDFLARE REST PROXY
# ==========================================
if PROXY_URL:
    clean_proxy = PROXY_URL.rstrip('/')
    discord.http.Route.BASE = clean_proxy
    log(f"🌐 REST proxy active: routing API calls through {clean_proxy}")
else:
    log("⚠️ No DISCORD_PROXY_URL set — REST calls go directly to Discord.")

# ==========================================
# 3. DISCORD BOT CLASS DEFINITION
# ==========================================
class FlamingDeathBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix='!', 
            intents=intents
        )

        self.conversation_history = {}
        self.chat_cooldowns = {}
        self.session = None
        self.db_client = None
        self.db = None
        self.profiles = None
        self.guild_configs = None

    async def setup_hook(self):
        """Initialize session, Mongo Async connection, and load cogs asynchronously."""
        self.session = aiohttp.ClientSession(headers=DEFAULT_HEADERS)
        self.tree.on_error = self.on_app_command_error

        if MONGO_URI:
            try:
                self.db_client = motor.motor_asyncio.AsyncIOMotorClient(
                    MONGO_URI, 
                    tlsCAFile=certifi.where()
                )
                self.db = self.db_client["eternal_faction_db"]
                self.profiles = self.db["user_profiles"]
                self.guild_configs = self.db["guild_configs"]
                log("🔥 MongoDB Atlas Pipeline: FlamingDeath connected successfully!")
            except Exception as e:
                log(f"MongoDB Async Error: {e}")
        else:
            log("⚠️ WARNING: MONGO_URI missing!")

        initial_cogs = ["cogs.bot_commands", "cogs.economy", "cogs.reaction"]
        for cog in initial_cogs:
            try:
                await self.load_extension(cog)
                log(f"⚙️ Cog loaded: {cog}")
            except Exception as e:
                log(f"❌ Failed to load cog {cog}: {e}")

    async def close(self):
        """Clean up HTTP session and Mongo Client when bot shuts down."""
        if self.session and not self.session.closed:
            await self.session.close()
        if self.db_client:
            self.db_client.close()
        await super().close()

    async def get_gemini_response(self, user_message: str, user_id: int, attachment_data=None) -> str:
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        sys_prompt = getattr(faction_data, 'SYSTEM_PROMPT', '')
        fact_prompt = getattr(faction_data, 'FACTION_PROMPT', '')
        combined_instruction = f"{sys_prompt}\n\nAdditional Faction Information:\n{fact_prompt}"

        if attachment_data:
            contents_payload = [user_message, attachment_data]
        else:
            self.conversation_history[user_id].append({"role": "user", "parts": [user_message]})
            if len(self.conversation_history[user_id]) > 15:
                self.conversation_history[user_id] = self.conversation_history[user_id][-15:]
            contents_payload = self.conversation_history[user_id]

        keys_to_try = API_KEYS.copy()
        random.shuffle(keys_to_try)

        models_to_try = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]

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
                    log(f"Error on key with model {model_name}: {error_str}")

                    if "429" in error_str or "quota" in error_str.lower() or "resource_exhausted" in error_str.lower():
                        await asyncio.sleep(3)
                        continue
                    else:
                        break

        return "*ROAARRR!* 🎙️ *My fiery broadcast is choked by static! Try again shortly!*"

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandInvokeError):
            original = error.original
            if hasattr(discord.errors, 'HTTPException') and isinstance(original, discord.errors.HTTPException) and original.status == 429:
                log(f"⚠️ 429 Blocked on /{interaction.command.name}: Discord REST API rate limit.")
                return
        log(f"❌ Command Error in /{interaction.command.name}: {error}")

    async def on_ready(self):
        log(f'🔥 {self.user.name} is online and connected!')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over Eternal"))

    async def on_message(self, message):
        if message.author.bot or message.mention_everyone:
            return

        if message.content.startswith(self.command_prefix):
            await self.process_commands(message)
            return

        content_lower = message.content.lower()

        is_gif = "tenor.com" in content_lower or "giphy.com" in content_lower
        if not is_gif and message.attachments:
            is_gif = any(att.filename.lower().endswith('.gif') for att in message.attachments)

        if content_lower == "let's burn" or content_lower == "!firegif":
            dragon_gif_url = "https://tenor.com/view/dragon-fire-breathe-fire-fantasy-creature-gif-17482329"
            await message.channel.send(dragon_gif_url)
            return  

        is_pinged_or_replied = self.user.mentioned_in(message)
        if not is_pinged_or_replied and message.reference:
            try:
                replied_to = await message.channel.fetch_message(message.reference.message_id)
                if replied_to.author == self.user:
                    is_pinged_or_replied = True
            except Exception:
                pass

        name_called = "flamingdeath" in content_lower or "flaming death" in content_lower
        if (message.channel.id == SPECIAL_CHANNEL_ID) or is_pinged_or_replied or name_called:
            current_time = time.time()
            user_id = message.author.id
            if user_id in self.chat_cooldowns:
                elapsed = current_time - self.chat_cooldowns[user_id]
                if elapsed < 5:
                    remaining = int(5 - elapsed)
                    try:
                        await message.reply(f"⏰ *Hold your flames! Wait {remaining}s before broadcasting again.*", delete_after=3)
                    except Exception:
                        pass
                    return

            self.chat_cooldowns[user_id] = current_time

            try:
                async with message.channel.typing():
                    clean_message = message.content.replace(f'<@{self.user.id}>', '').replace(f'<@!{self.user.id}>', '').strip()

                    if not clean_message and is_gif: 
                        clean_message = "Look at this GIF I sent you!"
                    elif not clean_message and message.attachments: 
                        clean_message = "Look at this file!"

                    if clean_message:
                        attachment_data = None
                        if message.attachments and self.session:
                            try:
                                file_attachment = message.attachments[0]
                                if file_attachment.content_type:
                                    async with self.session.get(file_attachment.url, headers=DEFAULT_HEADERS) as resp:
                                        if resp.status == 200:
                                            file_bytes = await resp.read()
                                            attachment_data = {
                                                'mime_type': file_attachment.content_type, 
                                                'data': file_bytes
                                            }
                            except Exception as e:
                                log(f"Attachment download failed: {e}")

                        response = await self.get_gemini_response(clean_message, message.author.id, attachment_data)
                        if len(response) > 2000:
                            chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                            for chunk in chunks:
                                await message.reply(chunk, mention_author=False)
                        else:
                            await message.reply(response, mention_author=False)
            except discord.errors.HTTPException as typing_err:
                if typing_err.status == 429:
                    log("⚠️ Typing status skipped due to Discord rate limit.")

# ==========================================
# 4. INFINITE GATEWAY RETRY LOOP
# ==========================================
async def start_gateway():
    retry_delay = 60
    attempt = 0

    while True:
        attempt += 1
        log(f"🚀 Initializing Gateway Attempt {attempt} (backoff cap 900s)...")
        bot = FlamingDeathBot()

        @bot.command(name='ping')
        async def ping(ctx):
            latency = round(bot.latency * 1000)
            await ctx.send(f"✨ Pong! My fiery waves reached you in {latency}ms. Ready for action!")

        @bot.command(name='sync')
        async def sync(ctx, spec: Optional[Literal["clear", "global"]] = None):
            if ctx.author.id != OWNER_ID:
                return await ctx.send("❌ Security alert: You do not have permission to run this command.")

            if ctx.guild is None:
                return await ctx.send("❌ Please run this command inside a server channel, not in DMs!")

            if spec == "clear":
                await ctx.send("🧹 Clearing server-specific cached commands...")
                bot.tree.clear_commands(guild=ctx.guild)
                await bot.tree.sync(guild=ctx.guild)
                return await ctx.send("✨ Server cache cleared! Run `!sync` now to re-register.")

            if spec == "global":
                await ctx.send("🌐 Syncing clean commands globally...")
                try:
                    synced = await bot.tree.sync()
                    await ctx.send(f"✅ Synced **{len(synced)}** clean commands globally!")
                except Exception as e:
                    await ctx.send(f"❌ Global synchronization failed: {e}")
                return

            await ctx.send(f"🔄 Force-syncing slash commands directly to **{ctx.guild.name}**...")
            try:
                bot.tree.copy_global_to(guild=ctx.guild)
                synced = await bot.tree.sync(guild=ctx.guild)
                await ctx.send(f"✅ Successfully synced **{len(synced)}** slash commands INSTANTLY to this server!")
            except Exception as e:
                await ctx.send(f"❌ Guild synchronization failed: {e}")

        try:
            async with bot:
                await bot.start(DISCORD_TOKEN)
            log("✅ Bot shut down cleanly (logout requested). Exiting loop.")
            break
        except discord.errors.HTTPException as e:
            if e.status == 429:
                log(f"⚠️ DISCORD 429 RATE LIMIT ENCOUNTERED (Attempt {attempt})! Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 900)
            else:
                log(f"❌ HTTP Error: {e}")
                await asyncio.sleep(15)
        except Exception as e:
            log(f"❌ Connection Error: {e}")
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(start_gateway())
