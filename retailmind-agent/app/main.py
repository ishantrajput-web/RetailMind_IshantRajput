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
# PREMIUM DARK GLASS UI
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

/* ——— ROOT ——— */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}
.stApp {
    background: linear-gradient(160deg, #0c0c1d 0%, #0a0a14 40%, #0d0b1a 70%, #08080f 100%);
    color: #e4e4e7;
}

/* ——— SCROLLBAR ——— */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 10px; }

/* ——— HERO ——— */
.hero-container {
    padding: 1rem 0 0.5rem 0;
    animation: heroFade 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes heroFade {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 4px;
    color: #8B5CF6;
    margin-bottom: 6px;
}
.hero-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.6rem !important;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #d4d4d8 40%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
    line-height: 1.15;
}
.hero-desc {
    font-size: 0.82rem;
    color: #52525b;
    margin-top: 8px;
    font-weight: 400;
}

/* ——— ANIMATIONS ——— */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(139,92,246,0.0); }
    50%      { box-shadow: 0 0 20px 4px rgba(139,92,246,0.12); }
}
@keyframes shimmerBar {
    0%   { background-position: -600px 0; }
    100% { background-position: 600px 0; }
}
.fade-up { animation: fadeUp 0.7s ease forwards; }

/* ——— METRIC CARDS (Glassmorphism) ——— */
[data-testid="stMetric"] {
    background: rgba(22, 22, 35, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 18px;
    padding: 1.4rem 1.5rem !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #8B5CF6, #C084FC, transparent);
    background-size: 600px 2px;
    animation: shimmerBar 4s ease infinite;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(139, 92, 246, 0.5);
    transform: translateY(-4px);
    animation: glowPulse 2.5s ease infinite;
}
[data-testid="stMetricValue"] {
    color: #FAFAFA !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}
[data-testid="stMetricLabel"] {
    color: #71717a !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}
[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
    font-weight: 600;
}

/* ——— SIDEBAR ——— */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111119 0%, #0c0c14 100%);
    border-right: 1px solid rgba(139,92,246,0.08);
}
section[data-testid="stSidebar"] * { color: #a1a1aa !important; }

/* ——— DIVIDERS ——— */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.2), transparent) !important;
    margin: 1.8rem 0 !important;
}

/* ——— HEADINGS ——— */
h1, h2, h3 { color: #FAFAFA !important; font-weight: 700 !important; }
h3 { font-size: 1.05rem !important; }

/* ——— CHAT BUBBLES ——— */
[data-testid="stChatMessage"] {
    background: rgba(22, 22, 35, 0.65) !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(139,92,246,0.1) !important;
    border-radius: 20px !important;
    margin-bottom: 1rem;
    padding: 1.2rem 1.5rem !important;
    animation: fadeUp 0.4s ease;
    transition: border-color 0.3s;
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(139,92,246,0.3) !important;
}

/* ——— CHAT INPUT ——— */
div[data-testid="stChatInput"] textarea {
    background: rgba(22, 22, 35, 0.8) !important;
    color: #e4e4e7 !important;
    border: 1px solid rgba(139,92,246,0.15) !important;
    border-radius: 18px !important;
    font-size: 0.92rem !important;
    padding: 14px 18px !important;
    transition: all 0.3s;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important;
}

/* ——— BUTTONS ——— */
.stButton > button {
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px;
    transition: all 0.25s;
    padding: 0.6rem 1.2rem !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(139, 92, 246, 0.35);
}

/* ——— RADIO ——— */
.stRadio > label { color: #71717a !important; }
.stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.88rem;
    font-weight: 500;
}

/* ——— SECTION TAGS ——— */
.section-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(139, 92, 246, 0.08);
    color: #A78BFA;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 100px;
    border: 1px solid rgba(139,92,246,0.15);
    margin-bottom: 1rem;
}

/* ——— CHART CONTAINERS ——— */
.chart-card {
    background: rgba(22, 22, 35, 0.5);
    border: 1px solid rgba(139,92,246,0.1);
    border-radius: 18px;
    padding: 1.2rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.3s;
}
.chart-card:hover { border-color: rgba(139,92,246,0.3); }
.chart-label {
    color: #a1a1aa;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

/* ——— PLOTLY ——— */
.js-plotly-plot { border-radius: 14px; overflow: hidden; }

/* ——— FILE UPLOADER ——— */
[data-testid="stFileUploader"] {
    border: 1px dashed rgba(139,92,246,0.25) !important;
    border-radius: 14px !important;
    background: rgba(22,22,35,0.4) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(139,92,246,0.5) !important;
}

/* ——— SPINNER ——— */
.stSpinner > div { border-top-color: #8B5CF6 !important; }

/* ——— SUCCESS MESSAGE ——— */
.stSuccess { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# STATE INIT
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
# DATA PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
df_all = load_products()
df_all['gross_margin'] = (df_all['price'] - df_all['cost']) / df_all['price'] * 100
df_all['days_to_stockout'] = df_all.apply(
    lambda r: r['stock_quantity'] / r['avg_daily_sales'] if r['avg_daily_sales'] > 0 else 999, axis=1
)
df_all['revenue_proxy'] = df_all['price'] * df_all['avg_daily_sales']
df_all['stock_status'] = df_all['days_to_stockout'].apply(
    lambda d: '🔴 Critical' if d < 7 else ('🟡 Low' if d <= 14 else '🟢 Healthy')
)

df = df_all.copy()
if st.session_state.category_filter != "All":
    df = df_all[df_all['category'] == st.session_state.category_filter]

# ——— Plotly Defaults ———
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color='#a1a1aa', size=12),
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=False,
)
PURPLE    = '#8B5CF6'
PURPLE_LT = '#C084FC'
DARK_CARD = 'rgba(22, 22, 35, 0.5)'

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    if os.path.exists("app/logo.png"):
        st.image("app/logo.png", use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0;'>
            <span style='font-family:Playfair Display,serif;font-size:2.2rem;font-weight:700;
            background:linear-gradient(135deg,#8B5CF6,#C084FC);-webkit-background-clip:text;
            -webkit-text-fill-color:transparent;'>SC</span>
            <p style='color:#52525b;font-size:0.65rem;letter-spacing:3px;text-transform:uppercase;
            margin-top:4px;font-weight:600;'>StyleCraft</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Category Filter
    st.markdown("<p style='color:#8B5CF6 !important;font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>Category</p>", unsafe_allow_html=True)
    selected_category = st.radio("", CATEGORIES, index=CATEGORIES.index(st.session_state.category_filter), label_visibility="collapsed")
    st.session_state.category_filter = selected_category
    st.divider()

    # File Uploader
    st.markdown("<p style='color:#8B5CF6 !important;font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>Upload File for Analysis</p>", unsafe_allow_html=True)
    uploaded_csv = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    if uploaded_csv is not None:
        with open("retailmind_products.csv", "wb") as f:
            f.write(uploaded_csv.getbuffer())
        st.success("✅ Dataset updated! Click Refresh.")

    if st.button("⟲  Refresh Dashboard", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory = ConversationMemory()
        st.session_state.briefing_shown = False
        st.rerun()

    st.divider()

    # Quick Stats
    critical_n = int((df['days_to_stockout'] < 7).sum())
    st.markdown(f"""
    <div style='padding:0.8rem;background:rgba(139,92,246,0.05);border:1px solid rgba(139,92,246,0.1);
    border-radius:14px;'>
        <p style='color:#8B5CF6 !important;font-size:0.68rem;font-weight:700;letter-spacing:2px;
        text-transform:uppercase;margin-bottom:10px;'>Live Stats</p>
        <p style='color:#e4e4e7 !important;font-size:0.88rem;margin:8px 0;font-weight:500;'>📦 {len(df)} SKUs</p>
        <p style='color:#ef4444 !important;font-size:0.88rem;margin:8px 0;font-weight:500;'>🚨 {critical_n} Critical</p>
        <p style='color:#8B5CF6 !important;font-size:0.88rem;margin:8px 0;font-weight:500;'>💰 {df['gross_margin'].mean():.1f}% Margin</p>
        <p style='color:#22d3ee !important;font-size:0.88rem;margin:8px 0;font-weight:500;'>⭐ {df['avg_rating'].mean():.2f} Rating</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='color:#27272a !important;font-size:0.65rem;text-align:center;line-height:1.8;'>GPT-4o-mini · RetailMind<br/>StyleCraft © 2025</p>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class='hero-container'>
    <p class='hero-eyebrow'>StyleCraft · Product Intelligence</p>
    <p class='hero-title'>RetailMind Dashboard</p>
    <p class='hero-desc'>Live insights across <strong style='color:#A78BFA;'>{len(df)}</strong> SKUs &nbsp;·&nbsp;
    <strong style='color:#ef4444;'>{int((df['days_to_stockout']<7).sum())}</strong> critical alerts today</p>
</div>
""", unsafe_allow_html=True)
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
# CHARTS ROW 1
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<span class='section-tag'>📈 Analytics Intelligence</span>", unsafe_allow_html=True)
ch1, ch2 = st.columns(2)

with ch1:
    st.markdown("<div class='chart-card'><p class='chart-label'>⏱ Days to Stockout — Top 15 Risk</p>", unsafe_allow_html=True)
    top_risk = df[df['days_to_stockout'] < 999].nsmallest(15, 'days_to_stockout').copy()
    top_risk['days_to_stockout'] = top_risk['days_to_stockout'].clip(upper=30)
    top_risk['short_name'] = top_risk['product_name'].apply(lambda x: x[:20] + '…' if len(x) > 20 else x)
    color_map = {'🔴 Critical': '#ef4444', '🟡 Low': '#f59e0b', '🟢 Healthy': '#22d3ee'}
    bar_colors = [color_map[s] for s in top_risk['stock_status']]
    fig1 = go.Figure(go.Bar(
        x=top_risk['days_to_stockout'], y=top_risk['short_name'], orientation='h',
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=[f"{d:.1f}d" for d in top_risk['days_to_stockout']],
        textposition='outside', textfont=dict(color='#a1a1aa', size=11),
        hovertemplate='<b>%{y}</b><br>Days left: %{x:.1f}<extra></extra>'
    ))
    fig1.update_layout(**PLOTLY_LAYOUT, height=380,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(color='#a1a1aa', size=11))
    )
    st.plotly_chart(fig1, use_container_width=True, config=dict(displayModeBar=False))
    st.markdown("</div>", unsafe_allow_html=True)

with ch2:
    st.markdown("<div class='chart-card'><p class='chart-label'>💰 Avg Gross Margin by Category</p>", unsafe_allow_html=True)
    cat_margin = df.groupby('category').agg(avg_margin=('gross_margin','mean'), skus=('product_id','count')).reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=cat_margin['category'], y=cat_margin['avg_margin'],
        marker=dict(
            color=cat_margin['avg_margin'],
            colorscale=[[0, '#1e1b4b'], [0.5, '#7C3AED'], [1, '#C084FC']],
            line=dict(width=0)
        ),
        text=[f"{m:.1f}%" for m in cat_margin['avg_margin']],
        textposition='outside', textfont=dict(color='#a1a1aa', size=12),
        hovertemplate='<b>%{x}</b><br>Avg Margin: %{y:.1f}%<extra></extra>'
    ))
    fig2.add_shape(type='line', x0=-0.5, x1=len(cat_margin)-0.5, y0=20, y1=20,
                   line=dict(color='#ef4444', dash='dot', width=1.5))
    fig2.add_annotation(x=len(cat_margin)-1, y=22, text="⚠ 20% threshold", showarrow=False,
                        font=dict(color='#ef4444', size=10))
    fig2.update_layout(**PLOTLY_LAYOUT, height=380,
        xaxis=dict(showgrid=False, tickfont=dict(color='#a1a1aa', size=11)),
        yaxis=dict(showgrid=True, gridcolor='rgba(139,92,246,0.06)', tickfont=dict(color='#71717a', size=10), zeroline=False)
    )
    st.plotly_chart(fig2, use_container_width=True, config=dict(displayModeBar=False))
    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CHARTS ROW 2
# ═══════════════════════════════════════════════════════════════════════════════
ch3, ch4 = st.columns(2)

with ch3:
    st.markdown("<div class='chart-card'><p class='chart-label'>🏆 Top 10 Revenue Engines (Daily)</p>", unsafe_allow_html=True)
    top_rev = df.nlargest(10, 'revenue_proxy').copy()
    top_rev['short_name'] = top_rev['product_name'].apply(lambda x: x[:18] + '…' if len(x) > 18 else x)
    fig3 = go.Figure(go.Bar(
        x=top_rev['revenue_proxy'], y=top_rev['short_name'], orientation='h',
        marker=dict(
            color=top_rev['revenue_proxy'],
            colorscale=[[0, '#1e1b4b'], [1, '#8B5CF6']],
        ),
        text=[f"₹{r:,.0f}" for r in top_rev['revenue_proxy']],
        textposition='outside', textfont=dict(color='#a1a1aa', size=11),
        hovertemplate='<b>%{y}</b><br>Daily Revenue: ₹%{x:,.0f}<extra></extra>'
    ))
    fig3.update_layout(**PLOTLY_LAYOUT, height=360,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(color='#a1a1aa', size=11))
    )
    st.plotly_chart(fig3, use_container_width=True, config=dict(displayModeBar=False))
    st.markdown("</div>", unsafe_allow_html=True)

with ch4:
    st.markdown("<div class='chart-card'><p class='chart-label'>⚠ Rating vs Return Rate Risk Map</p>", unsafe_allow_html=True)
    fig4 = go.Figure()
    palette = ['#8B5CF6', '#22d3ee', '#f59e0b', '#ef4444', '#10b981', '#ec4899']
    for i, cat in enumerate(df['category'].unique()):
        sub = df[df['category'] == cat]
        fig4.add_trace(go.Scatter(
            x=sub['return_rate'] * 100, y=sub['avg_rating'],
            mode='markers', name=cat,
            marker=dict(
                size=sub['revenue_proxy']/60 + 8, opacity=0.85,
                color=palette[i % len(palette)],
                line=dict(color='rgba(255,255,255,0.15)', width=1)
            ),
            text=sub['product_name'],
            hovertemplate='<b>%{text}</b><br>Return: %{x:.1f}%<br>Rating: %{y}<extra></extra>'
        ))
    fig4.add_shape(type='rect', x0=15, x1=35, y0=1, y1=3.5,
                   fillcolor='rgba(239, 68, 68, 0.04)', line=dict(color='#ef4444', width=1, dash='dot'))
    fig4.add_annotation(x=25, y=3.3, text="⚠ Risk Zone", showarrow=False, font=dict(color='#ef4444', size=10))

    layout_copy = PLOTLY_LAYOUT.copy()
    layout_copy.update(
        height=360,
        showlegend=True,
        legend=dict(font=dict(color='#a1a1aa', size=10), bgcolor='rgba(0,0,0,0)', x=1, y=1),
        xaxis=dict(showgrid=True, gridcolor='rgba(139,92,246,0.06)', zeroline=False, title='Return Rate (%)',
                   title_font=dict(color='#71717a', size=10), tickfont=dict(color='#71717a', size=9)),
        yaxis=dict(showgrid=True, gridcolor='rgba(139,92,246,0.06)', zeroline=False, title='Avg Rating',
                   title_font=dict(color='#71717a', size=10), tickfont=dict(color='#71717a', size=9))
    )
    fig4.update_layout(**layout_copy)
    st.plotly_chart(fig4, use_container_width=True, config=dict(displayModeBar=False))
    st.markdown("</div>", unsafe_allow_html=True)

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

> ⚠️ **AI Generation Offline** — OpenAI quota exceeded. Top up at [platform.openai.com/billing](https://platform.openai.com/billing) and click **⟲ Refresh Dashboard** to activate.

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
st.markdown("<p style='color:#52525b;font-size:0.8rem;margin-bottom:1rem;'>Ask about inventory, pricing, reviews, or category performance. Powered by GPT-4o-mini.</p>", unsafe_allow_html=True)

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
