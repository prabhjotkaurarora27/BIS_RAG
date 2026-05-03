"""
src/retriever.py
Hybrid retriever: combines FAISS semantic search + BM25 keyword search.

Enhancements:
  - Dynamic weighting: short queries (<4 words) → BM25=0.6/FAISS=0.4
                       long queries (>=4 words)  → BM25=0.3/FAISS=0.7
  - Explainability: each result carries faiss_score, bm25_score, hybrid_score
"""

import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import re

MODEL_NAME = "BAAI/bge-small-en-v1.5"
INDEX_PATH = "data/faiss.index"
CHUNKS_PKL_PATH = "data/chunks.pkl"


class HybridRetriever:
    def __init__(self):
        print("Loading retriever...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index(INDEX_PATH)

        with open(CHUNKS_PKL_PATH, "rb") as f:
            self.chunks = pickle.load(f)

        # Build BM25 index from tokenized chunk texts
        tokenized = [self._tokenize(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)
        print(f"Retriever ready. {len(self.chunks)} chunks indexed.")

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace + lowercase tokenizer."""
        return re.sub(r'[^a-zA-Z0-9\s:]', ' ', text.lower()).split()

    def _semantic_search(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        """Returns list of (chunk_index, score) from FAISS."""
        # BGE query prefix
        query_text = f"Represent this sentence for searching relevant BIS standards: {query}"
        q_vec = self.model.encode(
            [query_text],
            normalize_embeddings=True
        ).astype(np.float32)

        scores, indices = self.index.search(q_vec, top_k)
        return [(int(idx), float(score)) for idx, score in zip(indices[0], scores[0]) if idx >= 0]

    def _bm25_search(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        """Returns list of (chunk_index, score) from BM25."""
        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(int(i), float(scores[i])) for i in top_indices if scores[i] > 0]

    def retrieve(self, query: str, top_k: int = 7) -> list[dict]:
        """
        Hybrid search with dynamic weighting based on query length.

        - Short query (<4 words): BM25=0.6, FAISS=0.4  (keyword-heavy)
        - Long  query (>=4 words): BM25=0.3, FAISS=0.7 (semantic-heavy)

        Each result dict includes:
          faiss_score   — normalized [0,1] semantic similarity
          bm25_score    — normalized [0,1] keyword match strength
          hybrid_score  — weighted combination (= score, kept for backward compat)
          faiss_weight  — FAISS weight used for this query
          bm25_weight   — BM25 weight used for this query
        """
        word_count = len(query.split())
        if word_count < 4:
            faiss_w, bm25_w = 0.4, 0.6   # short / keyword query
        else:
            faiss_w, bm25_w = 0.7, 0.3   # long / semantic query

        # Retrieve candidates from both methods
        semantic_results = self._semantic_search(query, top_k=10)
        bm25_results     = self._bm25_search(query, top_k=10)

        # Normalize scores to [0, 1] independently
        def normalize_scores(results: list[tuple[int, float]]) -> dict[int, float]:
            if not results:
                return {}
            max_s = max(s for _, s in results)
            min_s = min(s for _, s in results)
            rng = max_s - min_s if max_s != min_s else 1.0
            return {idx: (s - min_s) / rng for idx, s in results}

        sem_norm  = normalize_scores(semantic_results)
        bm25_norm = normalize_scores(bm25_results)

        # Merge: weighted combination
        all_indices = set(sem_norm.keys()) | set(bm25_norm.keys())
        combined = {}
        for idx in all_indices:
            combined[idx] = (
                faiss_w * sem_norm.get(idx, 0.0) +
                bm25_w  * bm25_norm.get(idx, 0.0)
            )

        # Sort by combined score descending
        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)

        results = []
        for idx, hybrid in ranked[:top_k]:
            chunk = dict(self.chunks[idx])
            # Explainability scores
            chunk["faiss_score"]  = round(sem_norm.get(idx, 0.0), 4)
            chunk["bm25_score"]   = round(bm25_norm.get(idx, 0.0), 4)
            chunk["hybrid_score"] = round(hybrid, 4)
            chunk["score"]        = chunk["hybrid_score"]  # backward compat
            chunk["faiss_weight"] = faiss_w
            chunk["bm25_weight"]  = bm25_w
            results.append(chunk)

        return results


# Singleton — loaded once, reused across all queries
_retriever = None

def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def retrieve(query: str, top_k: int = 7) -> list[dict]:
    return get_retriever().retrieve(query, top_k=top_k)