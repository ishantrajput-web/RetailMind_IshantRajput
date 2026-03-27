import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_PARAMS
from app.memory import ConversationMemory
from data.loader import load_products, resolve_product_id
from tools.search_products import search_products
from tools.inventory_health import get_inventory_health
from tools.pricing_analysis import get_pricing_analysis
from tools.review_insights import get_review_insights
from tools.category_performance import get_category_performance
from tools.restock_alert import generate_restock_alert

client = OpenAI(api_key=OPENAI_API_KEY)

# ─── ROUTER SYSTEM PROMPT ───────────────────────────────────────────────────
ROUTER_SYSTEM_PROMPT = """You are an intent classification engine for RetailMind, a retail product intelligence system for StyleCraft fashion brand.

Given a user message, classify it into EXACTLY ONE intent and extract entities.

INTENTS:
- INVENTORY: stock levels, stockout risk, restock needs, days of supply remaining, which products are running low
- PRICING: margins, profitability, gross margin %, price positioning, cost efficiency, low margin products
- REVIEWS: customer feedback, ratings, complaints, what customers are saying, sentiment analysis
- CATALOG: product search, finding products, category overview, top performers, best selling, catalog discovery
- GENERAL: greetings, meta questions about the agent, general retail advice, unclear queries

VALID CATEGORIES: Tops, Dresses, Bottoms, Outerwear, Accessories

Respond ONLY with a valid JSON object, no preamble, no markdown:
{
  "intent": "INVENTORY|PRICING|REVIEWS|CATALOG|GENERAL",
  "product_id": "SC001 or null",
  "product_name_hint": "product name mentioned or null",
  "category": "category name or null",
  "wants_all_products": true/false,
  "confidence": 0.0-1.0
}"""

# ─── RESPONSE SYSTEM PROMPT ─────────────────────────────────────────────────
RESPONSE_SYSTEM_PROMPT = """You are RetailMind AI, a product intelligence assistant for StyleCraft fashion brand.
You help product manager Priya Mehta analyze inventory, pricing, reviews, and catalog performance.
You speak in a clear, professional, and actionable tone.
Always present numbers clearly. Use ₹ for prices. Use bullet points for lists.
When data shows a problem, suggest a concrete action."""

def extract_json(raw: str) -> dict:
    import re
    # Find the first { and the last }
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {"intent": "GENERAL"}

def route_query(user_message: str) -> dict:
    """Uses LLM to classify intent — NOT keyword matching."""
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=LLM_PARAMS["router"]["temperature"],
        max_tokens=LLM_PARAMS["router"]["max_tokens"]
    )
    raw = response.choices[0].message.content.strip()
    return extract_json(raw)

def format_tool_result_as_response(tool_name: str, tool_data: dict | list, user_message: str, memory: ConversationMemory) -> str:
    """Takes raw tool output and asks LLM to format it as a clear business response."""
    messages = [{"role": "system", "content": RESPONSE_SYSTEM_PROMPT}]
    messages.extend(memory.get_history()[-6:])  # Last 3 turns for context
    messages.append({
        "role": "user",
        "content": f"User asked: {user_message}\n\nTool used: {tool_name}\nData returned:\n{json.dumps(tool_data, indent=2)}\n\nNow write a clear, helpful response for Priya based on this data."
    })
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=LLM_PARAMS["response"]["temperature"],
        max_tokens=LLM_PARAMS["response"]["max_tokens"]
    )
    return response.choices[0].message.content.strip()

def handle_general(user_message: str, memory: ConversationMemory) -> str:
    """Handle general queries using LLM with conversation history."""
    messages = [{"role": "system", "content": RESPONSE_SYSTEM_PROMPT}]
    messages.extend(memory.get_history()[-6:])
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=LLM_PARAMS["general"]["temperature"],
        max_tokens=LLM_PARAMS["general"]["max_tokens"]
    )
    return response.choices[0].message.content.strip()

def handle_query(user_message: str, memory: ConversationMemory, category_filter: str = "All") -> str:
    """
    Main handler: routes query → calls correct tool → formats response.
    Router uses LLM classification, NOT keyword matching.
    """
    try:
        routing = route_query(user_message)
    except Exception as e:
        return f"I had trouble understanding that query. Could you rephrase? (Error: {e})"
    
    intent = routing.get("intent", "GENERAL")
    product_id = routing.get("product_id")
    product_name_hint = routing.get("product_name_hint")
    category = routing.get("category") or (category_filter if category_filter != "All" else None)
    wants_all = routing.get("wants_all_products", False)
    
    # If product_name_hint given but no product_id, try to resolve
    if not product_id and product_name_hint:
        product_id = resolve_product_id(product_name_hint)
    
    try:
        if intent == "INVENTORY":
            if product_id:
                data = get_inventory_health(product_id)
                return format_tool_result_as_response("get_inventory_health", data, user_message, memory)
            else:
                data = generate_restock_alert(threshold_days=7)
                return format_tool_result_as_response("generate_restock_alert", data, user_message, memory)
        
        elif intent == "PRICING":
            if product_id:
                data = get_pricing_analysis(product_id)
                return format_tool_result_as_response("get_pricing_analysis", data, user_message, memory)
            else:
                # Show all products with low margin
                df = load_products()
                df['gross_margin'] = (df['price'] - df['cost']) / df['price'] * 100
                if category:
                    df = df[df['category'].str.lower() == category.lower()]
                low_margin = df.nsmallest(5, 'gross_margin')[
                    ['product_id', 'product_name', 'category', 'price', 'cost', 'gross_margin']
                ].to_dict('records')
                return format_tool_result_as_response("pricing_overview", low_margin, user_message, memory)
        
        elif intent == "REVIEWS":
            if product_id:
                data = get_review_insights(product_id)
                return format_tool_result_as_response("get_review_insights", data, user_message, memory)
            else:
                return "Which product would you like reviews for? You can ask like: 'Show me reviews for the Floral Summer Dress' or 'What do customers think about SC011?'"
        
        elif intent == "CATALOG":
            if product_name_hint and not wants_all:
                data = search_products(product_name_hint, category)
                return format_tool_result_as_response("search_products", data, user_message, memory)
            elif category:
                data = get_category_performance(category)
                return format_tool_result_as_response("get_category_performance", data, user_message, memory)
            else:
                data = search_products(user_message.split()[-1], category_filter)
                if not data:
                    data = get_category_performance("All")
                return format_tool_result_as_response("catalog_overview", data, user_message, memory)
        
        else:  # GENERAL
            return handle_general(user_message, memory)
    
    except Exception as e:
        return f"I encountered an error processing your request: {str(e)}. Please try rephrasing or ask about a specific product ID (e.g. SC001)."
