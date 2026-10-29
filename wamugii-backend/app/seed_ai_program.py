"""
Load the ENTIRE WAMUGII AI Program in one command.

Runs every course seed in order. Each one is idempotent (it skips a course that
already exists), so this is safe to run more than once and safe to run even if
some courses are already loaded.

Run inside the backend container:

    docker exec wamugii-backend python -m app.seed_ai_program
"""

from app import (
    seed_courses,                 # Course 0: AI Career Essentials (intro)
    seed_ai_foundations,          # Course 1: AI Foundations
    seed_ai_c2_math_python,       # Course 2: Math & Python for AI
    seed_ai_c3_ml_fundamentals,   # Course 3: Machine Learning Fundamentals
    seed_ai_c4_deep_learning,     # Course 4: Deep Learning & Neural Networks
    seed_ai_c5_llms_genai,        # Course 5: Modern AI: LLMs & Generative AI
    seed_ai_c6_responsible_deploy,  # Course 6: Responsible AI & Deployment
)

COURSES = [
    seed_courses,
    seed_ai_foundations,
    seed_ai_c2_math_python,
    seed_ai_c3_ml_fundamentals,
    seed_ai_c4_deep_learning,
    seed_ai_c5_llms_genai,
    seed_ai_c6_responsible_deploy,
]


def main() -> None:
    print("=" * 60)
    print("  Loading the WAMUGII AI Program")
    print("=" * 60)
    for module in COURSES:
        print(f"\n--- {module.__name__} ---")
        module.main()
    print("\n" + "=" * 60)
    print("  AI Program load complete. All courses are in the catalog.")
    print("=" * 60)


if __name__ == "__main__":
    main()
