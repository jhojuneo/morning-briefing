#!/usr/bin/env python3
"""
Morning Briefing — Main orchestrator script.
Runs collector agents in parallel, synthesizes results, generates PDF + notifications.

Usage:
    python3 briefing.py              # Full daily briefing
    python3 briefing.py --weekly     # Weekly digest (expanded)
    python3 briefing.py --quick      # Quick briefing (skip research)
    python3 briefing.py --test       # Test mode (no notifications)
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Paths
SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "config" / "default.json"
AGENTS_DIR = SKILL_DIR / "agents"
OUTPUT_DIR = Path.home() / "Desktop" / "Briefings"
HISTORY_DIR = SKILL_DIR / "history"

def load_config():
    """Load skill configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)

def ensure_dirs():
    """Create output directories if needed."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def run_collector(agent_name, config, extra_args=None):
    """Run a single collector agent via claude -p."""
    agent_file = AGENTS_DIR / f"{agent_name}.md"
    if not agent_file.exists():
        return {"agent": agent_name, "error": f"Agent file not found: {agent_file}"}

    agent_prompt = agent_file.read_text()

    prompt = f"""You are the {agent_name} agent. Follow your instructions exactly.

{agent_prompt}

Configuration:
{json.dumps(config, indent=2)}

Today's date: {datetime.now().strftime('%Y-%m-%d')}
Current time: {datetime.now().strftime('%H:%M')}

Execute your collection task NOW and return ONLY the JSON output as specified in your instructions.
Do not explain, do not add commentary. Just the JSON.
"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "CLAUDE_MODEL": "sonnet"}
        )

        if result.returncode == 0:
            try:
                # Try to parse as JSON
                output = result.stdout.strip()
                # Find JSON in output (may have wrapper)
                if '"result"' in output:
                    parsed = json.loads(output)
                    return {"agent": agent_name, "data": parsed.get("result", output)}
                return {"agent": agent_name, "data": json.loads(output)}
            except json.JSONDecodeError:
                return {"agent": agent_name, "data": result.stdout.strip()}
        else:
            return {"agent": agent_name, "error": result.stderr[:500]}

    except subprocess.TimeoutExpired:
        return {"agent": agent_name, "error": "Timeout (120s)"}
    except FileNotFoundError:
        return {"agent": agent_name, "error": "claude CLI not found in PATH"}

def run_synthesizer(collector_results, config, weekly=False):
    """Run the synthesizer agent with all collector outputs."""
    synth_file = AGENTS_DIR / "synthesizer.md"
    synth_prompt = synth_file.read_text()

    prompt = f"""You are the synthesizer agent. Follow your instructions exactly.

{synth_prompt}

## Collector Outputs

{json.dumps(collector_results, indent=2, default=str)}

## Configuration
{json.dumps(config, indent=2)}

{"GENERATE WEEKLY DIGEST (it's Sunday)." if weekly else "Generate daily briefing."}

Return ONLY the JSON output as specified. No explanation.
"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=180,
            env={**os.environ, "CLAUDE_MODEL": "opus"}
        )

        if result.returncode == 0:
            try:
                output = result.stdout.strip()
                if '"result"' in output:
                    parsed = json.loads(output)
                    return parsed.get("result", output)
                return json.loads(output)
            except json.JSONDecodeError:
                return {"raw": result.stdout.strip()}
        else:
            return {"error": result.stderr[:500]}

    except subprocess.TimeoutExpired:
        return {"error": "Synthesizer timeout (180s)"}

def generate_pdf(briefing_data, output_path):
    """Generate PDF from briefing data using the template."""
    gen_script = SKILL_DIR / "scripts" / "outputs" / "pdf_generator.py"

    # Write briefing data to temp file
    temp_data = output_path.with_suffix(".json")
    with open(temp_data, "w") as f:
        json.dump(briefing_data, f, indent=2, ensure_ascii=False)

    try:
        result = subprocess.run(
            [sys.executable, str(gen_script), str(temp_data), str(output_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"PDF generated: {output_path}")
            return True
        else:
            print(f"PDF generation failed: {result.stderr[:200]}")
            return False
    finally:
        if temp_data.exists():
            temp_data.unlink()

def send_telegram(briefing_data, pdf_path, config):
    """Send briefing summary + PDF to Telegram."""
    tg = config.get("notifications", {}).get("telegram", {})
    if not tg.get("enabled") or not tg.get("bot_token") or not tg.get("chat_id"):
        return False

    token = tg["bot_token"]
    chat_id = tg["chat_id"]

    # Build summary message
    greeting = briefing_data.get("greeting", "Bom dia!")
    health = briefing_data.get("health", {})
    alerts = briefing_data.get("alerts", [])

    status_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}

    msg = f"☀️ *Morning Briefing — {briefing_data.get('date', 'hoje')}*\n\n"
    msg += f"{greeting}\n\n"
    msg += f"Projetos: {status_emoji.get(health.get('projects', 'green'))} "
    msg += f"Clientes: {status_emoji.get(health.get('clients', 'green'))} "
    msg += f"Financeiro: {status_emoji.get(health.get('finance', 'green'))}\n\n"

    if alerts:
        msg += "⚠️ *Alertas:*\n"
        for alert in alerts[:3]:
            msg += f"• {alert.get('message', str(alert))}\n"
        msg += "\n"

    msg += "📄 PDF completo em anexo."

    import urllib.request
    import urllib.parse

    # Send text message
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }).encode()

    try:
        urllib.request.urlopen(url, data, timeout=10)
    except Exception as e:
        print(f"Telegram text failed: {e}")

    # Send PDF
    if pdf_path and pdf_path.exists():
        try:
            import mimetypes
            boundary = "----MorningBriefingBoundary"

            body = []
            body.append(f"--{boundary}")
            body.append(f'Content-Disposition: form-data; name="chat_id"')
            body.append("")
            body.append(str(chat_id))
            body.append(f"--{boundary}")
            body.append(f'Content-Disposition: form-data; name="document"; filename="{pdf_path.name}"')
            body.append("Content-Type: application/pdf")
            body.append("")

            text_parts = "\r\n".join(body).encode() + b"\r\n"
            pdf_data = pdf_path.read_bytes()
            end_boundary = f"\r\n--{boundary}--\r\n".encode()

            full_body = text_parts + pdf_data + end_boundary

            doc_url = f"https://api.telegram.org/bot{token}/sendDocument"
            req = urllib.request.Request(doc_url, data=full_body)
            req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
            urllib.request.urlopen(req, timeout=30)
            print("Telegram: PDF sent successfully")
        except Exception as e:
            print(f"Telegram PDF failed: {e}")

    return True

def send_macos_notification(briefing_data):
    """Send macOS notification."""
    greeting = briefing_data.get("greeting", "Bom dia! Seu briefing esta pronto.")
    alerts_count = len(briefing_data.get("alerts", []))

    title = "☀️ Morning Briefing"
    subtitle = f"{briefing_data.get('date', 'hoje')} — {briefing_data.get('weekday', '')}"
    message = greeting
    if alerts_count:
        message += f" ({alerts_count} alertas)"

    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}" subtitle "{subtitle}" sound name "Glass"'
    ], capture_output=True, timeout=5)

def save_history(briefing_data, pdf_path):
    """Save briefing to history for self-improvement tracking."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    history_file = HISTORY_DIR / f"{date_str}.json"

    record = {
        "date": date_str,
        "briefing": briefing_data,
        "pdf_path": str(pdf_path) if pdf_path else None,
        "feedback_score": None,  # User fills this later via /briefing:score
        "generated_at": datetime.now().isoformat()
    }

    with open(history_file, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Morning Briefing")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly digest")
    parser.add_argument("--quick", action="store_true", help="Skip research agent")
    parser.add_argument("--test", action="store_true", help="Test mode (no notifications)")
    args = parser.parse_args()

    print(f"☀️ Morning Briefing — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    config = load_config()
    ensure_dirs()

    # Determine which collectors to run
    collectors = ["project-scanner", "session-analyst", "goals-tracker"]
    if not args.quick:
        collectors.append("research-scout")

    # Phase 1: Run collectors in parallel
    print(f"\n📡 Fase 1: Coletando dados ({len(collectors)} agentes)...")
    collector_results = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(run_collector, name, config): name
            for name in collectors
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                collector_results[name] = result
                status = "✅" if "error" not in result else "❌"
                print(f"  {status} {name}")
            except Exception as e:
                collector_results[name] = {"agent": name, "error": str(e)}
                print(f"  ❌ {name}: {e}")

    # Phase 2: Synthesize
    print("\n🧠 Fase 2: Sintetizando com Claude Opus...")
    is_sunday = datetime.now().weekday() == 6
    briefing = run_synthesizer(collector_results, config, weekly=args.weekly or is_sunday)

    # Phase 3: Generate outputs
    print("\n📄 Fase 3: Gerando outputs...")

    date_str = datetime.now().strftime("%Y-%m-%d")
    suffix = "_weekly" if (args.weekly or is_sunday) else ""
    pdf_filename = f"Briefing_{date_str}{suffix}.pdf"
    pdf_path = OUTPUT_DIR / pdf_filename

    # Generate PDF
    pdf_ok = generate_pdf(briefing, pdf_path)

    if not args.test:
        # Send notifications
        if config.get("notifications", {}).get("macos", True):
            send_macos_notification(briefing)
            print("  ✅ macOS notification")

        if config.get("notifications", {}).get("telegram", {}).get("enabled"):
            send_telegram(briefing, pdf_path if pdf_ok else None, config)
            print("  ✅ Telegram")
    else:
        print("  ⏭️  Test mode — notifications skipped")

    # Save to history
    save_history(briefing, pdf_path if pdf_ok else None)
    print("  ✅ History saved")

    print(f"\n✨ Briefing completo! PDF: {pdf_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
