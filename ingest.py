"""
ingest.py — Document Ingestion Pipeline
Rutgers MS CS Unofficial Guide

Pipeline:
  Load .txt files → preprocess (strip noise) → chunk (500 chars / 100 overlap)
  → return list of dicts with text, source, chunk_index

Run directly to inspect chunks:
  python ingest.py
"""

import re
import random
from pathlib import Path


# ── 1. PREPROCESSING ──────────────────────────────────────────────────────────

def preprocess(text: str) -> str:
    """
    Strip structural noise from a document so only substantive content remains.

    What we remove:
    - Lines made entirely of '=' characters  (section dividers like ====)
    - Lines of the pattern '-- heading --'   (sub-section dividers)
    - Lines that contain ONLY a section label with no content value
      e.g. "SECTION 1 — STUDENT REVIEWS (Rate My Professors)"
    - Runs of 3+ blank lines collapsed to a single blank line

    What we keep:
    - Review text, ratings, professor names, course codes, official descriptions,
      workload breakdowns, tips, reddit excerpts — everything with real content.
    """
    lines = text.split('\n')
    cleaned = []

    for line in lines:
        stripped = line.strip()

        # Drop lines that are only '=' characters (any length)
        if re.fullmatch(r'=+', stripped):
            continue

        # Drop lines of the form '-- anything --'
        if re.fullmatch(r'--.*--', stripped):
            continue

        # Drop lines that are purely a SECTION header label with no data
        # e.g. "SECTION 1 — STUDENT REVIEWS (Rate My Professors)"
        # These match: starts with "SECTION" followed by a number
        if re.match(r'^SECTION \d+\s*[—–-]', stripped):
            continue

        cleaned.append(line)

    # Collapse 3+ consecutive blank lines into one blank line
    result = '\n'.join(cleaned)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


# ── 2. CHUNKING ───────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    Split text into overlapping character-based chunks.

    chunk_size = 500: large enough to contain one complete review plus a line of
                      surrounding context (professor name, date, course code).
    overlap    = 100: ensures a review that straddles a chunk boundary is not
                      split into two meaningless fragments.

    Returns a list of non-empty, stripped strings.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if len(chunk) >= 50:  # discard empty strings and short tail fragments
            chunks.append(chunk)

        # Advance by (chunk_size - overlap) so next chunk shares the last
        # 'overlap' characters with this one
        start += chunk_size - overlap

    return chunks


# ── 3. INGESTION ──────────────────────────────────────────────────────────────

def ingest_documents(docs_dir: str = 'documents') -> list[dict]:
    """
    Load every .txt file in docs_dir, preprocess it, chunk it, and return
    a flat list of chunk dicts.

    Each dict has:
      text         — the chunk content
      source       — the filename it came from (e.g. 'professor_boularias.txt')
      chunk_index  — position of this chunk within that document (0-based)
    """
    docs_path = Path(docs_dir)
    all_chunks = []

    txt_files = sorted(docs_path.glob('*.txt'))

    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in '{docs_dir}/'")

    for filepath in txt_files:
        raw_text = filepath.read_text(encoding='utf-8')
        clean_text = preprocess(raw_text)
        chunks = chunk_text(clean_text)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'text': chunk,
                'source': filepath.name,
                'chunk_index': i,
            })

    return all_chunks


# ── 4. VERIFICATION ───────────────────────────────────────────────────────────

def verify_chunks(chunks: list[dict]) -> None:
    """
    Print a diagnostic report so you can inspect chunk quality before embedding.
    Checks for: empty chunks, noise artifacts, chunk length distribution,
    and chunk count per source file.
    """
    print("\n" + "=" * 60)
    print("CHUNK VERIFICATION REPORT")
    print("=" * 60)

    # Summary stats
    sources = {}
    lengths = []
    noise_flags = []

    for chunk in chunks:
        src = chunk['source']
        sources[src] = sources.get(src, 0) + 1
        lengths.append(len(chunk['text']))

        # Flag anything that looks like leftover noise
        if re.match(r'^=+', chunk['text']):
            noise_flags.append(chunk)
        if chunk['text'].startswith('--') and chunk['text'].strip().endswith('--'):
            noise_flags.append(chunk)

    print(f"\nTotal chunks      : {len(chunks)}")
    print(f"Documents loaded  : {len(sources)}")
    print(f"Avg chunk length  : {sum(lengths) // len(lengths)} chars")
    print(f"Min chunk length  : {min(lengths)} chars")
    print(f"Max chunk length  : {max(lengths)} chars")

    print("\nChunks per document:")
    for src, count in sorted(sources.items()):
        print(f"  {count:>3}  {src}")

    # Range check
    print()
    if len(chunks) < 50:
        print("⚠️  WARNING: Fewer than 50 chunks — chunks may be too large.")
    elif len(chunks) > 2000:
        print("⚠️  WARNING: More than 2,000 chunks — chunks may be too small.")
    else:
        print(f"✅ Chunk count ({len(chunks)}) is in the healthy range (50–2,000).")

    # Noise check
    if noise_flags:
        print(f"\n⚠️  WARNING: {len(noise_flags)} chunk(s) start with noise patterns.")
        for c in noise_flags[:3]:
            print(f"  [{c['source']}] {repr(c['text'][:80])}")
    else:
        print("✅ No obvious noise artifacts detected in chunk starts.")

    # Print 5 random sample chunks for manual inspection
    print("\n" + "=" * 60)
    print("5 RANDOM SAMPLE CHUNKS (read each — is it self-contained?)")
    print("=" * 60)

    sample = random.sample(chunks, min(5, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        print(f"\n── Sample {i} ──────────────────────────────────────────────")
        print(f"Source : {chunk['source']}  |  chunk_index : {chunk['chunk_index']}")
        print(f"Length : {len(chunk['text'])} chars")
        print()
        print(chunk['text'])

    print("\n" + "=" * 60)
    print("Inspect the 5 samples above. Each should be:")
    print("  ✓ Readable on its own (no hanging fragments)")
    print("  ✓ About one topic (one review, one description, one section)")
    print("  ✓ Free of '===', '--', or HTML artifacts")
    print("=" * 60 + "\n")


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Loading and chunking documents...")
    chunks = ingest_documents('documents')
    verify_chunks(chunks)
