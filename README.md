# 🏛️ BIS Standard Finder — AI-Powered Compliance Tool

> **Built for the "Accelerating MSE Compliance" Hackathon | Track: RAG**

An AI-powered Retrieval-Augmented Generation (RAG) system that maps any product description to the relevant Bureau of Indian Standards (BIS) IS regulations — in seconds. Designed for Indian Micro & Small Enterprises (MSEs) who manufacture building materials.

---

## 🎯 Problem

India's BIS SP 21 handbook spans **929 pages** with **820+ IS standards**. Small business owners have no efficient way to find which standards apply to their products — leading to non-compliance, fines, or expensive consultant fees.

**This tool solves it with a 3-second AI query.**

---

## 🚀 Quick Start (Full Setup for New Clones)

Follow every step in order. **All commands must be run from the project root folder.**

### Step 1 — Clone the repository

```bash
git clone https://github.com/prabhjotkaurarora27/BIS_RAG.git
cd BIS_RAG
```

### Step 2 — Create and activate a virtual environment

```bash
python3 -m venv venv

# On macOS / Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

> ✅ You should see `(venv)` in your terminal prompt after activation.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> ⏳ This takes 2–3 minutes. It downloads PyMuPDF, FAISS, sentence-transformers, and Groq.

### Step 4 — Add your Groq API key

```bash
cp .env.example .env
```

Now open the `.env` file and replace the placeholder with your actual key:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

> 🔑 Get a **free** Groq API key at [console.groq.com](https://console.groq.com) — takes 1 minute.

### Step 5 — Add the BIS SP 21 PDF

Place the BIS SP 21 PDF at exactly this path inside the project folder:

```
data/raw/bis_sp21.pdf
```

> 📄 The PDF must be named `bis_sp21.pdf` and placed inside the `data/raw/` folder.

### Step 6 — Parse the PDF (one-time, ~1–2 min)

```bash
python3 src/ingest.py --pdf data/raw/bis_sp21.pdf
```

This reads all 929 pages and extracts 820+ IS standard entries into `data/chunks.json`.

### Step 7 — Build the FAISS vector index (one-time, ~3–5 min)

```bash
python3 src/embed.py
```

This creates the semantic search index (`data/faiss.index`) and saves chunks to `data/chunks.pkl`.

### Step 8 — Run the app ✅

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 📋 Command Summary (Quick Reference)

```bash
# 1. Clone & enter project
git clone https://github.com/prabhjotkaurarora27/BIS_RAG.git
cd BIS_RAG

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install packages
pip install -r requirements.txt

# 4. Set up API key
cp .env.example .env
# ✏️  Edit .env → add your GROQ_API_KEY

# 5. Add PDF → data/raw/bis_sp21.pdf

# 6. Build index (run once)
python3 src/ingest.py --pdf data/raw/bis_sp21.pdf
python3 src/embed.py

# 7. Launch
streamlit run app.py
```

---

## 🔁 After First Setup — How to Run Again

If you've already done the setup, just activate your environment and run the app:

```bash
source venv/bin/activate        # Windows: venv\Scripts\activate
streamlit run app.py
```

> You do **not** need to re-run `ingest.py` or `embed.py` again unless you change the PDF.

---

## 📊 Evaluation

Evaluated on the **public test set (10 queries)** using the organizer-provided `eval_script.py`:

| Metric | Score | Hackathon Target |
|--------|-------|-----------------|
| **Hit Rate @3** | **100%** | > 80% ✅ |
| **MRR @5** | **0.93** | > 0.70 ✅ |
| **Avg Latency** | **~3.4s** | < 5s ✅ |

### Reproduce evaluation results

```bash
python3 inference.py --input data/public_test_set.json --output data/public_results.json
python3 eval_script.py --results data/public_results.json
```

Results file: `data/public_results.json`

---

## 🏗️ Architecture

```
BIS SP 21 PDF (929 pages)
    └─► src/ingest.py      — PyMuPDF parsing → 820+ structured IS standard chunks
    └─► src/embed.py       — BGE-small-en-v1.5 embeddings → FAISS vector index

User Query
    └─► src/generator.py   — LLM Query Expansion (Groq) → richer search terms
    └─► src/retriever.py   — Dynamic Hybrid Search:
    │                           • FAISS semantic search (cosine similarity)
    │                           • BM25 keyword search (Okapi)
    │                           • Dynamic weighting by query length
    └─► src/generator.py   — Groq LLM reranking + rationale (anti-hallucination)
    └─► src/pipeline.py    — End-to-end glue layer
    └─► inference.py       — Judge entry point (batch evaluation)
    └─► app.py             — Streamlit multi-page UI
```

---

## 🔍 Retrieval Strategy (Core Innovation)

### 1. Dynamic Hybrid Weighting
Instead of fixed weights, the system adapts based on query type:

| Query Type | Example | FAISS | BM25 |
|------------|---------|-------|------|
| Short / keyword (`< 4 words`) | `"IS 269 cement"` | 40% | **60%** |
| Long / descriptive (`≥ 4 words`) | `"33 grade ordinary portland cement physical requirements"` | **70%** | 30% |

### 2. LLM Query Expansion
Before retrieval, Groq LLM expands vague queries into technical BIS terminology — improving recall for non-expert users.

### 3. Anti-Hallucination Enforcement
The LLM reranker is strictly constrained to only cite IS numbers present in the retrieved context. A post-processing validation step further filters any hallucinated IDs.

### 4. Explainability
Every result shows its **FAISS score**, **BM25 score**, and **hybrid score** — with the weighting strategy used — in an expandable "Why this result?" panel.

---

## 📁 Project Structure

```
BIS_RAG/
├── app.py                      # Streamlit entry point
├── inference.py                # ⚖️ Judge entry point — DO NOT MODIFY
├── eval_script.py              # ⚖️ Organizer evaluation script — DO NOT MODIFY
├── requirements.txt            # Python dependencies
├── .env.example                # Safe API key template (copy to .env)
├── .gitignore
│
├── src/
│   ├── ingest.py               # PDF parsing with PyMuPDF
│   ├── embed.py                # BGE embedding + FAISS index builder
│   ├── chunking.py             # Text chunking logic
│   ├── retriever.py            # 🔍 Dynamic hybrid retriever (FAISS + BM25)
│   ├── generator.py            # 🤖 Groq LLM — query expansion, reranking
│   └── pipeline.py             # End-to-end pipeline glue
│
├── pages/
│   ├── 1_🏠_Home.py            # Landing page
│   ├── 2_🔍_Find_Standards.py  # Main search with explainability
│   ├── 3_💬_Chat.py            # Multi-turn AI chatbot
│   ├── 4_📖_Browse.py          # Browse all standards
│   └── 5_ℹ️_About.py          # Architecture + eval results
│
├── styles/
│   └── main.css                # Global design system (saffron/navy theme)
│
└── data/
    ├── raw/
    │   └── bis_sp21.pdf        # ⬅️ Add this manually (not in repo)
    ├── chunks.json             # Generated by ingest.py (not in repo)
    ├── faiss.index             # Generated by embed.py (not in repo)
    ├── chunks.pkl              # Generated by embed.py (not in repo)
    ├── public_test_set.json    # 10 public evaluation queries
    └── public_results.json     # ✅ Our results on public test set
```

> **Note:** Files marked "not in repo" are gitignored (large binary/generated files). You must generate them locally by following the setup steps above.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| UI | Streamlit (multi-page) |
| Embeddings | `BAAI/bge-small-en-v1.5` via sentence-transformers |
| Vector DB | FAISS (CPU) |
| Keyword Search | BM25 Okapi (rank-bm25) |
| LLM | Groq `llama-3.3-70b-versatile` + `llama-3.1-8b-instant` |
| PDF Parsing | PyMuPDF |
| Language | Python 3.9+ |

---

## 💡 Features

- 🔍 **Smart Standard Search** — Natural language → relevant IS standards in 3 seconds
- 🔀 **Dynamic Hybrid RAG** — Adapts FAISS/BM25 weights based on query type
- 💡 **Query Expansion** — LLM enriches vague queries before retrieval
- 🤖 **AI Rationale** — Explains *why* each standard applies, in plain English
- 🔬 **Explainability Panel** — Shows FAISS, BM25, and hybrid scores per result
- 💬 **Conversational Chatbot** — Multi-turn Q&A about BIS standards
- 📖 **Browse Database** — Filter and explore all 820+ indexed standards
- 📄 **Download Report** — One-click compliance report as `.txt` or `.csv`
- 🏷️ **Category Tags** — Auto-tagged by material type (Cement, Steel, Aggregates…)

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Make sure `(venv)` is active: `source venv/bin/activate` |
| `Data not found` error in app | Run `python3 src/ingest.py --pdf data/raw/bis_sp21.pdf` then `python3 src/embed.py` |
| `GROQ_API_KEY not set` | Add your key to `.env` (copy from `.env.example`) |
| PDF not found | Place `bis_sp21.pdf` at `data/raw/bis_sp21.pdf` |
| Port 8501 in use | Run `streamlit run app.py --server.port 8502` |

---

## 👥 Team

PRABHJOT KAUR,
HARPREET KAUR,
HIMANSHI TREHAN,
SUKHPREET KAUR
