<p align="center">
  <img src="https://cdn.discordapp.com/attachments/1478401568159170752/1536399680215187496/IMG_20260712_150837-removebg-preview.png?ex=6a7bebf4&is=6a7a9a74&hm=9f7f30e6e68b009071ebba5faaeb9881cd2c6bda3045ad3c17135f98a22845c2&" alt="FlamingDeath Logo" width="200"/>
</p>
  
# 🔥 FlamingDeath — Faction Gamification & AI Intelligence Core

**FlamingDeath** serves as the dynamic interactive intelligence, RPG gamification engine, and co-guardian of the **Eternal** faction ecosystem. Built on asynchronous Python and `discord.py`, it integrates **Gemini 2.5 Flash** to power conversational AI, multi-modal media analysis, shared faction memory, and a custom economy system.

---

## 🛠️ System Architecture & Core Features

* **Dragon AI Persona Matrix:** Powered by Gemini 2.5 Flash with custom system directives, enabling context-aware responses and continuous chat history retention.
* **Shared Faction Memory (Atlas Core):** Allows high keepers to dynamically store (`/remember`) and retrieve (`/recall`) critical faction intelligence in real-time.
* **Multi-Modal Vision & Web Reader Engine:** Direct analysis of uploaded images, audio, and video files, alongside web scraping capabilities (`/readweb`) with automated AI summaries.
* **Gamified Economy System:** Fully integrated RPG loop featuring interactive journeys (`/play`), timed hunting expeditions, gambling risk vectors, and custom member profile cards.
* **Stealth Admin Commands:** Secret administrative tools allowing high keepers to distribute rewards (`/give_player`, `/give_everyone`) publicly attributed to FlamingDeath while hiding user execution.
* **24/7 Cloud Resilience:** Built-in Flask web server with background self-ping heartbeat threads to maintain active uptime on deployment platforms (e.g., Render).

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
| `/analyze` | `prompt`, `attachment` | 10s Cooldown | Executes multi-modal visual and audio analysis on uploaded media files. |

### ⚔️ Faction RPG & Crystal Economy
| Command | Parameters | Cooldown / Cost | Description |
| :--- | :--- | :--- | :--- |
| `/profile` | None | None | Retrieves your Eternal member card, join date, and active Crystal balance. |
| `/leaderboard` | None | None | Displays top Dragon Crystal hoarders across the Eternal faction. |
| `/play` | None | 1 Hour Cooldown | Embark on interactive journeys (Caverns, Ruins, Wilderness) to harvest crystals. |
| `/hunt` | None | 1 Hour Cooldown | Dispatches a scouting array into the wild to harvest Dragon Crystals. |
| `/coinflip` | `choice`, `bet` | None | Wagers active Dragon Crystals on a high-stakes probability toss. |
| `/slots` | None | 10 Crystals | Triggers the Dragon Slot Machine for randomized payout multipliers. |
| `/give_player` | `member`, `amount` | Admin Only (Stealth) | Publicly bestows Dragon Crystals on a target user in FlamingDeath's name while hiding admin execution. |
| `/give_everyone` | `amount` | Admin Only (Stealth) | Publicly bestows Dragon Crystals on all members in FlamingDeath's name while hiding admin execution. |
| `/give_role` | `role`, `amount` | Admin Only | Distributes Dragon Crystals to all members holding a specified role. |

---

*Co-guarding the **Eternal** faction network. Undefeated, massive, and structurally sound.* 🐉🔥
