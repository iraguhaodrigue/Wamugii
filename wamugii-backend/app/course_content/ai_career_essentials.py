"""
AI Career Essentials -- full 4-week course (24 lessons, about 19 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content ai_career_essentials
"""

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
}
