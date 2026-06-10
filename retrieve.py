"""
retrieve.py — Embedding and Retrieval Pipeline
Rutgers MS CS Unofficial Guide

Pipeline:
  chunks (from ingest.py) → embed with all-MiniLM-L6-v2
  → upsert into ChromaDB (in-memory, cosine similarity)
  → retrieve top-k chunks for a query string

Run directly to test retrieval with evaluation plan queries:
  python retrieve.py
"""

import os

import chromadb
from sentence_transformers import SentenceTransformer

# Suppress ChromaDB telemetry without needing Settings import
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from ingest import ingest_documents


# ── 1. MODEL (loaded once, reused for all embed calls) ────────────────────────

_MODEL = None

def get_model() -> SentenceTransformer:
    """Load all-MiniLM-L6-v2 once and cache it."""
    global _MODEL
    if _MODEL is None:
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded.")
    return _MODEL


# ── 2. EMBED AND STORE ────────────────────────────────────────────────────────

def embed_and_store(chunks: list[dict]) -> chromadb.Collection:
    """
    Embed all chunks with all-MiniLM-L6-v2 and upsert into a ChromaDB
    in-memory collection with cosine similarity.

    Each chunk dict must have:
      text         — the chunk string to embed
      source       — filename it came from
      chunk_index  — position within that document

    Returns the ChromaDB collection (pass this to retrieve()).
    """
    model = get_model()

    # EphemeralClient = in-memory, nothing written to disk (ChromaDB >= 0.4)
    client = chromadb.EphemeralClient()

    # cosine similarity: distance = 1 - cosine_sim
    # distance 0.0 = identical, 0.5 = loosely related, 1.0 = unrelated
    collection = client.create_collection(
        name="rutgers_guide",
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["text"] for c in chunks]

    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_list=True)
    print("Embeddings done.")

    # ChromaDB requires string IDs
    ids        = [f"{c['source']}__chunk_{c['chunk_index']}" for c in chunks]
    metadatas  = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB collection '{collection.name}'.\n")
    return collection


# ── 3. RETRIEVE ───────────────────────────────────────────────────────────────

def retrieve(query: str, collection: chromadb.Collection, k: int = 5) -> list[dict]:
    """
    Embed the query and return the top-k most semantically similar chunks.

    Returns a list of dicts, each with:
      text         — the chunk text
      source       — source filename
      chunk_index  — position in that document
      distance     — cosine distance (lower = more similar; < 0.5 is good)
    """
    model = get_model()
    query_embedding = model.encode([query], convert_to_list=True)[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    # Unpack ChromaDB's nested list structure (one query → one row)
    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "text":        doc,
            "source":      meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance":    round(dist, 4),
        }
        for doc, meta, dist in zip(docs, metas, distances)
    ]


# ── 4. PRETTY PRINT HELPER ───────────────────────────────────────────────────

def print_results(query: str, results: list[dict]) -> None:
    """Print retrieved chunks with distance scores for manual inspection."""
    print("\n" + "=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)

    for i, r in enumerate(results, 1):
        score_label = "✅ strong" if r["distance"] < 0.35 else \
                      "⚠️  ok"    if r["distance"] < 0.5  else \
                      "❌ weak"
        print(f"\n── Result {i} ── distance: {r['distance']} {score_label}")
        print(f"   Source : {r['source']}  (chunk {r['chunk_index']})")
        print()
        # Print first 400 chars so output stays readable
        preview = r["text"][:400] + ("..." if len(r["text"]) > 400 else "")
        print(f"   {preview}")

    print()


# ── MAIN — run 3 evaluation plan queries ─────────────────────────────────────

if __name__ == "__main__":
    # Load and embed chunks
    chunks     = ingest_documents("documents")
    collection = embed_and_store(chunks)

    # ── Evaluation query 1 ────────────────────────────────────────────────────
    # Expected: chunks from professor_karthik_srikanta.txt mentioning
    # disorganized lectures, proof-heavy exams, no posted notes
    q1 = "What do students say about Professor Srikanta's organization and grading in his algorithms course?"
    print_results(q1, retrieve(q1, collection, k=5))

    # ── Evaluation query 3 ────────────────────────────────────────────────────
    # Expected: chunks from both professor_abdeslam_boularias.txt (4.8/5, 97%)
    # and professor_casimir_kulikowski.txt (2.6/5, 10% would take again)
    q3 = "Which professor should I take for Intro to AI — Boularias or Kulikowski?"
    print_results(q3, retrieve(q3, collection, k=5))

    # ── Evaluation query 5 ────────────────────────────────────────────────────
    # Expected: ≥ 2 chunks from professor_mario_szegedy.txt mentioning
    # missed classes, didn't attend final exam, 40% final weight
    q5 = "Is Mario Szegedy a reliable professor — does he show up to class?"
    print_results(q5, retrieve(q5, collection, k=5))

    print("=" * 70)
    print("RETRIEVAL TEST COMPLETE")
    print("Check: are top results on-topic? Are distances < 0.5?")
    print("If weak results appear, see planning.md Anticipated Challenges.")
    print("=" * 70 + "\n")
