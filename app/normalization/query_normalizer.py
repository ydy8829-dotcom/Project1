import csv
from pathlib import Path

DEFAULT_TERMS = {
    "high aspect ratio": ["har", "high aspect ratio", "har etch"],
    "chemical vapor deposition": ["cvd"],
    "atomic layer deposition": ["ald"],
    "plasma enhanced chemical vapor deposition": ["pecvd"],
    "atomic layer etch": ["ale"],
    "reactive ion etch": ["rie"],
    "deep reactive ion etch": ["drie"],
    "gate-all-around": ["gaa", "gate all around"],
    "through-silicon via": ["tsv", "through silicon via"],
    "chemical mechanical planarization": ["cmp", "chemical mechanical polishing"],
    "critical dimension": ["cd"],
    "wafer clean": ["wet clean"],
    "applied materials": ["amat", "applied"],
    "lam research": ["lam"],
}


def load_terms(path: str | Path | None = None) -> dict[str, list[str]]:
    terms = {key: list(values) for key, values in DEFAULT_TERMS.items()}
    if not path or not Path(path).exists():
        return terms
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            canonical = row.get("canonical", "").strip().lower()
            alias = row.get("alias", "").strip().lower()
            if canonical and alias:
                terms.setdefault(canonical, []).append(alias)
    return terms


def normalize_query(query: str, terms: dict[str, list[str]] | None = None) -> dict:
    original = query.strip()
    lowered = original.lower()
    terms = terms or DEFAULT_TERMS
    expansions: list[str] = []
    for canonical, variants in terms.items():
        if any(variant in lowered for variant in [canonical, *variants]):
            expansions.extend([canonical, *variants])
    return {"original": original, "normalized": " ".join(dict.fromkeys([lowered, *expansions])), "terms": list(dict.fromkeys(expansions))}
