from data.loader import load_products
from app.config import CRITICAL_DAYS, LOW_DAYS

def get_category_performance(category: str) -> dict:
    """
    Aggregated category metrics: SKU count, avg rating, avg margin,
    total stock, critical/low stock counts, top 3 revenue products.
    Revenue proxy = price × avg_daily_sales
    """
    df = load_products()
    
    if category == "All":
        cat_df = df.copy()
    else:
        cat_df = df[df['category'].str.lower() == category.lower()].copy()
    
    if cat_df.empty:
        return {"error": f"No products found in category: {category}"}
    
    cat_df['days_to_stockout'] = cat_df.apply(
        lambda r: r['stock_quantity'] / r['avg_daily_sales']
        if r['avg_daily_sales'] > 0 else float('inf'), axis=1
    )
    cat_df['gross_margin'] = (cat_df['price'] - cat_df['cost']) / cat_df['price'] * 100
    cat_df['revenue_proxy'] = cat_df['price'] * cat_df['avg_daily_sales']
    
    top3 = cat_df.nlargest(3, 'revenue_proxy')[
        ['product_id', 'product_name', 'revenue_proxy', 'avg_rating']
    ].to_dict('records')
    
    for item in top3:
        item['estimated_daily_revenue'] = round(item.pop('revenue_proxy'), 2)
    
    return {
        "category": category,
        "total_skus": len(cat_df),
        "avg_rating": round(float(cat_df['avg_rating'].mean()), 2),
        "avg_margin_pct": round(float(cat_df['gross_margin'].mean()), 2),
        "total_stock_units": int(cat_df['stock_quantity'].sum()),
        "critical_stock_count": int((cat_df['days_to_stockout'] < CRITICAL_DAYS).sum()),
        "low_stock_count": int(
            ((cat_df['days_to_stockout'] >= CRITICAL_DAYS) &
             (cat_df['days_to_stockout'] <= LOW_DAYS)).sum()
        ),
        "top_3_revenue_products": top3
    }
