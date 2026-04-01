# Contributing to Morning Briefing

Thanks for your interest in contributing! This project is open to everyone.

## How to Contribute

### Reporting Bugs
- Open an issue with the `bug` label
- Include: your OS, Python version, Claude Code version
- Paste relevant error logs from `logs/briefing_error.log`

### Suggesting Features
- Open an issue with the `enhancement` label
- Describe the use case, not just the feature
- If it's a new agent, describe: what data it collects, from where, and what insights it produces

### Pull Requests

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test locally: `python3 scripts/briefing.py --test`
5. Commit with clear messages
6. Push and open a PR

### Code Style
- Python: PEP 8, type hints where helpful
- Markdown agents: Follow the existing agent template structure
- Config: JSON with comments explaining non-obvious fields

## Creating a New Agent

Agents live in `agents/` as Markdown files. Follow this template:

```markdown
---
name: your-agent-name
description: One-line description of what it does
role: collector
---

# @your-agent-name

You are a [description] agent. Your job is to [purpose].

## Data Sources
- Where it reads data from

## What to Collect
- Detailed instructions for what to gather

## Output Format
- JSON schema for the output

## Rules
- Constraints and guidelines
```

The orchestrator (`scripts/briefing.py`) automatically picks up agents from the `agents/` directory.

## Creating a New Notification Channel

1. Add a `send_<channel>()` function in `scripts/briefing.py`
2. Add config fields in `config/default.json`
3. Call it from the `main()` function
4. Document in README.md

## Areas We Need Help

- **Linux scheduling** — cron setup and testing
- **Windows support** — Task Scheduler integration
- **New agents** — Email scanner, Slack summarizer, GitHub notifications
- **Notification channels** — Discord, Slack, email (SMTP)
- **PDF templates** — Better layouts, charts, dark mode
- **Localization** — English version of agent prompts
- **Tests** — Unit tests for PDF generator and orchestrator
- **CI/CD** — GitHub Actions for linting and testing

## Questions?

Open an issue or reach out to [@jhojuneo](https://github.com/jhojuneo).
