from data.loader import load_products
from app.config import CRITICAL_DAYS, LOW_DAYS

def get_inventory_health(product_id: str) -> dict:
    """
    Returns inventory status for a product.
    Formula: days_to_stockout = stock_quantity / avg_daily_sales
    Status: Critical (<7 days), Low (7-14 days), Healthy (>14 days)
    Edge case: avg_daily_sales == 0 → infinity days, status Healthy
    """
    df = load_products()
    matches = df[df['product_id'] == product_id]
    
    if matches.empty:
        return {"error": f"Product {product_id} not found"}
    
    row = matches.iloc[0]
    
    if row['avg_daily_sales'] == 0:
        days_to_stockout = float('inf')
        status = "Healthy"
    else:
        days_to_stockout = row['stock_quantity'] / row['avg_daily_sales']
        if days_to_stockout < CRITICAL_DAYS:
            status = "Critical"
        elif days_to_stockout <= LOW_DAYS:
            status = "Low"
        else:
            status = "Healthy"
    
    return {
        "product_id": product_id,
        "product_name": row['product_name'],
        "category": row['category'],
        "stock_quantity": int(row['stock_quantity']),
        "avg_daily_sales": float(row['avg_daily_sales']),
        "days_to_stockout": round(days_to_stockout, 1) if days_to_stockout != float('inf') else "No sales",
        "status": status,
        "reorder_level": int(row['reorder_level']),
        "below_reorder": bool(row['stock_quantity'] < row['reorder_level'])
    }
