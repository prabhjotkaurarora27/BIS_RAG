"""
src/generator.py
Uses Groq (Llama 3) to:
  1. Expand queries for better recall (expand_query)
  2. Rerank retrieved chunks and return top 3-5 relevant BIS standards with rationale
  3. Generate descriptions for standards missing PDF body text

Anti-hallucination enforced in reranker.
"""

import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_MODEL = "llama-3.1-8b-instant"


def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set. Add it to your .env file.")
    return Groq(api_key=api_key)


def expand_query(query: str) -> str:
    """
    Use Groq LLM to expand a product query into richer search keywords,
    improving recall for vague or short queries before retrieval.

    Falls back silently to the original query on any error — zero regression risk.
    """
    try:
        client = get_client()
        prompt = (
            "Expand this product query into detailed technical search keywords for finding "
            "Bureau of Indian Standards (BIS) IS standards. Include material names, "
            "manufacturing terms, and relevant properties. "
            "Return ONLY the expanded search string — no explanation, no bullet points:\n\n"
            f"{query}"
        )
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )
        expanded = response.choices[0].message.content.strip()
        # Sanity check: must be meaningfully longer than original but not absurd
        if len(expanded) > len(query) and len(expanded) < 600:
            return expanded
        return query
    except Exception as e:
        print(f"Query expansion fallback (error: {e})")
        return query


def rerank_and_explain(query: str, chunks: list[dict]) -> list[dict]:
    """
    Given a query and retrieved chunks, ask the LLM to:
    1. Select the most relevant standards
    2. Return them in order of relevance with rationale
    3. ONLY use IS numbers present in the provided context (no hallucination)

    Returns list of dicts: [{ full_id, title, rationale }]
    """
    if not chunks:
        return []

    # Build context — list of standards with their full_id and text
    context_lines = []
    valid_ids = []
    for i, chunk in enumerate(chunks):
        fid = chunk.get("full_id", chunk.get("is_number", f"Unknown-{i}"))
        title = chunk.get("title", "")
        text = chunk.get("text", "")[:400]  # limit context length
        context_lines.append(f"[{fid}] {title}\n{text}")
        valid_ids.append(fid)

    context = "\n\n---\n\n".join(context_lines)
    valid_ids_str = ", ".join(valid_ids)

    prompt = f"""You are an expert on Bureau of Indian Standards (BIS) regulations for building materials.

A Micro or Small Enterprise (MSE) has this question:
"{query}"

Below are potentially relevant BIS standards retrieved from the database:

{context}

---
INSTRUCTIONS:
- Select the TOP 3 to 5 most relevant standards for this query from the list above.
- You MUST only use IS numbers from this exact list: {valid_ids_str}
- Do NOT invent or hallucinate any IS numbers not in the list above.
- Return your answer as a JSON array with this exact structure:
[
  {{
    "full_id": "IS XXX: YYYY",
    "title": "title of the standard",
    "rationale": "one sentence explaining why this standard is relevant"
  }}
]
- Return ONLY the JSON array, no extra text before or after."""

    client = get_client()

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()

        # Clean up: sometimes the model wraps in ```json ... ```
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'^```\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)

        results = json.loads(raw)

        # Validate: strip any hallucinated IDs not in valid_ids
        valid_set = set(vid.lower().replace(" ", "") for vid in valid_ids)
        cleaned = []
        for item in results:
            fid = item.get("full_id", "")
            if fid.lower().replace(" ", "") in valid_set:
                cleaned.append(item)

        return cleaned[:5]  # max 5 results

    except (json.JSONDecodeError, Exception) as e:
        # Fallback: return top chunks without LLM rationale
        print(f"Generator fallback (LLM error: {e})")
        return [
            {
                "full_id": c.get("full_id", c.get("is_number", "Unknown")),
                "title": c.get("title", ""),
                "rationale": "Retrieved based on semantic similarity to query."
            }
            for c in chunks[:5]
        ]


def generate_description(full_id: str, title: str) -> str:
    """
    Generate a 2-3 sentence technical description for a BIS IS standard
    when the PDF body text is unavailable or too short.
    Uses Groq LLM with a focused prompt.
    """
    if not full_id or not title:
        return ""

    prompt = f"""You are an expert on Bureau of Indian Standards (BIS) specifications for building materials.

Provide a concise 2-3 sentence technical description of the following Indian Standard:

Standard: {full_id}
Title: {title}

The description should explain:
1. What this standard covers (scope)
2. Key requirements or specifications it defines
3. Which industry/products it applies to

Write in formal technical language suitable for an engineer or compliance officer.
Return ONLY the description text, no preamble."""

    try:
        client = get_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Description generation failed for {full_id}: {e}")
        return f"This standard ({full_id}) defines technical specifications and requirements for {title.lower()}."