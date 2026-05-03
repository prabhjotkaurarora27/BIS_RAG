"""
src/pipeline.py
End-to-end pipeline: query → expand → retrieve → rerank → enrich → return results.
"""

from src.retriever import retrieve
from src.generator import rerank_and_explain, generate_description, expand_query


def run_pipeline(query: str) -> tuple[list[str], list[dict]]:
    """
    Run the full RAG pipeline for a single query.

    Steps:
      1. Query expansion  — LLM broadens vague queries for better recall
      2. Hybrid retrieval — FAISS + BM25 with dynamic weighting
      3. LLM reranking    — Groq selects + explains top 3-5 results
      4. Enrichment       — PDF body text or AI-generated description per result

    Returns:
        retrieved_standards : list of full_id strings e.g. ["IS 269: 1989", ...]
        details             : list of dicts with full_id, title, rationale,
                              description, faiss_score, bm25_score, hybrid_score
    """
    # Step 1: Query expansion (improves recall for vague / short queries)
    expanded_query = expand_query(query)

    # Step 2: Hybrid retrieval — use expanded query to maximise recall
    chunks = retrieve(expanded_query, top_k=7)

    # Build lookups: full_id → PDF body text and explainability scores
    body_lookup  = {}
    score_lookup = {}
    for c in chunks:
        fid = c.get("full_id", c.get("is_number", ""))
        body_lookup[fid] = c.get("body", "").strip()
        score_lookup[fid] = {
            "faiss_score":  c.get("faiss_score",  0.0),
            "bm25_score":   c.get("bm25_score",   0.0),
            "hybrid_score": c.get("hybrid_score", c.get("score", 0.0)),
            "faiss_weight": c.get("faiss_weight", 0.7),
            "bm25_weight":  c.get("bm25_weight",  0.3),
        }

    # Step 3: LLM reranking — use ORIGINAL query so explanation is grounded
    results = rerank_and_explain(query, chunks)

    # Step 4: Enrich each result with description + explainability scores
    for r in results:
        fid  = r.get("full_id", "")
        body = body_lookup.get(fid, "")

        if body and len(body) > 60:
            r["description"]        = body[:600]
            r["description_source"] = "pdf"
        else:
            r["description"]        = generate_description(fid, r.get("title", ""))
            r["description_source"] = "ai"

        # Attach explainability scores from retrieval layer
        scores = score_lookup.get(fid, {})
        r["faiss_score"]  = scores.get("faiss_score",  0.0)
        r["bm25_score"]   = scores.get("bm25_score",   0.0)
        r["hybrid_score"] = scores.get("hybrid_score", 0.5)
        r["faiss_weight"] = scores.get("faiss_weight", 0.7)
        r["bm25_weight"]  = scores.get("bm25_weight",  0.3)

    # Surface expanded query on first result for UI display (None if unchanged)
    if results:
        results[0]["_expanded_query"] = (
            expanded_query if expanded_query != query else None
        )

    # Extract just the IS IDs for eval scoring (judge entry point uses this)
    retrieved_standards = [r["full_id"] for r in results]

    return retrieved_standards, results