# backend/app/report/report_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
os.makedirs(OUT_DIR, exist_ok=True)

class ReportGenerator:
    def generate_pdf(self, summary: dict) -> str:
        """Create a very small PDF that lists clinical trials and a one-line market insight."""
        molecule = summary.get("molecule", "unknown")
        fname = f"report_{molecule}.pdf"
        path = os.path.join(OUT_DIR, fname)

        c = canvas.Canvas(path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"Research Report — {molecule}")

        # Clinical trials
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 720, "Clinical Trials (mock):")
        c.setFont("Helvetica", 10)
        trials = summary.get("clinical_trials", {}).get("data", {}).get("trials", [])
        y = 700
        for t in trials[:10]:
            title = t.get("title", "untitled")
            phase = t.get("phase", "N/A")
            c.drawString(60, y, f"- {title} (phase {phase})")
            y -= 14
            if y < 80:
                c.showPage()
                y = 750

        # IQVIA market snippet (if present)
        iq = summary.get("market_insights", {}).get("data", {})
        if iq:
            if y < 150:
                c.showPage()
                y = 750
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y - 10, "Market Insights (mock):")
            c.setFont("Helvetica", 10)
            c.drawString(60, y - 30, f"Market size (USD mn): {iq.get('market_size_usd_mn', 'N/A')}")
            c.drawString(60, y - 44, f"CAGR: {iq.get('cagr', 'N/A')}")

        c.showPage()
        c.save()
        return path
