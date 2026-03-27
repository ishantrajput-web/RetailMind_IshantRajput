# 🛍️ RetailMind — AI Product Intelligence Agent

> **StyleCraft's AI-powered business intelligence dashboard** — A conversational agent that provides real-time catalog analysis, inventory risk assessment, and pricing intelligence for fashion retail.

---

## ✨ What is This?

RetailMind is a full-stack **Conversational AI Agent** built for StyleCraft, a fashion retail brand. It transforms raw product data into actionable business insights using natural language.

Instead of manually scanning spreadsheets, a business analyst can simply ask:
- *"Which products are at stockout risk?"*
- *"Show me the gross margin for all Tops"*
- *"What do customers say about the Denim Jacket?"*
- *"Give me a full pricing analysis"*

The agent understands intent, selects the right tool, runs analysis on live data, and replies like an expert business analyst.

---

## 🚀 Live Features

### 🤖 AI Conversational Agent
- Powered by **GPT-4o-mini** for smart intent classification (no keyword matching — real LLM routing)
- Maintains full **conversation memory** across the session
- Auto-generates a **Daily Briefing** on startup with live stockout alerts and margin flags

### 📊 Interactive Analytics Dashboard
Four live **Plotly charts** that update dynamically with your category filter:
| Chart | Description |
|---|---|
| ⏱ Days to Stockout | Top 15 products closest to running out of stock, colour-coded by urgency |
| 💰 Avg Margin by Category | Gross margin across all product categories with a 20% warning threshold |
| 🏆 Top 10 Revenue Engines | Highest daily revenue products visualised as a gradient bar chart |
| ⚠️ Rating vs Return Rate | Scatter plot risk map highlighting products with low ratings and high returns |

### 🧰 6 Intelligent Business Tools
| Tool | Purpose |
|---|---|
| `inventory_health` | Days to stockout, critical stock alerts |
| `pricing_analysis` | Gross margin, pricing flags, underpriced items |
| `review_insights` | Customer sentiment from reviews |
| `category_performance` | Revenue and margin comparison across categories |
| `search_products` | SKU and product name lookup |
| `restock_alert` | Automated restock priority recommendations |

### 💎 Premium Apple-Inspired UI
- **Pure black `#000000` background** with frosted-glass metric tiles
- **SF Pro / Inter typography** for a silicon-valley aesthetic
- **Smooth fade & slide animations** on every component load using CSS `@keyframes`
- **Live category filter** — selecting "Dresses" instantly filters all 4 charts and KPI metrics
- **File Upload** — drag and drop any custom `.csv` product catalog to analyse it

---

## 📁 Project Structure

```
retailmind-agent/
├── app/
│   ├── agent.py          # LLM-based intent router (GPT-4o-mini)
│   ├── briefing.py       # Auto Daily Briefing generator
│   ├── config.py         # App-wide constants (categories etc.)
│   ├── main.py           # Streamlit UI — full dashboard + chat
│   └── memory.py         # Conversation memory manager
│
├── data/
│   └── loader.py         # Cached CSV data loader
│
├── tools/
│   ├── inventory_health.py
│   ├── pricing_analysis.py   # ← Gross margin formula: (price-cost)/price × 100
│   ├── review_insights.py
│   ├── category_performance.py
│   ├── search_products.py
│   └── restock_alert.py
│
├── retailmind_products.csv   # Main product catalog (30 SKUs)
├── retailmind_reviews.csv    # Customer reviews dataset
├── requirements.txt
├── run.py                    # App entry point
└── .env.example              # Environment variable template
```

---

## ⚙️ Setup & Installation

### Step 1 — Clone the Repository
```bash
git clone https://github.com/ishantrajput-web/midterm.git
cd midterm/retailmind-agent
```

### Step 2 — Create a Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure Your API Key
Create a `.env` file in the `retailmind-agent/` directory:
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```
> 💡 Get your API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Step 5 — Run the Application
```bash
python run.py
```

Then open your browser at **http://localhost:8501** 🎉

---

## 💬 Example Queries to Try

Once the app is running, type any of these into the chat:

```
"Which products need restocking urgently?"
"Show me pricing analysis for all products"
"What's the gross margin for Accessories?"
"What do customers say about SC011?"
"Give me a category performance report"
"Which products have the lowest inventory?"
```

---

## 🔑 Key Technical Decisions

### ✅ LLM-Based Intent Router
The agent uses GPT-4o-mini to classify the user's intent — **not** simple keyword matching. This means it can understand paraphrased or ambiguous questions correctly.

```python
# app/agent.py — Real LLM call for routing
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "system", "content": ROUTER_PROMPT}, ...],
    temperature=0
)
```

### ✅ Correct Gross Margin Formula
```python
# tools/pricing_analysis.py
gross_margin = (price - cost) / price * 100   # ✅ Correct
# NOT: (price - cost) / cost * 100            # ❌ Wrong
```

### ✅ Graceful API Fallback
If your OpenAI quota runs out, the app **does not crash**. It displays a clean fallback briefing directly from the live CSV data and shows a friendly message to top up at [platform.openai.com/billing](https://platform.openai.com/billing).

---

## 📦 Dependencies

```
streamlit
openai
pandas
python-dotenv
plotly
```

---

## 👤 Author

**Ishant Rajput** — StyleCraft Retail AI Midterm Project  
Built with ❤️ using Python, Streamlit, Plotly & OpenAI GPT-4o-mini
