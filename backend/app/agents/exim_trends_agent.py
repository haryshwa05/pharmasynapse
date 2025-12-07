import json
import os
from typing import Any, Dict, List, Optional

from .worker_base import WorkerBase

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "mock_exim.json"
)


class EximTrendsAgent(WorkerBase):
    """
    Summarizes import/export trends for a molecule using mock EXIM data.
    Returns totals, top exporters/importers, import dependency, and bullet insights.
    """

    def __init__(self, data_path: str = DATA_FILE, top_n: int = 5):
        self.data_path = data_path
        self.top_n = top_n
        self._cache: Optional[Dict[str, Any]] = None

    def _load_data(self) -> Dict[str, Any]:
        if self._cache is None:
            with open(self.data_path, "r") as f:
                self._cache = json.load(f)
        return self._cache

    def _get_entry(self, molecule: str) -> Optional[Dict[str, Any]]:
        data = self._load_data()
        return data.get(molecule.lower())

    def _filter(
        self,
        records: List[Dict[str, Any]],
        year: Optional[int] = None,
        countries: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        if not records:
            return []
        filtered = records
        if year is not None:
            filtered = [r for r in filtered if r.get("year") == year]
        if countries:
            country_set = {c.lower() for c in countries}
            filtered = [r for r in filtered if r.get("country", "").lower() in country_set]
        return filtered

    def _sum(self, records: List[Dict[str, Any]], key: str) -> float:
        return float(sum(r.get(key, 0) or 0 for r in records))

    def _top(self, records: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        return sorted(records, key=lambda r: r.get(key, 0) or 0, reverse=True)[: self.top_n]

    def _dependency_table(self, imports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        total_value = self._sum(imports, "value_usd_mn")
        if total_value == 0:
            return []
        table = []
        for r in imports:
            share = round((r.get("value_usd_mn", 0) or 0) / total_value * 100, 1)
            table.append({
                "country": r.get("country"),
                "year": r.get("year"),
                "value_usd_mn": r.get("value_usd_mn"),
                "volume_tons": r.get("volume_tons"),
                "share_percent": share,
            })
        return self._top(table, "value_usd_mn")

    def _build_summary(
        self,
        molecule: str,
        exports: List[Dict[str, Any]],
        imports: List[Dict[str, Any]],
        top_exports: List[Dict[str, Any]],
        top_imports: List[Dict[str, Any]],
    ) -> str:
        total_export = self._sum(exports, "value_usd_mn")
        total_import = self._sum(imports, "value_usd_mn")
        lead_exporter = top_exports[0]["country"] if top_exports else "N/A"
        lead_importer = top_imports[0]["country"] if top_imports else "N/A"
        return (
            f"EXIM trends for {molecule}: exports ${total_export:.1f}M, "
            f"imports ${total_import:.1f}M. "
            f"Top exporter: {lead_exporter}; top importer: {lead_importer}."
        )

    def run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        query = {
          "molecule": "metformin",
          "year": 2024,           # optional
          "countries": ["India"]  # optional filter list
        }
        """
        molecule = query.get("molecule")
        year = query.get("year")
        countries = query.get("countries")

        if not molecule:
            raise ValueError("EximTrendsAgent requires 'molecule' in query")

        entry = self._get_entry(molecule)
        if not entry:
            return {
                "molecule": molecule,
                "available": False,
                "message": f"No EXIM mock data found for {molecule}"
            }

        exports = self._filter(entry.get("exports", []), year=year, countries=countries)
        imports = self._filter(entry.get("imports", []), year=year, countries=countries)

        top_exporters = self._top(exports, "value_usd_mn")
        top_importers = self._top(imports, "value_usd_mn")
        dependency = self._dependency_table(imports)

        summary = self._build_summary(
            molecule=entry.get("molecule", molecule),
            exports=exports,
            imports=imports,
            top_exports=top_exporters,
            top_imports=top_importers,
        )

        # Combine canned insights with auto-generated ones
        insights = list(entry.get("insights", []))
        if top_exporters:
            insights.append(f"Top exporter {top_exporters[0]['country']} holds ~{top_exporters[0]['value_usd_mn']}M export value.")
        if dependency:
            lead_dep = dependency[0]
            insights.append(f"Highest import dependency: {lead_dep['country']} at {lead_dep['share_percent']}% of import value.")

        overview = {
            "total_export_value_usd_mn": self._sum(exports, "value_usd_mn"),
            "total_export_volume_tons": self._sum(exports, "volume_tons"),
            "total_import_value_usd_mn": self._sum(imports, "value_usd_mn"),
            "total_import_volume_tons": self._sum(imports, "volume_tons"),
            "top_exporters": top_exporters,
            "top_importers": top_importers,
        }

        return {
            "molecule": entry.get("molecule", molecule),
            "filters": {"year": year, "countries": countries},
            "exports": exports,
            "imports": imports,
            "overview": overview,
            "import_dependency": dependency,
            "insights": insights,
            "summary": summary,
            "available": True,
        }


# Quick self-test: python -m app.agents.exim_trends_agent
if __name__ == "__main__":
    agent = EximTrendsAgent()
    result = agent.run({"molecule": "metformin", "year": 2024})
    print("Available:", result.get("available"))
    print("Summary:", result.get("summary"))
    print("Top exporters:", result.get("overview", {}).get("top_exporters"))

