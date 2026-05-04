from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import time

from src.core.router import route
from src.core.safety_guard import check

app = FastAPI()


def sse_format(data: dict):
    return f"data: {json.dumps(data)}\n\n"


@app.get("/query")
def query_endpoint(q: str):
    user_profile = {
        "portfolio": {
            "holdings": [
                {"ticker": "AAPL", "value": 5000, "return_pct": 10},
                {"ticker": "TSLA", "value": 2000, "return_pct": 5},
            ]
        }
    }

    def stream():
        # -------------------------
        # SAFETY CHECK
        # -------------------------
        verdict = check(q)
        if verdict.blocked:
            yield sse_format({"error": verdict.message})
            return

        # -------------------------
        # ROUTE + RESPONSE
        # -------------------------
        response = route(q, user_profile)

        # simulate streaming
        yield sse_format({"status": "processing"})
        time.sleep(0.5)

        yield sse_format(response)

    return StreamingResponse(stream(), media_type="text/event-stream")