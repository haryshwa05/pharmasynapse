from .clinical_trials_agent import ClinicalTrialsAgent

class MasterAgent:
    def __init__(self):
        self.ct_agent = ClinicalTrialsAgent()

    async def handle_query(self, payload: dict):
        ct_res = await self.ct_agent.run(payload)

        return {
            "molecule": payload.get("molecule"),
            "clinical_trials": ct_res
        }
