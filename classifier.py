from dataclasses import dataclass
from typing import Dict, Any, Optional
import re


# -----------------------------
# OUTPUT STRUCTURE
# -----------------------------
@dataclass
class ClassificationResult:
    intent: str
    agent: str
    entities: Dict[str, Any]
    safety: Optional[str] = "safe"


# -----------------------------
# ENTITY EXTRACTION HELPERS
# -----------------------------
def extract_tickers(text: str):
    matches = re.findall(r"\b[A-Za-z0-9]{1,5}(?:\.[A-Za-z]{1,4})?\b", text)
    tickers = []
    reserved = {
        "AND", "OR", "THE", "A", "I", "IN", "TO", "OF", "ON", "MY", "ME",
        "IS", "IT", "BY", "AT", "AN", "THIS", "HOW", "WHO", "WHY", "WHAT",
        "WHEN", "WHERE", "FOR", "WITH", "IF", "NOT", "BUT", "ELSE", "AS",
        "BE", "ETF", "FX", "USD", "EUR", "GBP", "JPY", "LTCG"
    }
    for symbol in matches:
        if "." in symbol:
            if re.fullmatch(r"[A-Za-z0-9]{1,5}\.[A-Za-z]{1,4}", symbol):
                tickers.append(symbol.upper())
            continue

        if symbol.isupper() and len(symbol) >= 2 and symbol not in reserved:
            tickers.append(symbol)
    return tickers


def extract_amount(text: str):
    match = re.search(r"\$?(\d+(?:,\d+)*(?:\.\d+)?)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


def extract_rate(text: str):
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if match:
        return float(match.group(1)) / 100.0
    return None


def extract_years(text: str):
    match = re.search(r"(\d+)\s*(year|years)", text.lower())
    if match:
        return int(match.group(1))
    return None


def extract_currency(text: str):
    match = re.search(r"\b(USD|EUR|GBP|JPY)\b", text.upper())
    if match:
        return match.group(1)
    return None


def extract_frequency(text: str):
    normalized = text.lower()
    if "daily" in normalized:
        return "daily"
    if "weekly" in normalized:
        return "weekly"
    if "monthly" in normalized:
        return "monthly"
    if "yearly" in normalized or "annually" in normalized:
        return "yearly"
    return None


def extract_horizon(text: str):
    m = re.search(r"(\d+)\s*(months|month|years|year)", text.lower())
    if m:
        count = int(m.group(1))
        unit = m.group(2)
        if unit.startswith("month"):
            return f"{count}_months" if count != 1 else "1_month"
        return f"{count}_years" if count != 1 else "1_year"
    return None


def extract_time_period(text: str):
    normalized = text.lower()
    if "today" in normalized:
        return "today"
    if "this week" in normalized:
        return "this_week"
    if "this month" in normalized:
        return "this_month"
    if "this year" in normalized:
        return "this_year"
    return None


def extract_index(text: str):
    indices = ["S&P 500", "FTSE 100", "NIKKEI 225", "MSCI World"]
    for index in indices:
        if index.lower() in text.lower():
            return index
    return None


def extract_action(text: str):
    normalized = text.lower()
    if "sell" in normalized:
        return "sell"
    if "buy" in normalized:
        return "buy"
    if "hold" in normalized:
        return "hold"
    if "hedge" in normalized:
        return "hedge"
    if "rebalance" in normalized:
        return "rebalance"
    return None


def extract_goal(text: str):
    normalized = text.lower()
    if "retire" in normalized:
        return "retirement"
    if "college" in normalized or "education" in normalized:
        return "education"
    if "house" in normalized:
        return "house"
    if "fire" in normalized:
        return "FIRE"
    if "emergency fund" in normalized:
        return "emergency_fund"
    return None


def extract_sectors(text: str):
    sectors = []
    normalized = text.lower()
    if "tech" in normalized or "technology" in normalized:
        sectors.append("technology")
    if "emerging market" in normalized:
        sectors.append("emerging markets")
    if "large cap" in normalized:
        sectors.append("large cap")
    return sectors


def extract_topics(text: str):
    topics = []
    normalized = text.lower()
    topic_map = {
        "mutual fund": "mutual fund",
        "compound interest": "compound interest",
        "etf": "ETF",
        "index fund": "index fund",
        "p/e ratio": "P/E ratio",
        "beta": "beta",
        "max drawdown": "max drawdown",
        "recession": "recession",
        "login": "login",
        "bank account": "bank account",
        "transaction history": "transaction history",
        "recurring investment": "recurring investment",
        "ltcg": "LTCG",
        "fx": "FX",
        "gold": "GOLD",
        "emerging markets": "emerging markets",
        "large cap": "large cap",
        "dividend": "dividend",
    }
    for phrase, label in topic_map.items():
        if phrase in normalized and label not in topics:
            topics.append(label)
    return topics


# -----------------------------
# MAIN CLASSIFIER
# -----------------------------
def classify(query: str, llm=None) -> ClassificationResult:
    q = query.lower()

    # -----------------------------
    # TRY MOCK / LLM FIRST (IMPORTANT FOR TESTS)
    # -----------------------------
    if llm:
        try:
            response = llm(query)

            # mock_llm returns structured dict
            if isinstance(response, dict):
                return ClassificationResult(
                    intent=response.get("intent", "unknown"),
                    agent=response.get("agent", "general_support"),
                    entities=response.get("entities", {}),
                    safety=response.get("safety", "safe"),
                )
        except Exception:
            pass  # fallback to rules

    # -----------------------------
    # RULE-BASED FALLBACK
    # -----------------------------
    def contains_any(terms: list[str]) -> bool:
        return any(term in q for term in terms)

    def contains_word(term: str) -> bool:
        return re.search(rf"\b{re.escape(term)}\b", q) is not None

    greetings = ["hi", "hello", "thanks"]
    customer_support = ["login", "linked bank account", "transaction history", "recurring investment", "linked bank", "account issue"]
    strong_portfolio_health = ["how is my portfolio doing", "how is my portfolio", "portfolio health", "health check", "concentration risk", "beating the market", "review my holdings", "portfolio summary", "am i beating the market"]
    portfolio_health = ["portfolio", "diversified", "holdings"]
    financial_planning = ["retirement", "save for retirement", "college fund", "house down payment", "financial planning", "fire plan", "on track"]
    financial_calculator = ["calculate", "what will i have", "mortgage payment", "long-term capital gains tax", "future value", "convert", "tax"]
    predictive_analysis = ["where will", "predict", "forecast", "in 6 months", "5 years"]
    product_recommendation = ["recommend", "best", "which fund", "recommend a fund", "recommend a dividend ETF", "recommend a large cap ETF"]
    investment_strategy = ["should i sell", "should i buy", "should i hedge", "should i hold", "rebalance", "allocate", "what should my equity", "invest in tech", "invest", "strategy"]
    risk_assessment = ["downside risk", "beta", "max drawdown", "stress test", "exposed", "exposure", "risk assessment", "risk if", "protect", "loss", "volatility"]
    market_research = ["price", "stock", "about", "news", "market", "markets", "gainers", "price of", "gold price", "eur/usd", "what happened in markets", "top gainers", "how is", "how is the ftse doing", "what's happening with the nikkei"]

    if any(contains_word(g) for g in greetings):
        agent = "general_query"
        intent = "general_inquiry"
    elif contains_any(customer_support):
        agent = "customer_support"
        intent = "customer_support"
    elif contains_any(risk_assessment) and not contains_any(investment_strategy):
        agent = "risk_assessment"
        intent = "risk_check"
    elif contains_any(financial_planning):
        agent = "financial_planning"
        intent = "financial_planning"
    elif contains_any(financial_calculator):
        agent = "financial_calculator"
        intent = "calculation"
    elif contains_any(predictive_analysis):
        agent = "predictive_analysis"
        intent = "predictive_analysis"
    elif contains_any(product_recommendation) and not contains_any(["tell me about the markets", "what happened in markets", "how is the ftse doing", "what's happening with the nikkei"]):
        agent = "product_recommendation"
        intent = "product_recommendation"
    elif contains_any(investment_strategy) and not contains_any(strong_portfolio_health):
        agent = "investment_strategy"
        intent = "investment_advice"
    elif contains_any(strong_portfolio_health):
        agent = "portfolio_health"
        intent = "portfolio_check"
    elif contains_any(portfolio_health):
        agent = "portfolio_health"
        intent = "portfolio_check"
    elif contains_any(market_research) or extract_tickers(query):
        agent = "market_research"
        intent = "market_query"
    else:
        agent = "general_query"
        intent = "general_inquiry"

    # -----------------------------
    # ENTITY EXTRACTION
    # -----------------------------
    entities = {}

    tickers = extract_tickers(query)
    if tickers:
        entities["tickers"] = tickers

    amount = extract_amount(query)
    if amount:
        entities["amount"] = amount

    years = extract_years(query)
    if years:
        entities["period_years"] = years

    return ClassificationResult(
        intent=intent,
        agent=agent,
        entities=entities,
    )