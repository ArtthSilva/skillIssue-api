import re
from collections import Counter
from typing import Dict, List, Tuple
from .lexicon import DEV_STACK, CLOUD, SOFT_SKILLS, ALIASES

TOKENIZER = re.compile(r"[\w+#.]+", re.UNICODE)

def normalize_token(t: str) -> str:
    t = t.lower()
    return ALIASES.get(t, t)

def classify_tokens(text: str) -> Dict[str, Counter]:
    tokens = [normalize_token(t) for t in TOKENIZER.findall(text.lower())]
    dev = Counter(t for t in tokens if t in DEV_STACK)
    cloud = Counter(t for t in tokens if t in CLOUD)
    soft = Counter(t for t in tokens if t in SOFT_SKILLS)
    return {"dev": dev, "cloud": cloud, "soft": soft}

def aggregate_descriptions(descs: List[str]) -> Dict[str, Counter]:
    agg = {"dev": Counter(), "cloud": Counter(), "soft": Counter()}
    for d in descs:
        cls = classify_tokens(d)
        for k in agg:
            agg[k].update(cls[k])
    return agg

def top_n(agg: Dict[str, Counter], n: int = 10) -> Dict[str, List[Tuple[str, int]]]:
    return {k: cnt.most_common(n) for k, cnt in agg.items()}
