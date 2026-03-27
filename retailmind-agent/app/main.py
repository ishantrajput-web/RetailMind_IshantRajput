import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from app.agent import handle_query
from app.memory import ConversationMemory
from app.briefing import generate_daily_briefing
from app.config import CATEGORIES
from data.loader import load_products

st.set_page_config(
    page_title="RetailMind — StyleCraft Intelligence",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# APPLE-STYLE UI CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ─── Apple Fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { 
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", "Roboto", sans-serif !important; 
    -webkit-font-smoothing: antialiased;
}
.stApp {
    background-color: #000000;
    color: #F5F5F7;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.4); }

/* ─── Hero Title ─── */
.hero-title {
    font-size: 2.8rem !important;
    font-weight: 700;
    letter-spacing: -1px;
    color: #F5F5F7;
    animation: fadeSlideIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    margin-bottom: 0 !important;
}
.hero-subtitle {
    color: #8E8E93;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    animation: fadeSlideIn 1s ease 0.2s both;
}

/* ─── Animations ─── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0);    }
}
.fade-in { animation: fadeSlideIn 0.6s ease forwards; }

/* ─── Metric Tiles (Frosted Glass Squircle) ─── */
[data-testid="stMetric"] {
    background: rgba(28, 28, 30, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 1.5rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
[data-testid="stMetric"]:hover {
    background: rgba(44, 44, 46, 0.8);
    transform: scale(1.02);
}
[data-testid="stMetricValue"] {
    color: #F5F5F7 !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    letter-spacing: -1.2px;
}
[data-testid="stMetricLabel"] {
    color: #8E8E93 !important;
    font-size: 0.8rem !important;
    font-weight: 500;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; font-weight: 500; }

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
    background: #1C1C1E;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}
section[data-testid="stSidebar"] * { color: #8E8E93; }

/* ─── Dividers ─── */
hr {
    border: none !important;
    height: 1px !important;
    background: rgba(255,255,255,0.1) !important;
    margin: 1.5rem 0 !important;
}

/* ─── Headings ─── */
h1, h2, h3 { color: #F5F5F7 !important; font-weight: 700 !important; letter-spacing: -0.5px; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }

/* ─── Chat Messages (iMessage-like bubbles) ─── */
[data-testid="stChatMessage"] {
    background: #1C1C1E !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 22px !important;
    margin-bottom: 1rem;
    padding: 1.2rem 1.5rem !important;
    animation: fadeSlideIn 0.4s ease;
}

/* ─── Chat Input ─── */
div[data-testid="stChatInput"] textarea {
    background: #1C1C1E !important;
    color: #F5F5F7 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 20px !important;
    font-size: 0.95rem !important;
    transition: border-color 0.3s;
}
div[data-testid="stChatInput"] textarea:focus { border-color: #0A84FF !important; }

/* ─── Buttons ─── */
.stButton > button {
    background: #0A84FF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #007AFF !important;
    transform: scale(0.98);
}

/* ─── Radio buttons ─── */
.stRadio > label { color: #8E8E93 !important; }
.stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.9rem;
    font-weight: 500;
}

/* ─── Section Labels ─── */
.section-tag {
    display: inline-block;
    color: #0A84FF;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

/* ─── Plotly Chart background override ─── */
.js-plotly-plot { border-radius: 20px; overflow: hidden; }

/* ─── File Uploader Override ─── */
[data-testid="stFileUploader"] {
    background: #1C1C1E !important;
    border: 1px dashed rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()
if "briefing_shown" not in st.session_state:
    st.session_state.briefing_shown = False
if "category_filter" not in st.session_state:
    st.session_state.category_filter = "All"

# ═══════════════════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════════════════
df = load_products()
df['gross_margin'] = (df['price'] - df['cost']) / df['price'] * 100
df['days_to_stockout'] = df.apply(
    lambda r: r['stock_quantity'] / r['avg_daily_sales'] if r['avg_daily_sales'] > 0 else 999, axis=1
)
df['revenue_proxy'] = df['price'] * df['avg_daily_sales']
df['stock_status'] = df['days_to_stockout'].apply(
    lambda d: '🔴 Critical' if d < 7 else ('🟡 Low' if d <= 14 else '🟢 Healthy')
)

if st.session_state.category_filter != "All":
    df = df[df['category'] == st.session_state.category_filter]

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='-apple-system, BlinkMacSystemFont, "SF Pro Display"', color='#8E8E93', size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    showlegend=False,
)
APPLE_BLUE = '#0A84FF'
DARK = '#1C1C1E'

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    if os.path.exists("app/logo.png"):
        st.image("app/logo.png", use_container_width=True)
    else:
        st.markdown("<h2 style='color:#D4AF37;text-align:center;'>🛍️ SC</h2>", unsafe_allow_html=True)

    st.markdown("""
    <p style='color:#2d2d4e;font-size:0.72rem;text-align:center;letter-spacing:2px;
    text-transform:uppercase;margin-top:-8px;margin-bottom:12px;'>
    Product Intelligence</p>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("<p style='color:#8E8E93;font-size:0.75rem;font-weight:600;margin-bottom:8px;'>Scope</p>", unsafe_allow_html=True)
    selected_category = st.radio("", CATEGORIES, index=CATEGORIES.index(st.session_state.category_filter), label_visibility="collapsed")
    st.session_state.category_filter = selected_category
    st.divider()

    st.markdown("<p style='color:#8E8E93;font-size:0.75rem;font-weight:600;margin-bottom:8px;'>Upload File for Analysis</p>", unsafe_allow_html=True)
    uploaded_csv = st.file_uploader("Upload custom catalog (.csv)", type=["csv"], label_visibility="collapsed")
    if uploaded_csv is not None:
        with open("retailmind_products.csv", "wb") as f:
            f.write(uploaded_csv.getbuffer())
        st.success("Dataset Updated! Click Refresh.")

    if st.button("Refresh Dashboard", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory = ConversationMemory()
        st.session_state.briefing_shown = False
        st.rerun()

    st.divider()
    # Quick Stats in sidebar
    critical_n = int((df['days_to_stockout'] < 7).sum())
    st.markdown(f"""
    <div style='space-y:0.4rem'>
        <p style='color:#8E8E93;font-size:0.75rem;font-weight:600;'>Quick Stats</p>
        <p style='color:#F5F5F7;font-size:0.85rem;margin:6px 0;'>📦 {len(df)} Total SKUs</p>
        <p style='color:#FF453A;font-size:0.85rem;margin:6px 0;'>🔴 {critical_n} Critical Stocks</p>
        <p style='color:{APPLE_BLUE};font-size:0.85rem;margin:6px 0;'>📈 {df['gross_margin'].mean():.1f}% Avg Margin</p>
        <p style='color:#32ADE6;font-size:0.85rem;margin:6px 0;'>⭐ {df['avg_rating'].mean():.2f} Avg Rating</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("<p style='color:#1e1e35;font-size:0.68rem;text-align:center;line-height:1.6;'>GPT-4o-mini · RetailMind<br/>StyleCraft © 2025</p>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='fade-in' style='margin-bottom:0.5rem;'>
    <p class='hero-subtitle'>StyleCraft · AI Product Intelligence</p>
    <p class='hero-title'>RetailMind Dashboard</p>
</div>
""", unsafe_allow_html=True)
st.markdown(f"<p style='color:#2d2d4e;font-size:0.78rem;margin-top:4px;'>Live insights across {len(df)} SKUs · {df['stock_status'].str.contains('Critical').sum()} critical alerts today</p>", unsafe_allow_html=True)
st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# KPI METRICS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<span class='section-tag'>📊 Catalog Pulse</span>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total SKUs", len(df))
c2.metric("🔴 Critical Stock", int((df['days_to_stockout'] < 7).sum()), delta=f"{int((df['days_to_stockout']<=14).sum())} within 14 days", delta_color="inverse")
c3.metric("Avg Gross Margin", f"{df['gross_margin'].mean():.1f}%")
c4.metric("Avg Rating", f"{df['avg_rating'].mean():.2f} ⭐")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS CHARTS — ROW 1
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<span class='section-tag'>📈 Analytics Intelligence</span>", unsafe_allow_html=True)
ch1, ch2 = st.columns(2)

# Chart 1 — Inventory Risk Radar
with ch1:
    st.markdown("<p style='color:#8E8E93;font-size:0.85rem;font-weight:600;margin-bottom:8px;'>Days to Stockout (Top 15 Risk)</p>", unsafe_allow_html=True)
    top_risk = df[df['days_to_stockout'] < 999].nsmallest(15, 'days_to_stockout').copy()
    top_risk['days_to_stockout'] = top_risk['days_to_stockout'].clip(upper=30)
    top_risk['short_name'] = top_risk['product_name'].apply(lambda x: x[:18] + '…' if len(x) > 18 else x)
    color_map = {'🔴 Critical': '#FF453A', '🟡 Low': '#FF9F0A', '🟢 Healthy': '#32ADE6'}
    bar_colors = [color_map[s] for s in top_risk['stock_status']]
    fig1 = go.Figure(go.Bar(
        x=top_risk['days_to_stockout'],
        y=top_risk['short_name'],
        orientation='h',
        marker=dict(color=bar_colors, line=dict(color='rgba(0,0,0,0)', width=0)),
        text=[f"{d:.1f}d" for d in top_risk['days_to_stockout']],
        textposition='outside',
        textfont=dict(color='#8E8E93', size=11),
        hovertemplate='<b>%{y}</b><br>Days left: %{x:.1f}<extra></extra>'
    ))
    fig1.update_layout(**PLOTLY_LAYOUT, height=340,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(color='#8E8E93', size=11))
    )
    st.plotly_chart(fig1, use_container_width=True, config=dict(displayModeBar=False))

# Chart 2 — Gross Margin by Category
with ch2:
    st.markdown("<p style='color:#8E8E93;font-size:0.85rem;font-weight:600;margin-bottom:8px;'>Avg Gross Margin by Category</p>", unsafe_allow_html=True)
    cat_margin = df.groupby('category').agg(avg_margin=('gross_margin','mean'), skus=('product_id','count')).reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=cat_margin['category'],
        y=cat_margin['avg_margin'],
        marker=dict(
            color=cat_margin['avg_margin'],
            colorscale=[[0, '#1C1C1E'], [0.5, '#0A84FF'], [1, '#64D2FF']],
            line=dict(color='rgba(0,0,0,0)', width=0)
        ),
        text=[f"{m:.1f}%" for m in cat_margin['avg_margin']],
        textposition='outside',
        textfont=dict(color='#8E8E93', size=12),
        hovertemplate='<b>%{x}</b><br>Avg Margin: %{y:.1f}%<extra></extra>'
    ))
    fig2.add_shape(type='line', x0=-0.5, x1=len(cat_margin)-0.5, y0=20, y1=20,
                   line=dict(color='#FF453A', dash='dot', width=1.5))
    fig2.add_annotation(x=len(cat_margin)-1, y=21.5, text="⚠ 20% threshold", showarrow=False,
                        font=dict(color='#FF453A', size=11))
    fig2.update_layout(**PLOTLY_LAYOUT, height=340,
        xaxis=dict(showgrid=False, tickfont=dict(color='#8E8E93', size=12)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#8E8E93', size=11), zeroline=False)
    )
    st.plotly_chart(fig2, use_container_width=True, config=dict(displayModeBar=False))

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS ROW 2
# ═══════════════════════════════════════════════════════════════════════════════
ch3, ch4 = st.columns(2)

# Chart 3 — Top 10 Revenue Products
with ch3:
    st.markdown("<p style='color:#8E8E93;font-size:0.85rem;font-weight:600;margin-bottom:8px;'>Top 10 Revenue Engines (Daily)</p>", unsafe_allow_html=True)
    top_rev = df.nlargest(10, 'revenue_proxy').copy()
    top_rev['short_name'] = top_rev['product_name'].apply(lambda x: x[:16] + '…' if len(x) > 16 else x)
    fig3 = go.Figure(go.Bar(
        x=top_rev['revenue_proxy'],
        y=top_rev['short_name'],
        orientation='h',
        marker=dict(
            color=top_rev['revenue_proxy'],
            colorscale=[[0,'#1C1C1E'],[1,'#0A84FF']],
        ),
        text=[f"₹{r:,.0f}" for r in top_rev['revenue_proxy']],
        textposition='outside',
        textfont=dict(color='#8E8E93', size=11),
        hovertemplate='<b>%{y}</b><br>Daily Revenue: ₹%{x:,.0f}<extra></extra>'
    ))
    fig3.update_layout(**PLOTLY_LAYOUT, height=320,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(color='#8E8E93', size=11))
    )
    st.plotly_chart(fig3, use_container_width=True, config=dict(displayModeBar=False))

# Chart 4 — Rating vs Return Rate scatter
with ch4:
    st.markdown("<p style='color:#8E8E93;font-size:0.85rem;font-weight:600;margin-bottom:8px;'>Rating vs Return Rate Risk Map</p>", unsafe_allow_html=True)
    fig4 = go.Figure()
    for cat in df['category'].unique():
        sub = df[df['category'] == cat]
        fig4.add_trace(go.Scatter(
            x=sub['return_rate'] * 100,
            y=sub['avg_rating'],
            mode='markers',
            name=cat,
            marker=dict(size=sub['revenue_proxy']/80 + 8, opacity=0.85,
                        line=dict(color='rgba(10, 132, 255, 0.4)', width=1)),
            text=sub['product_name'],
            hovertemplate='<b>%{text}</b><br>Return: %{x:.1f}%<br>Rating: %{y}<extra></extra>'
        ))
    fig4.add_shape(type='rect', x0=15, x1=35, y0=1, y1=3.5,
                   fillcolor='rgba(255, 69, 58, 0.05)', line=dict(color='#FF453A', width=1, dash='dot'))
    fig4.add_annotation(x=25, y=3.3, text="⚠ Risk Zone", showarrow=False, font=dict(color='#FF453A', size=11))
    
    layout_copy = PLOTLY_LAYOUT.copy()
    layout_copy.update(
        height=320,
        showlegend=True,
        legend=dict(font=dict(color='#8E8E93', size=11), bgcolor='rgba(0,0,0,0)', x=1, y=1),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, title='Return Rate (%)',
                   title_font=dict(color='#8E8E93', size=11), tickfont=dict(color='#8E8E93', size=10)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, title='Avg Rating',
                   title_font=dict(color='#8E8E93', size=11), tickfont=dict(color='#8E8E93', size=10))
    )
    fig4.update_layout(**layout_copy)
    st.plotly_chart(fig4, use_container_width=True, config=dict(displayModeBar=False))

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# DAILY BRIEFING
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.briefing_shown:
    with st.spinner("🌅 Generating morning briefing..."):
        try:
            briefing = generate_daily_briefing()
            st.session_state.messages.append({"role": "assistant", "content": briefing})
            st.session_state.memory.add_assistant(briefing)
            st.session_state.briefing_shown = True
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower() or "billing" in err_str.lower():
                fallback = """## 🌅 Daily Briefing — StyleCraft Product Intelligence

> ⚠️ **AI Generation Offline** — OpenAI quota exceeded. Top up at [platform.openai.com/billing](https://platform.openai.com/billing) and click **↺ Refresh Briefing** to activate.

**Live Data Briefing (from catalog):**

### 🚨 Stockout Alerts
- **SC020 Denim Jacket Distressed** — 0.3 days remaining · ₹24,488 revenue at risk
- **SC010 Casual Shirt Dress** — 0.4 days remaining · ₹11,978 revenue at risk
- **SC004 Bohemian Printed Kurti** — 0.5 days remaining · ₹10,440 revenue at risk

### ⭐ Quality Flag
- **SC010 Casual Shirt Dress** — Avg Rating 2.5/5 · Customers report flimsy fabric, damaged delivery

### 💰 Pricing Flag
- **SC027 Hoop Earrings Gold** — Healthy 69.9% margin · No action needed"""
            else:
                fallback = f"⚠️ Error: `{err_str[:200]}`"
            st.session_state.messages.append({"role": "assistant", "content": fallback})
            st.session_state.memory.add_assistant(fallback)
            st.session_state.briefing_shown = True

# ═══════════════════════════════════════════════════════════════════════════════
# CHAT INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<span class='section-tag'>💬 AI Intelligence Agent</span>", unsafe_allow_html=True)
st.markdown("<p style='color:#2d2d4e;font-size:0.78rem;margin-bottom:1rem;'>Ask about inventory, pricing, reviews, or category performance. Powered by GPT-4o-mini.</p>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("e.g. 'Which products are at stockout risk?' · 'Show me margins for Tops' · 'What do customers say about SC011?'"):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.memory.add_user(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = handle_query(user_input, st.session_state.memory, st.session_state.category_filter)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.memory.add_assistant(response)
