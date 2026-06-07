# Deep Research Prompt — Rutgers MS CS Unofficial Guide
Use this prompt with ChatGPT Deep Research or Gemini Deep Research.
Two runs total: Run 1 for all professors, Run 2 for all courses.

---

## RUN 1 — ALL 5 PROFESSORS (copy everything between the triple backticks)

```
You are a research assistant helping build an "Unofficial Guide" for Rutgers University's MS CS program.
The guide is a RAG (Retrieval-Augmented Generation) system that answers questions like:
"Is Professor X a good teacher?", "How hard is CS 513?", "What's the workload like for Machine Learning?"

Research ALL 5 of the following Rutgers CS professors. Return a fully separate output block for each one.
Do NOT fabricate reviews. Do NOT summarize from memory. Only report what you actually find via web search.

PROFESSORS TO RESEARCH:
1. Karthik Srikanta — Rutgers CS (algorithms, CS 513/514)
2. Mario Szegedy — Rutgers CS (theory of computing, CS 509/538)
3. Casimir Kulikowski — Rutgers CS (AI / biomedicine, CS 520/530)
4. Ahmed Elgammal — Rutgers CS (machine learning, CS 536)
5. Abdeslam Boularias — Rutgers CS (robotics / AI, CS 560/562)

---

### SOURCES TO SEARCH FOR EACH PROFESSOR (in this order)

1. **Rate My Professors** — ratemyprofessors.com
   - Search each professor by name at Rutgers University
   - Retrieve: overall rating, difficulty score, "would take again" %, total # of ratings
   - Copy 6–10 verbatim student reviews (include date and course name if shown)
   - Include both positive AND negative reviews — do not cherry-pick

2. **Reddit — r/rutgers** — reddit.com/r/rutgers
   - Search queries to try for each professor:
     - "[professor last name] rutgers"
     - "[professor last name] CS rutgers grad"
   - Copy verbatim excerpts from relevant comments/posts
   - Include thread title, URL, username (if not deleted), and approximate date

3. **Official Rutgers CS department page** — cs.rutgers.edu/people/professors
   - Retrieve: title, research areas, courses listed, personal/lab website URL

4. **Professor's personal or course website** (if publicly accessible)
   - Look for syllabi, grading breakdowns, office hours

---

### OUTPUT FORMAT — repeat this block for each of the 5 professors

#### ══ PROFESSOR: [Name] ══

BASIC INFO
- RMP URL:
- RMP Rating: X.X/5 | Difficulty: X.X/5 | Would Take Again: XX% | Total Ratings: XX
- Title & Research Areas (from cs.rutgers.edu):
- Courses known for teaching:

RMP REVIEWS (6–10 verbatim, positive and negative)
Date: | Course: | Rating: /5 | Difficulty: /5
"[verbatim quote]"
[repeat]

REDDIT EXCERPTS
Thread: [title] | URL: [link] | User: [username] | Date: [approx]
"[verbatim excerpt]"
[repeat]

ANYTHING ELSE NOTABLE
[Patterns, warnings, standout praise, office hours reputation, etc.]

---

### RULES
- Only include information actually found via web search — cite every source
- Verbatim quotes must be exact — do not paraphrase reviews
- If a source has no results, write "No results found on [source]" — do not skip or hallucinate
- If RMP has fewer than 6 reviews, include all of them
- Flag reviews that may be about a different course with [POSSIBLY WRONG COURSE]
```

---

## RUN 2 — ALL 5 COURSES (copy everything between the triple backticks)

```
You are a research assistant helping build an "Unofficial Guide" for Rutgers University's MS CS program.
The guide is a RAG (Retrieval-Augmented Generation) system that answers questions like:
"How hard is CS 513?", "What's the workload like for Machine Learning?", "Who teaches CS 527?"

Research ALL 5 of the following Rutgers MS CS graduate courses. Return a fully separate output block for each one.
Do NOT fabricate reviews. Do NOT summarize from memory. Only report what you actually find via web search.

COURSES TO RESEARCH:
1. 16:198:513 — Design & Analysis of Data Structures & Algorithms I
2. 16:198:536 — Machine Learning
3. 16:198:520 — Introduction to Artificial Intelligence
4. 16:198:527 — Database Systems for Data Science
5. 16:198:543 — Massive Data Storage, Retrieval and Deep Learning

---

### SOURCES TO SEARCH FOR EACH COURSE (in this order)

1. **Official Rutgers CS course synopses** — cs.rutgers.edu
   - URL: https://www.cs.rutgers.edu/academics/graduate/m-s-program/course-synopses
   - Retrieve: official description, prerequisites, credits, semester offered, MS category (A or B)
   - Also check: https://www.cs.rutgers.edu/academics/graduate/m-s-program/graduate-courses-schedule for current professor

2. **Professor's course website or syllabus** (search "[course code] rutgers syllabus" or "[course name] rutgers cs")
   - Look for: grading breakdown (HW/exam/project weights), grading scale, textbooks, weekly schedule

3. **Rate My Professors** — ratemyprofessors.com
   - Search for the professor(s) who teach this course at Rutgers
   - Filter/look for reviews that mention this specific course code or name
   - Copy verbatim reviews that reference this course

4. **Reddit — r/rutgers** — reddit.com/r/rutgers
   - Search queries to try:
     - "[course code] rutgers" (e.g., "CS 513 rutgers" or "16:198:513")
     - "[course name] rutgers grad"
     - "[course code] review rutgers ms"
   - Copy verbatim excerpts from relevant comments/posts
   - Include thread title, URL, username (if not deleted), and approximate date

---

### OUTPUT FORMAT — repeat this block for each of the 5 courses

#### ══ COURSE: [Code] — [Name] ══

BASIC INFO
- Official page URL:
- Credits:
- MS Category (A or B):
- Semester(s) offered:
- Prerequisites:
- Professor(s) who teach it:

OFFICIAL DESCRIPTION (verbatim from cs.rutgers.edu)
[paste here]

WORKLOAD & GRADING (from syllabus or student reports)
- Homework: [weight % and frequency]
- Exams: [midterm/final format]
- Projects: [if any]
- Grading scale: [if published]
- Curve policy: [if known]
- Estimated hours/week: [student-reported]

STUDENT REVIEWS MENTIONING THIS COURSE (verbatim, from RMP or Reddit)
Source: [RMP / Reddit]
"[verbatim quote]"
[repeat]

REDDIT DISCUSSION THREADS
Thread: [title] | URL: [link] | User: [username] | Date: [approx]
Key excerpt: "[verbatim]"
[repeat]

GRADE DISTRIBUTION (if found anywhere)
Source:
Data:

TIPS & SURVIVAL NOTES
[Practical patterns from reviews: difficulty level, what trips people up, what helps, etc.]

---

### RULES
- Only include information actually found via web search — cite every source
- Verbatim quotes must be exact — do not paraphrase reviews
- If a source has no results, write "No results found on [source]" — do not skip or hallucinate
- Flag reviews that may be about a different course with [POSSIBLY WRONG COURSE]
```

---

## FILE MAPPING — where to paste each result

| Output block | Paste into file |
|-------------|----------------|
| Professor: Karthik Srikanta | `professor_karthik_srikanta.txt` |
| Professor: Mario Szegedy | `professor_mario_szegedy.txt` |
| Professor: Casimir Kulikowski | `professor_casimir_kulikowski.txt` |
| Professor: Ahmed Elgammal | `professor_ahmed_elgammal.txt` |
| Professor: Abdeslam Boularias | `professor_abdeslam_boularias.txt` |
| Course: 16:198:513 | `course_513_algorithms.txt` |
| Course: 16:198:536 | `course_536_machine_learning.txt` |
| Course: 16:198:520 | `course_520_intro_ai.txt` |
| Course: 16:198:527 | `course_527_database_systems.txt` |
| Course: 16:198:543 | `course_543_massive_data.txt` |

## IF A SOURCE GETS SKIPPED
If the AI doesn't search Reddit, follow up with:
"You did not search Reddit. Please search r/rutgers for [professor name / course code] and add those results."
