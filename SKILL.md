---
name: morning-briefing
description: Daily AI-powered intelligence briefing — analyzes projects, sessions, finances, clients, and generates PDF + notifications every morning
version: 1.0.0
author: Jhon Carvalho
triggers:
  - schedule: "0 6 * * *"
  - command: /briefing
  - command: /briefing:weekly
  - command: /briefing:now
  - command: /briefing:config
tags: [productivity, intelligence, multi-agent, daily, briefing]
---

# Morning Briefing

Sistema multi-agente que analisa todo o seu ambiente de trabalho durante a madrugada e gera um briefing personalizado com insights, alertas, dicas e plano do dia.

## Como funciona

### Trigger
- **Automatico**: launchd roda `briefing.py` as 6h da manha
- **Manual**: `/briefing:now` para gerar sob demanda
- **Semanal**: Domingos gera versao expandida com graficos

### Fase 1 — Coleta (Agentes Paralelos)
4 agentes rodam simultaneamente coletando dados:

| Agente | Fonte | O que coleta |
|--------|-------|-------------|
| `@project-scanner` | ~/Desktop/Sites e sistemas/ | git log 24h, branches, TODOs, erros de build |
| `@session-analyst` | ~/.claude/ | instintos, sessoes salvas, padroes aprendidos, erros recorrentes |
| `@research-scout` | Web | noticias tech, updates de ferramentas usadas, vulnerabilidades |
| `@goals-tracker` | memory/, Calendar, finance | metas, prazos, agenda do dia, saldo financeiro, gastos ads |

### Fase 2 — Sintese
`@synthesizer` (Claude Opus) combina todos os dados e gera:
- Top 5 insights priorizados por urgencia
- Alertas (gastos anomalos, deadlines proximos, erros criticos)
- Dicas praticas baseadas em dificuldades recentes
- Sugestoes de melhoria com base em padroes detectados
- Plano sugerido para o dia
- Score de cada cliente ativo

### Fase 3 — Output
- **PDF** salvo em ~/Desktop/Briefings/
- **Telegram** resumo + PDF via bot
- **WhatsApp** destaques via Evolution API (opcional)
- **macOS notification** com preview
- **Audio** resumo em MP3 via TTS (opcional)
- **Memory update** atualiza ~/.claude/memory/ com novos insights
- **Instincts evolved** promove padroes que se repetiram

### Fase 4 — Auto-melhoria
- Cada briefing gera um `feedback_score` (1-5) que voce pode dar
- Scores baixos fazem o skill ajustar o que prioriza
- Padroes de alta utilidade viram instintos permanentes
- Weekly digest inclui meta-analise: "o que o briefing acertou/errou essa semana"

## Comandos

| Comando | Descricao |
|---------|-----------|
| `/briefing:now` | Gera briefing imediatamente |
| `/briefing:weekly` | Gera digest semanal expandido |
| `/briefing:config` | Configura preferencias (horario, canais, clientes) |
| `/briefing:score <1-5>` | Da feedback sobre o briefing de hoje |
| `/briefing:history` | Lista briefings anteriores |

## Requisitos
- macOS com launchd (ou cron no Linux)
- Claude Code CLI (`claude` no PATH)
- Python 3.10+ com fpdf2
- Telegram bot token (opcional)
- Evolution API endpoint (opcional, para WhatsApp)
