"""
pages/1_🏠_Home.py — Landing page
"""
import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="BIS Standard Finder", page_icon="🏗️", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Hero Section ──
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">🇮🇳 Bureau of Indian Standards · SP 21 Knowledge Base</div>
    <h1 class="hero-title">BIS Standard Finder</h1>
    <p class="hero-subtitle">
        AI-powered compliance recommendations for building material manufacturers.
        Instantly find the right Indian Standard for your product — powered by RAG.
    </p>
    <div class="stats-row">
        <div class="stat-card">
            <span class="stat-number">820+</span>
            <span class="stat-label">IS Standards Indexed</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">900</span>
            <span class="stat-label">PDF Pages Processed</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">Hybrid</span>
            <span class="stat-label">RAG Search Engine</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">Llama 3</span>
            <span class="stat-label">AI Model (via Groq)</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CTA Buttons ──
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🔍 Find BIS Standards", use_container_width=True, type="primary"):
        st.switch_page("pages/2_🔍_Find_Standards.py")
with col2:
    if st.button("💬 Chat with AI", use_container_width=True):
        st.switch_page("pages/3_💬_Chat.py")
with col3:
    if st.button("📖 Browse All Standards", use_container_width=True):
        st.switch_page("pages/4_📖_Browse.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Features Section ──
st.markdown("""
<div class="section-header">
    <div class="section-title">Everything You Need for BIS Compliance</div>
    <div class="section-subtitle">Built for Indian Micro & Small Enterprises (MSEs) manufacturing building materials</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <span class="feature-icon">🔍</span>
        <div class="feature-title">Smart Standard Search</div>
        <div class="feature-desc">Describe your product in plain English and instantly get the most relevant BIS IS standards. No need to know the exact standard number.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🤖</span>
        <div class="feature-title">AI-Powered Rationale</div>
        <div class="feature-desc">Llama 3 explains exactly why each standard applies to your product — not just the result, but the reasoning behind it.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🔀</span>
        <div class="feature-title">Hybrid RAG Engine</div>
        <div class="feature-desc">Combines semantic vector search (FAISS) + keyword search (BM25) for higher accuracy than either method alone.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">💬</span>
        <div class="feature-title">Conversational Mode</div>
        <div class="feature-desc">Ask follow-up questions in a chat interface. Understand testing requirements, scope, and applicability through dialogue.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">📖</span>
        <div class="feature-title">Browse All 820+ Standards</div>
        <div class="feature-desc">Explore the full BIS SP 21 database. Filter by category, search by keyword, and read the full extracted text of any standard.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">📥</span>
        <div class="feature-title">Export Results</div>
        <div class="feature-desc">Download your compliance search results as a CSV file for documentation, reporting, or sharing with your team.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── How It Works ──
st.markdown("""
<div class="section-header">
    <div class="section-title">How It Works</div>
    <div class="section-subtitle">Three simple steps from question to compliance</div>
</div>

<div class="steps-container">
    <div class="step">
        <div class="step-number">1</div>
        <div class="step-title">Describe Your Product</div>
        <div class="step-desc">Type a plain-English description of your building material or compliance question</div>
    </div>
    <div class="step">
        <div class="step-number">2</div>
        <div class="step-title">AI Searches the Database</div>
        <div class="step-desc">Our hybrid RAG engine searches 820+ IS standards from BIS SP 21 using semantic + keyword search</div>
    </div>
    <div class="step">
        <div class="step-number">3</div>
        <div class="step-title">Get Ranked Results</div>
        <div class="step-desc">Receive top relevant standards with AI-generated rationale explaining why each one applies</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Try ──
st.markdown("""
<div class="section-header">
    <div class="section-title">Quick Examples to Try</div>
    <div class="section-subtitle">Click any card to instantly search for that standard</div>
</div>
""", unsafe_allow_html=True)

examples = [
    ("🧱", "Ordinary Portland Cement", "Cement for structural building work"),
    ("🔩", "TMT Steel Bars", "Reinforced concrete construction"),
    ("🪨", "Coarse Aggregates", "Structural concrete mix design"),
    ("🧱", "Hollow Concrete Blocks", "Masonry wall construction"),
    ("🪵", "Portland Slag Cement", "Low-heat construction applications"),
    ("🚿", "PVC Water Pipes", "Plumbing and water supply systems"),
]

cols = st.columns(3)
for i, (icon, title, desc) in enumerate(examples):
    with cols[i % 3]:
        if st.button(f"{icon} {title}\n{desc}", key=f"home_ex_{i}", use_container_width=True):
            st.session_state["prefill_query"] = f"{title} — {desc}"
            st.switch_page("pages/2_🔍_Find_Standards.py")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color: #475569; font-size: 0.8rem;">
    Built with ❤️ using Streamlit · FAISS · BGE Embeddings · Groq Llama 3 · BIS SP 21<br>
    Data source: Bureau of Indian Standards SP 21 (929 pages)
</div>
""", unsafe_allow_html=True)
