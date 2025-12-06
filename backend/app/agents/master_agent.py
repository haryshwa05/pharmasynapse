import asyncio
from .clinical_trials_agent import ClinicalTrialsAgent
from .iqvia_agent import IQVIAAgent
from app.report.report_generator import ReportGenerator

class MasterAgent:
    def __init__(self):
        self.ct_agent = ClinicalTrialsAgent()
        self.iq_agent = IQVIAAgent()
        self.reporter = ReportGenerator()

    async def handle_query(self, payload: dict) -> dict:
        """
        Run ClinicalTrialsAgent and IQVIAAgent in parallel and synthesize result.
        """
        # prepare payloads (same molec)
        molec = payload.get("molecule", "")
        ct_payload = {"molecule": molec}
        iq_payload = {"molecule": molec}

        # run concurrently
        ct_task = asyncio.create_task(self.ct_agent.run(ct_payload))
        iq_task = asyncio.create_task(self.iq_agent.run(iq_payload))

        ct_res, iq_res = await asyncio.gather(ct_task, iq_task)

        # simple synthesis
        summary = {
            "molecule": molec,
            "clinical_trials": ct_res,
            "market_insights": iq_res
        }

        # generate PDF path (same simple report)
        pdf_path = self.reporter.generate_pdf(summary)
        summary["report"] = {"pdf_path": pdf_path}

        return summary
