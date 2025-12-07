# backend/app/agents/worker_base.py

from abc import ABC, abstractmethod
from typing import Dict, Any


class WorkerBase(ABC):
    """
    Abstract base class for all worker agents.

    Each worker must implement `run` and return a dict, so the master agent
    can treat them all in a uniform way.
    """

    @abstractmethod
    def run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the worker's task.

        Args:
            query: A dictionary containing the worker-specific inputs
                   (e.g., {"molecule": "metformin", "region": "US"}).

        Returns:
            A dictionary with structured results for this worker.
        """
        raise NotImplementedError
