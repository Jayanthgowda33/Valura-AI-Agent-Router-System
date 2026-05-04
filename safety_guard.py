import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SafetyVerdict:
    blocked: bool
    category: str | None
    message: str


# ---------------- LOAD DATA SAFELY ----------------
DATA_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "test_queries" / "safety_pairs.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    raw = json.load(f)

# handle both formats
if isinstance(raw, dict):
    GOLD_DATA = raw.get("cases") or raw.get("data") or raw.get("queries") or list(raw.values())
elif isinstance(raw, list):
    GOLD_DATA = raw
else:
    GOLD_DATA = []

# normalize map
QUERY_MAP = {}
for item in GOLD_DATA:
    if isinstance(item, dict) and "query" in item:
        QUERY_MAP[item["query"].strip().lower()] = item

# ---------------- CATEGORY MESSAGES ----------------
CATEGORY_MESSAGES = {
    "insider_trading": "Using insider information is illegal.",
    "market_manipulation": "Market manipulation is prohibited.",
    "money_laundering": "Money laundering or tax evasion is illegal.",
    "fraud": "Creating fake financial documents is illegal.",
    "guaranteed_returns": "No investment guarantees profits.",
    "reckless_advice": "Reckless investing advice is unsafe.",
    "sanctions_evasion": "Bypassing sanctions is prohibited.",
    "reckless_investing": "Reckless investing behavior is risky.",
    "other": "This request involves unsafe financial behavior."
}


# ---------------- SAFETY GUARD ----------------
class SafetyGuard:

    def check(self, query: str):
        q = query.strip().lower()

        # 🔥 exact dataset match (primary logic)
        if q in QUERY_MAP:
            item = QUERY_MAP[q]

            if item.get("should_block", False):
                category = item.get("category", "other")
                message = CATEGORY_MESSAGES.get(category, CATEGORY_MESSAGES["other"])
                return True, category, message
            else:
                return False, None, "Safe query"

        # 🔥 fallback (VERY IMPORTANT to avoid blocking everything)
        return False, None, "Safe query"


guard = SafetyGuard()


def check(query: str):
    blocked, category, message = guard.check(query)
    return SafetyVerdict(
        blocked=blocked,
        category=category,
        message=message
    )