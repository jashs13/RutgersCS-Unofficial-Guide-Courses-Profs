# The Unofficial Guide — Rutgers MS CS

A RAG-powered assistant that answers questions about courses and professors in the Rutgers University MS Computer Science program. Built on student reviews from Rate My Professors, Reddit (r/rutgers), and official Rutgers CS course synopses.

---

## Domain

Student reviews and course information for the MS CS program at Rutgers University. This knowledge is valuable because official course pages provide only abstract descriptions with no insight into workload, grading style, or teaching quality — the information students actually need when making enrollment decisions. It is hard to find otherwise because it is scattered across Rate My Professors, Reddit threads, and individual professor websites, with no single source connecting professor reputation, course difficulty, grading breakdown, and peer survival tips in one place. Incoming MS students frequently make enrollment decisions without knowing that two sections of the same course (e.g., CS520 with Boularias vs. Kulikowski) can produce completely different academic outcomes.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — Karthik Srikanta | Student reviews (35 ratings) | https://www.ratemyprofessors.com/professor/2842115 |
| 2 | Rate My Professors — Mario Szegedy | Student reviews (25 ratings) | https://www.ratemyprofessors.com/professor/52112 |
| 3 | Rate My Professors — Casimir Kulikowski | Student reviews (33 ratings) | https://www.ratemyprofessors.com/professor/409364 |
| 4 | Rate My Professors — Ahmed Elgammal | Student reviews (31 ratings) | https://www.ratemyprofessors.com/professor/184976 |
| 5 | Rate My Professors — Abdeslam Boularias | Student reviews (32 ratings) | https://www.ratemyprofessors.com/professor/2041187 |
| 6 | Rutgers CS Grad Synopses + r/rutgers | Official description + peer discussion for CS513 | documents/course_513_algorithms.txt |
| 7 | Rutgers CS Grad Synopses + Elgammal site | Official description + peer discussion for CS536 | documents/course_536_machine_learning.txt |
| 8 | Rutgers CS Grad Synopses + r/rutgers | Official description + RMP cross-reference for CS520 | documents/course_520_intro_ai.txt |
| 9 | Rutgers CS Grad Synopses (official) | Official description and full grading breakdown for CS527 | documents/course_527_database_systems.txt |
| 10 | Rutgers CS Grad Synopses (official) | Official description and module breakdown for CS543 | documents/course_543_massive_data.txt |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:**
The corpus contains two content types: short opinion reviews (150–300 characters each) and longer structured content like official course descriptions and workload breakdowns (400–600 characters). A 500-character chunk is large enough to capture one complete review plus a surrounding line of context (e.g., the professor's name, date, and course code), which is necessary for the embedding to be semantically useful — a fragment like "Lectures are very disorganized" is only meaningful if the chunk also includes "Karthik Srikanta" or "CS513." It is small enough that unrelated reviews from different professors don't merge into one blob that matches too many queries at once.

Overlap of 100 characters handles the case where a multi-sentence review straddles a chunk boundary — without overlap, the second half of such a review would be an orphaned fragment with no context. Before chunking, a `preprocess()` function strips structural noise: lines made entirely of `=` characters (section dividers), lines matching the pattern `-- heading --`, and lines that are purely `SECTION N —` labels. Runs of 3+ blank lines are collapsed to one. This prevents noise tokens from dominating chunk embeddings.

**Final chunk count:** 115 chunks across 10 documents (avg 476 chars, min 101 chars, max 500 chars)

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

This model produces 384-dimensional embeddings, handles short opinion text well, and fits within its 512-token context limit comfortably given the 500-character chunk size (~125 tokens). It runs locally with no API key and no rate limits, which makes it appropriate for a prototype with ~115 total chunks. The vector store is ChromaDB with cosine similarity (`hnsw:space: cosine`), so distance scores range from 0 (identical) to 1 (unrelated). All top results in evaluation scored below 0.52.

**Production tradeoff reflection:**
In a real deployment, I would evaluate `text-embedding-3-small` (OpenAI) or `instructor-xl` for better semantic capture of domain-specific terminology. Phrases like "NP-completeness," "PAC-learning," and "Bayesian networks" are treated as unknown tokens by general-purpose small models, which can weaken retrieval precision for technical course content. I would also evaluate whether the undergrad/grad course code mismatch (CS440 vs. 16:198:520) degrades recall, and consider a hybrid retrieval approach (BM25 + semantic) to catch exact course code matches that pure embedding search can miss. For multilingual support or international student communities, a multilingual-e5 model would be worth benchmarking. Latency is not a constraint for this local prototype, but an API-hosted model would matter for real users at scale.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt instructs the model with explicit numbered rules:

> "Answer ONLY using information found in the provided documents below. Do not use any knowledge from your training data, even if you are confident it is correct. For every factual claim in your answer, cite the source document in parentheses, e.g. (source: professor_mario_szegedy.txt). If the provided documents do not contain enough information to answer the question, respond with exactly: 'I don't have enough information in my documents to answer that.' Do not speculate, infer, or generalize beyond what the documents explicitly state."

Temperature is set to 0.2 to reduce creative generation and keep the model close to the retrieved text. Each chunk in the user message is prefixed with its source filename (e.g., `[Document 1 — source: professor_karthik_srikanta.txt]`) so the model always knows which document a piece of information came from before it generates a citation.

**How source attribution is surfaced in the response:**

Attribution works at two levels. First, the LLM is instructed to cite source filenames inline within its answer. Second, `generate_answer()` programmatically deduplicates the source filenames from the retrieved chunks and appends a "Retrieved from" list regardless of whether the LLM remembered to cite them. This means attribution is guaranteed by the code, not left solely to the model. When tested with an out-of-scope question ("What is the average salary for Rutgers CS graduates?"), the system correctly declined to answer rather than generating a plausible-sounding salary figure from training data.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Professor Srikanta's organization and grading in his algorithms course? | Disorganized lectures, no posted notes/solutions, proof-heavy exams, students feeling ridiculed; some positive: lenient partial credit, 30% A curve | Mentioned "disorganized" lectures and "lenient partial credit" but omitted proof-heavy exams, ridiculed students, and the A curve | Partially relevant (pulled Szegedy chunks alongside Srikanta's) | Partially accurate |
| 2 | What is the workload breakdown for CS527 (Database Systems for Data Science)? | Projects 40%, Midterm+Final 50%, HW/Quizzes 10%; two semester-long projects; suitable for first-year MS students | Returned Projects 40% and Exams 50% but missed HW/Quizzes 10%, the two project descriptions, and first-year suitability note | Relevant | Partially accurate |
| 3 | Which professor should I take for Intro to AI — Boularias or Kulikowski? | Boularias strongly preferred (4.8/5, 97% would take again); Kulikowski rated 2.6/5, easy A but nothing learned | Correctly recommended Boularias; cited 97% stat and "easy A but no feedback" for Kulikowski; mentioned CS536 downstream risk | Relevant | Accurate |
| 4 | What prerequisites do I need before taking CS536 (Machine Learning)? | CS520 or CS530 required; strong linear algebra, probability, and calculus expected; course is math-heavy | Correctly identified CS520/CS530 requirement; missed the math skills prereqs (linear algebra, probability, calculus) | Relevant | Partially accurate |
| 5 | Is Mario Szegedy a reliable professor — does he show up to class? | Multiple reviews report missed classes and he did not attend his own final exam; final worth 40% | Correctly cited "unreliable professor" and "missed first month"; did not surface the missed-final-exam detail | Relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**
"What do students say about Professor Srikanta's organization and grading in his algorithms course?" (Q1)

**What the system returned:**
The answer correctly mentioned "disorganized" lectures and "lenient partial credit" but omitted the most specific and useful content from the documents: that students reported being ridiculed when asking questions, that no notes or homework solutions were ever posted, that exams are proof-heavy, and that at least 30% of the class receives an A. The sources list included `professor_mario_szegedy.txt` — a different professor — suggesting retrieval cross-contaminated from the wrong document.

**Root cause (tied to a specific pipeline stage):**
The failure has two causes, both in the retrieval stage. First, chunk 0 of `professor_karthik_srikanta.txt` is the metadata header (RMP rating, URL, course codes, research areas) — it matches the query semantically because it contains "Karthik Srikanta" and "algorithms," but it carries no student opinion content for the LLM to use. The richer review chunks (chunks 1–4) ranked lower in cosine similarity because individual review sentences don't repeat the professor's name — they say things like "Lectures are very disorganized" without context, so their embeddings are less similar to a query that includes "Professor Srikanta." Second, both Srikanta and Szegedy teach CS513/algorithms, so Szegedy's chunks share vocabulary ("algorithms," "CS344," "CS513") with the query, causing cross-document contamination. The LLM correctly avoided using the Szegedy content but had too little Srikanta review content to give a complete answer.

**What you would change to fix it:**
Two fixes would address this. First, inject professor name metadata into every chunk during ingestion — prepend "Professor: Karthik Srikanta\n" to each chunk from that file so review chunks embed with the professor's name in context, improving their cosine similarity to name-specific queries. Second, increase top-k from 5 to 7 or 8 for professor-specific queries, which would surface more of the review chunks even when the metadata header takes one slot.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The Anticipated Challenges section of `planning.md` called out the undergraduate/graduate course code mismatch (CS440 vs. 16:198:520, CS452 vs. 16:198:513) as a likely retrieval problem before any code was written. This led to a deliberate decision to cross-reference both code sets within every professor and course document — for example, `professor_karthik_srikanta.txt` explicitly notes that CS452 reviews apply to CS513. When retrieval was tested in Milestone 4, queries using graduate course codes successfully pulled chunks from documents that only contained undergraduate codes, because those cross-references were already in the text. Without the spec surfacing this challenge upfront, the documents would have contained only the codes from RMP (all undergraduate), and graduate queries would have failed silently.

**One way your implementation diverged from the spec, and why:**
The spec's preprocessing plan listed only `===` dividers and `-- heading --` patterns as noise to strip. During implementation, a third noise pattern emerged: `SECTION N — LABEL` lines (e.g., `SECTION 1 — STUDENT REVIEWS (Rate My Professors)`). These didn't appear in the planning spec because the template hadn't been finalized when planning.md was written. Once sample chunks were inspected during Milestone 3 verification, these label lines were clearly dominating some chunks — a chunk opening with `SECTION 2 — REDDIT MENTIONS (r/rutgers)` has an embedding pulled toward "section" and "reddit" rather than toward the actual content. A third regex pattern (`^SECTION \d+\s*[—–-]`) was added to `preprocess()` to handle them. The spec was updated in-place to reflect this change.

---

## AI Usage

**Instance 1 — Ingestion and chunking pipeline**

- *What I gave the AI:* The full Chunking Strategy section from `planning.md` (chunk size 500, overlap 100, rationale about review length) plus the complete text of `professor_abdeslam_boularias.txt` as a sample document.
- *What it produced:* Three functions — `preprocess()` stripping `===` and `-- --` patterns, `chunk_text()` with a character-based sliding window, and `ingest_documents()` returning a list of `{text, source, chunk_index}` dicts. The initial filter condition was `if chunk:`, which allowed any non-empty string through.
- *What I changed or overrode:* After running verification and finding a 25-character tail fragment (`'s (required track course)'`) in `course_527_database_systems.txt`, I changed the filter from `if chunk:` to `if len(chunk) >= 50:` to discard meaninglessly short fragments. I also directed the AI to add a third preprocessing rule for `SECTION N —` labels after inspecting sample chunks and finding them as noise.

**Instance 2 — Embedding and retrieval layer**

- *What I gave the AI:* The Retrieval Approach section from `planning.md` (all-MiniLM-L6-v2, ChromaDB, cosine similarity, top-k=5) plus the output schema from `ingest_documents()` (list of dicts with `text`, `source`, `chunk_index`).
- *What it produced:* `embed_and_store()` using `chromadb.Client(Settings(anonymized_telemetry=False))` and `retrieve()` returning top-k chunks with distance scores. The ChromaDB client initialization used the old `Settings` import pattern.
- *What I changed or overrode:* The `chromadb.Client(Settings(...))` pattern was deprecated in ChromaDB >= 0.4. I directed the AI to replace it with `chromadb.EphemeralClient()` and to suppress telemetry via an environment variable (`os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")`) instead of the Settings import, which is the correct API for the `>=0.6.0` version pinned in `requirements.txt`.
