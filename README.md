<p align="center">
  <img src="https://cdn.discordapp.com/attachments/1478401568159170752/1536399680215187496/IMG_20260712_150837-removebg-preview.png?ex=6a7bebf4&is=6a7a9a74&hm=9f7f30e6e68b009071ebba5faaeb9881cd2c6bda3045ad3c17135f98a22845c2&" alt="FlamingDeath Logo" width="200"/>
</p>
  
# 🔥 FlamingDeath — Faction Gamification & AI Intelligence Core

**FlamingDeath** serves as the dynamic interactive intelligence, RPG gamification engine, and co-guardian of the **Eternal** faction ecosystem. Built on asynchronous Python and `discord.py`, it integrates **Gemini 2.5 Flash** to power conversational AI, multi-modal media analysis, shared faction memory, and a custom interactive economy system.

---

## 🛠️ System Architecture & Core Features

* **Dragon AI Persona Matrix:** Powered by Gemini 2.5 Flash with custom system directives, enabling context-aware responses and continuous chat history retention.
* **Shared Faction Memory (Atlas Core):** Allows high keepers to dynamically store (`/remember`) and retrieve (`/recall`) critical faction intelligence in real-time.
* **Multi-Modal Vision & Web Reader Engine:** Direct analysis of uploaded images, audio, and video files, alongside web scraping capabilities (`/readweb`) with automated AI summaries.
* **Interactive Oracle Control Panel:** Integrated UI dropdown menus (`/flamy-oracle`) and button routing systems for effortless, click-based command access.
* **Gamified Economy System:** Fully integrated RPG loop featuring daily rations (`/daily`), faction work quests (`/work`), high-risk crimes (`/crime`), slots mini-games, and custom member profile cards.
* **Stealth Admin Commands:** Secret administrative tools allowing high keepers to manipulate messages (`/copy`) and distribute rewards publicly attributed to FlamingDeath while hiding user execution.

---

## ⚔️ Operational Command Matrix

### 🐉 General Utilities & Intelligence
| Command | Parameters | Auth / Limits | Description |
| :--- | :--- | :--- | :--- |
| `/ping` | None | Public | Evaluates tactical network response speed and API latency. |
| `/help` | None | Public | Deploys the interactive UI dropdown command directory. |
| `/ask` | `question` | 5s Cooldown | Directly queries the Dragon core neural model from any channel. |
| `/readweb` | `url` | 10s Cooldown | Scrapes and generates a concise AI summary of web page content. |
| `/remember` | `topic`, `information` | Public | Stores critical faction data into the persistent MongoDB cluster. |
| `/recall` | `topic` | Public | Retrieves previously saved information from the faction database. |
| `/copy` | `message_input`, `reply_text`, `target_channel` | Admin Only | Anonymously sends messages, replies, or clones contents into targeted channels. |

### 🎨 AI Multimedia & Vision
| Command | Parameters | Auth / Limits | Description |
| :--- | :--- | :--- | :--- |
| `/imagine` | `prompt` | 5s Cooldown | Generates AI images instantly using Pollinations.ai. |
| `/analyze` | `prompt`, `attachment` | 10s Cooldown | Executes multi-modal visual and audio analysis on uploaded media files. |

### ⚔️ Faction RPG & Crystal Economy
| Command | Parameters | Cooldown / Cost | Description |
| :--- | :--- | :--- | :--- |
| `/flamy-oracle` | None | None | Deploys the main interactive UI control dashboard with dynamic buttons and dropdowns. |
| `/profile` | None | None | Retrieves your Eternal member card, join date, and active Crystal balance. |
| `/leaderboard` | None | None | Displays top Dragon Crystal hoarders across the Eternal faction. |
| `/daily` | None | 24 Hours Cooldown | Claims daily faction rations and maintains active streak multipliers. |
| `/work` | None | 10 Mins Cooldown | Completes faction tasks to earn Dragon Crystals. |
| `/crime` | None | 45 Mins Cooldown | Attempts high-risk/high-payout crimes with crystal fine risks. |
| `/slots` | None | 10 Crystals | Triggers the Dragon Slot Machine for randomized payout multipliers. |

---

*Co-guarding the **Eternal** faction network. Undefeated, massive, and structurally sound.* 🐉🔥
