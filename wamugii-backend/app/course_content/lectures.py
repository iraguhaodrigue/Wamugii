"""
"Go deeper" full-lecture videos, attached to lessons by title.

Long, free lectures from respected teachers (Harvard CS50, MIT, Stanford,
freeCodeCamp, 3Blue1Brown, Andrej Karpathy, Crash Course). Every video ID was
checked against a public index of the channel before it was added. One long
lecture often covers several lessons' subtopics, so some appear more than once.
"""

YT = "https://www.youtube.com/watch?v="

# name -> (title shown to students, url, minutes or None)
L = {
    "cs50_ai_2020": ("Harvard CS50: Artificial Intelligence — full lecture", YT + "eey91kzfOZs", None),
    "cs50x_ai_2024": ("Harvard CS50x 2024: Artificial Intelligence — full lecture", YT + "6X58aP7yXC4", None),
    "cs50x_ai_2026": ("Harvard CS50x 2026: Artificial Intelligence — full lecture", YT + "-9bo8HlSxwQ", None),
    "cs50_search": ("Harvard CS50 AI, Lecture 0: Search", YT + "WbzNRTTrX0g", None),
    "cs50_knowledge": ("Harvard CS50 AI, Lecture 1: Knowledge", YT + "HWQLez87vqM", None),
    "cs50_uncertainty": ("Harvard CS50 AI, Lecture 2: Uncertainty (probability and Bayes)", YT + "D8RRq3TbtHU", None),
    "cs50_learning": ("Harvard CS50 AI, Lecture 4: Learning (supervised, reinforcement, unsupervised)", YT + "E4M_IQG0d9g", None),
    "cs50_nn": ("Harvard CS50 AI, Lecture 5: Neural Networks", YT + "mFZazxxCKbw", None),
    "cs50_language": ("Harvard CS50 AI, Lecture 6: Language (attention and transformers)", YT + "QAZc9xsQNjQ", None),
    "cs50_one_word": ("CS50 Seminar: How to Predict the Future with AI, One Word at a Time", YT + "NGEEN0BzH-s", None),
    "cs50_llm_programming": ("CS50 Tech Talk: Large Language Models and the End of Programming", YT + "JhCl-GeT4jw", None),
    "cs50_writers": ("CS50 Tech Talk with OpenAI: ChatGPT for Writers", YT + "ZeTeHYHOtuw", None),
    "cs50_editing": ("CS50 Tech Talk: Why You're Still Better Than AI at Editing Documents", YT + "FqB_4QY6x6g", None),
    "cs50_teaching_ai": ("Teaching CS50 with AI (2025): AI as a personal tutor", YT + "6rAWxGAG6EI", None),
    "cs50_law": ("Harvard: Understanding the Impact of AI on the Legal Profession", YT + "Y8UHDl2IJOM", None),
    "karpathy_llm": ("Andrej Karpathy: Intro to Large Language Models (1-hour talk)", YT + "zjkBMFhNj_g", 60),
    "mit_dl": ("MIT 6.S191: Introduction to Deep Learning (2024)", YT + "ErnWZxJovaM", None),
    "stanford_ml1": ("Stanford Machine Learning, Lecture 1 — Andrew Ng", YT + "UzxYlbK2c7E", None),
    "fei_fei": ("AI's Human Factor: Fei-Fei Li and Mira Murati", YT + "9B02MzWwkSo", None),
    "cc_bias": ("Crash Course AI: Algorithmic Bias and Fairness", YT + "gV0_raKR2UQ", None),
    "fcc_python": ("freeCodeCamp: Python for Beginners — full course", YT + "eWRfhZUzrAc", None),
    "fcc_data": ("freeCodeCamp: Data Analysis with Python (NumPy, Pandas, Matplotlib) — full course", YT + "r-uOLxNrNk8", None),
    "fcc_linalg": ("freeCodeCamp: Linear Algebra for Machine Learning — full course", YT + "rSjt1E9WHaQ", None),
    "fcc_stats": ("freeCodeCamp: Statistics — a full university course", YT + "xxpc-HPKN28", None),
    "3b1b_calculus": ("3Blue1Brown: The Essence of Calculus", YT + "WUvTyaaNkzM", None),
    # Machine Learning Fundamentals
    "fcc_sklearn": ("freeCodeCamp: scikit-learn — full course", YT + "pqNCD_5r0IU", None),
    "fcc_ml_sklearn": ("freeCodeCamp: Machine Learning with Python and scikit-learn — full course", YT + "hDKCxebp88A", None),
    "scipy_sklearn_1": ("SciPy 2018 tutorial: Machine Learning with scikit-learn, Part 1 (scikit-learn core developers)", YT + "4PXAztQtoTg", 205),
    "scipy_sklearn_2": ("SciPy 2018 tutorial: Machine Learning with scikit-learn, Part 2 (scikit-learn core developers)", YT + "gK43gtGh49o", 194),
    "ds_what_is_ml": ("Data School: What is machine learning, and how does it work?", YT + "elojMnjn4kk", 10),
    "ds_iris": ("Data School: Getting started in scikit-learn with the famous iris dataset", YT + "hd1W4CyPX58", 15),
    "ds_compare": ("Data School: Comparing machine learning models in scikit-learn", YT + "0pP4EwWJgIU", 27),
    "ds_regression": ("Data School: Data science in Python — pandas, seaborn and linear regression", YT + "3ZWuPVWq7p4", 34),
    "ds_cv": ("Data School: Selecting the best model using cross-validation", YT + "6dbrR-WymjI", 36),
    "ds_eval": ("Data School: How to evaluate a classifier in scikit-learn", YT + "85dtiMz9tSo", 55),
    "ds_grid": ("Data School: How to find the best model parameters (grid search)", YT + "Gol_qOgRqfA", 28),
    "ds_dummies": ("Data School: How do I create dummy variables in pandas?", YT + "0s_1IsROgDc", 13),
    "knn_talk": ("PyData: Know Thy Neighbor — an introduction to scikit-learn and k-NN", YT + "e3-DjsKhFug", 40),
    "sq_tree2": ("StatQuest: Decision Trees, Part 2 — feature selection and missing data", YT + "wpNl-JwwplA", None),
    "sq_adaboost": ("StatQuest: AdaBoost, Clearly Explained", YT + "LsK-xG1cLYA", None),
    "sq_ridge": ("StatQuest: Regularization Part 1 — Ridge (L2) Regression", YT + "Q81RR3yKn30", None),
    "sq_sens": ("StatQuest: Sensitivity and Specificity", YT + "vP06aMoz4v8", None),
    "sq_pca_python": ("StatQuest: PCA in Python", YT + "Lsue2gEM9D0", None),
    "imbalance_talk": ("PyCon Thailand: Addressing class imbalance in machine learning", YT + "rDR0egRhJ1Y", 26),
    "fairness_talk": ("PyCon 2019: Measuring Model Fairness", YT + "pYXz507ths0", 28),
    "fairness_measures": ("PyCon 2019: Measures and Mismeasures of Algorithmic Fairness", YT + "olCKhigTVuY", 38),
}


def attach(course: dict, mapping: dict[str, list[str]]) -> None:
    """Set each lesson's "lectures" from {lesson title: [lecture names]}."""
    titles = {l["title"] for m in course["modules"] for l in m["lessons"]}
    unknown = set(mapping) - titles
    if unknown:
        raise ValueError(f"lectures mapped to unknown lessons: {sorted(unknown)}")
    for module in course["modules"]:
        for lesson in module["lessons"]:
            names = mapping.get(lesson["title"], [])
            lesson["lectures"] = [L[n] for n in names]
