# Architecture

## System Overview

Morning Briefing is a multi-agent pipeline that collects, synthesizes, and delivers daily intelligence reports.

```
┌────────────────��──────────────────���─────────────────────────────┐
│                        TRIGGER LAYER                            │
│  launchd (6AM) ──> briefing.py ──> load config.json            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    COLLECTION LAYER (Parallel)                   │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  ┌─────────┐│
│  │  @project   │  │  @session   │  │ @research  │  │ @goals  ││
│  │   scanner   │  │   analyst   │  │   scout    │  │ tracker ││
│  │             │  │             │  │            │  │         ││
│  │ git log     │  │ session-data│  │ WebSearch  │  │ memory/ ││
│  │ file system │  │ instincts   │  │ tech blogs │  │ calendar││
│  │ npm/build   │  │ patterns    │  │ framework  │  │ finance ││
│  │ TODOs       │  │ errors      │  │ updates    │  │ clients ││
│  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘  └────┬────┘│
│         │                │               │              │      │
│         └────────────────┼───────────────┼──────────────┘      │
│                          │               │                      │
└──────────────────────────┼───────────────┼──────────────────────┘
                           ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SYNTHESIS LAYER                              │
│                                                                  ��
│  ┌──────────────────────────────────────────��──────────────┐    │
│  │                    @synthesizer                          │    │
│  │                  (Claude Opus model)                     │    │
│  │                                                          │    │
│  │  1. Score each item: Urgency (1-5) x Impact (1-5)      │    │
│  │  2. Sort by priority score                               │    │
│  │  3. Generate greeting + health dashboard                 │    │
│  │  4. Build alerts, agenda, client cards                   │    │
│  │  5. Write insights and daily tip                         │    │
│  │  6. Weekly digest if Sunday                              │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │   PDF    │  │ Telegram │  │ WhatsApp │  │    History      │  │
│  │ Desktop/ │  │   Bot    │  │ Evolution│  │  + Instincts   │  │
│  │ Briefings│  │   API    │  │   API    │  │  + Feedback    │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Communication

Agents don't communicate directly with each other. The orchestrator (`briefing.py`) manages the pipeline:

1. **Parallel execution**: Uses Python's `ThreadPoolExecutor` to run 4 collectors simultaneously
2. **Claude CLI**: Each agent runs via `claude -p <prompt>` with Sonnet for speed
3. **JSON contract**: Each agent outputs a defined JSON schema
4. **Synthesis**: All JSON outputs are bundled and sent to the synthesizer (Claude Opus)

## Model Selection

| Agent | Model | Why |
|-------|-------|-----|
| Collectors (4x) | Claude Sonnet | Fast, cheap, structured data extraction |
| Synthesizer | Claude Opus | Complex reasoning, cross-source synthesis |
| PDF Generator | Python (no LLM) | Deterministic, fast, no API cost |

## Self-Improvement System

```
Briefing Generated ──> User reads ──> /briefing score N
                                              │
                                              ▼
                                    history/YYYY-MM-DD.json
                                              │
                                              ▼
                                    Weekly Meta-Analysis
                                    ├── Which sections scored high?
                                    ├── Which alerts were acted on?
                                    ├── Which insights were useful?
                                    └── Adjust priorities for next week
```

## Security Considerations

- **No secrets in output**: Agents are instructed to never include passwords/tokens in JSON
- **Local execution**: Everything runs on your machine, no cloud services except Claude API
- **Config gitignored**: If you customize config with real tokens, add it to .gitignore
- **History gitignored**: Past briefings contain personal data and are not committed

## Performance

| Phase | Time | API Calls |
|-------|------|-----------|
| Collection | ~60s | 4 (parallel Sonnet) |
| Synthesis | ~30s | 1 (Opus) |
| PDF + Notifications | ~10s | 0-2 (Telegram/WhatsApp) |
| **Total** | **~100s** | **5-7** |

## Extending the System

### Adding a new collector agent

1. Create `agents/my-agent.md` following the template
2. Add the agent name to the `collectors` list in `scripts/briefing.py`
3. The synthesizer will automatically receive the new data

### Adding a notification channel

1. Add a `send_<channel>()` function in `scripts/briefing.py`
2. Add config fields in `config/default.json`
3. Call it from the `main()` function

### Customizing the PDF

Edit `scripts/outputs/pdf_generator.py`. The `BriefingPDF` class uses fpdf2 and is designed to be extended with new sections.
