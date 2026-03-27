import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_PARAMS, BRIEFING_MARGIN_THRESHOLD
from tools.restock_alert import generate_restock_alert
from tools.review_insights import get_review_insights
from data.loader import load_products

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_daily_briefing() -> str:
    """
    Auto-generated daily briefing shown on startup.
    Contains:
    1. Top 3 most critical stockout products
    2. Worst-rated product + one-line reason
    3. Lowest margin product (if below 25%) + suggested action
    """
    df = load_products()
    
    # 1. Top 3 stockout alerts
    alerts = generate_restock_alert(threshold_days=14)
    top3_stock = alerts[:3]
    
    # 2. Worst rated product
    worst_idx = df['avg_rating'].idxmin()
    worst_product = df.loc[worst_idx]
    review_data = get_review_insights(worst_product['product_id'])
    
    # 3. Lowest margin product
    df['gross_margin'] = (df['price'] - df['cost']) / df['price'] * 100
    low_margin_idx = df['gross_margin'].idxmin()
    low_margin_product = df.loc[low_margin_idx]
    low_margin_pct = round(low_margin_product['gross_margin'], 1)
    
    briefing_prompt = f"""You are a retail business intelligence assistant generating a daily briefing for a fashion brand product manager named Priya.

Generate a clear, actionable daily briefing with exactly 3 sections. Be concise and urgent where needed.

DATA:

SECTION 1 - STOCKOUT ALERTS (Top 3 most urgent):
{json.dumps(top3_stock, indent=2)}

SECTION 2 - WORST RATED PRODUCT:
Product: {worst_product['product_name']} (ID: {worst_product['product_id']})
Rating: {worst_product['avg_rating']}/5.0
Review Summary: {review_data.get('sentiment_summary', 'No reviews available')}
Negative Themes: {review_data.get('negative_themes', [])}

SECTION 3 - PRICING FLAG:
Product: {low_margin_product['product_name']} (ID: {low_margin_product['product_id']})
Gross Margin: {low_margin_pct}% (flag if below {BRIEFING_MARGIN_THRESHOLD}%)

Format the briefing like this:
## 🌅 Daily Briefing — StyleCraft Product Intelligence

### 🚨 Stockout Alerts
[3 bullet points with product name, days remaining, revenue at risk]

### ⭐ Quality Flag  
[Product name, rating, one-line reason customers are unhappy]

### 💰 Pricing Flag
[Product name, margin %, suggested action]

Keep total length under 250 words. Use INR (₹) for all currency."""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": briefing_prompt}],
        temperature=LLM_PARAMS["briefing"]["temperature"],
        max_tokens=LLM_PARAMS["briefing"]["max_tokens"]
    )
    
    return response.choices[0].message.content.strip()
