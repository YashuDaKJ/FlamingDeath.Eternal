import io
import asyncio
import urllib.parse
from bs4 import BeautifulSoup

import discord
from discord.ext import commands
from discord import app_commands
import faction_data

SPECIAL_CHANNEL_ID = 1521899264265945109
ADMIN_IDS = [1477528681709830297]

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def build_help_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🔥 FlamingDeath Command Center 🔥", 
        description="Welcome Eternal member! Here is the full list of operational commands:", 
        color=discord.Color.teal()
    )

    embed.add_field(
        name="🐉 General & Utility Commands",
        value=(
            "`/ping` - Check latency matrix.\n"
            "`/ask <question>` - Ask FlamingDeath anything.\n"
            "`/copy` - Echo or send text anonymously (Admin).\n"
            "`/remember <topic> <info>` - Save faction info to DB.\n"
            "`/recall <topic>` - Recall saved faction info.\n"
            "`/readweb <url>` - Summarize web page content.\n"
            f"💬 **Chat Mode:** Talk directly in <#{SPECIAL_CHANNEL_ID}> without pings!"
        ),
        inline=False
    )

    embed.add_field(
        name="🎨 AI & Vision Commands",
        value=(
            "`/imagine <prompt>` - Generate AI images via Pollinations.ai!\n"
            "`/analyze <prompt> <attachment>` - Analyze images, videos, or audio."
        ),
        inline=False
    )

    embed.add_field(
        name="⚔️ RPG Games & Economy System",
        value=(
            "`/flamy-oracle` - Interactive Faction Dashboard.\n"
            "`/profile [member]` - View Eternal member card & Crystals.\n"
            "`/daily` - Claim daily rations & maintain streak.\n"
            "`/work` - Complete faction tasks for Crystals.\n"
            "`/crime` - Attempt high-risk raids for Crystals.\n"
            "`/slots <bet>` - Play Dragon Slot Machine.\n"
            "`/hunt` - Hunt beasts for rare crystal rewards.\n"
            "`/coinflip <heads/tails> <bet>` - 50/50 crystal wager.\n"
            "`/play` - Mini RPG challenges.\n"
            "`/leaderboard` - Top crystal hoarders in the faction.\n"
            "`/match <member>` - Test compatibility with a member.\n"
            "`/calc <expr>` - Quick math calculator."
        ),
        inline=False
    )

    embed.set_footer(text="Guarding Eternal Faction | Type !flamy help anytime")
    return embed

class FactionBotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_words = ["nsfw", "nude", "blood", "gore", "explicit"]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.content.lower().strip() == "!flamy help":
            embed = build_help_embed()
            await message.channel.send(embed=embed)

    async def _async_fetch_web_content(self, url: str) -> str:
        try:
            async with self.bot.session.get(url, headers=DEFAULT_HEADERS, timeout=10) as resp:
                if resp.status != 200:
                    return "Error: Website could not be reached."
                html_text = await resp.text()

            soup = BeautifulSoup(html_text, 'html.parser')
            for script in soup(["script", "style"]): 
                script.extract()
                
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            clean_text = '\n'.join(chunk for chunk in lines if chunk)
            return clean_text[:1500]
        except Exception as e:
            return f"Error: {str(e)}"

    @app_commands.command(name="help", description="Show all available features of FlamingDeath")
    async def help_command(self, interaction: discord.Interaction):
        embed = build_help_embed()
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="imagine", description="Generate an AI image using Pollinations.ai")
    @app_commands.describe(prompt="Describe the image you want to create")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def imagine(self, interaction: discord.Interaction, prompt: str):
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in self.banned_words):
            await interaction.response.send_message(
                "🚫 *This prompt contains restricted terms. Please keep it clean!*", 
                ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            encoded_prompt = urllib.parse.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?safe=true&width=1024&height=1024&nologo=true"

            async with self.bot.session.get(image_url, headers=DEFAULT_HEADERS, timeout=15) as resp:
                if resp.status != 200:
                    await interaction.followup.send("🔥 *Grrr...* Cloudflare or Image service blocked the request. Try again shortly!")
                    return
                image_bytes = await resp.read()

            file = discord.File(fp=io.BytesIO(image_bytes), filename="generated_art.png")

            embed = discord.Embed(
                title="✨ Generated AI Art",
                description=f"**Prompt:** {prompt}",
                color=discord.Color.blue()
            )
            embed.set_image(url="attachment://generated_art.png")
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name}", 
                icon_url=interaction.user.display_avatar.url
            )

            await interaction.followup.send(embed=embed, file=file)

        except Exception as e:
            await interaction.followup.send(f"🔥 *Grrr...* Image generation failed: {str(e)}")

    @app_commands.command(name="ask", description="Ask FlamingDeath anything, anywhere!")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        try:
            answer = await self.bot.get_gemini_response(question, interaction.user.id)
            formatted_response = f"**Your question:** {question}\n\n**Answer:** {answer}"
            if len(formatted_response) > 2000:
                await interaction.followup.send(f"**Your question:** {question}")
                chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
                for chunk in chunks:
                    await interaction.followup.send(f"**Answer (part):** {chunk}")
            else:
                await interaction.followup.send(formatted_response)
        except Exception as e:
            await interaction.followup.send(f"🔥 *Grrr...* Error: {str(e)}")

    @app_commands.command(name="remember", description="Make the Dragon remember a faction detail or rule")
    async def remember(self, interaction: discord.Interaction, topic: str, information: str):
        await interaction.response.defer()
        if self.bot.db is not None:
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
        if self.bot.db is not None:
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
        
        web_raw_data = await self._async_fetch_web_content(url)
        
        if "Error:" in web_raw_data:
            await interaction.followup.send(f"🔥 {web_raw_data}")
            return
            
        try:
            ai_prompt = f"Summarize the web page content concisely:\nWebsite URL: {url}\nWebsite Content:\n{web_raw_data}"
            summary = await self.bot.get_gemini_response(ai_prompt, interaction.user.id)
            
            await interaction.followup.send(f"🌐 **Web Reader Report:** {url}\n\n{summary}")
        except Exception as e:
            await interaction.followup.send(f"🔥 Web read error: {str(e)}")

    @app_commands.command(name="copy", description="Copy a message, send text, or reply anonymously (Admin Only)")
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
                    await interaction.followup.send(f"🤫 **Secret Output:** Replied to message `{msg_id}` in {interaction.channel.mention}!", ephemeral=True)
                else:
                    files = [await attachment.to_file() for attachment in original_msg.attachments]
                    new_msg = await destination.send(content=original_msg.content, files=files)
                    
                    for reaction in original_msg.reactions:
                        try:
                            await new_msg.add_reaction(reaction.emoji)
                        except discord.HTTPException:
                            pass
                    
                    await interaction.followup.send(f"🤫 **Secret Output:** Cloned message `{msg_id}` to {destination.mention}!", ephemeral=True)
            else:
                await destination.send(content=message_input)
                await interaction.followup.send(f"🤫 **Secret Output:** Dispatched text directly to {destination.mention}!", ephemeral=True)

        except discord.NotFound:
            await interaction.followup.send(f"❌ Could not find message ID `{message_input}` in this channel.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(f"❌ I lack permission to send messages in {destination.mention}.", ephemeral=True)
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
            if hasattr(self.bot, 'session') and self.bot.session:
                async with self.bot.session.get(attachment.url, headers=DEFAULT_HEADERS) as resp:
                    if resp.status == 200:
                        file_bytes = await resp.read()
                        attachment_data = {'mime_type': attachment.content_type, 'data': file_bytes}
            
            if attachment_data and hasattr(self.bot, 'get_gemini_response'):
                response_text = await self.bot.get_gemini_response(prompt, interaction.user.id, attachment_data)
                await interaction.followup.send(f"🐉 **FlamingDeath Vision:** {response_text}")
            else:
                await interaction.followup.send("🔥 Could not download attachment or Gemini handler missing.")
        except Exception as e:
            await interaction.followup.send(f"🔥 Error: {str(e)}")

    @imagine.error
    @ask.error
    @readweb.error
    @analyze.error
    async def command_cooldown_error_handler(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = f"⏰ *Hold your horses! Command cooling down. Try again in {error.retry_after:.1f}s.*"
        else:
            msg = f"🔥 Execution error: {str(error)}"

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(FactionBotCommands(bot))
        
