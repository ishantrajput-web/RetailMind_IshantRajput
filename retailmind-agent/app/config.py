import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-4o-mini"

CATEGORIES = ["All", "Tops", "Dresses", "Bottoms", "Outerwear", "Accessories"]

# LLM params — documented with rationale
LLM_PARAMS = {
    "router": {
        "temperature": 0.1,    # Near-zero: classification must be deterministic
        "max_tokens": 200,     # Small JSON response only
    },
    "review": {
        "temperature": 0.4,    # Slight creativity for natural language summaries
        "max_tokens": 400,     # Summary + themes
    },
    "briefing": {
        "temperature": 0.3,    # Factual but readable business output
        "max_tokens": 600,
    },
    "response": {
        "temperature": 0.3,    # Accurate and clear final responses
        "max_tokens": 700,
    },
    "general": {
        "temperature": 0.5,    # More conversational for general queries
        "max_tokens": 400,
    }
}

# Business thresholds
CRITICAL_DAYS = 7
LOW_DAYS = 14
LOW_MARGIN_THRESHOLD = 20.0
BRIEFING_MARGIN_THRESHOLD = 25.0
PREMIUM_MULTIPLIER = 1.20
BUDGET_MULTIPLIER = 0.80
