"""
app.py — Gradio Web Interface
Rutgers MS CS Unofficial Guide

Run:
  python app.py
  → open http://localhost:7860

The pipeline (document loading + embedding) runs once at startup.
Each query triggers retrieval + grounded generation via Groq.
"""

import gradio as gr

from generate import build_pipeline, generate_answer

# ── Build the pipeline once when the app starts ───────────────────────────────
# This takes ~2–3 seconds (loads model, embeds 115 chunks, stores in ChromaDB).
# After this, each query is fast (~1–2s for Groq API round-trip).
print("Starting Rutgers MS CS Unofficial Guide...")
COLLECTION = build_pipeline()


# ── Query handler ─────────────────────────────────────────────────────────────

def handle_query(question: str):
    """
    Called by Gradio on every button click or Enter press.
    Returns (answer_text, sources_text) to populate the two output boxes.
    """
    question = question.strip()
    if not question:
        return "Please enter a question.", ""

    try:
        result = generate_answer(question, COLLECTION)
        answer = result["answer"]

        # Programmatic source list appended below the LLM answer
        # so attribution is guaranteed even if the LLM forgets to cite
        source_lines = "\n".join(f"• {s}" for s in result["sources"])

        return answer, source_lines

    except EnvironmentError as e:
        return f"⚠️ Configuration error:\n{e}", ""
    except Exception as e:
        return f"⚠️ Error: {e}", ""


# ── Gradio UI ─────────────────────────────────────────────────────────────────

DESCRIPTION = """
### Rutgers MS CS Unofficial Guide
Ask anything about MS CS courses and professors at Rutgers.
Answers are grounded in student reviews from Rate My Professors, Reddit (r/rutgers), and official course synopses.

**Example questions:**
- What do students say about Srikanta's grading?
- Should I take Boularias or Kulikowski for Intro to AI?
- What is the workload for CS527?
- Is Szegedy a reliable professor?
- What are the prerequisites for CS536?
"""

with gr.Blocks(title="Rutgers MS CS Unofficial Guide") as demo:
    gr.Markdown(DESCRIPTION)

    with gr.Row():
        with gr.Column(scale=3):
            question_box = gr.Textbox(
                label="Your question",
                placeholder="e.g. What do students say about Szegedy?",
                lines=2,
            )
        with gr.Column(scale=1):
            ask_btn = gr.Button("Ask", variant="primary")

    answer_box = gr.Textbox(
        label="Answer",
        lines=10,
        interactive=False,
    )

    sources_box = gr.Textbox(
        label="Retrieved from",
        lines=4,
        interactive=False,
        info="Documents the answer was drawn from",
    )

    # Wire up both button click and Enter key
    ask_btn.click(
        fn=handle_query,
        inputs=question_box,
        outputs=[answer_box, sources_box],
    )
    question_box.submit(
        fn=handle_query,
        inputs=question_box,
        outputs=[answer_box, sources_box],
    )

    gr.Markdown(
        "_Answers are generated from ~115 document chunks covering 5 Rutgers MS CS professors "
        "and 5 courses. Source documents are listed in planning.md._"
    )


if __name__ == "__main__":
    demo.launch()
