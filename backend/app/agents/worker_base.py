from abc import ABC, abstractmethod

class WorkerAgent(ABC):
    @abstractmethod
    async def run(self, payload: dict) -> dict:
        """Return dict: {status, data, notes, references}"""
        pass
