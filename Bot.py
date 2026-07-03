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

# Store conversation history for context (optional, per user)
conversation_history = {}

async def get_gemini_response(user_message: str, user_id: int) -> str:
    """
    Get a response from Gemini API using conversation history.
    """
    try:
        # Initialize conversation history for user if not exists
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        # Add user message to history
        conversation_history[user_id].append({
            "role": "user",
            "parts": [user_message]
        })
        
        # Create model and send message with system prompt
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        # Send the entire conversation history for context
        response = model.generate_content(conversation_history[user_id])
        
        assistant_message = response.text
        
        # Add

