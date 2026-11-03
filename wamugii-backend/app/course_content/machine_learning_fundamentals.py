"""
Machine Learning Fundamentals -- full 4-week course (24 lessons, about 22 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content machine_learning_fundamentals

It replaces the short 9-lesson version created by seed_ai_c3_ml_fundamentals.py:
the old lessons are hidden, students keep their enrolment.
"""

from app.course_content.lectures import attach
from app.course_content.ml_exam import EXAM
from app.course_content.ml_week1 import WEEK1
from app.course_content.ml_week2 import WEEK2
from app.course_content.ml_week3 import WEEK3
from app.course_content.ml_week4 import WEEK4

COURSE = {
    "slug": "machine-learning-fundamentals",
    "title": "Machine Learning Fundamentals",
    "category": "Artificial Intelligence",
    "display_order": 4,
    "is_free": True,
    "description": (
        "A complete 4-week, hands-on course in classic machine learning with Python and "
        "scikit-learn — explained in simple English, with every line of code tested. "
        "Week 1: the scikit-learn workflow, encoding and scaling, linear and logistic "
        "regression and k-nearest neighbours. Week 2: decision trees, random forests, "
        "gradient boosting, support vector machines and Naive Bayes. Week 3: cross-validation, "
        "the confusion matrix, precision and recall, ROC curves and cost-based thresholds, "
        "bias, variance and regularisation, and hyperparameter tuning. Week 4: k-means "
        "clustering, PCA, feature engineering and pipelines, imbalanced data and fairness, "
        "and saving and monitoring models.\n\n"
        "Practise on Kigali rents, mobile-money micro-loans and real medical data — free in "
        "Google Colab, nothing to install. 24 lessons, each with a short video, a full "
        "lecture to go deeper, notes with ready-to-run code, a downloadable handout and a "
        "quiz, plus a project every week, a final exam and a certificate. Built by WAMUGII "
        "TECH SOLUTIONS for students and professionals in Rwanda and beyond."
    ),
    "modules": [WEEK1, WEEK2, WEEK3, WEEK4],
    # Final exam: these questions plus every lesson-quiz question (as single answer).
    "exam": EXAM,
}

# "Go deeper" full lectures under the short videos (see lectures.py).
attach(COURSE, {
    "What Machine Learning Really Is — and scikit-learn": ["ds_what_is_ml", "stanford_ml1", "fcc_sklearn"],
    "Preparing Data: Encoding and Scaling": ["ds_dummies", "scipy_sklearn_1"],
    "Linear Regression with scikit-learn": ["ds_regression", "fcc_ml_sklearn"],
    "Logistic Regression: Predicting Yes or No": ["cs50_learning", "fcc_ml_sklearn"],
    "k-Nearest Neighbours: Learning from Similar Cases": ["knn_talk", "ds_iris"],
    "Week 1 Project: Predict Rents in Kigali": ["ds_compare", "fcc_sklearn"],
    "Decision Trees: Models You Can Read": ["sq_tree2", "scipy_sklearn_2"],
    "Random Forests: The Wisdom of Many Trees": ["scipy_sklearn_2"],
    "Boosting: Learning from Mistakes": ["sq_adaboost", "scipy_sklearn_2"],
    "Support Vector Machines: The Widest Street": ["cs50_learning", "scipy_sklearn_1"],
    "Naive Bayes: Fast Probability Classifiers": ["cs50_uncertainty"],
    "Week 2 Project: Compare Models on Medical Data": ["fcc_ml_sklearn"],
    "Cross-Validation: Testing Without Luck": ["ds_cv", "scipy_sklearn_1"],
    "Confusion Matrix, Precision and Recall": ["sq_sens", "ds_eval"],
    "ROC Curves and Choosing a Threshold": ["ds_eval"],
    "Bias, Variance and Regularisation": ["sq_ridge", "stanford_ml1"],
    "Hyperparameter Tuning with Grid Search": ["scipy_sklearn_2", "fcc_sklearn"],
    "Week 3 Project: Build a Trustworthy Loan Model": ["ds_cv", "fcc_ml_sklearn"],
    "k-Means Clustering: Finding Customer Groups": ["cs50_learning", "scipy_sklearn_2"],
    "PCA: Seeing Many Features in Two": ["sq_pca_python", "fcc_linalg"],
    "Feature Engineering and Pipelines": ["scipy_sklearn_2"],
    "Imbalanced Data and Fairness": ["imbalance_talk", "fairness_talk", "fairness_measures"],
    "Final Project: An End-to-End Model and Certificate": ["fcc_sklearn", "scipy_sklearn_1"],
})
