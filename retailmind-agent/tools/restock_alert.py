from data.loader import load_products
from app.config import CRITICAL_DAYS

def generate_restock_alert(threshold_days: int = 7) -> list:
    """
    Scans all products for stockout risk within threshold_days.
    Sorted ascending by days_to_stockout (most urgent first).
    Revenue at risk = price × (current_stock + avg_daily_sales × threshold_days)
    """
    df = load_products()
    results = []
    
    for _, row in df.iterrows():
        if row['avg_daily_sales'] == 0:
            continue
        
        days = row['stock_quantity'] / row['avg_daily_sales']
        
        if days <= threshold_days:
            revenue_at_risk = float(row['price']) * (
                float(row['stock_quantity']) + float(row['avg_daily_sales']) * threshold_days
            )
            results.append({
                "product_id": row['product_id'],
                "product_name": row['product_name'],
                "category": row['category'],
                "days_to_stockout": round(days, 1),
                "current_stock": int(row['stock_quantity']),
                "avg_daily_sales": float(row['avg_daily_sales']),
                "price": float(row['price']),
                "revenue_at_risk": round(revenue_at_risk, 2)
            })
    
    return sorted(results, key=lambda x: x['days_to_stockout'])
