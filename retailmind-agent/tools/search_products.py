from data.loader import load_products

def search_products(query: str, category: str = None) -> list:
    """Search catalog by keyword and optional category filter. Returns top 5 matches."""
    df = load_products()
    
    if category and category != "All":
        df = df[df['category'].str.lower() == category.lower()]
    
    mask = df['product_name'].str.lower().str.contains(query.lower(), na=False)
    results = df[mask].head(5)
    
    if results.empty:
        # Try partial word match on any word in query
        words = query.lower().split()
        for word in words:
            mask = df['product_name'].str.lower().str.contains(word, na=False)
            results = df[mask].head(5)
            if not results.empty:
                break
    
    if results.empty:
        return []
    
    return results[['product_id', 'product_name', 'category', 'price',
                     'stock_quantity', 'avg_rating', 'avg_daily_sales']].to_dict('records')
