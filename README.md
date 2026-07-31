<p align="center">
  <img src="https://cdn.discordapp.com/attachments/1492172037500698758/1528035129593696326/IMG_20260712_150837-removebg-preview.png?ex=6a5cd51c&is=6a5b839c&hm=75b9431811d03080c2800492e6c53fd0829ae7237c583210f79a9ba0747a987d&" alt="FlamingDeath Logo" width="200"/>
</p>
  
# 🔥 FlamingDeath — Faction Gamification & AI Intelligence Core

**FlamingDeath** serves as the dynamic interactive intelligence, RPG gamification engine, and co-guardian of the **Eternal** faction ecosystem. Built on asynchronous Python and `discord.py`, it integrates **Gemini 2.5 Flash** to power conversational AI, multi-modal media analysis, shared faction memory, and a custom economy system.

---

## 🛠️ System Architecture & Core Features

* **Dragon AI Persona Matrix:** Powered by Gemini 2.5 Flash with custom system directives, enabling context-aware responses and continuous chat history retention.
* **Shared Faction Memory (Atlas Core):** Allows high keepers to dynamically store (`/remember`) and retrieve (`/recall`) critical faction intelligence in real-time.
* **Multi-Modal Vision & Web Reader Engine:** Direct analysis of uploaded images, audio, and video files, alongside web scraping capabilities (`/readweb`) with automated AI summaries.
* **Gamified Economy System:** Fully integrated RPG loop featuring timed hunting expeditions, gambling risk vectors, and custom member profile cards.
* **24/7 Cloud Resilience:** Built-in Flask web server with background self-ping heartbeat threads to maintain active uptime on deployment platforms (e.g., Render).

---

## ⚔️ Operational Command Matrix

### 🐉 General Utilities & Intelligence
| Command | Parameters | Auth / Limits | Description |
| :--- | :--- | :--- | :--- |
| `?ping` | None | Public | Evaluates tactical network response speed and API latency. |
| `/help` | None | Public | Deploys the interactive UI dropdown command directory. |
| `/ask` | `question` | 5s Cooldown | Directly queries the Dragon core neural model from any channel. |
| `/readweb` | `url` | 10s Cooldown | Scrapes and generates a concise AI summary of web page content. |
| `/remember` | `topic`, `information` | Public | Stores critical faction data into the persistent MongoDB cluster. |
| `/recall` | `topic` | Public | Retrieves previously saved information from the faction database. |
| `/behave` | `script` | Admin Only | Commands the Dragon instance to speak and execute explicit scripted directives. |

### 🎨 AI Multimedia & Vision
| Command | Parameters | Auth / Limits | Description |
| :--- | :--- | :--- | :--- |
| `/analyze` | `prompt`, `attachment` | 10s Cooldown | Executes multi-modal visual and audio analysis on uploaded media files. |

### ⚔️ Faction RPG & Crystal Economy
| Command | Parameters | Cooldown / Cost | Description |
| :--- | :--- | :--- | :--- |
| `/profile` | None | None | Retrieves your Eternal member card, join date, and active Crystal balance. |
| `/hunt` | None | 1 Hour Cooldown | Dispatches a scouting array into the wild to harvest Dragon Crystals. |
| `/coinflip` | `choice`, `bet` | None | Wagers active Dragon Crystals on a high-stakes quantum probability toss. |
| `/slots` | None | 10 Crystals | Triggers the Dragon Slot Machine for randomized payout multipliers. |

---

*Co-guarding the **Eternal** faction network. Undefeated, massive, and structurally sound.* 🐉🔥
