# bot_commands.py
import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import requests
import random
from datetime import datetime
import faction_data  # Import the secret data file

SPECIAL_CHANNEL_ID = 1521899264265945109
ADMIN_IDS = [1477528681709830297]

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
            embed.add_field(name="`!ping`", value="Check the bot's speed.", inline=False)
            embed.add_field(name="`/ask`", value="Ask FlamingDeath a question from anywhere in the server.", inline=False)
            embed.add_field(name="💬 Chat Mode", value=f"Talk to me directly in <#{SPECIAL_CHANNEL_ID}> without pings!", inline=False)
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "AI Multimedia":
            embed = discord.Embed(title="🎨 AI Multimedia Commands", color=discord.Color.cyan())
            embed.add_field(name="`/analyze`", value="Upload an image, video, or audio file for Dragon Vision!", inline=False)
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "Faction Games & RPG":
            embed = discord.Embed(title="⚔️ Faction Games & Economy System", color=discord.Color.dark_red())
            embed.add_field(name="`/profile`", value="View your Eternal member card and Crystal balance.", inline=False)
            embed.add_field(name="`/hunt`", value="Go out on a hunt to earn Dragon Crystals (1 hour cooldown).", inline=False)
            embed.add_field(name="`/coinflip`", value="Bet your crystals on Heads or Tails!", inline=False)
            embed.add_field(name="`/slots`", value="Try your luck on the Dragon Slot Machine (Cost: 10 Crystals).", inline=False)
            await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())

class FactionBotCommands(commands.Cog):
    def __init__(self, bot, conversation_history, dragon_currency, hunt_cooldowns, get_gemini_response_func):
        self.bot = bot
        self.conversation_history = conversation_history
        self.dragon_currency = dragon_currency
        self.hunt_cooldowns = hunt_cooldowns
        self.get_gemini_response = get_gemini_response_func

    @commands.command(name='ping')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"*Grrr...* Pong! My flames reached you in {latency}ms!")

    @app_commands.command(name="help", description="Show all available features of FlamingDeath")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔥 FlamingDeath Command Center 🔥", description="Welcome, Eternal member! Select a category from the dropdown menu below.", color=discord.Color.cyan())
        embed.set_footer(text="Guarding Eternal since 2025")
        await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)

    @app_commands.command(name="ask", description="Ask FlamingDeath anything, anywhere!")
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        try:
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=faction_data.SYSTEM_PROMPT)
            response = model.generate_content(question)
            answer = response.text
            formatted_response = f"**Your question:** {question}\n\n**Answer:** {answer}"
            if len(formatted_response) > 2000:
                await interaction.followup.send(f"**Your question:** {question}")
                chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
                for chunk in chunks: await interaction.followup.send(f"**Answer (part):** {chunk}")
            else:
                await interaction.followup.send(formatted_response)
        except Exception as e:
            await interaction.followup.send(f"🔥 *Grrr...* Error: {str(e)}")

    @app_commands.command(name="behave", description="Let the Dragon speak and act for you (Admin Only)")
    async def behave(self, interaction: discord.Interaction, script: str):
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("🔥 *Growls...* Only the high keepers can command me!", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=faction_data.SYSTEM_PROMPT)
            acting_prompt = f"Act completely as FlamingDeath. Directly generate the final text based on this script: {script}"
            response = model.generate_content(acting_prompt)
            acting_message = response.text
            if acting_message:
                await interaction.channel.send(acting_message)
                await interaction.followup.send("✅ Script executed successfully!", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ No message was generated.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"🔥 Acting error: {str(e)}", ephemeral=True)

    @app_commands.command(name="analyze", description="Let FlamingDeath look at your photos, videos, or audio files")
    async def analyze(self, interaction: discord.Interaction, prompt: str, attachment: discord.Attachment):
        await interaction.response.defer()
        if not attachment.content_type:
            await interaction.followup.send("🔥 *Grrr...* I can't read this file format!")
            return
        try:
            file_response = requests.get(attachment.url)
            attachment_data = {'mime_type': attachment.content_type, 'data': file_response.content}
            response_text = await self.get_gemini_response(prompt, interaction.user.id, attachment_data)
            await interaction.followup.send(f"🐉 **FlamingDeath Vision:** {response_text}")
        except Exception as e:
            await interaction.followup.send(f"🔥 *Coughs smoke* Error: {str(e)}")

    @app_commands.command(name="profile", description="Check your Eternal faction member card")
    async def profile(self, interaction: discord.Interaction):
        user = interaction.user
        joined_at = user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown"
        crystals = self.dragon_currency.get(user.id, 0)
        embed = discord.Embed(title=f"⚔️ Eternal Member Profile: {user.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Faction Standing", value="**Loyal Member** 🛡️", inline=True)
        embed.add_field(name="Dragon Crystals", value=f"✨ `{crystals}` Crystals", inline=True)
        embed.add_field(name="Arrival Date", value=f"📅 {joined_at}", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hunt", description="Go out on a dynamic dragon hunt to collect crystals!")
    async def hunt(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.now()
        if user_id in self.hunt_cooldowns:
            diff = now - self.hunt_cooldowns[user_id]
            if diff.total_seconds() < 3600:
                remaining_mins = int((3600 - diff.total_seconds()) // 60)
                await interaction.response.send_message(f"🔥 *Growls...* You are exhausted! Wait `{remaining_mins} more minutes`.", ephemeral=True)
                return
        self.hunt_cooldowns[user_id] = now
        crystals_found = random.randint(15, 50)
        self.dragon_currency[user_id] = self.dragon_currency.get(user_id, 0) + crystals_found
        scenarios = [
            f"🐉 You flew into the sky with FlamingDeath and raided an enemy base! Found **{crystals_found}** Crystals! 🔥",
            f"⚔️ You cleared out rogue monsters threatening the boundaries of Eternal. Earned **{crystals_found}** Crystals!",
            f"💎 You discovered a hidden crystalline cave beneath the SquareOne base! Extracted **{crystals_found}** Crystals!"
        ]
        await interaction.response.send_message(random.choice(scenarios))

    @app_commands.command(name="coinflip", description="Bet your crystals on a coin toss!")
    @app_commands.choices(choice=[app_commands.Choice(name="Heads", value="heads"), app_commands.Choice(name="Tails", value="tails")])
    async def coinflip(self, interaction: discord.Interaction, choice: app_commands.Choice[str], bet: int):
        user_id = interaction.user.id
        current_balance = self.dragon_currency.get(user_id, 0)
        if bet <= 0:
            await interaction.response.send_message("🔥 *Grrr...* You must bet at least `1 Crystal`!", ephemeral=True)
            return
        if current_balance < bet:
            await interaction.response.send_message(f"🔥 *Growls...* You only have `{current_balance}` Crystals!", ephemeral=True)
            return
        result = random.choice(["heads", "tails"])
        if choice.value == result:
            self.dragon_currency[user_id] = current_balance + bet
            await interaction.response.send_message(f"🪙 **Coinflip:** It's **{result.upper()}**! 🎉 You win **{bet}** Crystals!")
        else:
            self.dragon_currency[user_id] = current_balance - bet
            await interaction.response.send_message(f"🪙 **Coinflip:** It's **{result.upper()}**. 💀 You lost **{bet}** Crystals.")

    @app_commands.command(name="slots", description="Play the Dragon Slot Machine! (Cost: 10 Crystals)")
    async def slots(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_balance = self.dragon_currency.get(user_id, 0)
        cost = 10
        if current_balance < cost:
            await interaction.response.send_message(f"🔥 *Coughs smoke...* You only have `{current_balance}` Crystals.", ephemeral=True)
            return
        self.dragon_currency[user_id] = current_balance - cost
        items = ["🐉", "💎", "⚔️", "🔥", "🍉"]
        slot1, slot2, slot3 = random.choice(items), random.choice(items), random.choice(items)
        embed = discord.Embed(title="🎰 Eternal DRAGON SLOTS 🎰", color=discord.Color.gold())
        embed.description = f"\n> **[ {slot1} | {slot2} | {slot3} ]**\n"
        if slot1 == slot2 == slot3:
            self.dragon_currency[user_id] += 150
            embed.add_field(name="🎉 JACKPOT!!! 🎉", value=f"Matched! Won 150 Crystals!")
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            self.dragon_currency[user_id] += 30
            embed.add_field(name="✨ Small Win! ✨", value=f"Two matched! Won 30 Crystals!")
        else:
            embed.add_field(name="💀 No Match!", value="Lost 10 Crystals.")
        await interaction.response.send_message(embed=embed)

async def setup(bot, conversation_history, dragon_currency, hunt_cooldowns, get_gemini_response_func):
    cog = FactionBotCommands(bot, conversation_history, dragon_currency, hunt_cooldowns, get_gemini_response_func)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.help_command)
    bot.tree.add_command(cog.ask)
    bot.tree.add_command(cog.behave)
    bot.tree.add_command(cog.analyze)
    bot.tree.add_command(cog.profile)
    bot.tree.add_command(cog.hunt)
    bot.tree.add_command(cog.coinflip)
    bot.tree.add_command(cog.slots)
