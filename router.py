from dataclasses import asdict
from src.core.classifier import classify
from src.agents.portfolio_health import portfolio_health_agent


def route(query: str, user_profile: dict, llm=None):
    classification = classify(query, llm=llm)
    classification_data = asdict(classification)

    agent = classification.agent

    # -------------------------
    # ROUTING
    # -------------------------
    if agent == "portfolio_health":
        result = portfolio_health_agent(user_profile, llm=llm)

    elif agent == "general_query":
        result = {
            "intent": classification.intent,
            "agent": agent,
            "entities": classification.entities,
            "message": (
                "I'm a financial assistant. You can ask about:\n"
                "- Portfolio health\n"
                "- Stock analysis\n"
                "- Investment strategies"
            )
        }

    elif agent == "stock_lookup":
        result = {
            "intent": classification.intent,
            "agent": agent,
            "entities": classification.entities,
            "message": "Stock lookup feature coming soon."
        }

    elif agent == "investment_strategy":
     result = {
        "intent": classification.intent,
        "agent": agent,
        "entities": classification.entities,
        "message": (
            "Tesla is a high-growth but volatile stock. "
            "Consider diversification and your risk tolerance before investing."
        )
    }

    else:
        # fallback (important)
        result = {
            "intent": classification.intent,
            "agent": agent,
            "entities": classification.entities,
            "message": "Sorry, I couldn't understand your request."
        }

    return {
        "classification": classification_data,
        "result": result
    }