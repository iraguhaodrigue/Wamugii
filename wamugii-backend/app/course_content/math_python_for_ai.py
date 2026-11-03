"""
Math & Python for AI -- full 4-week course (24 lessons, about 20 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content math_python_for_ai

It replaces the short 9-lesson version created by seed_ai_c2_math_python.py:
the old lessons are hidden, students keep their enrolment.
"""

from app.course_content.mp_week1 import WEEK1
from app.course_content.mp_week2 import WEEK2
from app.course_content.mp_week3 import WEEK3
from app.course_content.mp_week4 import WEEK4

COURSE = {
    "slug": "math-python-for-ai",
    "title": "Math & Python for AI",
    "category": "Artificial Intelligence",
    "display_order": 3,
    "is_free": True,
    "description": (
        "A complete 4-week, hands-on course in the two skills every AI builder needs: "
        "Python and the maths behind machine learning — explained in simple English. "
        "Week 1: Python basics — variables, lists, loops, decisions, functions and files. "
        "Week 2: working with data — NumPy, Pandas, cleaning, grouping and charts. "
        "Week 3: vectors, matrices, statistics, probability and the normal distribution. "
        "Week 4: Bayes' theorem, correlation, derivatives and gradient descent — then you "
        "build a linear regression model from scratch.\n\n"
        "Everything runs free in your browser with Google Colab — nothing to install. "
        "24 lessons, each with a video, notes with ready-to-run code, a downloadable handout "
        "and worksheet and a quiz, plus a hands-on project every week and a certificate of "
        "completion. Built by WAMUGII TECH SOLUTIONS for students and professionals in Rwanda "
        "and beyond."
    ),
    "modules": [WEEK1, WEEK2, WEEK3, WEEK4],
}
