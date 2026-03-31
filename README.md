# Morning Briefing

Daily AI-powered intelligence briefing for Claude Code. Analyzes your projects, sessions, finances, clients, and generates a PDF + notifications every morning.

## What it does

Every day at 6AM (configurable), 4 AI agents run in parallel:

| Agent | What it scans |
|-------|--------------|
| **@project-scanner** | Git history, file changes, TODOs, build status |
| **@session-analyst** | Claude sessions, learned patterns, errors, instincts |
| **@research-scout** | Tech news, tool updates, industry insights |
| **@goals-tracker** | Client status, deadlines, finances, calendar |

A 5th agent (`@synthesizer`) combines everything into a prioritized briefing with:
- Urgent alerts (overdue tasks, build failures, budget anomalies)
- Today's agenda with suggested task order
- Client scorecards with health indicators
- Yesterday's work summary
- Actionable insights from research
- Daily tip based on your recent difficulties

## Installation

### Quick Install (one command)
```bash
git clone https://github.com/jhoncarvalho/morning-briefing.git ~/.claude/skills/morning-briefing
```

### Setup
1. Edit `config/default.json` with your preferences:
   - Project directories
   - Client list and budgets
   - Telegram bot token (optional)
   - WhatsApp Evolution API (optional)

2. Install the launchd schedule (macOS):
```bash
mkdir -p ~/.claude/skills/morning-briefing/logs
cp ~/.claude/skills/morning-briefing/com.jhon.morning-briefing.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jhon.morning-briefing.plist
```

3. Install the slash command:
```bash
cp ~/.claude/skills/morning-briefing/briefing.md ~/.claude/commands/briefing.md
```

### Requirements
- macOS (launchd) or Linux (cron)
- Claude Code CLI (`claude` in PATH)
- Python 3.10+
- fpdf2 (`pip install fpdf2`)

## Usage

### Manual (inside Claude Code)
```
/briefing           # Generate now
/briefing weekly    # Weekly expanded digest
/briefing quick     # Skip research, faster
/briefing score 5   # Rate today's briefing
/briefing history   # Show past briefings
```

### Automatic
Runs daily at 6AM via launchd. Configure time in the plist file.

## Notifications

| Channel | Setup |
|---------|-------|
| **macOS** | Works out of the box |
| **Telegram** | Add `bot_token` and `chat_id` to config.json |
| **WhatsApp** | Add Evolution API URL and instance to config.json |

## Self-Improvement

The skill learns from your feedback:
- Rate each briefing with `/briefing score <1-5>`
- Low scores adjust what gets prioritized
- High-value patterns become permanent instincts
- Weekly meta-analysis reviews what the briefing got right/wrong

## Structure

```
morning-briefing/
├── SKILL.md                    # Skill definition
├── README.md                   # This file
├── config/
│   └── default.json           # User preferences
├── agents/
│   ├── project-scanner.md     # Git + file analysis
│   ├── session-analyst.md     # Session + instinct analysis
│   ├── research-scout.md      # Web research
│   ├── goals-tracker.md       # Goals + deadlines + finance
│   └── synthesizer.md         # Combines all outputs
├── scripts/
│   ├── briefing.py            # Main orchestrator
│   └── outputs/
│       └── pdf_generator.py   # PDF creation
├── history/                   # Past briefings + scores
├── logs/                      # launchd output
└── com.jhon.morning-briefing.plist  # macOS schedule
```

## License

MIT
