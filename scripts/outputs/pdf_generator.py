#!/usr/bin/env python3
"""
Generate a beautiful PDF briefing from synthesized JSON data.
Usage: python3 pdf_generator.py <input.json> <output.pdf>
"""

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    # Try venv
    import subprocess
    venv = Path("/tmp/briefing_env")
    if not venv.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        subprocess.run([str(venv / "bin" / "pip"), "install", "fpdf2", "-q"], check=True)

    sys.path.insert(0, str(venv / "lib"))
    # Re-find fpdf2 in venv site-packages
    import glob
    site_pkgs = glob.glob(str(venv / "lib" / "python*" / "site-packages"))
    if site_pkgs:
        sys.path.insert(0, site_pkgs[0])
    from fpdf import FPDF


class BriefingPDF(FPDF):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        date = self.data.get("date", "")
        self.cell(0, 8, f"Morning Briefing — {date}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 16, 200, 16)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def status_color(self, status):
        colors = {
            "green": (34, 197, 94),
            "yellow": (245, 158, 11),
            "red": (239, 68, 68),
        }
        return colors.get(status, (120, 120, 120))

    def section_title(self, emoji, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 60, 120)
        self.cell(0, 10, f"{emoji}  {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def body_text(self, text, bold=False):
        self.set_font("Helvetica", "B" if bold else "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, str(text))
        self.ln(1)

    def bullet(self, text, indent=6):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(indent)
        # Use a simple dash instead of bullet char for encoding safety
        self.multi_cell(0, 6, f"- {text}")

    def alert_box(self, text, level="warning"):
        colors = {
            "critical": (239, 68, 68),
            "warning": (245, 158, 11),
            "info": (59, 130, 246),
        }
        r, g, b = colors.get(level, (245, 158, 11))
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, f"  {level.upper()}: {text}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(40, 40, 40)
        self.ln(2)

    def client_card(self, client):
        name = client.get("name", "Cliente")
        status = client.get("status", "active")
        health = client.get("health", "green")

        r, g, b = self.status_color(health)
        self.set_draw_color(r, g, b)
        self.set_line_width(0.5)

        y_start = self.get_y()
        self.rect(10, y_start, 190, 35)

        self.set_font("Helvetica", "B", 11)
        self.set_text_color(r, g, b)
        self.cell(10)
        self.cell(0, 7, f"{name}", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 80)

        details = []
        if "last_action" in client:
            days = client.get("days_since_last_action", "?")
            details.append(f"Ultimo contato: {days} dias atras")
        if "budget" in client and client["budget"]:
            b = client["budget"]
            details.append(f"Budget: R${b.get('spent', 0)} / R${b.get('monthly', 0)} ({b.get('pct', 0)}%)")
        if "next_action" in client:
            details.append(f"Proximo: {client['next_action']}")
        if "alert" in client and client["alert"]:
            details.append(f"ALERTA: {client['alert']}")

        for detail in details:
            self.cell(10)
            self.cell(0, 5, detail, new_x="LMARGIN", new_y="NEXT")

        self.set_y(y_start + 38)

    def build(self):
        self.alias_nb_pages()

        # Cover page
        self.add_page()
        self.ln(30)
        self.set_font("Helvetica", "B", 32)
        self.set_text_color(30, 60, 120)
        self.cell(0, 15, "Morning Briefing", align="C", new_x="LMARGIN", new_y="NEXT")

        self.ln(5)
        self.set_font("Helvetica", "", 16)
        self.set_text_color(80, 80, 80)
        date = self.data.get("date", datetime.now().strftime("%Y-%m-%d"))
        weekday = self.data.get("weekday", "")
        self.cell(0, 10, f"{weekday}, {date}", align="C", new_x="LMARGIN", new_y="NEXT")

        self.ln(10)

        # Health indicators
        health = self.data.get("health", {})
        labels = [("Projetos", "projects"), ("Clientes", "clients"), ("Financeiro", "finance")]

        x_start = 45
        for i, (label, key) in enumerate(labels):
            x = x_start + i * 50
            status = health.get(key, "green")
            r, g, b = self.status_color(status)
            self.set_fill_color(r, g, b)
            self.set_xy(x, self.get_y())
            self.ellipse(x + 15, self.get_y(), 12, 12, style="F")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(80, 80, 80)
            self.set_xy(x + 5, self.get_y() + 15)
            self.cell(30, 6, label, align="C")

        self.ln(30)

        # Greeting
        greeting = self.data.get("greeting", "Bom dia! Seu briefing esta pronto.")
        self.set_font("Helvetica", "I", 12)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 8, greeting, align="C")

        # Alerts
        alerts = self.data.get("alerts", [])
        if alerts:
            self.add_page()
            self.section_title("!", "Alertas Urgentes")
            for alert in alerts:
                if isinstance(alert, dict):
                    level = alert.get("priority", "warning").lower()
                    msg = alert.get("message", str(alert))
                else:
                    level = "warning"
                    msg = str(alert)
                self.alert_box(msg, level)

        # Agenda
        agenda = self.data.get("agenda", [])
        if agenda:
            self.section_title(">>", "Agenda do Dia")
            for item in agenda:
                if isinstance(item, dict):
                    time = item.get("time", "")
                    task = item.get("task", item.get("event", str(item)))
                    duration = item.get("duration", "")
                    self.bullet(f"{time} — {task} ({duration})" if time else str(task))
                else:
                    self.bullet(str(item))

        # Clients
        clients = self.data.get("clients", [])
        if clients:
            self.add_page()
            self.section_title("$", "Status dos Clientes")
            for client in clients:
                if isinstance(client, dict):
                    self.client_card(client)
                else:
                    self.bullet(str(client))

        # Yesterday
        yesterday = self.data.get("yesterday", {})
        if yesterday:
            self.section_title("<", "O que voce fez ontem")
            if isinstance(yesterday, dict):
                for key, val in yesterday.items():
                    self.bullet(f"{key}: {val}")
            else:
                self.body_text(str(yesterday))

        # Insights
        insights = self.data.get("insights", [])
        if insights:
            self.add_page()
            self.section_title("*", "Insights do Dia")
            for i, insight in enumerate(insights, 1):
                if isinstance(insight, dict):
                    self.body_text(f"{i}. {insight.get('title', '')}", bold=True)
                    self.body_text(f"   {insight.get('description', str(insight))}")
                    if insight.get("action"):
                        self.bullet(f"Acao: {insight['action']}")
                else:
                    self.body_text(f"{i}. {insight}")
                self.ln(2)

        # Tip of the day
        tip = self.data.get("tip_of_day", {})
        if tip:
            self.section_title("#", "Dica do Dia")
            if isinstance(tip, dict):
                self.body_text(tip.get("title", ""), bold=True)
                self.body_text(tip.get("description", str(tip)))
                if tip.get("source"):
                    self.set_font("Helvetica", "I", 9)
                    self.set_text_color(100, 100, 100)
                    self.cell(0, 6, f"Fonte: {tip['source']}", new_x="LMARGIN", new_y="NEXT")
            else:
                self.body_text(str(tip))

        # Weekly digest
        weekly = self.data.get("weekly_digest")
        if weekly:
            self.add_page()
            self.section_title("W", "Digest Semanal")
            if isinstance(weekly, dict):
                for key, val in weekly.items():
                    self.body_text(f"{key}:", bold=True)
                    if isinstance(val, list):
                        for item in val:
                            self.bullet(str(item))
                    else:
                        self.body_text(str(val))
                    self.ln(2)
            else:
                self.body_text(str(weekly))

        # Meta footer
        self.add_page()
        self.ln(20)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(150, 150, 150)
        meta = self.data.get("meta", {})
        self.cell(0, 6, f"Gerado por Morning Briefing v1.0.0", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, f"Agentes: {meta.get('collectors_used', 4)} | Dados analisados: {meta.get('data_points_analyzed', 'N/A')}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, f"Tempo de geracao: {meta.get('generation_time_seconds', 'N/A')}s", align="C", new_x="LMARGIN", new_y="NEXT")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 pdf_generator.py <input.json> <output.pdf>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path) as f:
        data = json.load(f)

    pdf = BriefingPDF(data)
    pdf.build()
    pdf.output(str(output_path))
    print(f"PDF saved: {output_path}")


if __name__ == "__main__":
    main()
