"""
src/embed.py
Loads chunks from data/chunks.json, creates sentence embeddings,
and saves a FAISS index for fast semantic search.
Run once (offline): python src/embed.py
"""

import json
import pickle
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


MODEL_NAME = "BAAI/bge-small-en-v1.5"  # Better than MiniLM for retrieval
CHUNKS_PATH = "data/chunks.json"
INDEX_PATH = "data/faiss.index"
CHUNKS_PKL_PATH = "data/chunks.pkl"


def build_index(chunks_path: str = CHUNKS_PATH):
    print(f"Loading chunks from {chunks_path}")
    with open(chunks_path) as f:
        chunks = json.load(f)

    if not chunks:
        print("ERROR: No chunks found. Run ingest.py first.")
        return

    print(f"Loaded {len(chunks)} chunks")
    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    # For BGE models, prepend instruction for retrieval
    texts = [
        f"Represent this sentence for searching relevant BIS standards: {c['text']}"
        for c in chunks
    ]

    print("Creating embeddings (this takes 1-2 minutes)...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        normalize_embeddings=True  # for cosine similarity
    )

    print(f"Embedding shape: {embeddings.shape}")

    # Build FAISS index (inner product = cosine similarity since embeddings are normalized)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))

    print(f"FAISS index built with {index.ntotal} vectors")

    # Save
    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PKL_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"Saved index to {INDEX_PATH}")
    print(f"Saved chunks to {CHUNKS_PKL_PATH}")
    print("Done! Index is ready for search.")


if __name__ == "__main__":
    build_index()