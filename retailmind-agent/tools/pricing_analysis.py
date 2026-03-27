from data.loader import load_products
from app.config import LOW_MARGIN_THRESHOLD, PREMIUM_MULTIPLIER, BUDGET_MULTIPLIER

def get_pricing_analysis(product_id: str) -> dict:
    """
    Returns pricing intelligence for a product.
    Formula: gross_margin = (price - cost) / price * 100
    Positioning: Premium (>120% cat avg), Budget (<80% cat avg), Mid-Range (else)
    """
    df = load_products()
    matches = df[df['product_id'] == product_id]
    
    if matches.empty:
        return {"error": f"Product {product_id} not found"}
    
    row = matches.iloc[0]
    
    gross_margin = (row['price'] - row['cost']) / row['price'] * 100
    
    cat_df = df[df['category'] == row['category']]
    category_avg_price = cat_df['price'].mean()
    
    if row['price'] > category_avg_price * PREMIUM_MULTIPLIER:
        positioning = "Premium"
    elif row['price'] < category_avg_price * BUDGET_MULTIPLIER:
        positioning = "Budget"
    else:
        positioning = "Mid-Range"
    
    suggested_action = None
    if gross_margin < LOW_MARGIN_THRESHOLD:
        suggested_action = f"⚠️ Margin below {LOW_MARGIN_THRESHOLD}% — consider raising price or reducing cost."
    
    return {
        "product_id": product_id,
        "product_name": row['product_name'],
        "category": row['category'],
        "price": float(row['price']),
        "cost": float(row['cost']),
        "gross_margin_pct": round(gross_margin, 2),
        "price_positioning": positioning,
        "category_avg_price": round(category_avg_price, 2),
        "margin_flag": gross_margin < LOW_MARGIN_THRESHOLD,
        "suggested_action": suggested_action
    }
