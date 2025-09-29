import re, unicodedata

def weighted_avg(scores: dict[str,float], weights: dict[str,float]) -> float:
    total_w = sum(weights.values())
    s = sum(scores[k] * weights[k] for k in scores)
    return s / total_w if total_w > 0 else 0.0

def normalize(text: str) -> str:
    _ws = re.compile(r"\s+")
    t = unicodedata.normalize("NFKC", text)
    t = t.strip().lower()
    return _ws.sub(" ", t)


CV_WEIGHTS = {"skills":0.40, "experiences":0.35, "projects":0.25}
PROJECT_WEIGHTS = {"correctness":0.30, "code_quality":0.25, "resilience":0.20, "docs":0.15, "creativity":0.10}
