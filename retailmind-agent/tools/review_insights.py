import json
from data.loader import load_reviews, load_products
from openai import OpenAI
from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_PARAMS

client = OpenAI(api_key=OPENAI_API_KEY)

# Cache to avoid repeated LLM calls within a session
_review_cache = {}

def get_review_insights(product_id: str) -> dict:
    """
    LLM-powered sentiment summary of customer reviews.
    Returns avg rating, total reviews, 2-sentence summary, top 2 positive/negative themes.
    Results are cached per product_id.
    """
    if product_id in _review_cache:
        return _review_cache[product_id]
    
    reviews_df = load_reviews()
    products_df = load_products()
    
    product_reviews = reviews_df[reviews_df['product_id'] == product_id]
    product_match = products_df[products_df['product_id'] == product_id]
    
    if product_reviews.empty:
        return {
            "product_id": product_id,
            "avg_rating": None,
            "total_reviews": 0,
            "sentiment_summary": "No reviews available for this product.",
            "positive_themes": [],
            "negative_themes": []
        }
    
    product_name = product_match.iloc[0]['product_name'] if not product_match.empty else product_id
    avg_rating = float(product_reviews['rating'].mean())
    
    review_texts = "\n".join([
        f"Rating: {r['rating']}/5 — {r['review_title']}: {r['review_text']}"
        for _, r in product_reviews.iterrows()
    ])
    
    prompt = f"""You are analyzing customer reviews for a fashion product called "{product_name}".

Reviews:
{review_texts}

Analyze these reviews and return ONLY a valid JSON object (no preamble, no markdown):
{{
  "sentiment_summary": "2-sentence summary of overall customer sentiment",
  "positive_themes": ["theme 1", "theme 2"],
  "negative_themes": ["theme 1", "theme 2"]
}}

If there are fewer than 2 positive or negative themes, fill with the best available."""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=LLM_PARAMS["review"]["temperature"],
        max_tokens=LLM_PARAMS["review"]["max_tokens"]
    )
    
    raw = response.choices[0].message.content.strip()
    import re
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    parsed = {}
    if match:
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    result = {
        "product_id": product_id,
        "product_name": product_name,
        "avg_rating": round(avg_rating, 2),
        "total_reviews": len(product_reviews),
        "sentiment_summary": parsed.get("sentiment_summary", ""),
        "positive_themes": parsed.get("positive_themes", []),
        "negative_themes": parsed.get("negative_themes", [])
    }
    
    _review_cache[product_id] = result
    return result
