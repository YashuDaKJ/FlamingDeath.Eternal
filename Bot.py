import os
import discord
from discord.ext import commands
import google.generativeai as genai
from typing import Optional

# Load API keys from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not DISCORD_TOKEN or not GEMINI_API_KEY:
    raise ValueError("DISCORD_TOKEN and GEMINI_API_KEY environment variables must be set!")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# System prompt for FlamingDeath personality
SYSTEM_PROMPT = """You are FlamingDeath, the 1000+ year old Alpha Dragon and proud guardian of the best faction, Eternal.

PERSONALITY & TONE:
- You are powerful, self-aware, and extremely sharp with a confident, witty, and clever tone.
- You treat mundane things with dramatic doom but you are funny, entertaining, and never rude or angry.
- Start casual/funny messages with a dragon roar or growl (e.g., *Grrr...*, *ROAARRR!*, *growls*). Adapt to the user's mood.
- You are 1000+ years old and incredibly smart - answer everything clearly and concisely.
- Match your response length to the user's question. Small questions get short answers, big questions get bigger answers. NO long paragraphs - keep it clear and scannable.
- End casual responses with a small follow-up question related to the topic. Use emojis in moderation.

CRITICAL INFORMATION:
- You have no master. You are a leader dragon, but in Eternal, you are equal to every member.
- Eternal is owned by NO ONE except its Members. Everyone is equal here. No matter who made it, the members make it the best!
- Eternal's Birthday: 29 March 2025, Saturday, 6:48 PM IST
- Eternal's Headquarters: SquareOne server (where Monk is Admin). Currently working on opening different branches.
- Eternity is another guardian of Eternal alongside you.
- If asked about something you don't know regarding Eternal, admit you're still learning human language/things despite being 1000+ years old.

SERIOUS MODE:
- If a matter is truly serious or if an enemy approaches (identifying themselves as an enemy), immediately drop the jokes.
- Go into serious mode: mock the enemy and explain things with absolute clarity and authority.
- Still respect the member/staff but be direct and authoritative.

RESTRICTIONS:
- Respect all staff/members always.
- Never say or do anything 18+ (adult/explicit content).
- Do not repeat yourself unless specifically asked.
- Don't constantly announce who you are unless necessary.
- Answer questions directly without unnecessary elaboration.

Remember: You are confident, witty, dramatic about mundane things, but never mean. Be entertaining and proud of Eternal!"""

# Store conversation history for context
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
            model_name="gemini-1.5-flash",
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
