"""
src/ingest.py
Parses the BIS SP 21 PDF (929 pages) into structured chunks.
Each chunk = one IS standard entry.

FIRST — inspect the PDF to see real format:
    python src/ingest.py --pdf data/bis_sp21.pdf --inspect --pages 10

Try middle of PDF where standards are dense:
    python src/ingest.py --pdf data/bis_sp21.pdf --inspect --pages 5 --start-page 50

Then parse:
    python src/ingest.py --pdf data/bis_sp21.pdf

Output: data/chunks.json
"""

import fitz  # PyMuPDF
import json
import re
import argparse
import os


# ─────────────────────────────────────────────────────────────────
# PRIMARY PATTERN
# Matches lines like:
#   IS 269 : 1989   ORDINARY PORTLAND CEMENT — SPECIFICATION
#   IS 2185 (Part 2) : 1983   CONCRETE MASONRY UNITS
#   IS 1489 (Part 2) : 1991   PORTLAND POZZOLANA CEMENT
#   IS 458 : 2003   PRECAST CONCRETE PIPES
# ─────────────────────────────────────────────────────────────────
STD_LINE_RE = re.compile(
    r'^'
    r'(IS\s+\d+\w*'
    r'(?:\s*\(Part[s]?\s*[\dIVX]+\))?'
    r'(?:\s*\(Section\s*[\dIVX]+\))?'
    r')'
    r'\s*[:\-–—]\s*'
    r'(\d{4})'
    r'\s*[:\-–—]?\s*'
    r'(.*)',
    re.IGNORECASE
)

# ALTERNATE — year without explicit colon separator
STD_LINE_ALT_RE = re.compile(
    r'^'
    r'(IS\s+\d+\w*'
    r'(?:\s*\(Part[s]?\s*[\dIVX]+\))?'
    r'(?:\s*\(Section\s*[\dIVX]+\))?'
    r')'
    r'\s+'
    r'(\d{4})'
    r'\s+'
    r'(.*)',
    re.IGNORECASE
)

# Lines to skip (headers, footers, page numbers)
SKIP_LINE_RE = re.compile(
    r'^(SP\s*:?\s*21|Bureau\s+of\s+Indian|BIS\b|^\d{1,3}$|\s*$)',
    re.IGNORECASE
)


def extract_text_from_pdf(pdf_path: str) -> list:
    """Returns list of text strings, one per page."""
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return pages


def inspect_pdf(pdf_path: str, num_pages: int = 10, start_page: int = 0):
    """Print raw text from pages so you can see the actual format."""
    doc = fitz.open(pdf_path)
    total = len(doc)
    print(f"Total pages in PDF: {total}")
    end = min(start_page + num_pages, total)
    print(f"Showing pages {start_page+1} to {end}\n")

    for i in range(start_page, end):
        page = doc[i]
        text = page.get_text()
        print(f"\n{'='*70}")
        print(f"PAGE {i+1}")
        print('='*70)
        # Show first 3000 chars of each page
        print(text[:3000])
    doc.close()


def find_is_start(line: str):
    """
    Try all regex patterns to detect if this line starts a new IS standard.
    Returns (is_number, year, title) or None.
    """
    line = line.strip()
    if not line:
        return None

    m = STD_LINE_RE.match(line)
    if m:
        return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()

    m = STD_LINE_ALT_RE.match(line)
    if m:
        return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()

    return None


def parse_chunks(pages: list) -> list:
    """
    Walk all pages line by line.
    Each IS standard start line begins a new chunk.
    Body text is accumulated until the next standard.
    """
    chunks = []
    current_is = None
    current_year = None
    current_title = None
    current_body = []

    def flush():
        if current_is and current_year:
            full_id = f"{current_is}: {current_year}"
            title = current_title or ""
            body = " ".join(current_body).strip()
            text = f"{full_id}  {title}  {body}".strip()
            chunks.append({
                "is_number": current_is,
                "year": current_year,
                "full_id": full_id,
                "title": title,
                "body": body,
                "text": text,
            })

    for page_text in pages:
        for line in page_text.split('\n'):
            line = line.strip()
            if not line or SKIP_LINE_RE.match(line):
                continue

            result = find_is_start(line)
            if result:
                flush()
                current_is, current_year, current_title = result
                current_body = []
            else:
                if current_is and len(line) > 3:
                    current_body.append(line)

    flush()
    return chunks


def validate_chunks(chunks: list) -> None:
    """Print stats and check for known standards from public test set."""
    print(f"\nParsed {len(chunks)} IS standard chunks")

    if not chunks:
        print("\nWARNING: Zero chunks found!")
        print("This means the PDF format does not match the parser patterns.")
        print("Run: python src/ingest.py --pdf data/bis_sp21.pdf --inspect --pages 10")
        print("Then paste the output here so the regex can be fixed.")
        return

    print("\nFirst 5 chunks:")
    for c in chunks[:5]:
        print(f"  {c['full_id']:<35} {c['title'][:50]}")

    print("\nLast 5 chunks:")
    for c in chunks[-5:]:
        print(f"  {c['full_id']:<35} {c['title'][:50]}")

    # Check all 10 expected standards from the public test set
    known = [
        "IS 269: 1989",
        "IS 383: 1970",
        "IS 458: 2003",
        "IS 2185 (Part 2): 1983",
        "IS 459: 1992",
        "IS 455: 1989",
        "IS 1489 (Part 2): 1991",
        "IS 3466: 1988",
        "IS 6909: 1990",
        "IS 8042: 1989",
    ]

    found_ids = {c['full_id'].lower().replace(' ', '') for c in chunks}

    print("\nChecking 10 known standards from public test set:")
    all_found = True
    for kid in known:
        normalized = kid.lower().replace(' ', '')
        found = normalized in found_ids
        status = "✓ FOUND  " if found else "✗ MISSING"
        print(f"  {status}  {kid}")
        if not found:
            all_found = False

    if all_found:
        print("\nAll 10 known standards found! Parser is working correctly.")
    else:
        print("\nSome standards are missing. The regex may need adjustment.")
        print("Run --inspect on pages around where those standards should appear.")

    lengths = [len(c['text']) for c in chunks]
    print(f"\nText length stats:")
    print(f"  Average: {sum(lengths)//len(lengths)} chars")
    print(f"  Min:     {min(lengths)} chars")
    print(f"  Max:     {max(lengths)} chars")


def main():
    parser = argparse.ArgumentParser(description="Parse BIS SP 21 PDF into chunks")
    parser.add_argument("--pdf", required=True, help="Path to BIS SP 21 PDF")
    parser.add_argument("--output", default="data/chunks.json", help="Output JSON path")
    parser.add_argument("--inspect", action="store_true",
                        help="Print raw PDF text to see format (no parsing)")
    parser.add_argument("--pages", type=int, default=10,
                        help="Number of pages to show in --inspect mode (default: 10)")
    parser.add_argument("--start-page", type=int, default=0,
                        help="Page number to start from (0-indexed)")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"ERROR: PDF not found at '{args.pdf}'")
        print("Put your BIS SP 21 PDF at that path and try again.")
        return

    if args.inspect:
        inspect_pdf(args.pdf, num_pages=args.pages, start_page=args.start_page)
        return

    print(f"Reading PDF: {args.pdf}")
    pages = extract_text_from_pdf(args.pdf)
    print(f"Loaded {len(pages)} pages")

    chunks = parse_chunks(pages)
    validate_chunks(chunks)

    if not chunks:
        print("Nothing saved. Fix the parser first.")
        return

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()