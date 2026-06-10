"""
generate.py — Grounded Generation via Groq
Rutgers MS CS Unofficial Guide

Pipeline:
  query → retrieve top-k chunks → format context block
  → Groq (llama-3.3-70b-versatile) with grounding system prompt
  → return { answer, sources, chunks }

Usage:
  from generate import build_pipeline, ask

  collection = build_pipeline()          # run once at startup
  result = ask("Is Boularias good?", collection)
  print(result["answer"])
  print(result["sources"])
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from ingest import ingest_documents
from retrieve import embed_and_store, retrieve

load_dotenv()


# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
#
# Grounding rules:
#   1. Answer ONLY from the provided documents — never from training knowledge.
#   2. Cite the source document for every claim.
#   3. If the documents don't contain enough information, say so explicitly.
#
# Rule 3 is critical: without it the LLM will fill gaps with plausible-sounding
# training-data answers that look grounded but aren't.

SYSTEM_PROMPT = """You are the Rutgers MS CS Unofficial Guide — a helpful assistant that answers questions about courses and professors in the Rutgers University MS Computer Science program.

STRICT GROUNDING RULES — follow these exactly:
1. Answer ONLY using information found in the provided documents below. Do not use any knowledge from your training data, even if you are confident it is correct.
2. For every factual claim in your answer, cite the source document in parentheses, e.g. (source: professor_mario_szegedy.txt).
3. If the provided documents do not contain enough information to answer the question, respond with exactly: "I don't have enough information in my documents to answer that. Try asking about a professor or course covered in the guide."
4. Do not speculate, infer, or generalize beyond what the documents explicitly state.
5. If different documents contradict each other, report both perspectives and note the disagreement.

Keep answers concise and direct. Students are making enrollment decisions — be specific."""


# ── CONTEXT FORMATTER ─────────────────────────────────────────────────────────

def format_context(chunks: list[dict]) -> str:
    """
    Turn retrieved chunks into a labeled context block for the prompt.

    Each chunk is prefixed with its source filename so the LLM knows
    which document a piece of information came from and can cite it.
    """
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Document {i} — source: {chunk['source']}]\n{chunk['text']}"
        )
    return "\n\n".join(parts)


# ── CORE GENERATION FUNCTION ──────────────────────────────────────────────────

def generate_answer(
    query: str,
    collection,
    k: int = 5,
    model: str = "llama-3.3-70b-versatile",
) -> dict:
    """
    Full RAG pipeline: retrieve → format context → generate grounded answer.

    Returns a dict with:
      answer   — the LLM's response (grounded, with citations)
      sources  — deduplicated list of source filenames that were retrieved
      chunks   — the raw retrieved chunks (for debugging / transparency)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY not set. Add it to your .env file:\n  GROQ_API_KEY=gsk_..."
        )

    # Step 1 — Retrieve top-k relevant chunks
    chunks = retrieve(query, collection, k=k)

    # Step 2 — Format chunks into a labeled context block
    context = format_context(chunks)

    # Step 3 — Build the user message: context + question
    user_message = f"""Here are the relevant documents retrieved for this question:

{context}

---

Question: {query}

Remember: answer ONLY from the documents above. Cite the source filename for each claim."""

    # Step 4 — Call Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,   # low temp = more faithful, less creative
        max_tokens=1024,
    )

    answer = response.choices[0].message.content.strip()

    # Step 5 — Programmatic source attribution (don't rely solely on LLM)
    # Deduplicate while preserving order (best-match first)
    seen = set()
    sources = []
    for chunk in chunks:
        src = chunk["source"]
        if src not in seen:
            seen.add(src)
            sources.append(src)

    return {
        "answer":  answer,
        "sources": sources,
        "chunks":  chunks,
    }


# ── PIPELINE BUILDER ──────────────────────────────────────────────────────────

def build_pipeline(docs_dir: str = "documents") -> object:
    """
    Load documents, embed all chunks, and return a ready-to-query ChromaDB
    collection. Call this ONCE at startup — it takes ~2–3 seconds.
    """
    print("Building pipeline...")
    chunks = ingest_documents(docs_dir)
    collection = embed_and_store(chunks)
    print("Pipeline ready.\n")
    return collection


# ── CLI TEST ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    collection = build_pipeline()

    # ── Test 1: grounded answer (Srikanta)
    q1 = "What do students say about Professor Srikanta's organization and grading?"
    r1 = generate_answer(q1, collection)
    print("=" * 70)
    print(f"Q: {q1}")
    print(f"\nA: {r1['answer']}")
    print(f"\nSources: {', '.join(r1['sources'])}")

    # ── Test 2: comparison (Boularias vs Kulikowski)
    q2 = "Which professor should I take for Intro to AI — Boularias or Kulikowski?"
    r2 = generate_answer(q2, collection)
    print("\n" + "=" * 70)
    print(f"Q: {q2}")
    print(f"\nA: {r2['answer']}")
    print(f"\nSources: {', '.join(r2['sources'])}")

    # ── Test 3: out-of-scope query — should trigger the "not enough info" response
    q3 = "What is the average salary for Rutgers CS graduates?"
    r3 = generate_answer(q3, collection)
    print("\n" + "=" * 70)
    print(f"Q: {q3}")
    print(f"\nA: {r3['answer']}")
    print(f"\nSources: {', '.join(r3['sources'])}")

    print("\n" + "=" * 70)
    print("Generation test complete.")
