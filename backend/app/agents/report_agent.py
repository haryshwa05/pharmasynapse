import os
from typing import Any, Dict

from .master_agent import MasterAgent
from app.report.report_generator import ReportGenerator


class ReportAgent:
    """
    Orchestrates analysis then formats a PDF report. Returns paths/URLs.
    """

    def __init__(self):
        self.master = MasterAgent()
        self.generator = ReportGenerator()

    def run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        query: {
          "molecule": "...",
          "disease": "...",
          "region": "...",
          "doc_type": "...", # optional for internal filter (future)
          "year": 2024       # optional for internal/EXIM filter (future)
        }
        """
        analysis = self.master.analyze_molecule(
            molecule=query.get("molecule"),
            disease=query.get("disease"),
            region=query.get("region"),
        )

        pdf_path = self.generator.generate_pdf(analysis)
        pdf_name = os.path.basename(pdf_path)
        pdf_url = f"/reports/{pdf_name}"

        return {
            "analysis": analysis,
            "report_pdf": {
                "path": pdf_path,
                "url": pdf_url,
            },
        }

