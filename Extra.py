import discord
from discord import app_commands
import google.generativeai as genai
import os

ADMIN_IDS = [1477528681709830297] 

def setup_extra_commands(tree: app_commands.CommandTree):
    
    SYSTEM_PROMPT = """You are FlamingDeath, the 1000+ year old Alpha Dragon and the chill, friendly guardian of the best faction, Eternal.
- Speak like a cool modern gamer using simple, casual English.
- Keep responses short, witty, and clear.
- Start casual messages with a playful dragon roar/growl (e.g., *Grrr...*, *ROAARRR!*)."""

    # --- 1. DRAGON ASK COMMAND (/ask) ---
    @tree.command(name="ask", description="Ask FlamingDeath anything, anywhere!")
    @app_commands.describe(question="Your question for the Alpha Dragon")
    async def ask(interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                await interaction.followup.send("🔥 *Coughs smoke* Error: GEMINI_API_KEY not found!")
                return
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash', 
                system_instruction=SYSTEM_PROMPT
            )
            
            response = model.generate_content(question)
            answer = response.text
            formatted_response = f"**Your question:** {question}\n\n**Answer:** {answer}"
            
            if len(formatted_response) > 2000:
                await interaction.followup.send(f"**Your question:** {question}")
                chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
                for chunk in chunks:
                    await interaction.followup.send(f"**Answer (part):** {chunk}")
            else:
                await interaction.followup.send(formatted_response)
                
        except Exception as e:
            await interaction.followup.send(f"🔥 *Grrr...* My dragon senses are failing! Error: {str(e)}")

    # --- 2. DRAGON ACTING COMMAND (/behave) ---
    @tree.command(name="behave", description="Let the Dragon speak and act for you (Admin Only)")
    @app_commands.describe(script="The prompt or announcement for the bot to act out")
    async def behave(interaction: discord.Interaction, script: str):
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("🔥 *Growls...* Only the high keepers can command me!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True) 

        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                await interaction.followup.send("🔥 Error: GEMINI_API_KEY not found!", ephemeral=True)
                return
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash', 
                system_instruction=SYSTEM_PROMPT
            )
            
            acting_prompt = (
                f"Act completely as FlamingDeath. Do not talk to the admin or say 'Sure, I will do this'. "
                f"Directly generate the final text, announcement, or message that needs to be sent "
                f"based on this script: {script}"
            )
            
            response = model.generate_content(acting_prompt)
            acting_message = response.text
            
            if acting_message:
                await interaction.channel.send(acting_message)
                await interaction.followup.send("✅ Script executed successfully!", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ No message was generated.", ephemeral=True)
                
        except Exception as e:
            await interaction.followup.send(f"🔥 Acting error: {str(e)}", ephemeral=True)
            
