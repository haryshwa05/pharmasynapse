# backend/app/report/report_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from typing import Dict, Any, List
import os

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
os.makedirs(OUT_DIR, exist_ok=True)


class ReportGenerator:
    """
    Formats the synthesized response into a simple PDF with tables and bullet sections.
    """

    def _draw_header(self, c: canvas.Canvas, molecule: str):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"PharmaSynapse Report — {molecule}")
        c.setStrokeColor(colors.grey)
        c.line(50, 745, 560, 745)

    def _draw_section_title(self, c: canvas.Canvas, title: str, y: int) -> int:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, title)
        return y - 16

    def _draw_bullets(self, c: canvas.Canvas, items: List[str], y: int) -> int:
        c.setFont("Helvetica", 10)
        for it in items:
            c.drawString(60, y, f"• {it}")
            y -= 14
            if y < 80:
                c.showPage()
                y = 750
        return y

    def _draw_simple_table(self, c: canvas.Canvas, rows: List[List[str]], y: int) -> int:
        c.setFont("Helvetica", 10)
        for row in rows:
            line = " | ".join(row)
            c.drawString(60, y, line)
            y -= 14
            if y < 80:
                c.showPage()
                y = 750
        return y

    def _safe_get(self, d: Dict[str, Any], key: str, default: str = "N/A") -> Any:
        return d.get(key, default) if isinstance(d, dict) else default

    def generate_pdf(self, analysis: Dict[str, Any]) -> str:
        molecule = analysis.get("molecule", "unknown")
        fname = f"report_{molecule}.pdf"
        path = os.path.join(OUT_DIR, fname)

        c = canvas.Canvas(path, pagesize=letter)
        y = 750
        self._draw_header(c, molecule)
        y -= 24

        # Market (IQVIA)
        iq = analysis.get("iqvia", {}) or {}
        y = self._draw_section_title(c, "Market (IQVIA mock)", y)
        iq_rows = []
        regions = iq.get("regions", {}) if isinstance(iq, dict) else {}
        for rname, rdata in regions.items():
            iq_rows.append([
                rname,
                f"${rdata.get('market_size_usd_mn','?')}M",
                f"{rdata.get('cagr_5y_percent','?')}% CAGR",
                f"{len(rdata.get('competitors', []))} comps"
            ])
        if iq_rows:
            y = self._draw_simple_table(c, iq_rows, y)
        else:
            y = self._draw_bullets(c, [iq.get("message", "No market data found")], y)

        # Patents
        patents = analysis.get("patents", {}) or {}
        y = self._draw_section_title(c, "Patent Landscape", y)
        pov = patents.get("overview", {}) if isinstance(patents, dict) else {}
        patent_summary = patents.get("summary") or "No patent summary available."
        bullets = [
            f"Total: {pov.get('total','?')} | Active: {pov.get('active_count','?')} | Expired: {pov.get('expired_count','?')}",
            patent_summary
        ]
        y = self._draw_bullets(c, bullets, y)

        # Clinical trials
        trials = analysis.get("trials", {}) or {}
        y = self._draw_section_title(c, "Clinical Trials", y)
        tlist = trials.get("trials", []) if isinstance(trials, dict) else []
        trial_rows = []
        for t in tlist[:8]:
            trial_rows.append([
                t.get("trial_id", "N/A"),
                t.get("phase", "N/A"),
                t.get("status", "N/A"),
                t.get("condition", "N/A"),
            ])
        if trial_rows:
            y = self._draw_simple_table(c, trial_rows, y)
        else:
            y = self._draw_bullets(c, [trials.get("message", "No trials data found")], y)

        # Web intelligence
        web = analysis.get("web", {}) or {}
        y = self._draw_section_title(c, "Web Intelligence (guidelines/RWE/news)", y)
        web_summary = web.get("summary") or "No web results."
        y = self._draw_bullets(c, [web_summary], y)

        # EXIM
        exim = analysis.get("exim", {}) or {}
        y = self._draw_section_title(c, "EXIM Trade", y)
        exim_summary = exim.get("summary") or "No EXIM data."
        y = self._draw_bullets(c, [exim_summary], y)

        # Internal docs
        internal = analysis.get("internal", {}) or {}
        y = self._draw_section_title(c, "Internal Documents", y)
        docs = internal.get("documents", []) if isinstance(internal, dict) else []
        doc_rows = []
        for d in docs[:6]:
            doc_rows.append([
                d.get("title", "Untitled"),
                d.get("type", "doc"),
                str(d.get("year", "")),
            ])
        if doc_rows:
            y = self._draw_simple_table(c, doc_rows, y)
        else:
            y = self._draw_bullets(c, [internal.get("message", "No internal docs found")], y)

        c.showPage()
        c.save()
        return path
