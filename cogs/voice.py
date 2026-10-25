import asyncio
import logging
import os
import re
import tempfile
import time
from dataclasses import dataclass, field

import discord
from discord import app_commands
from discord.ext import commands, tasks
from gtts import gTTS

log = logging.getLogger("voice")

IDLE_TIMEOUT = 300      # seconds of silence before the dragon leaves
MAX_CHARS = 350         # max spoken length (keeps TTS fast)
QUEUE_LIMIT = 5

# gTTS outputs 24 kHz audio. asetrate lowers the pitch, atempo restores the speed,
# aecho adds a cave-like rumble. All done in a single ffmpeg pass (no pydub needed).
DRAGON_FX = "asetrate=18720,aresample=48000,atempo=1.282,aecho=0.8:0.85:70:0.25"

SPOKEN_RULES = (
    "[VOICE MODE: your reply will be read aloud by text-to-speech. Answer in 1-3 short "
    "sentences of plain spoken words. No emojis, no asterisks, no markdown, no lists, "
    "no links. Stay in your dragon character.]\n\nUser says: "
)


def _ensure_opus():
    if discord.opus.is_loaded():
        return
    for name in ("libopus.so.0", "libopus.so", "opus"):
        try:
            discord.opus.load_opus(name)
            return
        except Exception:
            continue
    log.warning("Opus library not found. Install libopus0 in your Docker image.")


def clean_for_speech(text: str) -> str:
    text = re.sub(r"<a?:\w+:\d+>", "", text)            # custom emojis
    text = re.sub(r"<[@#][!&]?\d+>", "", text)          # mentions / channels
    text = re.sub(r"https?://\S+", "a link", text)
    text = re.sub(r"[*_`~>#|]", "", text)               # markdown
    text = re.sub(r"[^\w\s.,!?'\-]", "", text)          # emojis / symbols
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_CHARS:
        cut = text[:MAX_CHARS]
        end = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
        text = cut[: end + 1] if end > 80 else cut
    return text


def _tts_to_file(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        gTTS(text=text, lang="en", tld="com").save(path)
    except Exception:
        os.remove(path)
        raise
    return path


@dataclass
class GuildVoice:
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=QUEUE_LIMIT))
    worker: asyncio.Task | None = None
    last_active: float = field(default_factory=time.monotonic)


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.state: dict[int, GuildVoice] = {}
        _ensure_opus()
        self.idle_check.start()

    def cog_unload(self):
        self.idle_check.cancel()
        for vc in list(self.bot.voice_clients):
            asyncio.create_task(vc.disconnect(force=True))

    # ---------------- internals ----------------
    def _get_state(self, guild: discord.Guild) -> GuildVoice:
        st = self.state.setdefault(guild.id, GuildVoice())
        if st.worker is None or st.worker.done():
            st.worker = asyncio.create_task(self._worker(guild, st))
        return st

    async def _worker(self, guild: discord.Guild, st: GuildVoice):
        loop = asyncio.get_running_loop()
        while True:
            text = await st.queue.get()
            path = None
            try:
                vc = guild.voice_client
                if not vc or not vc.is_connected():
                    continue
                path = await loop.run_in_executor(None, _tts_to_file, text)
                done = asyncio.Event()

                def after(err):
                    if err:
                        log.error("Playback error: %s", err)
                    loop.call_soon_threadsafe(done.set)

                vc.play(discord.FFmpegPCMAudio(path, options=f'-vn -af "{DRAGON_FX}"'), after=after)
                await done.wait()
            except Exception:
                log.exception("Voice worker failed")
            finally:
                st.last_active = time.monotonic()
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                st.queue.task_done()

    async def _disconnect(self, guild: discord.Guild):
        st = self.state.pop(guild.id, None)
        if st and st.worker:
            st.worker.cancel()
        vc = guild.voice_client
        if vc:
            await vc.disconnect(force=True)

    async def say(self, guild: discord.Guild, text: str) -> bool:
        """Queue text to be spoken. Other cogs can call: bot.get_cog('Voice').say(guild, text)"""
        vc = guild.voice_client
        text = clean_for_speech(text)
        if not vc or not vc.is_connected() or not text:
            return False
        st = self._get_state(guild)
        try:
            st.queue.put_nowait(text)
        except asyncio.QueueFull:
            return False
        st.last_active = time.monotonic()
        return True

    async def _precheck(self, interaction: discord.Interaction) -> bool:
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.followup.send("Summon me first with `/summon`.", ephemeral=True)
            return False
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            await interaction.followup.send("Join my voice channel first.", ephemeral=True)
            return False
        return True

    # ---------------- commands ----------------
    @app_commands.command(name="summon", description="Call the dragon into your voice channel")
    @app_commands.guild_only()
    async def summon(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.followup.send("Join a voice channel first!")
        channel = interaction.user.voice.channel
        perms = channel.permissions_for(interaction.guild.me)
        if not (perms.connect and perms.speak):
            return await interaction.followup.send("I need Connect and Speak permissions there.")
        try:
            vc = interaction.guild.voice_client
            if vc:
                await vc.move_to(channel)
            else:
                await channel.connect(self_deaf=True, timeout=20)
        except Exception:
            log.exception("Voice connect failed")
            return await interaction.followup.send("The winds blocked my wings. Try again in a moment.")
        self._get_state(interaction.guild).last_active = time.monotonic()
        await interaction.followup.send(f"*Grrr...* I have arrived in **{channel.name}**. 🐉")

    @app_commands.command(name="leave", description="Send the dragon away")
    @app_commands.guild_only()
    async def leave(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)
        await interaction.response.send_message("*Wings spread...* Until next time. 🔥")
        await self._disconnect(interaction.guild)

    @app_commands.command(name="speak", description="Make the dragon say something out loud")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def speak(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(ephemeral=True)
        if not await self._precheck(interaction):
            return
        ok = await self.say(interaction.guild, text)
        await interaction.followup.send(
            "The dragon speaks. 🐉" if ok else "Nothing speakable, or too many words queued.",
            ephemeral=True)

    @app_commands.command(name="voiceask", description="Ask the dragon a question, answered by voice")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def voiceask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        if not await self._precheck(interaction):
            return
        try:
            # Separate history key so voice chats never mix with normal chat memory
            answer = await asyncio.wait_for(
                self.bot.get_gemini_response(SPOKEN_RULES + question, f"voice-{interaction.user.id}"),
                timeout=30)
        except Exception:
            log.exception("Gemini failed")
            return await interaction.followup.send("My ancient mind stalled. Ask again!")
        await self.say(interaction.guild, answer)
        await interaction.followup.send(f"**{interaction.user.display_name}:** {question}\n🐉 {answer}"[:2000])

    @speak.error
    @voiceask.error
    async def _cooldown_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = f"⏰ *Patience, young one. Try again in {error.retry_after:.0f}s.*"
        else:
            log.error("Voice command error: %r", error)
            msg = "🔥 *Grrr...* Something went wrong."
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

    # ---------------- idle / cleanup ----------------
    @tasks.loop(seconds=30)
    async def idle_check(self):
        now = time.monotonic()
        for vc in list(self.bot.voice_clients):
            st = self.state.get(vc.guild.id)
            if st and not vc.is_playing() and st.queue.empty() and now - st.last_active > IDLE_TIMEOUT:
                await self._disconnect(vc.guild)

    @idle_check.before_loop
    async def _wait_ready(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        if member.id == self.bot.user.id and after.channel is None:    # kicked / dropped
            st = self.state.pop(guild.id, None)
            if st and st.worker:
                st.worker.cancel()
            return
        vc = guild.voice_client
        if vc and vc.channel and not any(not m.bot for m in vc.channel.members):
            await self._disconnect(guild)    # everyone left, so leave too


async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))
