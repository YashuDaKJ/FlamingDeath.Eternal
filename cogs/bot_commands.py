import asyncio
import requests
from bs4 import BeautifulSoup

import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import faction_data

SPECIAL_CHANNEL_ID = 1521899264265945109
ADMIN_IDS = [1477528681709830297]

def fetch_web_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Error: Website could not be reached."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]): 
            script.extract()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        clean_text = '\n'.join(chunk for chunk in lines if chunk)
        return clean_text[:1500]
    except Exception as e:
        return f"Error: {str(e)}"

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
            embed.add_field(name="`/ask`", value="Ask FlamingDeath a question.", inline=False)
            embed.add_field(name="`/copy`", value="Copy/Echo a message, reply, or send files.", inline=False)
            embed.add_field(name="`/remember`", value="Save faction info to the database.", inline=False)
            embed.add_field(name="`/recall`", value="Recall remembered info.", inline=False)
            embed.add_field(name="`/readweb`", value="Summarize web page content.", inline=False)
            embed.add_field(name="💬 Chat Mode", value=f"Talk directly in <#{SPECIAL_CHANNEL_ID}> without pings!", inline=False)
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "AI Multimedia":
            embed = discord.Embed(title="🎨 AI Multimedia Commands", color=discord.Color.teal())
            embed.add_field(name="`/analyze`", value="Upload an image, video, or audio file for Dragon Vision!", inline=False)
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "Faction Games & RPG":
            embed = discord.Embed(title="⚔️ Faction Games & Economy System", color=discord.Color.dark_red())
            embed.add_field(name="`/profile`", value="View your member card and Crystal balance.", inline=False)
            embed.add_field(name="`/play`", value="Embark on interactive journeys to hunt for Crystals (1h cooldown).", inline=False)
            embed.add_field(name="`/hunt`", value="Hunt for Dragon Crystals (1h cooldown).", inline=False)
            embed.add_field(name="`/coinflip`", value="Bet crystals on Heads or Tails!", inline=False)
            embed.add_field(name="`/slots`", value="Try your luck on the Dragon Slot Machine (Cost: 10 Crystals).", inline=False)
            await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())

class FactionBotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ping', description="Check the operational response latency matrix")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"*Grrr...* Pong! My flames reached you in {latency}ms!")

    @app_commands.command(name="help", description="Show all available features of FlamingDeath")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔥 FlamingDeath Command Center 🔥", 
            description="Welcome, Eternal member! Select a category from the menu below.", 
            color=discord.Color.teal()
        )
        embed.set_footer(text="Guarding Eternal since 2025")
        await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=False)

    @app_commands.command(name="ask", description="Ask FlamingDeath anything, anywhere!")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        try:
            combined_instruction = f"{faction_data.SYSTEM_PROMPT}\n\nAdditional Faction Information:\n{faction_data.FACTION_PROMPT}"
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=combined_instruction)
            
            response = await asyncio.to_thread(model.generate_content, question)
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
            if "429" in str(e) or "quota" in str(e).lower():
                await interaction.followup.send("🔥 *ROAARRR!* Fiery broadcast choked by static! Try again shortly!")
            else:
                await interaction.followup.send(f"🔥 *Grrr...* Error: {str(e)}")

    @app_commands.command(name="remember", description="Make the Dragon remember a faction detail or rule")
    async def remember(self, interaction: discord.Interaction, topic: str, information: str):
        await interaction.response.defer()
        if self.bot.db:
            memory_coll = self.bot.db["faction_shared_memory"]
            await memory_coll.update_one(
                {"_id": topic.lower().strip()},
                {"$set": {"info": information}},
                upsert=True
            )
            await interaction.followup.send(f"📥 **Memory Updated!** Saved detail for `{topic}`.")
        else:
            await interaction.followup.send("❌ Database connection error.")

    @app_commands.command(name="recall", description="Ask the Dragon to recall something it remembered")
    async def recall(self, interaction: discord.Interaction, topic: str):
        await interaction.response.defer()
        info = None
        if self.bot.db:
            memory_coll = self.bot.db["faction_shared_memory"]
            doc = await memory_coll.find_one({"_id": topic.lower().strip()})
            if doc:
                info = doc.get("info")

        if info:
            await interaction.followup.send(f"🧠 **Memory Box:** Data regarding `{topic}`:\n> {info}")
        else:
            await interaction.followup.send(f"🔍 I do not have memory entries for `{topic}`.")

    @app_commands.command(name="readweb", description="Provide a URL to summarize it")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def readweb(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        
        web_raw_data = await asyncio.to_thread(fetch_web_content, url)
        
        if "Error:" in web_raw_data:
            await interaction.followup.send(f"🔥 {web_raw_data}")
            return
            
        try:
            combined_instruction = f"{faction_data.SYSTEM_PROMPT}\n\nAdditional Faction Information:\n{faction_data.FACTION_PROMPT}\n\nSummarize the raw text content below into a concise report."
            model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=combined_instruction)
            
            ai_prompt = f"Website URL: {url}\nWebsite Content:\n{web_raw_data}"
            
            response = await asyncio.to_thread(model.generate_content, ai_prompt)
            summary = response.text
            
            await interaction.followup.send(f"🌐 **Web Reader Report:** {url}\n\n{summary}")
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                await interaction.followup.send("🔥 *ROAARRR!* Rate limit hit! Try again shortly!")
            else:
                await interaction.followup.send(f"🔥 Web read error: {str(e)}")

    # ----------------------------------------------------
    # UPDATED COPY COMMAND
    # ----------------------------------------------------
    @app_commands.command(name="copy", description="Copy a message, send text, or reply to a message anonymously (Admin Only)")
    @app_commands.describe(
        message_input="Enter raw text to send OR a Message ID to target",
        reply_text="Optional text to reply directly to the target Message ID",
        target_channel="The channel where the message should be sent (Optional)"
    )
    async def copy(
        self, 
        interaction: discord.Interaction, 
        message_input: str,
        reply_text: str = None,
        target_channel: discord.TextChannel = None
    ):
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("🔥 *Growls...* Only the high keepers can command me!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        destination = target_channel or interaction.channel

        try:
            if message_input.strip().isdigit():
                msg_id = int(message_input.strip())
                original_msg = await interaction.channel.fetch_message(msg_id)
                
                if reply_text:
                    await original_msg.reply(reply_text)
                    await interaction.followup.send(
                        f"🤫 **Secret Output:** Replied to message `{msg_id}` in {interaction.channel.mention}!", 
                        ephemeral=True
                    )
                else:
                    files = []
                    for attachment in original_msg.attachments:
                        files.append(await attachment.to_file())
                    
                    new_msg = await destination.send(content=original_msg.content, files=files)
                    
                    for reaction in original_msg.reactions:
                        try:
                            await new_msg.add_reaction(reaction.emoji)
                        except discord.HTTPException:
                            pass
                    
                    await interaction.followup.send(
                        f"🤫 **Secret Output:** Cloned message `{msg_id}` (including attachments and reactions) to {destination.mention}!", 
                        ephemeral=True
                    )
            else:
                await destination.send(content=message_input)
                await interaction.followup.send(
                    f"🤫 **Secret Output:** Dispatched text directly to {destination.mention}!", 
                    ephemeral=True
                )

        except discord.NotFound:
            await interaction.followup.send(f"❌ Could not find message ID `{message_input}` in this channel.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(f"❌ I lack permission to send messages or add reactions in {destination.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Copy execution error: {str(e)}", ephemeral=True)

    @app_commands.command(name="analyze", description="Let FlamingDeath look at your photos, videos, or audio files")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def analyze(self, interaction: discord.Interaction, prompt: str, attachment: discord.Attachment):
        await interaction.response.defer()
        if not attachment.content_type:
            await interaction.followup.send("🔥 *Grrr...* I can't read this file format!")
            return
        try:
            attachment_data = None
            if self.bot.session:
                async with self.bot.session.get(attachment.url) as resp:
                    if resp.status == 200:
                        file_bytes = await resp.read()
                        attachment_data = {'mime_type': attachment.content_type, 'data': file_bytes}
            
            if attachment_data:
                response_text = await self.bot.get_gemini_response(prompt, interaction.user.id, attachment_data)
                await interaction.followup.send(f"🐉 **FlamingDeath Vision:** {response_text}")
            else:
                await interaction.followup.send("🔥 Could not download attachment.")
        except Exception as e:
            await interaction.followup.send(f"🔥 Error: {str(e)}")

    @ask.error
    @readweb.error
    @analyze.error
    async def command_cooldown_error_handler(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏰ *Hold your horses! Command cooling down. Try again in {error.retry_after:.1f}s.*", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(f"🔥 Execution error: {str(error)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(FactionBotCommands(bot))
        
