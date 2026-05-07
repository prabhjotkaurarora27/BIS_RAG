"""
pages/2_🔍_Find_Standards.py — Core search page
Upgrades:
  - Real confidence scores from hybrid_score (F1/F4)
  - Explainability expander per result (F1)
  - Dynamic weighting label (F2)
  - Expanded query display (F3)
  - Confidence labels: High/Medium/Low (F4)
  - Copy IS Number button (F4)
  - Download Text Report button (F4)
"""
import streamlit as st
import time, csv, io, os, sys, html as html_mod
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Find Standards · BIS", page_icon="🔍", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

def get_category(title: str) -> tuple[str, str]:
    t = title.lower()
    if any(w in t for w in ["cement", "portland", "pozzolana", "slag cement"]):
        return "Cement", "cat-cement"
    elif any(w in t for w in ["steel", "iron", "bar", "wire", "tmt", "rebar"]):
        return "Steel & Metal", "cat-steel"
    elif any(w in t for w in ["aggregate", "sand", "gravel", "stone"]):
        return "Aggregates", "cat-aggregate"
    elif any(w in t for w in ["brick", "block", "masonry", "clay", "tile"]):
        return "Bricks & Blocks", "cat-brick"
    elif any(w in t for w in ["pipe", "plumbing", "drainage", "sewage"]):
        return "Pipes", "cat-pipe"
    else:
        return "General", "cat-other"

def get_confidence_meta(hybrid_score: float) -> tuple[int, str, str, str]:
    """
    Returns (confidence_pct, fill_class, chip_class, chip_label)
    using actual hybrid retrieval score (0-1 scale).
    Thresholds: High > 0.80, Medium 0.50–0.80, Low < 0.50
    """
    pct = min(int(hybrid_score * 100), 99)
    if hybrid_score >= 0.80:
        return pct, "filled-high",   "confidence-chip-high",   "High"
    elif hybrid_score >= 0.50:
        return pct, "filled-medium", "confidence-chip-medium", "Medium"
    else:
        return pct, "filled-low",    "confidence-chip-low",    "Low"

def build_result_card(i: int, result: dict) -> str:
    """Build result card HTML. Confidence now uses actual hybrid_score."""
    fid       = result.get("full_id", "N/A")
    title_raw = result.get("title", "")
    rat_raw   = result.get("rationale", "")
    desc_raw  = result.get("description", "")
    desc_src  = result.get("description_source", "pdf")
    hybrid_s  = result.get("hybrid_score", max(1.0 - i * 0.12, 0.35))

    title = html_mod.escape(title_raw)
    rat   = html_mod.escape(rat_raw)
    desc  = html_mod.escape(desc_raw)

    confidence, fill_class, chip_class, chip_label = get_confidence_meta(hybrid_s)
    cat_label, cat_class = get_category(title_raw)

    filled_segs = round(confidence / 10)
    segs = ""
    for j in range(10):
        cls = "confidence-segment " + (fill_class if j < filled_segs else "")
        segs += '<div class="' + cls.strip() + '"></div>'

    # Source badge
    if desc_src == "pdf":
        src_badge = ('<span style="font-size:10px;background:rgba(26,154,80,0.12);'
                     'color:#1DC870;border:1px solid rgba(26,154,80,0.3);'
                     'padding:1px 8px;border-radius:4px;font-weight:700;">FROM PDF</span>')
    else:
        src_badge = ('<span style="font-size:10px;background:rgba(210,140,40,0.12);'
                     'color:#D28C28;border:1px solid rgba(210,140,40,0.3);'
                     'padding:1px 8px;border-radius:4px;font-weight:700;">AI GENERATED</span>')

    # Build card HTML
    h  = '<div class="result-card">'

    # Header
    h += '<div class="result-header">'
    h += '<div>'
    h += '<span class="result-badge">' + fid + '</span>'
    h += '<span class="cat-badge ' + cat_class + '">' + cat_label + '</span>'
    h += '</div>'
    h += '<div style="color:#4A6070;font-size:0.8rem;">#' + str(i+1) + ' match</div>'
    h += '</div>'

    # Title
    h += '<div class="result-title">' + title + '</div>'

    # Rationale
    h += '<div class="result-rationale">' + rat + '</div>'

    # Description box
    if desc.strip():
        h += '<div style="margin-top:12px;padding:12px 14px;'
        h += 'background:rgba(255,255,255,0.025);'
        h += 'border:1px solid rgba(255,255,255,0.08);border-radius:6px;">'
        h += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px;">'
        h += '<span style="font-size:10px;color:#4A6070;text-transform:uppercase;'
        h += 'letter-spacing:1px;font-weight:600;">Description</span>'
        h += src_badge
        h += '</div>'
        h += '<div style="font-size:0.85rem;color:#7A9AAA;line-height:1.7;">' + desc + '</div>'
        h += '</div>'

    # Confidence bar
    h += '<div class="confidence-bar-wrap">'
    h += '<div class="confidence-header">'
    h += '<span class="confidence-label">Relevance Score</span>'
    h += '<span class="confidence-chip ' + chip_class + '">'
    h += chip_label + ' &middot; ' + str(confidence) + '%</span>'
    h += '</div>'
    h += '<div class="confidence-bar">' + segs + '</div>'
    h += '</div>'

    h += '</div>'
    return h

def build_explainability_panel(result: dict):
    """Render the Why this result? expander using native Streamlit."""
    faiss_s  = result.get("faiss_score",  0.0)
    bm25_s   = result.get("bm25_score",   0.0)
    hybrid_s = result.get("hybrid_score", 0.0)
    faiss_w  = result.get("faiss_weight", 0.7)
    bm25_w   = result.get("bm25_weight",  0.3)
    fid      = result.get("full_id", "")

    with st.expander("🔍 Why this result? — Explainability", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric(
            label="🧠 Semantic Score",
            value=f"{faiss_s:.3f}",
            help="FAISS cosine similarity — how well the meaning matches"
        )
        c2.metric(
            label="🔤 Keyword Score",
            value=f"{bm25_s:.3f}",
            help="BM25 Okapi — exact term overlap with IS standard text"
        )
        c3.metric(
            label="⚡ Hybrid Score",
            value=f"{hybrid_s:.3f}",
            help="Weighted combination used for final ranking"
        )

        # Weight strategy explanation
        strategy = "BM25-heavy (short query)" if bm25_w > faiss_w else "FAISS-heavy (semantic query)"
        st.markdown(
            f'<div class="explain-weights">'
            f'<span class="explain-label">Weights applied:</span> '
            f'Semantic <span class="explain-val">{faiss_w:.0%}</span> &nbsp;·&nbsp; '
            f'Keyword <span class="explain-val">{bm25_w:.0%}</span> &nbsp;'
            f'<span class="explain-strategy">({strategy})</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Mini score bars
        st.markdown(
            f'<div class="explain-bars">'
            f'<div class="explain-bar-row">'
            f'  <span class="explain-bar-label">Semantic</span>'
            f'  <div class="explain-bar-track"><div class="explain-bar-fill sem" style="width:{int(faiss_s*100)}%"></div></div>'
            f'  <span class="explain-bar-pct">{int(faiss_s*100)}%</span>'
            f'</div>'
            f'<div class="explain-bar-row">'
            f'  <span class="explain-bar-label">Keyword</span>'
            f'  <div class="explain-bar-track"><div class="explain-bar-fill kw" style="width:{int(bm25_s*100)}%"></div></div>'
            f'  <span class="explain-bar-pct">{int(bm25_s*100)}%</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Copy IS number
        st.markdown(
            '<div style="margin-top:10px;font-size:0.75rem;color:#4A6070;'
            'text-transform:uppercase;letter-spacing:1px;font-weight:600;">IS Number</div>',
            unsafe_allow_html=True
        )
        st.code(fid, language=None)
        st.caption("👆 Click the copy icon to copy the IS number")


def build_text_report(query: str, details: list[dict], elapsed: float) -> str:
    """Generate a plain-text compliance report."""
    lines = [
        "=" * 60,
        "  BIS STANDARD FINDER — COMPLIANCE REPORT",
        "=" * 60,
        f"Query    : {query}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Results  : {len(details)} standards found in {elapsed:.2f}s",
        "=" * 60,
        "",
    ]
    for i, r in enumerate(details, 1):
        fid       = r.get("full_id", "N/A")
        title     = r.get("title", "")
        cat,  _   = get_category(title)
        rat       = r.get("rationale", "")
        desc      = r.get("description", "")
        hybrid_s  = r.get("hybrid_score", 0.0)
        _, _, _, label = get_confidence_meta(hybrid_s)

        lines += [
            f"RESULT {i}",
            f"  Standard : {fid}",
            f"  Title    : {title}",
            f"  Category : {cat}",
            f"  Match    : {label} ({int(hybrid_s*100)}%)",
            f"  Rationale: {rat}",
        ]
        if desc:
            lines += [f"  Details  : {desc[:300]}{'...' if len(desc) > 300 else ''}"]
        lines += ["", "-" * 60, ""]

    lines += [
        "DISCLAIMER",
        "Results are based on BIS SP 21 (929-page handbook).",
        "Always verify against official BIS documentation before",
        "making any regulatory or compliance decisions.",
        "",
        "Powered by BIS Standard Finder · FAISS + BM25 + Groq Llama 3",
    ]
    return "\n".join(lines)


# ── Header ──
st.markdown("""
<div class="page-header">
    <h1>🔍 Find BIS Standards</h1>
    <p>Describe your product or compliance question — AI will find the right IS standards from BIS SP 21</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Example Quick Buttons ──
st.markdown("**⚡ Quick Examples — Click to instantly search:**")

examples = [
    "Ordinary Portland Cement for structural use",
    "TMT steel bars for reinforced concrete construction",
    "Coarse and fine aggregates for structural concrete",
    "Hollow concrete masonry blocks dimensions and physical requirements",
    "Portland slag cement chemical and physical requirements",
    "PVC pipes for water supply systems",
]

if "search_query" not in st.session_state:
    st.session_state.search_query = st.session_state.get("prefill_query", "")
if "trigger_search" not in st.session_state:
    st.session_state.trigger_search = False
if "search_results" not in st.session_state:
    st.session_state.search_results = None

cols = st.columns(3)
for i, ex in enumerate(examples):
    if cols[i % 3].button(ex[:42] + "…", key=f"ex_{i}", use_container_width=True):
        st.session_state.search_query = ex
        st.session_state.trigger_search = True

st.markdown("<br>", unsafe_allow_html=True)

query = st.text_area(
    "📝 Or type your own product description:",
    value=st.session_state.search_query,
    height=110,
    placeholder="e.g. We manufacture 33 Grade Ordinary Portland Cement. Which BIS standard applies?",
    key="query_box"
)

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    search_clicked = st.button("🔍 Find Applicable BIS Standards", type="primary", use_container_width=True)
with col_btn2:
    clear = st.button("🗑️ Clear", use_container_width=True)

if clear:
    st.session_state.search_query = ""
    st.session_state.trigger_search = False
    st.session_state.search_results = None
    st.rerun()

should_search = (search_clicked and query.strip()) or (
    st.session_state.trigger_search and st.session_state.search_query.strip()
)

if st.session_state.trigger_search:
    st.session_state.trigger_search = False

if should_search:
    active_query = query.strip() or st.session_state.search_query.strip()
    st.session_state.search_query = active_query
    with st.spinner("🔍 Searching BIS standards — expanding query and running hybrid retrieval…"):
        try:
            from src.pipeline import run_pipeline
            start = time.time()
            retrieved_standards, details = run_pipeline(active_query)
            elapsed = time.time() - start
            st.session_state.search_results = (details, elapsed, active_query)
        except FileNotFoundError:
            st.error("⚠️ Index not found — the FAISS index has not been built yet.")
            st.markdown("""
**Run these commands once from the project root:**
```bash
python3 src/ingest.py --pdf data/raw/bis_sp21.pdf   # Parse PDF → chunks
python3 src/embed.py                                  # Build FAISS index
streamlit run app.py                                  # Restart app
```
> You need the BIS SP 21 PDF at `data/raw/bis_sp21.pdf` and a Groq API key in `.env`
""")
        except Exception as e:
            st.error(f"Error: {e}")
elif search_clicked:
    st.warning("Please enter a description first.")

# ── Display Results ──
if st.session_state.search_results:
    details, elapsed, last_query = st.session_state.search_results

    st.markdown("<br>", unsafe_allow_html=True)

    # Show expanded query if it differs from original
    expanded_q = details[0].get("_expanded_query") if details else None
    if expanded_q:
        st.info(f"💡 **Query expanded** for better recall:\n\n_{expanded_q}_")

    header = (
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">'
        '<div>'
        '<span style="font-size:1.2rem;font-weight:700;color:#EDE8D6;">&#10003; Found '
        + str(len(details)) +
        ' Relevant Standards</span>'
        '<span style="color:#64748B;font-size:0.85rem;margin-left:12px;">in '
        + str(round(elapsed, 2)) + 's</span>'
        '</div></div>'
    )
    st.markdown(header, unsafe_allow_html=True)

    if details:
        # ── Download buttons row ──
        dl_col1, dl_col2 = st.columns([1, 1])

        # CSV export
        csv_buf = io.StringIO()
        writer = csv.DictWriter(csv_buf, fieldnames=["full_id", "title", "rationale", "description", "hybrid_score"])
        writer.writeheader()
        writer.writerows([{
            "full_id":      r.get("full_id", ""),
            "title":        r.get("title", ""),
            "rationale":    r.get("rationale", ""),
            "description":  r.get("description", ""),
            "hybrid_score": r.get("hybrid_score", ""),
        } for r in details])
        dl_col1.download_button(
            label="📥 Export CSV",
            data=csv_buf.getvalue(),
            file_name="bis_standards_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Text report download
        report_txt = build_text_report(last_query, details, elapsed)
        dl_col2.download_button(
            label="📄 Download Report",
            data=report_txt,
            file_name=f"bis_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    for i, result in enumerate(details):
        # Result card (HTML)
        st.markdown(build_result_card(i, result), unsafe_allow_html=True)
        # Explainability expander (native Streamlit — interactive)
        build_explainability_panel(result)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if not details:
        st.warning("No relevant standards found. Try rephrasing your query.")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#475569;font-size:0.8rem;">'
    'Results based on BIS SP 21 &middot; Always verify with official BIS documentation'
    '</div>',
    unsafe_allow_html=True
)
