from typing import Dict, Any, List


def calculate_concentration(holdings: List[Dict]) -> Dict:
    if not holdings:
        return {
            "top_position_pct": 0,
            "top_3_positions_pct": 0,
            "flag": "none"
        }

    values = [h["value"] for h in holdings]
    total = sum(values)

    if total == 0:
        return {
            "top_position_pct": 0,
            "top_3_positions_pct": 0,
            "flag": "none"
        }

    sorted_vals = sorted(values, reverse=True)

    top_1 = (sorted_vals[0] / total) * 100
    top_3 = (sum(sorted_vals[:3]) / total) * 100

    if top_1 > 50:
        flag = "high"
    elif top_1 > 30:
        flag = "medium"
    else:
        flag = "low"

    return {
        "top_position_pct": round(top_1, 2),
        "top_3_positions_pct": round(top_3, 2),
        "flag": flag
    }


def calculate_performance(holdings: List[Dict]) -> Dict:
    if not holdings:
        return {
            "total_return_pct": 0,
            "annualized_return_pct": 0
        }

    returns = [h.get("return_pct", 0) for h in holdings]

    avg_return = sum(returns) / len(returns)

    return {
        "total_return_pct": round(avg_return, 2),
        "annualized_return_pct": round(avg_return * 0.7, 2)
    }


def normalize_holdings(user_profile: Dict[str, Any]) -> List[Dict]:
    portfolio = user_profile.get("portfolio", {})
    holdings = portfolio.get("holdings", [])

    if holdings:
        return holdings

    positions = user_profile.get("positions", [])
    normalized = []
    for position in positions:
        quantity = position.get("quantity", 0)
        avg_cost = position.get("avg_cost", 0)
        value = position.get("value", quantity * avg_cost)
        normalized.append({
            "ticker": position.get("ticker"),
            "value": value,
            "return_pct": position.get("return_pct", 0)
        })

    return normalized


def portfolio_health_agent(user_profile: Dict[str, Any], llm=None) -> Dict[str, Any]:
    holdings = normalize_holdings(user_profile)

    # -------------------------
    # EMPTY PORTFOLIO CASE
    # -------------------------
    if not holdings:
        return {
            "concentration_risk": {
                "top_position_pct": 0,
                "top_3_positions_pct": 0,
                "flag": "none"
            },
            "performance": {
                "total_return_pct": 0,
                "annualized_return_pct": 0
            },
            "benchmark_comparison": {
                "benchmark": "S&P 500",
                "portfolio_return_pct": 0,
                "benchmark_return_pct": 0,
                "alpha_pct": 0
            },
            "observations": [
                {
                    "severity": "info",
                    "text": "You don’t have any investments yet. Consider starting with diversified ETFs."
                }
            ],
            "disclaimer": "This is not investment advice."
        }

    # -------------------------
    # CALCULATIONS
    # -------------------------
    concentration = calculate_concentration(holdings)
    performance = calculate_performance(holdings)

    benchmark_return = 10  # simple placeholder
    alpha = performance["total_return_pct"] - benchmark_return

    observations = []

    if concentration["flag"] == "high":
        observations.append({
            "severity": "warning",
            "text": "Your portfolio is highly concentrated in a single position."
        })

    if alpha > 0:
        observations.append({
            "severity": "info",
            "text": f"You are outperforming the benchmark by {round(alpha, 2)}%."
        })
    else:
        observations.append({
            "severity": "warning",
            "text": "Your portfolio is underperforming the benchmark."
        })

    return {
        "concentration_risk": concentration,
        "performance": performance,
        "benchmark_comparison": {
            "benchmark": "S&P 500",
            "portfolio_return_pct": performance["total_return_pct"],
            "benchmark_return_pct": benchmark_return,
            "alpha_pct": round(alpha, 2)
        },
        "observations": observations,
        "disclaimer": "This is not investment advice. Please consult a financial advisor."
    }


run = portfolio_health_agent