"""
src/chunking.py
Utility module for chunking documents with overlap.
Currently used by ingest.py for BIS standard parsing.
"""

import json
import os


def chunk_documents(documents, chunk_size=512, overlap=50):
    """
    Split a list of documents into overlapping chunks.
    
    Args:
        documents: List of document dicts with 'text' field
        chunk_size: Target size of each chunk (in characters)
        overlap: Number of characters to overlap between consecutive chunks
    
    Returns:
        List of chunk dicts with original fields + chunk_start and chunk_end
    """
    if not documents:
        return []
    
    chunks = []
    chunk_id = 0
    
    for doc_idx, doc in enumerate(documents):
        text = doc.get("text", "")
        
        if len(text) <= chunk_size:
            # Document fits in a single chunk
            chunk = dict(doc)
            chunk["chunk_id"] = chunk_id
            chunk["doc_idx"] = doc_idx
            chunk["chunk_start"] = 0
            chunk["chunk_end"] = len(text)
            chunks.append(chunk)
            chunk_id += 1
        else:
            # Split into overlapping chunks
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk_text = text[start:end]
                
                chunk = dict(doc)
                chunk["chunk_id"] = chunk_id
                chunk["doc_idx"] = doc_idx
                chunk["chunk_start"] = start
                chunk["chunk_end"] = end
                chunk["text"] = chunk_text
                chunks.append(chunk)
                
                chunk_id += 1
                start += (chunk_size - overlap)
                
                if end == len(text):
                    break
    
    return chunks


def save_chunks(chunks, output_dir="data/processed"):
    """
    Save chunks to JSON file in the processed data directory.
    
    Args:
        chunks: List of chunk dicts
        output_dir: Directory to save chunks to
    
    Returns:
        Path to saved file
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "chunks.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    return output_path


def load_chunks(chunks_path="data/processed/chunks.json"):
    """
    Load previously saved chunks.
    
    Args:
        chunks_path: Path to chunks JSON file
    
    Returns:
        List of chunk dicts
    """
    if not os.path.exists(chunks_path):
        raise FileNotFoundError(f"Chunks file not found: {chunks_path}")
    
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    return chunks


def merge_overlapping_chunks(chunks, similarity_threshold=0.8):
    """
    Optionally merge chunks that have high text overlap.
    Useful for deduplication.
    
    Args:
        chunks: List of chunks
        similarity_threshold: Float between 0 and 1
    
    Returns:
        Deduplicated list of chunks
    """
    if not chunks:
        return []
    
    merged = []
    used = set()
    
    for i, chunk1 in enumerate(chunks):
        if i in used:
            continue
        
        text1 = chunk1.get("text", "").lower()
        best_merge = chunk1
        
        # Check for highly similar chunks to merge
        for j, chunk2 in enumerate(chunks[i+1:], start=i+1):
            if j in used:
                continue
            
            text2 = chunk2.get("text", "").lower()
            
            # Simple overlap check: if one is substring of other with threshold
            if len(text1) > 0 and len(text2) > 0:
                # Calculate Jaccard similarity of words
                words1 = set(text1.split())
                words2 = set(text2.split())
                if words1 and words2:
                    intersection = len(words1 & words2)
                    union = len(words1 | words2)
                    similarity = intersection / union if union > 0 else 0
                    
                    if similarity >= similarity_threshold:
                        # Merge by keeping the longer/more complete version
                        if len(text2) > len(best_merge.get("text", "")):
                            best_merge = chunk2
                        used.add(j)
        
        merged.append(best_merge)
    
    return merged
