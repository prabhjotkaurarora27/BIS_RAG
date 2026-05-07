"""
pages/4_📖_Browse.py — Browse all 820+ standards
"""
import streamlit as st
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Browse Standards · BIS", page_icon="📖", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

@st.cache_data
def load_chunks():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chunks.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)

def get_category(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["cement", "portland", "pozzolana", "slag cement", "lime"]):
        return "Cement & Binders"
    elif any(w in t for w in ["steel", "iron", "bar", "wire", "tmt", "rebar", "metal"]):
        return "Steel & Metals"
    elif any(w in t for w in ["aggregate", "sand", "gravel", "stone", "coarse", "fine"]):
        return "Aggregates"
    elif any(w in t for w in ["brick", "block", "masonry", "clay", "tile", "aac"]):
        return "Bricks & Blocks"
    elif any(w in t for w in ["pipe", "plumbing", "drainage", "sewage", "tube"]):
        return "Pipes & Plumbing"
    elif any(w in t for w in ["paint", "coat", "waterproof", "sealant", "bitumen"]):
        return "Paints & Waterproofing"
    elif any(w in t for w in ["glass", "window", "door", "shutter", "frame"]):
        return "Doors, Windows & Glass"
    else:
        return "Other Standards"

# ── Header ──
st.markdown("""
<div class="page-header">
    <h1>📖 Browse All BIS Standards</h1>
    <p>Explore all 820+ IS standards extracted from BIS SP 21. Filter by category or search by keyword.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

chunks = load_chunks()

if not chunks:
    st.error("⚠️ Data not found — the index has not been built yet.")
    st.markdown("""
### 🔧 One-time Setup Required

This app needs a pre-built index to work. Run these commands **once** from the project root:

```bash
# Step 1 — Parse the BIS SP 21 PDF into structured chunks
python3 src/ingest.py --pdf data/raw/bis_sp21.pdf

# Step 2 — Build the FAISS vector index (takes ~2–5 mins)
python3 src/embed.py

# Step 3 — Restart the Streamlit app
streamlit run app.py
```

> 📄 **You need the BIS SP 21 PDF** placed at `data/raw/bis_sp21.pdf`
> Get a free Groq API key at [console.groq.com](https://console.groq.com) and add it to `.env`
""")
    st.stop()

# Add category to each chunk
for c in chunks:
    c["category"] = get_category(c.get("title", ""))

# ── Filters ──
col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("🔎 Search by keyword, IS number, or title:", placeholder="e.g. cement, IS 269, aggregate…")
with col2:
    all_cats = sorted(set(c["category"] for c in chunks))
    selected_cat = st.selectbox("📂 Filter by Category:", ["All Categories"] + all_cats)

# ── Filter Logic ──
filtered = chunks
if selected_cat != "All Categories":
    filtered = [c for c in filtered if c["category"] == selected_cat]
if keyword.strip():
    kw = keyword.strip().lower()
    filtered = [c for c in filtered if kw in c.get("text", "").lower() or kw in c.get("full_id", "").lower() or kw in c.get("title", "").lower()]

# ── Stats Bar ──
st.markdown(f"""
<div style="display:flex; gap:20px; margin:16px 0; flex-wrap:wrap;">
    <div style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2); border-radius:8px; padding:10px 20px;">
        <span style="color:#60A5FA; font-weight:700; font-size:1.3rem;">{len(filtered)}</span>
        <span style="color:#94A3B8; font-size:0.85rem; margin-left:6px;">standards shown</span>
    </div>
    <div style="background:rgba(15,31,61,0.5); border:1px solid rgba(59,130,246,0.1); border-radius:8px; padding:10px 20px;">
        <span style="color:#94A3B8; font-size:0.85rem;">{len(chunks)} total in database</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Category Summary ──
if selected_cat == "All Categories" and not keyword.strip():
    cat_counts = {}
    for c in chunks:
        cat_counts[c["category"]] = cat_counts.get(c["category"], 0) + 1

    st.markdown("**Standards by Category:**")
    cat_cols = st.columns(4)
    for i, (cat, count) in enumerate(sorted(cat_counts.items(), key=lambda x: -x[1])):
        with cat_cols[i % 4]:
            st.metric(cat, count)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Results ──
if not filtered:
    st.warning("No standards match your filter. Try a different keyword or category.")
else:
    # Pagination
    PAGE_SIZE = 30
    total_pages = max(1, (len(filtered) - 1) // PAGE_SIZE + 1)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start_idx = (page - 1) * PAGE_SIZE
    page_chunks = filtered[start_idx: start_idx + PAGE_SIZE]

    st.markdown(f"<div style='color:#64748B; font-size:0.8rem; margin-bottom:12px;'>Showing {start_idx+1}–{min(start_idx+PAGE_SIZE, len(filtered))} of {len(filtered)}</div>", unsafe_allow_html=True)

    for chunk in page_chunks:
        fid   = chunk.get("full_id", "")
        title = chunk.get("title", "No title")
        year  = chunk.get("year", "")
        body  = chunk.get("body", "")[:200]
        cat   = chunk.get("category", "Other")

        with st.expander(f"**{fid}** — {title[:80]}"):
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.markdown(f"**IS Number:** `{fid}`")
                st.markdown(f"**Year:** {year}")
                st.markdown(f"**Category:** {cat}")
            with col_b:
                st.markdown(f"**Title:** {title}")
                if body:
                    st.markdown(f"**Extracted Text:**\n\n_{body}…_")
                else:
                    st.markdown("_No additional text extracted._")
