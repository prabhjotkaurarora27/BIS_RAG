# 🏛️ BIS Standard Finder — AI-Powered Compliance Tool

> **Built for the "Accelerating MSE Compliance" Hackathon | Track: RAG**

An AI-powered Retrieval-Augmented Generation (RAG) system that maps any product description to the relevant Bureau of Indian Standards (BIS) IS regulations — in seconds. Designed for Indian Micro & Small Enterprises (MSEs) who manufacture building materials.

---

## 🎯 Problem

India's BIS SP 21 handbook spans **929 pages** with **820+ IS standards**. Small business owners have no efficient way to find which standards apply to their products — leading to non-compliance, fines, or expensive consultant fees.

**This tool solves it with a 3-second AI query.**

---

## 🚀 Live Demo

```bash
git clone https://github.com/YOUR_USERNAME/bis-standard-finder.git
cd bis-standard-finder
pip install -r requirements.txt
streamlit run app.py
```

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
Before retrieval, Groq LLM expands vague queries into technical BIS terminology — improving recall for non-expert users who don't know the exact standard vocabulary.

### 3. Anti-Hallucination Enforcement
The LLM reranker is strictly constrained to only cite IS numbers present in the retrieved context. A post-processing validation step further filters any hallucinated IDs.

### 4. Explainability
Every result shows its **FAISS score**, **BM25 score**, and **hybrid score** — with the weighting strategy used — in an expandable "Why this result?" panel.

---

## 📊 Evaluation Results

Evaluated on the **public test set (10 queries)** using the organizer-provided `eval_script.py`:

| Metric | Score | Hackathon Target |
|--------|-------|-----------------|
| **Hit Rate @3** | **100%** | > 80% ✅ |
| **MRR @5** | **0.93** | > 0.70 ✅ |
| **Avg Latency** | **~3.4s** | < 5s ✅ |

Results file: `data/public_results.json`

To reproduce:
```bash
python inference.py --input data/public_test_set.json --output data/public_results.json
python eval_script.py --results data/public_results.json
```

---

## ⚙️ Setup

### 1. Clone and install
```bash
git clone https://github.com/YOUR_USERNAME/bis-standard-finder.git
cd bis-standard-finder
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your Groq API key
```bash
cp .env.example .env
# Edit .env and paste your key:
# GROQ_API_KEY=gsk_your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

### 3. Add the BIS SP 21 dataset
```
data/raw/bis_sp21.pdf
```

### 4. Build the FAISS index (one-time, ~5 mins)
```bash
python src/ingest.py --pdf data/raw/bis_sp21.pdf    # Parse PDF → chunks
python src/embed.py                                   # Build FAISS index
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
bis-standard-finder/
├── app.py                      # Streamlit entry point
├── inference.py                # ⚖️ Judge entry point — DO NOT MODIFY
├── eval_script.py              # ⚖️ Organizer evaluation script — DO NOT MODIFY
├── requirements.txt
├── .env.example                # Safe API key template
├── .gitignore
│
├── src/
│   ├── ingest.py               # PDF parsing with PyMuPDF
│   ├── embed.py                # BGE embedding + FAISS index builder
│   ├── chunking.py             # Text chunking logic
│   ├── retriever.py            # 🔍 Dynamic hybrid retriever (FAISS + BM25)
│   ├── generator.py            # 🤖 Groq LLM — query expansion, reranking, descriptions
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
    ├── public_test_set.json    # 10 public evaluation queries
    └── public_results.json     # ✅ Our results on public test set
```

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
- 💬 **Conversational Chatbot** — Multi-turn Q&A about BIS standards and construction
- 📖 **Browse Database** — Filter and explore all 820+ indexed standards
- 📄 **Download Report** — One-click compliance report as `.txt` or `.csv`
- 🏷️ **Category Tags** — Auto-tagged by material type (Cement, Steel, Aggregates…)

---

## 👥 Team

PRABHJOT KAUR,
HARPREET KAUR,
HIMANSHI TREHAN ,
SUKHPREET KAUR

---

