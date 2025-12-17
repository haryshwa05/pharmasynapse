import datetime
from typing import Any, Dict, List, Optional

from duckduckgo_search import DDGS

from .worker_base import WorkerBase


class WebIntelligenceAgent(WorkerBase):
    """
    Lightweight web intelligence agent using DuckDuckGo (free, no API key).
    Fetches recent guidelines, real-world evidence (RWE), and news links.
    """

    def __init__(self, max_results: int = 6):
        self.max_results = max_results

    def _search(self, query: str) -> List[Dict[str, Any]]:
        with DDGS() as ddgs:
            # duckduckgo_search returns a list of dicts with title, href, body
            return ddgs.text(query, max_results=self.max_results) or []

    def _dedupe(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        deduped = []
        for item in items:
            href = item.get("href")
            if href and href not in seen:
                seen.add(href)
                deduped.append(
                    {
                        "title": item.get("title"),
                        "url": href,
                        "snippet": item.get("body"),
                    }
                )
        return deduped

    def run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        query = {
          "molecule": "metformin",
          "disease": "NAFLD"   # optional
        }
        """
        molecule = query.get("molecule")
        disease = query.get("disease")

        if not molecule:
            raise ValueError("WebIntelligenceAgent requires 'molecule' in query")

        # Build comprehensive category-specific queries
        scope = f"{molecule} {disease}" if disease else molecule
        queries = {
            "guidelines": f"{scope} clinical practice guideline site:nih.gov OR site:fda.gov OR site:ema.europa.eu",
            "rwe": f"{scope} real world evidence study site:pubmed.ncbi.nlm.nih.gov OR site:nejm.org OR site:thelancet.com",
            "news": f"latest news {scope} drug development clinical trials",
            "regulatory": f"{scope} FDA approval EMA approval regulatory status",
            "publications": f"{scope} scientific publications review articles meta analysis",
            "market_news": f"{scope} market access reimbursement pricing strategy",
        }

        results: Dict[str, Any] = {"available": True, "as_of": datetime.date.today().isoformat()}

        for topic, q in queries.items():
            raw = self._search(q)
            cleaned = self._dedupe(raw)
            results[topic] = cleaned

        results["summary"] = self._build_summary(results, molecule, disease)
        results["molecule"] = molecule
        results["disease"] = disease
        return results

    def _build_summary(self, res: Dict[str, Any], molecule: str, disease: Optional[str]) -> str:
        parts = []
        scope = f"{molecule}" + (f" in {disease}" if disease else "")

        # Count total sources
        total_sources = sum(len(res.get(topic, [])) for topic in ["guidelines", "rwe", "news", "regulatory", "publications", "market_news"])

        # Build detailed summary
        categories = {
            "guidelines": "clinical guidelines",
            "rwe": "real-world evidence studies",
            "regulatory": "regulatory updates",
            "publications": "scientific publications",
            "market_news": "market intelligence",
            "news": "recent news articles"
        }

        active_categories = []
        for topic, description in categories.items():
            count = len(res.get(topic, []))
            if count > 0:
                active_categories.append(f"{count} {description}")

        summary = f"Comprehensive web intelligence for {scope}: {total_sources} sources across {', '.join(active_categories)}. "
        summary += f"Data sourced from PubMed, FDA, EMA, and major pharmaceutical news outlets as of {res.get('as_of', 'today')}."

        return summary


