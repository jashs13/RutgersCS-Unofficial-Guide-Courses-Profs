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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

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

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
