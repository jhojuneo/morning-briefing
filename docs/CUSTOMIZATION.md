# Customization Guide

## Adapting Morning Briefing for Your Workflow

This skill was built for a traffic manager/developer managing multiple clients, but it works for anyone. Here's how to adapt it.

## Step 1: Configure Your Projects

Edit `config/default.json`:

```json
{
  "projects_root": "~/path/to/your/projects",
  "clients": [
    {
      "name": "Your Client",
      "project_dir": "client-project-folder",
      "memory_file": "client-memory.md",
      "ads_platform": null,
      "monthly_budget": null
    }
  ]
}
```

**If you don't manage clients**, just list your personal projects with `"ads_platform": null` and `"monthly_budget": null`.

## Step 2: Customize Research Topics

```json
{
  "research_topics": [
    "Your framework updates",
    "Your industry news",
    "Tools you use daily"
  ]
}
```

The @research-scout agent uses these to find relevant news. Be specific:
- "React 19 breaking changes" instead of "React"
- "Python FastAPI security" instead of "Python"

## Step 3: Adjust the Schedule

**Change the time** in the plist file:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>7</integer>  <!-- Change this -->
    <key>Minute</key>
    <integer>30</integer>  <!-- And this -->
</dict>
```

**Run twice a day** (morning + evening):
```xml
<key>StartCalendarInterval</key>
<array>
    <dict><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
</array>
```

## Step 4: Disable Agents You Don't Need

In `scripts/briefing.py`, edit the collectors list:

```python
# Full suite (default)
collectors = ["project-scanner", "session-analyst", "goals-tracker", "research-scout"]

# Developer only (no client tracking)
collectors = ["project-scanner", "session-analyst", "research-scout"]

# Project manager only (no code analysis)
collectors = ["goals-tracker", "research-scout"]
```

## Step 5: Create Custom Agents

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the agent template. Ideas:

- **@email-scanner** — Summarize unread emails
- **@slack-digest** — Important Slack messages from overnight
- **@github-notifications** — PR reviews, issues assigned to you
- **@health-tracker** — Screen time, steps, sleep data
- **@market-monitor** — Stock prices, crypto, commodity prices

## Examples

### For a Solo Developer
```json
{
  "clients": [],
  "research_topics": ["Rust async patterns", "WASM updates", "Developer tools"],
  "financial": { "enabled": false }
}
```

### For a Marketing Agency
```json
{
  "clients": [
    { "name": "Client A", "ads_platform": "meta", "monthly_budget": 5000 },
    { "name": "Client B", "ads_platform": "google", "monthly_budget": 3000 }
  ],
  "research_topics": ["Meta Ads algorithm", "Google Ads Performance Max", "TikTok Ads"]
}
```

### For a Startup Founder
```json
{
  "clients": [
    { "name": "My Product", "project_dir": "my-saas", "monthly_budget": null }
  ],
  "research_topics": ["SaaS metrics", "Y Combinator advice", "Product-led growth"]
}
```
