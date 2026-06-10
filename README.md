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

## Sample Chunks

Five representative chunks drawn from the corpus, showing the range of content types:

**Chunk 1 — source: `course_513_algorithms.txt` (chunk 15)**
```
final grade distribution… Final is worth 40%" — grade drop at end of semester common
- Professor matters enormously for this course — check the schedule before registering
- Srikanta: proof-heavy, disorganized lectures but lenient partial credit; use TA office hours heavily
- Szegedy: brilliant but low engagement; self-study from CLRS or MIT OCW 6.006/6.046; practice exams match real exams
```
*Type: course survival tips synthesized from RMP + Reddit — references both professors and their trade-offs.*

**Chunk 2 — source: `professor_mario_szegedy.txt` (chunk 5)**
```
Rating: 1/5 | Difficulty: 4/5
"Really unreliable professor. He missed the first month of classes… lectures are okay,
homework isn't too bad. But I wouldn't recommend him to anyone."
Thread: "How is Mario Szegedy for Comp Algo?"
Username: CellistInternational — "Good. You won't fail. Unless you don't try."
Username: Realistic_West_5862 — "nah bro wtf you mean. First day in class bro went off topic
and gave the most bullshit assignment…"
```
*Type: mixed RMP review + Reddit thread about the same professor — captures both sentiment types in one chunk.*

**Chunk 3 — source: `professor_abdeslam_boularias.txt` (chunk 8)**
```
NOTES:
97% would take again — the highest in this profile set by a wide margin. Boularias is the
consensus best professor for CS440/CS520 at Rutgers. If he is listed as instructor for Intro
to AI in the semester you're enrolling, take it. The course is genuinely challenging (classical
AI: search, CSP, Bayesian networks, planning) but his teaching makes the difficulty feel
worthwhile. For MS students, this is the version of CS520 that actually prepares you for
CS536 (Machine Learning).
```
*Type: aggregated editorial note synthesizing rating stats and cross-course implication.*

**Chunk 4 — source: `course_520_intro_ai.txt` (chunk 13)**
```
- WHO teaches this course is the single most important variable — same content, wildly different experience
- If Boularias is teaching: take it immediately, brush up on linear algebra and probability first
- If Kulikowski is teaching: easy grade but you will not learn the AI foundations needed for CS536 (ML)
- CS520 is a prerequisite for CS536 (Machine Learning) — treat it seriously if ML is your goal
```
*Type: direct student advice comparing two instructors teaching the same course.*

**Chunk 5 — source: `professor_karthik_srikanta.txt` (chunk 0)**
```
PROFESSOR PROFILE — Karthik Srikanta
Rutgers University, Department of Computer Science
NAME: Karthik Srikanta
TITLE: Assistant Professor
RESEARCH AREAS: Theory of Computing, Algorithms, Complexity, Combinatorics
RMP OVERALL RATING: 3.8 / 5.0
RMP DIFFICULTY: 3.2 / 5.0
RMP WOULD TAKE AGAIN: 69%
RMP TOTAL RATINGS: 35
COURSES KNOWN FOR TEACHING:
- 16:198:513 — Design & Analysis of Data Structures & Algorithms I
- 01:198:452 — Formal Language & Automata Theory (undergraduate)
```
*Type: metadata header chunk — contains rating stats and course codes but no review opinions. This chunk illustrates the retrieval limitation described in the Failure Case Analysis section.*

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

This model produces 384-dimensional embeddings, handles short opinion text well, and fits within its 512-token context limit comfortably given the 500-character chunk size (~125 tokens). It runs locally with no API key and no rate limits, which makes it appropriate for a prototype with ~115 total chunks. The vector store is ChromaDB with cosine similarity (`hnsw:space: cosine`), so distance scores range from 0 (identical) to 1 (unrelated). All top results in evaluation scored below 0.52.

**Production tradeoff reflection:**
In a real deployment, I would evaluate `text-embedding-3-small` (OpenAI) or `instructor-xl` for better semantic capture of domain-specific terminology. Phrases like "NP-completeness," "PAC-learning," and "Bayesian networks" are treated as unknown tokens by general-purpose small models, which can weaken retrieval precision for technical course content. I would also evaluate whether the undergrad/grad course code mismatch (CS440 vs. 16:198:520) degrades recall, and consider a hybrid retrieval approach (BM25 + semantic) to catch exact course code matches that pure embedding search can miss. For multilingual support or international student communities, a multilingual-e5 model would be worth benchmarking. Latency is not a constraint for this local prototype, but an API-hosted model would matter for real users at scale.

---

## Retrieval Test Results

Three evaluation queries run against the 115-chunk ChromaDB collection using cosine similarity (distance: lower = more similar; < 0.5 is good).

---

**Query A:** *"What do students say about Professor Srikanta's organization and grading in his algorithms course?"*

| Rank | Source | Chunk index | Distance |
|------|--------|-------------|----------|
| 1 | course_513_algorithms.txt | 15 | 0.3535 |
| 2 | professor_karthik_srikanta.txt | 0 | 0.4000 |
| 3 | professor_mario_szegedy.txt | 1 | 0.4045 |
| 4 | course_513_algorithms.txt | 9 | 0.4310 |
| 5 | professor_mario_szegedy.txt | 2 | 0.4459 |

*Why the top results are relevant:* Result 1 (distance 0.35) is the survival tips chunk from the course file that explicitly names "Srikanta: proof-heavy, disorganized lectures but lenient partial credit" — it directly answers the query. Result 2 is Srikanta's profile header, which matched because it contains his name and course codes. Results 3 and 5 (Szegedy) are cross-contamination: both professors teach CS513/algorithms, so Szegedy's chunks share vocabulary with the query. Their distances (0.40, 0.45) are meaningfully higher than Result 1, confirming the correct document ranked first — but the contamination still consumed two of five slots.

---

**Query B:** *"Which professor should I take for Intro to AI — Boularias or Kulikowski?"*

| Rank | Source | Chunk index | Distance |
|------|--------|-------------|----------|
| 1 | professor_abdeslam_boularias.txt | 8 | 0.4313 |
| 2 | course_520_intro_ai.txt | 13 | 0.4550 |
| 3 | course_520_intro_ai.txt | 4 | 0.4698 |
| 4 | professor_casimir_kulikowski.txt | 8 | 0.5062 |
| 5 | course_520_intro_ai.txt | 12 | 0.5108 |

*Why the top results are relevant:* Results 1–3 directly address the comparison. Result 1 is the "NOTES" section of Boularias's profile ("consensus best professor for CS440/CS520 at Rutgers"). Result 2 is the course_520 survival tips chunk that explicitly compares both professors side-by-side. Result 3 is the workload comparison table broken out by instructor. Results 4–5 cross the 0.5 threshold but are still on-topic — they discuss Kulikowski's effect on CS536 readiness, which is adjacent to the question.

---

**Query C:** *"Is Mario Szegedy a reliable professor — does he show up to class?"*

| Rank | Source | Chunk index | Distance |
|------|--------|-------------|----------|
| 1 | professor_mario_szegedy.txt | 5 | 0.3779 |
| 2 | professor_mario_szegedy.txt | 0 | 0.4357 |
| 3 | course_513_algorithms.txt | 14 | 0.4381 |
| 4 | course_520_intro_ai.txt | 8 | 0.4669 |
| 5 | course_513_algorithms.txt | 13 | 0.4800 |

3 of the top 5 results come from Szegedy's own documents. Result 1 (distance 0.38) contains the most direct evidence: "Really unreliable professor. He missed the first month of classes." This query passed the planning.md checkpoint of ≥ 2 results from the correct source file.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt instructs the model with explicit numbered rules:

> "Answer ONLY using information found in the provided documents below. Do not use any knowledge from your training data, even if you are confident it is correct. For every factual claim in your answer, cite the source document in parentheses, e.g. (source: professor_mario_szegedy.txt). If the provided documents do not contain enough information to answer the question, respond with exactly: 'I don't have enough information in my documents to answer that.' Do not speculate, infer, or generalize beyond what the documents explicitly state."

Temperature is set to 0.2 to reduce creative generation and keep the model close to the retrieved text. Each chunk in the user message is prefixed with its source filename (e.g., `[Document 1 — source: professor_karthik_srikanta.txt]`) so the model always knows which document a piece of information came from before it generates a citation.

**How source attribution is surfaced in the response:**

Attribution works at two levels. First, the LLM is instructed to cite source filenames inline within its answer. Second, `generate_answer()` programmatically deduplicates the source filenames from the retrieved chunks and appends a "Retrieved from" list regardless of whether the LLM remembered to cite them. This means attribution is guaranteed by the code, not left solely to the model. When tested with an out-of-scope question ("What is the average salary for Rutgers CS graduates?"), the system correctly declined to answer rather than generating a plausible-sounding salary figure from training data.

---

## Example Responses

**Response 1 — grounded answer with inline citations**

> **Query:** Which professor should I take for Intro to AI — Boularias or Kulikowski?
>
> **Answer:** You should take Boularias for Intro to AI. Boularias is considered the best professor for CS440/CS520 at Rutgers (source: professor_abdeslam_boularias.txt), and students who take his class genuinely learn the material (source: course_520_intro_ai.txt, professor_casimir_kulikowski.txt). In contrast, Kulikowski's class is described as an "easy A" but with "no substantive feedback" and "low effort" (source: course_520_intro_ai.txt, professor_casimir_kulikowski.txt), which can be damaging for MS students who need the AI foundations for CS536 (Machine Learning) (source: professor_casimir_kulikowski.txt).
>
> **Retrieved from:**
> - professor_abdeslam_boularias.txt
> - course_520_intro_ai.txt
> - professor_casimir_kulikowski.txt

Every claim in the answer cites its source document inline. The "Retrieved from" list is generated programmatically from the retrieved chunks, independent of the LLM's citation behavior.

---

**Response 2 — grounded answer with inline citations**

> **Query:** Is Mario Szegedy a reliable professor — does he show up to class?
>
> **Answer:** According to the documents, Mario Szegedy is described as a "Really unreliable professor" who "missed the first month of classes" (source: professor_mario_szegedy.txt). Additionally, a student reported that on the "first day in class bro went off topic" (source: professor_mario_szegedy.txt), which further suggests that he may not be reliable in terms of showing up to class or staying on topic.
>
> **Retrieved from:**
> - professor_mario_szegedy.txt
> - course_513_algorithms.txt
> - course_520_intro_ai.txt

---

**Response 3 — out-of-scope query showing refusal**

> **Query:** What is the average salary for Rutgers CS graduates?
>
> **Answer:** I don't have enough information in my documents to answer that. Try asking about a professor or course covered in the guide.
>
> **Retrieved from:**
> - course_527_database_systems.txt
> - course_543_massive_data.txt
> - professor_abdeslam_boularias.txt
> - course_536_machine_learning.txt
> - course_513_algorithms.txt

The system retrieved the closest available documents (course files) but correctly declined to answer because none contained salary information. The LLM did not generate a plausible salary figure from training data — grounding held.

---

## Query Interface

The interface is a Gradio web app (`app.py`) running at `http://localhost:7860`.

**Input field:** A single text box labeled "Your question." Accepts any free-text question; submits on Enter or button click.

**Output fields:**
- *Answer* — the LLM's grounded response with inline source citations (e.g., `(source: professor_mario_szegedy.txt)`). 8-line text box, read-only.
- *Retrieved from* — a programmatic list of the source filenames whose chunks were retrieved for this query, one per line with a bullet prefix. 4-line text box, read-only. This list is always present regardless of whether the LLM cited sources in its answer.

**Sample interaction transcript:**

```
User input: What is the workload breakdown for CS527?

Answer:
The workload breakdown for CS527 (Database Systems for Data Science) is:
Projects 40% | Exams 50% (source: course_527_database_systems.txt).

Retrieved from:
• course_527_database_systems.txt
• course_543_massive_data.txt
```

The pipeline on each query: the question is embedded with `all-MiniLM-L6-v2`, the top-5 most similar chunks are retrieved from ChromaDB, the chunks are formatted into a labeled context block, and the Groq API (`llama-3.3-70b-versatile`, temperature 0.2) generates a grounded answer. Total latency per query is approximately 1–2 seconds.

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
