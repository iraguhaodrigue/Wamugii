"""
AI Foundations -- full 4-week course (24 lessons, about 20 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content ai_foundations

It replaces the short 9-lesson version created by seed_ai_foundations.py:
the old lessons are hidden, students keep their enrolment.
"""

from app.course_content.lectures import attach
from app.course_content.af_exam import EXAM
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
    # Final exam: these questions plus every lesson-quiz question (as single answer).
    "exam": EXAM,
}

# "Go deeper" full lectures under the short videos (see lectures.py).
attach(COURSE, {
    "Defining AI: AI, Machine Learning and Deep Learning": ["cs50_ai_2020"],
    "A Short History of AI": ["cs50x_ai_2024"],
    "Intelligent Agents and Environments": ["cs50_knowledge"],
    "The Types of AI Problems": ["cs50_learning"],
    "Search and Problem Solving": ["cs50_search"],
    "Week 1 Project: Analyse an AI System": ["cs50x_ai_2026"],
    "Data: Features, Labels and Quality": ["stanford_ml1"],
    "The Machine-Learning Workflow": ["stanford_ml1"],
    "Supervised Learning": ["cs50_learning"],
    "Unsupervised Learning": ["cs50_learning"],
    "Reinforcement Learning": ["cs50_learning"],
    "Training, Testing and Overfitting": ["cs50_learning"],
    "Neural Networks Explained": ["cs50_nn", "mit_dl"],
    "How Neural Networks Learn": ["mit_dl"],
    "Transformers and Large Language Models": ["karpathy_llm", "cs50_language"],
    "Bias and Fairness": ["cc_bias"],
    "Privacy, Security and Safety": ["karpathy_llm"],
})
