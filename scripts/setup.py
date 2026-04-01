#!/usr/bin/env python3
"""
Morning Briefing — Interactive Setup Wizard
Guides new users through configuration step by step.

Usage:
    python3 setup.py
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
CONFIG_DIR = SKILL_DIR / "config"
CONFIG_PATH = CONFIG_DIR / "default.json"
EXAMPLE_PATH = CONFIG_DIR / "example.json"
COMMANDS_DIR = Path.home() / ".claude" / "commands"

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header():
    print(f"""
{BLUE}{BOLD}
  ┌─────────────────────────────────┐
  │     ☀️  Morning Briefing        │
  │     Setup Wizard v1.0           │
  └─────────────────────────────────┘
{RESET}
  Vamos configurar seu briefing diario em 5 passos.
  Tempo estimado: 3 minutos.
""")

def ask(question, default=None, required=True):
    """Ask user a question with optional default."""
    suffix = f" [{default}]" if default else ""
    while True:
        answer = input(f"  {question}{suffix}: ").strip()
        if not answer and default:
            return default
        if answer or not required:
            return answer
        print(f"  {RED}Campo obrigatorio.{RESET}")

def ask_yn(question, default="s"):
    """Ask yes/no question."""
    suffix = "[S/n]" if default == "s" else "[s/N]"
    answer = input(f"  {question} {suffix}: ").strip().lower()
    if not answer:
        return default == "s"
    return answer in ("s", "sim", "y", "yes")

def step_1_projects(config):
    """Configure project directories."""
    print(f"\n{BOLD}Passo 1/5 — Seus Projetos{RESET}")
    print(f"  Onde ficam seus projetos de codigo?\n")

    projects_root = ask(
        "Diretorio raiz dos projetos",
        default="~/Desktop/Sites e sistemas"
    )
    config["projects_root"] = projects_root

    # Expand and check
    expanded = os.path.expanduser(projects_root)
    if os.path.isdir(expanded):
        dirs = [d for d in os.listdir(expanded)
                if os.path.isdir(os.path.join(expanded, d))
                and not d.startswith(".")]
        print(f"  {GREEN}Encontrei {len(dirs)} pastas de projeto.{RESET}")
    else:
        print(f"  {YELLOW}Diretorio nao encontrado. Voce pode criar depois.{RESET}")

    return config

def step_2_clients(config):
    """Configure clients."""
    print(f"\n{BOLD}Passo 2/5 — Seus Clientes{RESET}")
    print(f"  Adicione seus clientes (ou pule se nao gerencia clientes).\n")

    if not ask_yn("Voce gerencia clientes?"):
        config["clients"] = []
        print(f"  {GREEN}OK, sem clientes. O briefing foca nos seus projetos.{RESET}")
        return config

    clients = []
    while True:
        print(f"\n  {BLUE}--- Cliente {len(clients) + 1} ---{RESET}")
        name = ask("Nome do cliente")
        project_dir = ask("Pasta do projeto (relativa ao diretorio raiz)", required=False)

        budget = ask("Orcamento mensal em R$ (ou Enter para pular)", required=False)
        budget = int(budget) if budget and budget.isdigit() else None

        platform = ask("Plataforma de ads (google/meta/nenhuma)", default="nenhuma")
        if platform == "nenhuma":
            platform = None

        clients.append({
            "name": name,
            "project_dir": project_dir or "",
            "memory_file": f"{name.lower().replace(' ', '-')}.md",
            "ads_platform": platform,
            "monthly_budget": budget
        })

        print(f"  {GREEN}Cliente '{name}' adicionado.{RESET}")

        if not ask_yn("Adicionar outro cliente?", default="n"):
            break

    config["clients"] = clients
    return config

def step_3_notifications(config):
    """Configure notification channels."""
    print(f"\n{BOLD}Passo 3/5 — Notificacoes{RESET}")
    print(f"  Como voce quer receber seu briefing?\n")

    # macOS
    config["notifications"]["macos"] = True
    print(f"  {GREEN}macOS notification: Ativada automaticamente.{RESET}")

    # Telegram
    print(f"""
  {BOLD}Telegram (recomendado){RESET}
  Para receber o briefing no celular via Telegram:
  1. Abra o Telegram e busque @BotFather
  2. Envie /newbot e siga as instrucoes
  3. Copie o token do bot
  4. Envie uma mensagem para seu bot
  5. Acesse: https://api.telegram.org/bot<TOKEN>/getUpdates
  6. Copie o chat_id da resposta
""")

    if ask_yn("Configurar Telegram agora?", default="n"):
        token = ask("Bot token")
        chat_id = ask("Chat ID")
        config["notifications"]["telegram"] = {
            "enabled": True,
            "bot_token": token,
            "chat_id": chat_id
        }
        print(f"  {GREEN}Telegram configurado!{RESET}")
    else:
        config["notifications"]["telegram"] = {
            "enabled": False,
            "bot_token": "",
            "chat_id": ""
        }
        print(f"  {YELLOW}Telegram pulado. Configure depois no config/default.json{RESET}")

    # WhatsApp
    print(f"""
  {BOLD}WhatsApp (opcional){RESET}
  Requer Evolution API rodando no seu servidor.
  Guia: github.com/EvolutionAPI/evolution-api
""")

    if ask_yn("Configurar WhatsApp agora?", default="n"):
        api_url = ask("URL da Evolution API")
        instance = ask("Nome da instancia", default="default")
        number = ask("Numero destino (com DDI, ex: 5511999999999)")
        config["notifications"]["whatsapp"] = {
            "enabled": True,
            "evolution_api_url": api_url,
            "instance": instance,
            "target_number": number
        }
        print(f"  {GREEN}WhatsApp configurado!{RESET}")
    else:
        config["notifications"]["whatsapp"] = {
            "enabled": False,
            "evolution_api_url": "",
            "instance": "",
            "target_number": ""
        }

    return config

def step_4_schedule(config):
    """Configure schedule."""
    print(f"\n{BOLD}Passo 4/5 — Horario{RESET}")

    hour = ask("Que horas quer receber o briefing? (formato 24h)", default="06:00")
    config["schedule"]["daily"] = hour

    tz = ask("Seu fuso horario", default="America/Sao_Paulo")
    config["schedule"]["timezone"] = tz

    return config

def step_5_research(config):
    """Configure research topics."""
    print(f"\n{BOLD}Passo 5/5 — Topicos de Pesquisa{RESET}")
    print(f"  O agente @research-scout vai buscar noticias sobre esses temas.\n")

    print(f"  Exemplos: 'Google Ads updates', 'React best practices', 'AI tools'\n")

    topics = []
    while True:
        topic = ask("Adicione um topico (ou Enter para finalizar)", required=False)
        if not topic:
            break
        topics.append(topic)
        print(f"  {GREEN}+ {topic}{RESET}")

    if not topics:
        topics = ["technology updates", "developer tools", "AI news"]
        print(f"  {YELLOW}Usando topicos padrao: {', '.join(topics)}{RESET}")

    config["research_topics"] = topics
    return config

def install_command():
    """Install the /briefing slash command."""
    src = SKILL_DIR / "commands" / "briefing.md"
    if not src.exists():
        # Try root level
        src = SKILL_DIR.parent.parent / "commands" / "briefing.md"

    dest = COMMANDS_DIR / "briefing.md"
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        print(f"  {GREEN}Comando /briefing ja instalado.{RESET}")
    else:
        # Create a basic command file
        dest.write_text("""---
name: briefing
description: Generate your daily Morning Briefing
user_invocable: true
---

# /briefing

Run Morning Briefing on demand.

```bash
SKILL_DIR="$HOME/.claude/skills/morning-briefing"
python3 "$SKILL_DIR/scripts/briefing.py" --test
```
""")
        print(f"  {GREEN}Comando /briefing instalado.{RESET}")

def install_schedule(config):
    """Install launchd schedule on macOS."""
    if sys.platform != "darwin":
        print(f"  {YELLOW}Sistema nao e macOS. Use cron:{RESET}")
        hour = config["schedule"]["daily"].split(":")[0]
        minute = config["schedule"]["daily"].split(":")[1] if ":" in config["schedule"]["daily"] else "0"
        print(f"  {minute} {hour} * * * /usr/bin/python3 {SKILL_DIR}/scripts/briefing.py")
        return

    plist_src = SKILL_DIR / "com.jhon.morning-briefing.plist"
    plist_dest = Path.home() / "Library" / "LaunchAgents" / "com.morning-briefing.plist"

    # Create logs dir
    (SKILL_DIR / "logs").mkdir(exist_ok=True)

    if plist_src.exists():
        # Update plist with user's schedule
        hour = int(config["schedule"]["daily"].split(":")[0])
        minute = int(config["schedule"]["daily"].split(":")[1]) if ":" in config["schedule"]["daily"] else 0

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.morning-briefing</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{SKILL_DIR}/scripts/briefing.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{SKILL_DIR}/logs/briefing.log</string>
    <key>StandardErrorPath</key>
    <string>{SKILL_DIR}/logs/briefing_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
        <key>HOME</key>
        <string>{Path.home()}</string>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>Nice</key>
    <integer>10</integer>
</dict>
</plist>"""

        plist_dest.write_text(plist_content)

        # Load it
        subprocess.run(["launchctl", "unload", str(plist_dest)],
                       capture_output=True)
        result = subprocess.run(["launchctl", "load", str(plist_dest)],
                                capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  {GREEN}Schedule ativado: todo dia as {config['schedule']['daily']}{RESET}")
        else:
            print(f"  {YELLOW}Erro ao ativar schedule: {result.stderr}{RESET}")
    else:
        print(f"  {YELLOW}Arquivo plist nao encontrado. Configure manualmente.{RESET}")

def check_requirements():
    """Check if required tools are installed."""
    print(f"\n{BOLD}Verificando requisitos...{RESET}\n")

    checks = []

    # Python
    checks.append(("Python 3.10+", sys.version_info >= (3, 10)))

    # Claude CLI
    claude_ok = shutil.which("claude") is not None
    checks.append(("Claude Code CLI", claude_ok))

    # fpdf2
    try:
        import fpdf
        checks.append(("fpdf2 (PDF)", True))
    except ImportError:
        checks.append(("fpdf2 (PDF)", False))

    for name, ok in checks:
        status = f"{GREEN}OK{RESET}" if ok else f"{RED}FALTANDO{RESET}"
        print(f"  {status}  {name}")

    # Install fpdf2 if missing
    if not checks[2][1]:
        print(f"\n  Instalando fpdf2...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "fpdf2",
                           "--user", "--quiet"], check=True)
            print(f"  {GREEN}fpdf2 instalado!{RESET}")
        except subprocess.CalledProcessError:
            print(f"  {YELLOW}Nao consegui instalar. Rode: pip install fpdf2{RESET}")

    if not claude_ok:
        print(f"\n  {YELLOW}Claude Code CLI nao encontrado no PATH.")
        print(f"  Instale em: https://claude.ai/code{RESET}")

    return all(ok for _, ok in checks)

def main():
    print_header()

    # Check requirements
    all_ok = check_requirements()

    # Load example config as base
    if EXAMPLE_PATH.exists():
        with open(EXAMPLE_PATH) as f:
            config = json.load(f)
    else:
        config = {
            "schedule": {"daily": "06:00", "weekly_digest": "sunday", "timezone": "America/Sao_Paulo"},
            "projects_root": "~/Projects",
            "notifications": {"macos": True, "telegram": {}, "whatsapp": {}},
            "clients": [],
            "research_topics": [],
            "self_improvement": {"enabled": True, "min_feedback_score": 3, "auto_evolve_instincts": True, "weekly_meta_analysis": True}
        }

    # Run steps
    config = step_1_projects(config)
    config = step_2_clients(config)
    config = step_3_notifications(config)
    config = step_4_schedule(config)
    config = step_5_research(config)

    # Save config
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"\n  {GREEN}Configuracao salva em {CONFIG_PATH}{RESET}")

    # Install command
    print(f"\n{BOLD}Instalando...{RESET}\n")
    install_command()

    # Install schedule
    if ask_yn("Ativar briefing automatico diario?"):
        install_schedule(config)
    else:
        print(f"  {YELLOW}Schedule pulado. Ative depois ou use /briefing manualmente.{RESET}")

    # Summary
    print(f"""
{GREEN}{BOLD}
  ╔═══════════════════════════════════════╗
  ║   ☀️  Morning Briefing Configurado!   ║
  ╚═══════════════════════════════════════╝
{RESET}
  {BOLD}O que foi configurado:{RESET}
  • Projetos: {config['projects_root']}
  • Clientes: {len(config.get('clients', []))}
  • Telegram: {'Ativo' if config.get('notifications', {}).get('telegram', {}).get('enabled') else 'Desativado'}
  • WhatsApp: {'Ativo' if config.get('notifications', {}).get('whatsapp', {}).get('enabled') else 'Desativado'}
  • Horario: {config['schedule']['daily']}
  • Topicos: {', '.join(config.get('research_topics', [])[:3])}

  {BOLD}Proximos passos:{RESET}
  1. Teste agora: /briefing (dentro do Claude Code)
  2. Ou no terminal: python3 {SKILL_DIR}/scripts/briefing.py --test
  3. Amanha as {config['schedule']['daily']}: seu primeiro briefing automatico!

  {BOLD}Precisa de ajuda?{RESET}
  github.com/jhojuneo/morning-briefing/issues
""")

if __name__ == "__main__":
    main()
