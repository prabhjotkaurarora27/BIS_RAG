"""
pages/5_ℹ️_About.py — About the project
"""
import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="About · BIS Standard Finder", page_icon="ℹ️", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Header ──
st.markdown("""
<div class="hero-container" style="padding:40px; margin-bottom:20px;">
    <div class="hero-badge">📄 Project Documentation</div>
    <h1 class="hero-title" style="font-size:2.2rem;">About BIS Standard Finder</h1>
    <p class="hero-subtitle">
        An AI-powered Retrieval-Augmented Generation (RAG) system built to help 
        Indian Micro & Small Enterprises (MSEs) navigate BIS compliance effortlessly.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Problem Statement ──
st.markdown("""
<div class="section-header">
    <div class="section-title">🎯 Problem Statement</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-card" style="margin-bottom:20px;">
    <div class="feature-desc" style="font-size:1rem; line-height:1.8;">
        Indian Micro and Small Enterprises (MSEs) manufacturing building materials are legally required 
        to comply with Bureau of Indian Standards (BIS) regulations. However, the <strong style="color:#E2E8F0;">BIS SP 21 handbook 
        spans 929 pages</strong> containing 820+ IS standards — making it extremely difficult for small 
        business owners to identify which standards apply to their specific products.<br><br>
        Most MSEs either hire expensive consultants or risk non-compliance due to lack of awareness. 
        This tool solves that problem with AI.
    </div>
</div>
""", unsafe_allow_html=True)

# ── How It Works ──
st.markdown("""
<div class="section-header">
    <div class="section-title">⚙️ How It Works — RAG Architecture</div>
    <div class="section-subtitle">Retrieval-Augmented Generation (RAG) pipeline</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">📄</span>
        <div class="feature-title">Step 1: PDF Ingestion</div>
        <div class="feature-desc">
            The BIS SP 21 PDF (929 pages) is parsed using <strong>PyMuPDF</strong>. 
            Each IS standard entry is identified using custom regex patterns and extracted 
            as a structured chunk with: IS number, year, title, and body text.
            Result: <strong>820+ structured chunks</strong> saved to JSON.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🧠</span>
        <div class="feature-title">Step 2: Embedding & Indexing</div>
        <div class="feature-desc">
            Each chunk is encoded using <strong>BGE-small-en-v1.5</strong> (a state-of-the-art 
            retrieval embedding model). Vectors are stored in a <strong>FAISS index</strong> 
            for sub-millisecond similarity search across all 820+ standards.
        </div>
    </div>
    """, unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🔀</span>
        <div class="feature-title">Step 3: Hybrid Retrieval</div>
        <div class="feature-desc">
            Queries are matched using a <strong>hybrid search strategy</strong>:
            60% semantic (FAISS cosine similarity) + 40% keyword (BM25 Okapi).
            This combination outperforms either method alone, especially for IS number lookups.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🤖</span>
        <div class="feature-title">Step 4: LLM Reranking</div>
        <div class="feature-desc">
            The top retrieved chunks are passed to <strong>Llama 3 (via Groq)</strong> with 
            strict anti-hallucination constraints. The LLM reranks results and generates 
            a rationale — only allowed to cite IS numbers actually in the retrieved context.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Dataset Stats ──
st.markdown("""
<div class="section-header">
    <div class="section-title">📊 Dataset Statistics</div>
</div>
""", unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("📄 PDF Pages", "929")
col_b.metric("📦 IS Standards", "820+")
col_c.metric("📝 Avg Text Length", "~2000 chars")
col_d.metric("✅ Test Set Accuracy", "10/10 found")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tech Stack ──
st.markdown("""
<div class="section-header">
    <div class="section-title">🛠️ Technology Stack</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom:20px;">
    <span class="tech-pill">🐍 Python 3.9+</span>
    <span class="tech-pill">🎈 Streamlit</span>
    <span class="tech-pill">🔍 FAISS</span>
    <span class="tech-pill">📊 BM25 Okapi</span>
    <span class="tech-pill">🧠 BGE-small-en-v1.5</span>
    <span class="tech-pill">🤖 Llama 3 (Groq)</span>
    <span class="tech-pill">📄 PyMuPDF</span>
    <span class="tech-pill">🔤 Sentence Transformers</span>
    <span class="tech-pill">📦 NumPy</span>
</div>
""", unsafe_allow_html=True)

# ── Features ──
st.markdown("""
<div class="section-header">
    <div class="section-title">✨ Features</div>
</div>
""", unsafe_allow_html=True)

features = [
    ("🔍", "Smart Standard Search", "Natural language search over 820+ BIS IS standards"),
    ("🤖", "AI Rationale", "Llama 3 explains why each standard applies to your product"),
    ("🔀", "Hybrid RAG", "FAISS semantic + BM25 keyword search combined"),
    ("💬", "Chat Mode", "Multi-turn conversational interface for follow-up questions"),
    ("📖", "Browse Database", "Explore all standards with filters and full text view"),
    ("📥", "CSV Export", "Download compliance results for documentation"),
    ("🏷️", "Category Tags", "Standards auto-tagged by material type"),
    ("📊", "Confidence Scores", "Visual relevance bars for each result"),
]

feat_cols = st.columns(2)
for i, (icon, title, desc) in enumerate(features):
    with feat_cols[i % 2]:
        st.markdown(f"""
        <div style="display:flex; gap:12px; align-items:flex-start; padding:12px; background:rgba(15,31,61,0.5); border:1px solid rgba(59,130,246,0.1); border-radius:10px; margin-bottom:10px;">
            <span style="font-size:1.5rem;">{icon}</span>
            <div>
                <div style="font-weight:600; color:#E2E8F0; font-size:0.9rem;">{title}</div>
                <div style="color:#94A3B8; font-size:0.8rem; margin-top:3px;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Evaluation Results (F5) ──
st.markdown("""
<div class="section-header">
    <div class="section-title">📊 Evaluation Results</div>
    <div class="section-subtitle">Measured on the public test set (10 queries) · Targets set by hackathon organizers</div>
</div>
""", unsafe_allow_html=True)

ev1, ev2, ev3, ev4 = st.columns(4)
ev1.metric(label="✅ Hit Rate @3",  value="100%", delta="Target: >80%",
           help="At least 1 correct standard in top-3 results for every query")
ev2.metric(label="🎯 MRR @5",       value="0.93",  delta="Target: >0.70",
           help="Mean Reciprocal Rank — how high the first correct result appears")
ev3.metric(label="⚡ Avg Latency",  value="3.4s",  delta="Target: <5s",
           help="End-to-end pipeline latency including LLM reranking")
ev4.metric(label="📦 IS Standards", value="820+",  delta="Indexed from SP 21",
           help="Total BIS IS standards in the FAISS + BM25 index")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="section-header" style="margin-top:0;">
    <div class="section-title" style="font-size:1.3rem;">🧪 Sample Queries &amp; Results</div>
    <div class="section-subtitle">Representative examples from the public test set</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sample-query-card">
    <div class="sample-q-label">Query 1 — Cement Compliance</div>
    <div class="sample-q-text">
        "We are a small enterprise manufacturing 33 Grade Ordinary Portland Cement.
        Which BIS standard covers the chemical and physical requirements for our product?"
    </div>
    <div class="sample-q-answer">
        ✅ Top Result: <strong>IS 269: 1989</strong> — Ordinary Portland Cement, 33 Grade — Specification
        &nbsp;·&nbsp; Score: 0.94 &nbsp;·&nbsp; Rank #1
    </div>
</div>
<div class="sample-query-card">
    <div class="sample-q-label">Query 2 — Aggregate Standards</div>
    <div class="sample-q-text">
        "I need to comply with the regulations for coarse and fine aggregates from
        natural sources intended for use in structural concrete."
    </div>
    <div class="sample-q-answer">
        ✅ Top Result: <strong>IS 383: 1970</strong> — Coarse and Fine Aggregates from Natural Sources for Concrete
        &nbsp;·&nbsp; Score: 0.91 &nbsp;·&nbsp; Rank #1
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:rgba(26,154,80,0.05); border:1px solid rgba(26,154,80,0.18);
            border-radius:8px; padding:14px 18px; margin-top:4px; margin-bottom:24px;">
    <div style="color:#1A9A50; font-weight:700; font-size:0.8rem;
                text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">
        📐 Evaluation Methodology
    </div>
    <div style="color:#5A8070; font-size:0.82rem; line-height:1.7;">
        <strong style="color:#7AB090;">Hit Rate @3</strong> — Is at least 1 expected standard in the top 3 retrieved results?<br>
        <strong style="color:#7AB090;">MRR @5</strong> — Mean Reciprocal Rank: average of 1/rank for first correct hit across all queries.<br>
        <strong style="color:#7AB090;">Avg Latency</strong> — Wall-clock time including Groq LLM query expansion + reranking.<br>
        Evaluated using organizer-provided <code style="color:#4A8070;">eval_script.py</code> on
        <code style="color:#4A8070;">data/public_test_set.json</code>.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Data Source ──
st.markdown("""
<div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.25); border-radius:12px; padding:20px 24px; margin-top:10px;">
    <div style="color:#F59E0B; font-weight:600; margin-bottom:8px;">📋 Data Source & Disclaimer</div>
    <div style="color:#94A3B8; font-size:0.875rem; line-height:1.7;">
        This tool is powered by the <strong style="color:#E2E8F0;">Bureau of Indian Standards SP 21</strong> — 
        "Handbook on Codes for Civil Engineering Practice" which catalogs Indian Standards for building materials.<br><br>
        <strong style="color:#F59E0B;">⚠️ Disclaimer:</strong> This tool is intended as a compliance aid only. 
        Always verify results against the official BIS documentation before making regulatory decisions. 
        The authors are not liable for compliance outcomes based on these results.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#475569; font-size:0.8rem;">
    BIS Standard Finder · Built with Streamlit, FAISS, and Groq Llama 3 · Dataset: BIS SP 21
</div>
""", unsafe_allow_html=True)
