import os
import sys
import traceback
import discord
from discord.ext import commands

print("🚀 Starting Bot Launch Sequence (Debug Mode)...")

try:
    # 1. Check Discord Token
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    if not DISCORD_TOKEN:
        print("❌ CRITICAL ERROR: DISCORD_TOKEN is missing from Render Environment Variables!")
        sys.exit(1)
    print("✅ Discord Token Found.")

    # 2. Check Gemini Keys
    API_KEYS = [
        os.getenv('GEMINI_API_KEY'),
        os.getenv('GEMINI_KEY_1'),
        os.getenv('GEMINI_KEY_2')
    ]
    API_KEYS = [k for k in API_KEYS if k]
    if not API_KEYS:
        print("❌ CRITICAL ERROR: No Gemini API keys found in Render Environment Variables!")
        sys.exit(1)
    print(f"✅ Found {len(API_KEYS)} Gemini Key(s).")

    # 3. Setup Minimal Bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'✅ SUCCESS: {bot.user.name} is ONLINE and connected to Discord!')

    # 4. Run the Bot
    print("⏳ Attempting to connect to Discord Gateway...")
    bot.run(DISCORD_TOKEN)

except Exception as e:
    print("\n" + "="*50)
    print(f"💥 PYTHON CRASHED: {type(e).__name__}")
    print(f"Error Message: {e}")
    print("="*50)
    traceback.print_exc()
    print("="*50 + "\n")
    sys.exit(1)
    
