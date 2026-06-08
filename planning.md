# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Student reviews and course information for the MS CS program at Rutgers University. This knowledge is valuable because official course pages provide only abstract descriptions with no insight into workload, grading, or teaching quality — the information students actually need to make enrollment decisions. It is hard to find otherwise because it is scattered across Rate My Professors, Reddit threads, and individual professor websites, with no single source connecting professor reputation, course difficulty, grading breakdown, and peer survival tips in one place.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors — Karthik Srikanta | Student reviews of algorithms professor (CS452/513); 35 ratings, highly controversial | https://www.ratemyprofessors.com/professor/2842115 |
| 2 | Rate My Professors — Mario Szegedy | Student reviews of theory/complexity professor (CS344/513); 25 ratings, polarizing | https://www.ratemyprofessors.com/professor/52112 |
| 3 | Rate My Professors — Casimir Kulikowski | Student reviews of AI/biomedicine professor (CS440/520); 33 ratings, mostly negative | https://www.ratemyprofessors.com/professor/409364 |
| 4 | Rate My Professors — Ahmed Elgammal | Student reviews of machine learning professor (CS534/536); 31 ratings, mixed | https://www.ratemyprofessors.com/professor/184976 |
| 5 | Rate My Professors — Abdeslam Boularias | Student reviews of AI/robotics professor (CS440/520); 32 ratings, overwhelmingly positive | https://www.ratemyprofessors.com/professor/2041187 |
| 6 | Rutgers CS Grad Synopses + r/rutgers | Official description, workload, and peer discussion for CS513 (Algorithms I) | documents/course_513_algorithms.txt |
| 7 | Rutgers CS Grad Synopses + Elgammal site | Official description, workload, and peer discussion for CS536 (Machine Learning) | documents/course_536_machine_learning.txt |
| 8 | Rutgers CS Grad Synopses + r/rutgers | Official description and peer discussion for CS520 (Intro to AI); RMP cross-reference | documents/course_520_intro_ai.txt |
| 9 | Rutgers CS Grad Synopses (official) | Official description, full topic breakdown, and grading breakdown for CS527 (Database Systems) | documents/course_527_database_systems.txt |
| 10 | Rutgers CS Grad Synopses (official) | Official description, module breakdown, and project structure for CS543 (Massive Data + Deep Learning) | documents/course_543_massive_data.txt |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Reasoning:**
The corpus contains two distinct content types: short opinion reviews (150–300 characters each) and longer structured content like official course descriptions and workload breakdowns (400–600 characters). A 500-character chunk is large enough to capture one complete review plus a line of surrounding context (e.g., professor name and course), which is necessary for the embedding to be semantically meaningful — a review like "Lectures are very disorganized" is only useful if the chunk also contains "Karthik Srikanta" or "CS513." It is small enough that unrelated reviews don't merge into a single blob that would match too many queries indiscriminately.

Overlap of 100 characters handles the case where a multi-sentence review straddles a chunk boundary — without overlap, the second half of such a review would be an orphaned fragment with no context.

Before chunking, section dividers (`===`) and structural labels (`SECTION 1 —`, `Date: | Course: | Rating:`) will be stripped to prevent noise tokens from dominating chunk embeddings. Each chunk will be tagged with metadata: source filename and chunk index, so retrieved results can be traced back to a specific professor or course document.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 5

**Why these choices:** `all-MiniLM-L6-v2` produces 384-dimensional embeddings, handles short opinion text well, and fits within its 512-token limit comfortably given our 500-character chunk size. It is fast enough for a local prototype with a small corpus (~100–150 total chunks across 10 documents). The vector store is ChromaDB with cosine similarity.

Top-k of 5 retrieves approximately 2,500 characters of context per query — enough for the LLM to synthesize an answer that draws from both a professor file and its corresponding course file (e.g., retrieving both Boularias's teaching style and CS520's official description for a question about that course). Setting top-k lower (2–3) risks missing relevant context when a question spans multiple documents; setting it higher (10+) risks pulling in loosely related chunks from other professors or courses that dilute the answer.

**Production tradeoff reflection:**
In a real deployment, I would consider `text-embedding-3-small` (OpenAI) or `instructor-xl` for better semantic capture of domain-specific terminology — phrases like "NP-completeness," "PAC-learning," or "Bayesian networks" are treated as unknown tokens by general-purpose small models. I would also evaluate whether the undergrad/grad course code mismatch (CS440 vs. 16:198:520) degrades recall, and consider a hybrid retrieval approach (BM25 + semantic) to catch exact course code matches that pure embedding search misses. Latency is not a constraint for this prototype since it runs locally, but a hosted API embedding model would be faster for real users at scale.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Professor Srikanta's organization and grading in his algorithms course? | Reviews describe disorganized lectures, no posted notes or solutions, proof-heavy exams, and students feeling ridiculed; some positive reviews note lenient partial credit and a 30% A curve |
| 2 | What is the workload breakdown for CS527 (Database Systems for Data Science)? | Projects 40%, Midterm+Final 50%, HW/Quizzes 10%; two semester-long projects (web app + MongoDB data cleaning); suitable for first-year MS students |
| 3 | Which professor should I take for Intro to AI — Boularias or Kulikowski? | Boularias is overwhelmingly preferred (97% would take again, 4.8/5); Kulikowski is rated 2.6/5 with 10% would-take-again — students say easy grade but nothing learned |
| 4 | What prerequisites do I need before taking CS536 (Machine Learning)? | Must complete CS520 (Intro to AI) or CS530 (Principles of AI) first; strong linear algebra, probability, and calculus are expected; course is math-heavy |
| 5 | Is Mario Szegedy a reliable professor — does he show up to class? | Multiple 2025–2026 reviews report he missed significant portions of the semester and did not attend his own final exam; final exam worth 40% of grade |

---

## Anticipated Challenges

1. **Structural noise embedded as signal.** The documents contain section dividers (`===`), metadata labels (`RMP OVERALL RATING:`, `Date: | Course: | Rating:`), and instructional comments that were part of the template. If these are not stripped before chunking, the embedding model will treat them as content. A chunk containing mostly `================================================================` and `SECTION 2 — WORKLOAD & GRADING (official)` will have a meaningless embedding that could surface for unrelated queries. Mitigation: write a preprocessing step that strips lines matching divider patterns before passing text to the chunker.

2. **Undergraduate/graduate course code mismatch degrades recall.** All five professor review files contain reviews that reference undergraduate course codes (CS440, CS452, CS344) because those are the courses students actually reviewed on RMP. Graduate users will query using graduate codes (16:198:520, 16:198:513). The embedding model has no built-in knowledge that CS440 and 16:198:520 are the same course. A query like "what do students say about CS520?" may fail to retrieve Boularias reviews that only mention "CS440." Mitigation: each professor and course document explicitly cross-references both code sets (already done in the files), so chunks containing those cross-references will bridge the gap — but this should be verified during evaluation.

---

## Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌───────────────────────────┐
│  Document Ingestion │     │       Chunking        │     │  Embedding + Vector Store │
│                     │     │                       │     │                           │
│  Read all .txt      │────▶│  Strip noise lines    │────▶│  all-MiniLM-L6-v2         │
│  files from         │     │  chunk_text()         │     │  (sentence-transformers)  │
│  /documents/        │     │  500 chars            │     │                           │
│                     │     │  100 char overlap     │     │  ChromaDB collection      │
│  Python (pathlib)   │     │  + metadata tagging   │     │  cosine similarity        │
└─────────────────────┘     └──────────────────────┘     └───────────────────────────┘
                                                                        │
                                                                        ▼
                                                          ┌─────────────────────────┐
                                                          │        Retrieval        │
                                                          │                         │
                                                          │  User query embedded    │
                                                          │  ChromaDB similarity    │
                                                          │  search, top-k = 5      │
                                                          └─────────────────────────┘
                                                                        │
                                                                        ▼
                                                          ┌─────────────────────────┐
                                                          │       Generation        │
                                                          │                         │
                                                          │  Groq API               │
                                                          │  (llama-3.3-70b)        │
                                                          │  Grounded system prompt │
                                                          │  + retrieved chunks     │
                                                          │  → answer to user       │
                                                          └─────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
Tool: Claude. Input: the Chunking Strategy section of this file + the full text of `documents/professor_abdeslam_boularias.txt` as a sample document. Ask Claude to implement two functions: `preprocess(text)` that strips divider lines and structural labels, and `chunk_text(text, chunk_size=500, overlap=100)` that returns a list of character-sliced strings. Also ask it to implement `ingest_documents(docs_dir)` that reads every `.txt` file in a directory, runs preprocess + chunk_text on each, and returns a list of dicts with keys `text`, `source`, and `chunk_index`. Verify by printing the first 5 chunks of one document and checking that no chunk starts with `===` and that chunk lengths are within the expected range.

**Milestone 4 — Embedding and retrieval:**
Tool: Claude. Input: the Retrieval Approach section of this file + the output schema from `ingest_documents()` (list of dicts with `text`, `source`, `chunk_index`). Ask Claude to implement `embed_and_store(chunks)` that initializes a ChromaDB in-memory collection, embeds each chunk using `sentence-transformers/all-MiniLM-L6-v2`, and upserts with metadata. Also implement `retrieve(query, collection, k=5)` that embeds the query and returns the top-k matching chunks with their source filenames. Verify by running evaluation question 5 ("Is Mario Szegedy reliable?") and checking that at least 2 of the 5 returned chunks come from `professor_mario_szegedy.txt`.

**Milestone 5 — Generation and interface:**
Tool: Claude. Input: the full `planning.md` + the `retrieve()` function signature from Milestone 4. Ask Claude to implement `generate_answer(query, collection)` that calls `retrieve()`, formats the chunks into a context block, and calls the Groq API with a system prompt that instructs the model to answer only from the provided context and to cite the source document for each claim. Verify by running all 5 evaluation plan questions and checking responses against expected answers.
