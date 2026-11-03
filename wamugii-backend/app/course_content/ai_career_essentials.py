"""
AI Career Essentials -- full 4-week course (24 lessons, about 19 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content ai_career_essentials
"""

from app.course_content.lectures import attach
from app.course_content.ace_exam import EXAM
from app.course_content.ace_week1 import WEEK1
from app.course_content.ace_week2 import WEEK2
from app.course_content.ace_week3 import WEEK3
from app.course_content.ace_week4 import WEEK4

COURSE = {
    "slug": "ai-career-essentials",
    "title": "AI Career Essentials",
    "category": "Career & AI",
    "display_order": 1,
    "is_free": True,
    "description": (
        "A complete 4-week, practical course on using artificial intelligence to grow "
        "your career — no coding needed. Week 1: what AI is, how machines learn, how "
        "tools like ChatGPT work and where AI fails. Week 2: the right mindset, the "
        "main tools, and prompting skills that get real results. Week 3: AI for "
        "writing, research, spreadsheets, presentations and your own field. Week 4: "
        "privacy, ethics, the future of work, your portfolio and a 90-day career plan.\n\n"
        "24 lessons with videos, downloadable notes and worksheets, a quiz after every "
        "lesson, a hands-on project every week, and a certificate of completion. Built "
        "by WAMUGII TECH SOLUTIONS for students, business owners and professionals in "
        "Rwanda and beyond."
    ),
    "modules": [WEEK1, WEEK2, WEEK3, WEEK4],
    # Final exam: these questions plus every lesson-quiz question (as single answer).
    "exam": EXAM,
}

# "Go deeper" full lectures under the short videos (see lectures.py).
attach(COURSE, {
    "What AI Really Is (and Isn't)": ["cs50_ai_2020"],
    "How Machines Learn: Data, Patterns and Models": ["cs50_learning"],
    "Generative AI and Large Language Models": ["karpathy_llm"],
    "What AI Does Well — and Where It Fails": ["cs50_one_word"],
    "AI in Rwanda and Across Africa": ["fei_fei"],
    "The AI-Ready Mindset": ["cs50x_ai_2026"],
    "Core AI Tools for Everyday Work": ["cs50x_ai_2024"],
    "Prompting Like a Pro": ["cs50_writers"],
    "Advanced Prompting: Examples, Steps and Iteration": ["cs50_language"],
    "Checking AI's Work": ["cs50_editing"],
    "AI for Writing and Communication": ["cs50_writers"],
    "AI for Research and Learning": ["cs50_teaching_ai"],
    "Using AI in Your Field": ["cs50_law"],
    "Working Responsibly with AI": ["cc_bias"],
    "AI and the Future of Work": ["cs50_llm_programming"],
})
