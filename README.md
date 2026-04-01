# Morning Briefing

> Daily AI-powered intelligence briefing for Claude Code. 5 agents analyze your projects, sessions, clients, finances, and the web — then generate a prioritized PDF report with insights, alerts, and action items every morning.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-purple.svg)](https://claude.ai/code)
[![Agents](https://img.shields.io/badge/Agents-5-green.svg)](#architecture)

---

## The Problem

You work across multiple projects, clients, and tools. Every morning you need to:
- Check what happened in each project overnight
- Remember which client needs attention
- Catch up on relevant tech news
- Review your deadlines and finances
- Figure out what to work on first

**Morning Briefing does all of this automatically while you sleep.**

## How It Works

Every day at 6AM (configurable), the system launches 4 collector agents in parallel, then a synthesizer combines everything into one actionable report:

```
  06:00 AM                         06:02 AM                     06:03 AM
  ┌──────────┐
  │ @project  │──┐
  │  scanner  │  │
  └──────────┘  │
  ┌──────────┐  │  ┌─────────────┐    ┌──────────┐    ┌──────────┐
  │ @session  │──┼──│ @synthesizer│───>│   PDF    │───>│ Telegram │
  │  analyst  │  │  │ (Claude Opus)│   │ Briefing │    │ WhatsApp │
  └──────────┘  │  └─────────────┘    └──────────┘    │  macOS   │
  ┌──────────┐  │                                      └──────────┘
  │ @research │──┤
  │   scout   │  │
  └──────────┘  │
  ┌──────────┐  │
  │  @goals   │──┘
  │  tracker  │
  └──────────┘
```

### What each agent does

| Agent | Data Sources | Output |
|-------|-------------|--------|
| **@project-scanner** | Git logs, file changes, TODOs, build status | Project health cards with commits, branches, errors |
| **@session-analyst** | Claude sessions, learned instincts, error patterns | Difficulty analysis, growth metrics, recurring issues |
| **@research-scout** | Web search, tech blogs, framework updates | Relevant news, vulnerability alerts, new tools |
| **@goals-tracker** | Memory files, calendar, client data, finances | Client scorecards, deadline alerts, financial snapshot |
| **@synthesizer** | All of the above | Prioritized briefing with insights and action plan |

### What the PDF contains

1. **Health Dashboard** — Green/Yellow/Red status for Projects, Clients, Finance
2. **Urgent Alerts** — Overdue deadlines, build failures, budget anomalies
3. **Today's Agenda** — Suggested task order with estimated times
4. **Client Scorecards** — Status, budget %, last contact, next action per client
5. **Yesterday Summary** — What you accomplished (git commits, sessions, skills learned)
6. **Insights** — Top 3-5 actionable insights from all sources
7. **Tip of the Day** — One practical tip based on your recent difficulties
8. **Weekly Digest** (Sundays) — Week review with wins, improvements, next week plan

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/jhojuneo/morning-briefing.git ~/.claude/skills/morning-briefing
```

### 2. Configure

```bash
# Copy the example config and edit with your data
cp ~/.claude/skills/morning-briefing/config/default.json ~/.claude/skills/morning-briefing/config/my-config.json
```

Edit `config/default.json` with:
- Your project directories
- Client names and budgets
- Notification channels (Telegram, WhatsApp)
- Research topics relevant to your work

### 3. Install the slash command

```bash
cp ~/.claude/skills/morning-briefing/commands/briefing.md ~/.claude/commands/briefing.md
```

### 4. Schedule (optional)

**macOS (launchd):**
```bash
mkdir -p ~/.claude/skills/morning-briefing/logs
cp ~/.claude/skills/morning-briefing/com.jhon.morning-briefing.plist ~/Library/LaunchAgents/com.morning-briefing.plist

# Edit the plist to change username/paths if needed
# Then load it:
launchctl load ~/Library/LaunchAgents/com.morning-briefing.plist
```

**Linux (cron):**
```bash
# Add to crontab:
0 6 * * * /usr/bin/python3 ~/.claude/skills/morning-briefing/scripts/briefing.py
```

### 5. Test it

Inside Claude Code:
```
/briefing
```

Or from terminal:
```bash
python3 ~/.claude/skills/morning-briefing/scripts/briefing.py --test
```

---

## Requirements

| Requirement | Required | Notes |
|------------|----------|-------|
| Claude Code CLI | Yes | `claude` must be in PATH |
| Python 3.10+ | Yes | For the orchestrator and PDF generator |
| fpdf2 | Yes | `pip install fpdf2` or auto-installs in venv |
| macOS / Linux | Yes | launchd (macOS) or cron (Linux) for scheduling |
| Telegram Bot | No | For mobile notifications |
| Evolution API | No | For WhatsApp notifications |

---

## Usage

### Slash Commands

| Command | Description |
|---------|------------|
| `/briefing` | Generate briefing now (test mode, no notifications) |
| `/briefing now` | Generate with full notifications |
| `/briefing weekly` | Expanded weekly digest with charts |
| `/briefing quick` | Skip research agent, faster generation |
| `/briefing score <1-5>` | Rate today's briefing (feeds self-improvement) |
| `/briefing history` | List past briefings |
| `/briefing config` | Show current configuration |

### CLI

```bash
python3 scripts/briefing.py              # Full daily briefing
python3 scripts/briefing.py --weekly     # Weekly digest
python3 scripts/briefing.py --quick      # Skip research
python3 scripts/briefing.py --test       # No notifications
```

---

## Configuration

Edit `config/default.json`:

```jsonc
{
  "schedule": {
    "daily": "06:00",           // When to run (24h format)
    "weekly_digest": "sunday",  // Day for expanded report
    "timezone": "America/Sao_Paulo"
  },
  "projects_root": "~/Desktop/Sites e sistemas",  // Your projects directory
  "clients": [
    {
      "name": "Client Name",
      "project_dir": "project-folder",   // Relative to projects_root
      "memory_file": "client-memory.md", // In Claude memory dir
      "ads_platform": "google",          // google, meta, or null
      "monthly_budget": 1000             // In your currency
    }
  ],
  "notifications": {
    "macos": true,
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN",
      "chat_id": "YOUR_CHAT_ID"
    },
    "whatsapp": {
      "enabled": false,
      "evolution_api_url": "https://your-api.com",
      "instance": "default",
      "target_number": "5511999999999"
    }
  },
  "research_topics": [
    "Google Ads updates",
    "React + Vite best practices"
  ],
  "self_improvement": {
    "enabled": true,
    "min_feedback_score": 3,
    "auto_evolve_instincts": true
  }
}
```

### Notification Setup

<details>
<summary><strong>Telegram (recommended)</strong></summary>

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token
4. Send a message to your bot, then visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Find your `chat_id` in the response
6. Add both to `config/default.json`

</details>

<details>
<summary><strong>WhatsApp (Evolution API)</strong></summary>

1. Set up [Evolution API](https://github.com/EvolutionAPI/evolution-api) on your server
2. Create an instance and connect your WhatsApp
3. Add the API URL, instance name, and target number to `config/default.json`

</details>

<details>
<summary><strong>macOS Notifications</strong></summary>

Works out of the box. Uses `osascript` to display native macOS notifications with sound.

</details>

---

## Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the detailed system design.

### Agent Pipeline

```
Phase 1: Collection (parallel, ~60s)
├── @project-scanner  → Runs git commands, reads files
├── @session-analyst  → Reads Claude session data, instincts
├── @research-scout   → WebSearch for relevant news
└── @goals-tracker    → Reads memory files, calendar, finances

Phase 2: Synthesis (~30s)
└── @synthesizer      → Claude Opus combines all JSON outputs

Phase 3: Output (~10s)
├── PDF Generator     → Creates formatted PDF via fpdf2
├── Notifications     → Telegram, WhatsApp, macOS
├── History           → Saves to history/ for self-improvement
└── Instinct Update   → Promotes high-value patterns
```

### Self-Improvement Loop

```
Day 1: Generate briefing → User rates 4/5
Day 2: Generate briefing → User rates 2/5 (too many alerts)
Day 3: Adjust alert threshold → User rates 5/5
...
Week 4: Briefing evolved to match user's preferences
```

The system tracks:
- Feedback scores per section (alerts, insights, tips)
- Which insights led to action vs. were ignored
- Time-of-day patterns (when user reads briefings)
- Section read-time estimates (via follow-up interactions)

---

## Use Cases

### For Freelance Developers
- Track multiple client projects simultaneously
- Never miss a deadline or forget a client
- Stay updated on tech stack changes
- Financial overview across all clients

### For Agency / Traffic Managers
- Monitor ad spend across clients
- Get alerts when budgets are over/under
- Research competitor strategies automatically
- Client health scorecards for account reviews

### For Solo Founders
- Daily progress tracking on your product
- Market research delivered automatically
- Financial dashboard without spreadsheets
- Focus suggestions based on priority scoring

### For Development Teams
- Team-wide project health overview
- Code quality tracking (TODOs, build failures)
- Shared knowledge base via instincts
- Sprint progress summaries

---

## Roadmap

### v1.0 (Current)
- [x] 4 collector agents + 1 synthesizer
- [x] PDF generation
- [x] Telegram notifications
- [x] WhatsApp notifications (Evolution API)
- [x] macOS notifications
- [x] launchd scheduling
- [x] `/briefing` slash command
- [x] Feedback scoring system
- [x] Weekly digest mode

### v1.1 (Planned)
- [ ] Audio briefing via TTS (macOS `say` or ElevenLabs)
- [ ] Google Calendar integration via MCP
- [ ] UTMfy integration for ad spend tracking
- [ ] Interactive HTML version (opens in browser)
- [ ] Email delivery option

### v1.2 (Planned)
- [ ] Dashboard web UI (React + Vite)
- [ ] Historical trend charts
- [ ] Client comparison view
- [ ] Competitive monitoring agent
- [ ] Custom agent plugins (add your own collectors)

### v2.0 (Future)
- [ ] Multi-user support (team briefings)
- [ ] Slack/Discord notifications
- [ ] Integration with project management tools (ClickUp, Linear)
- [ ] AI-generated daily standup notes
- [ ] Voice assistant integration

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

We welcome contributions! Some ideas:
- New collector agents (e.g., email scanner, Slack summarizer)
- Additional notification channels
- PDF template improvements
- Localization (currently PT-BR focused)
- Linux/Windows scheduling support
- Tests and CI/CD

---

## Project Structure

```
morning-briefing/
├── README.md                          # You are here
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT License
├── SKILL.md                           # Claude Code skill definition
├── config/
│   ├── default.json                  # Default configuration
│   └── example.json                  # Example for new users
├── agents/
│   ├── project-scanner.md            # Git + file analysis agent
│   ├── session-analyst.md            # Session + instinct analysis agent
│   ├── research-scout.md             # Web research agent
│   ├── goals-tracker.md              # Goals + deadlines + finance agent
│   └── synthesizer.md                # Synthesis agent (combines all)
├── scripts/
│   ├── briefing.py                   # Main orchestrator (Python)
│   └── outputs/
│       └── pdf_generator.py          # PDF creation engine
├── docs/
│   ├── ARCHITECTURE.md               # System design details
│   └── CUSTOMIZATION.md              # How to customize for your needs
├── templates/                         # PDF templates (future)
├── history/                           # Past briefings + scores (gitignored)
├── logs/                              # launchd output (gitignored)
└── com.jhon.morning-briefing.plist   # macOS launchd schedule
```

---

## Acknowledgements

Built with:
- [Claude Code](https://claude.ai/code) — AI coding assistant by Anthropic
- [fpdf2](https://github.com/py-pdf/fpdf2) — PDF generation in Python
- [continuous-learning-v2](https://github.com/affaan-m/everything-claude-code) — Instinct system from ECC
- [last30days](https://github.com/ComposioHQ/awesome-claude-skills) — Research engine inspiration

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Wake up to clarity, not chaos.</strong><br>
  <em>Built by <a href="https://github.com/jhojuneo">Jhon Carvalho</a> with Claude Code</em>
</p>
