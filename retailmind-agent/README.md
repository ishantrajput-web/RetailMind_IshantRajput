# RetailMind Product Intelligence Agent

AI-powered product intelligence agent for StyleCraft's fashion catalog. Replaces 4-5 hours of manual weekly analysis with a real-time conversational Streamlit interface.

## Architecture
- **Router Pattern**: LLM-based intent classification (NOT keyword matching) routes each query to the correct specialised tool
- **6 Tools**: search_products, get_inventory_health, get_pricing_analysis, get_review_insights, get_category_performance, generate_restock_alert  
- **Memory**: Session-level multi-turn conversation with ConversationMemory class
- **Daily Briefing**: Auto-generated on startup — top 3 stockouts, worst-rated product, lowest margin flag
- **UI**: Streamlit with sidebar category filter, always-visible catalog summary panel, chat interface

## Setup

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```
   cp .env.example .env
   ```
4. Place `retailmind_products.csv` and `retailmind_reviews.csv` in the project root
5. Run:
   ```
   python run.py
   ```

## .env Variables
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Key Formulas
- Days to stockout: `stock_quantity / avg_daily_sales`
- Gross margin: `(price - cost) / price × 100`
- Revenue at risk: `price × (current_stock + avg_daily_sales × threshold_days)`
