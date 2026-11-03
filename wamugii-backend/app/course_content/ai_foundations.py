"""
AI Foundations -- full 4-week course (24 lessons, about 20 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content ai_foundations

It replaces the short 9-lesson version created by seed_ai_foundations.py:
the old lessons are hidden, students keep their enrolment.
"""

from app.course_content.af_week1 import WEEK1
from app.course_content.af_week2 import WEEK2
from app.course_content.af_week3 import WEEK3
from app.course_content.af_week4 import WEEK4

COURSE = {
    "slug": "ai-foundations",
    "title": "AI Foundations",
    "category": "Artificial Intelligence",
    "display_order": 2,
    "is_free": True,
    "description": (
        "A complete 4-week, university-level foundation in artificial intelligence — "
        "explained in simple English, with no coding needed. Week 1: what AI is, its "
        "history, intelligent agents, the types of AI problems and how search solves "
        "them. Week 2: data, the machine-learning workflow, and supervised, "
        "unsupervised and reinforcement learning. Week 3: training and testing, "
        "accuracy, precision and recall, neural networks, how they learn, and how "
        "transformers and large language models work. Week 4: bias and fairness, "
        "explainable AI, privacy and security (including Rwanda's data-protection law), "
        "AI governance (Rwanda's National AI Policy and the EU AI Act) and careers.\n\n"
        "24 lessons, each with a video, notes, a downloadable handout and worksheet and "
        "a quiz, plus a hands-on project every week and a certificate of completion. "
        "Built by WAMUGII TECH SOLUTIONS for students and professionals in Rwanda and beyond."
    ),
    "modules": [WEEK1, WEEK2, WEEK3, WEEK4],
}
