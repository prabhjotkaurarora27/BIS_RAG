"""
inference.py  —  JUDGE ENTRY POINT (root level, do not move)

Judges run:
    python inference.py --input hidden_private_dataset.json --output team_results.json

The eval_script.py then reads team_results.json and expects each item to have:
    - "expected_standards"   (copied from input)
    - "retrieved_standards"  (your pipeline output)
    - "latency_seconds"      (float)

eval_script.py is run separately by judges:
    python eval_script.py --results team_results.json
"""

import argparse
import json
import time
import sys
import os

# Make sure src/ is importable from root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="BIS RAG Inference — generates standard recommendations"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input JSON file (list of {id, query, expected_standards})"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write output JSON results"
    )
    args = parser.parse_args()

    # Load input queries
    print(f"Loading queries from: {args.input}")
    try:
        with open(args.input, "r") as f:
            queries = json.load(f)
    except Exception as e:
        print(f"ERROR reading input file: {e}")
        sys.exit(1)

    total = len(queries)
    print(f"Running pipeline on {total} queries...")

    results = []

    for i, item in enumerate(queries):
        query_id = item.get("id", f"item_{i}")
        query_text = item.get("query", "")
        expected = item.get("expected_standards", [])

        print(f"  [{i+1}/{total}] {query_id}: {query_text[:60]}...")

        start_time = time.time()
        try:
            retrieved_standards, _ = run_pipeline(query_text)
        except Exception as e:
            print(f"    WARNING: pipeline failed for {query_id}: {e}")
            retrieved_standards = []
        latency = round(time.time() - start_time, 4)

        print(f"    Retrieved: {retrieved_standards[:3]} | {latency:.2f}s")

        # Output format matches what eval_script.py expects:
        # it reads "expected_standards", "retrieved_standards", "latency_seconds"
        results.append({
            "id": query_id,
            "query": query_text,
            "expected_standards": expected,
            "retrieved_standards": retrieved_standards,
            "latency_seconds": latency
        })

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    avg_latency = sum(r["latency_seconds"] for r in results) / len(results) if results else 0
    print(f"\nDone! {total} queries processed.")
    print(f"Average latency: {avg_latency:.2f}s")
    print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()