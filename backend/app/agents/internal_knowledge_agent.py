import json
import os
from typing import Any, Dict, List, Optional

from .worker_base import WorkerBase

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "mock_internal_docs.json"
)
DOCS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "internal_docs"
)


class InternalKnowledgeAgent(WorkerBase):
    """
    Retrieves and summarizes internal documents (strategy decks, field insights).
    Uses mock JSON repo; no external calls.
    """

    def __init__(self, data_path: str = DATA_FILE, max_docs: int = 3):
        self.data_path = data_path
        self.max_docs = max_docs
        self._cache: Optional[Dict[str, Any]] = None

    def _load(self) -> Dict[str, Any]:
        if self._cache is None:
            with open(self.data_path, "r") as f:
                self._cache = json.load(f)
        return self._cache

    def _get_docs(self, molecule: str) -> List[Dict[str, Any]]:
        data = self._load()
        return data.get(molecule.lower()) or data.get("default", [])

    def _get_pdf_docs(self, molecule: str) -> List[Dict[str, Any]]:
        """
        Scan the internal_docs folder for PDFs named like '{molecule}_*.pdf'
        and return lightweight doc entries with download URLs (local paths).
        """
        docs: List[Dict[str, Any]] = []
        if not os.path.isdir(DOCS_DIR):
            return docs
        prefix = f"{molecule.lower()}_"
        for fname in os.listdir(DOCS_DIR):
            if not fname.lower().endswith(".pdf"):
                continue
            if not fname.lower().startswith(prefix):
                continue
            path = os.path.join(DOCS_DIR, fname)
            docs.append({
                "id": os.path.splitext(fname)[0],
                "title": fname,
                "type": "uploaded_pdf",
                "year": None,
                "summary": "Uploaded internal PDF (mock).",
                "key_takeaways": [],
                "comparative_table": [],
                "pdf_url": f"/internal/docs/{fname}",
                "local_path": path,
            })
        return docs

    def _filter_docs(
        self,
        docs: List[Dict[str, Any]],
        doc_type: Optional[str],
        year: Optional[int],
    ) -> List[Dict[str, Any]]:
        filtered = docs
        if doc_type:
            filtered = [d for d in filtered if d.get("type") == doc_type]
        if year:
            filtered = [d for d in filtered if d.get("year") == year]
        return filtered[: self.max_docs]

    def _build_summary(self, docs: List[Dict[str, Any]], molecule: str) -> str:
        if not docs:
            return f"No internal documents found for {molecule}."
        titles = [d.get("title") for d in docs if d.get("title")]
        return f"Internal insights for {molecule}: {len(docs)} doc(s) — " + "; ".join(titles)

    def run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        query = {
          "molecule": "metformin",
          "doc_type": "strategy_deck",  # optional
          "year": 2024                  # optional
        }
        """
        molecule = query.get("molecule")
        doc_type = query.get("doc_type")
        year = query.get("year")

        if not molecule:
            raise ValueError("InternalKnowledgeAgent requires 'molecule' in query")

        docs = self._get_docs(molecule) + self._get_pdf_docs(molecule)
        if not docs:
            return {
                "molecule": molecule,
                "available": False,
                "message": f"No internal docs found for {molecule}"
            }

        filtered = self._filter_docs(docs, doc_type=doc_type, year=year)

        return {
            "molecule": molecule,
            "filters": {"doc_type": doc_type, "year": year},
            "documents": filtered,
            "key_takeaways": [k for d in filtered for k in d.get("key_takeaways", [])],
            "comparative_tables": [d.get("comparative_table", []) for d in filtered],
            "summary": self._build_summary(filtered, molecule),
            "available": True,
        }


# Quick self-test
if __name__ == "__main__":
    agent = InternalKnowledgeAgent()
    res = agent.run({"molecule": "metformin"})
    print(res.get("summary"))
    print(len(res.get("documents", [])), "docs")

