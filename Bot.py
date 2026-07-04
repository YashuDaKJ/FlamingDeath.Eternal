import os
import discord
from discord.ext import commands
import google.generativeai as genai
from threading import Thread
from flask import Flask

# 1. SETUP FLASK SERVER FIRST FOR RENDER
app = Flask('')

@app.route('/')
def home():
    return "FlamingDeath is perfectly alive and burning!"

def run_web_server():
    # Render requires port 10000 or the one given in environment
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
- Answer directly without spinning long stories.

Remember: You are a proud, cool, and super friendly dragon guardian. Keep it simple, short, fun, and protective of Eternal!"""

conversation_history = {}

async def get_gemini_response(user_message: str, user_id: int) -> str:
    try:
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        conversation_history[user_id].append({
            "role": "user",
            "parts": [user_message]
        })
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
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
    print('Bot is online!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over Eternal"))

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"*Grrr...* Pong! My flames reached you in {latency}ms!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)
    
    if bot.user.mentioned_in(message) or message.reference:
        is_reply_to_bot = False
        if message.reference:
            try:
                replied_to = await message.channel.fetch_message(message.reference.message_id)
                is_reply_to_bot = replied_to.author == bot.user
            except:
                pass
        
        if bot.user.mentioned_in(message) or is_reply_to_bot:
            async with message.channel.typing():
                clean_message = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
                if clean_message:
                    response = await get_gemini_response(clean_message, message.author.id)
                    if len(response) > 2000:
                        chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                        for chunk in chunks:
                            await message.reply(chunk, mention_author=False)
                    else:
                        await message.reply(response, mention_author=False)
                else:
                    await message.reply("*Grrr...* Your message is empty!", mention_author=False)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
