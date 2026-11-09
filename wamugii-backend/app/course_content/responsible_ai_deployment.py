"""
Responsible AI & Deployment (Capstone) -- full 4-week course (24 lessons, about 27 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content responsible_ai_deployment

It replaces the short 8-lesson version created by seed_ai_c6_responsible_deploy.py:
the old lessons are hidden, students keep their enrolment.
"""

from app.course_content.lectures import attach
from app.course_content.rai_exam import EXAM
from app.course_content.rai_week1 import WEEK1
from app.course_content.rai_week2 import WEEK2
from app.course_content.rai_week3 import WEEK3
from app.course_content.rai_week4 import WEEK4

COURSE = {
    "slug": "responsible-ai-deployment",
    "title": "Responsible AI & Deployment (Capstone)",
    "category": "Artificial Intelligence",
    "display_order": 7,
    "is_free": True,
    "description": (
        "The capstone course of the WAMUGII AI Program: take a model from a notebook to a "
        "responsible, working product — explained in simple English, with every line of code "
        "tested. Week 1: from notebook to product — model artifacts and metadata, reproducible "
        "training, serving a model with FastAPI, testing ML systems, and packaging with Docker. "
        "Week 2: MLOps — CI/CD and quality gates, experiment tracking and a model registry, "
        "monitoring, data drift and concept drift, and safe releases with shadow mode, canary "
        "and A/B tests. Week 3: fairness metrics and bias mitigation, explaining decisions, "
        "privacy under Rwanda's data-protection law, and security for AI systems, ending in a "
        "full responsible-AI audit. Week 4: AI governance and law, model cards and datasheets, "
        "human oversight, and your own end-to-end capstone project.\n\n"
        "One realistic story runs through the whole course: a loan-repayment model for a SACCO. "
        "Free in Google Colab — nothing to install, no API key needed. 24 lessons, each with a "
        "short video, full lectures to go deeper, notes with ready-to-run code, a downloadable "
        "handout and a quiz, plus a project every week, a final exam and a certificate. Built "
        "by WAMUGII TECH SOLUTIONS for students and professionals in Rwanda and beyond."
    ),
    "modules": [WEEK1, WEEK2, WEEK3, WEEK4],
    # Final exam: these questions plus every lesson-quiz question (as single answer).
    "exam": EXAM,
}

# "Go deeper" full lectures under the short videos (see lectures.py).
attach(COURSE, {
    "The Deployment Gap: From Notebook to Product": ["painless_ml_prod", "mit_wild_2024"],
    "Reproducible Machine Learning": ["reproducible_ml", "reproducible_experiments"],
    "Serving a Model with FastAPI": ["fastapi_keynote", "deploy_nlp_talk"],
    "Testing Machine Learning Systems": ["continuous_testing_ml", "painless_ml_prod"],
    "Packaging with Docker and Configuration": ["docker_best", "onnx_talk"],
    "Week 1 Project: A Tested Loan-Scoring Service": ["mlops_bridge", "docker_best"],
    "CI/CD for Machine Learning": ["can_we_deploy", "mlops_bridge"],
    "Experiment Tracking and the Model Registry": ["mlflow_gems", "mlflow_serverless"],
    "Monitoring Models in Production": ["logging_module", "continuous_testing_ml"],
    "Data Drift and Concept Drift": ["ml_monitoring", "continuous_testing_ml"],
    "Releasing Safely: Shadow Mode, Canary and A/B Tests": ["ab_python", "can_we_deploy"],
    "Week 2 Project: Monitor, Detect and Retrain": ["detecting_drift", "mlflow_lifecycle"],
    "Measuring Fairness": ["fairness_talk", "fairness_measures", "cc_bias"],
    "Where Bias Comes From and How to Reduce It": ["debias_ml", "fairness_measures"],
    "Explaining Model Decisions": ["interpretability_tutorial", "shap_beyond"],
    "Privacy and Data Protection": ["privacy_methods", "privacy_tools", "chatgpt_privacy"],
    "Security for AI Systems": ["poisoned_pickles", "liveoverflow_injection"],
    "Week 3 Project: A Responsible AI Audit": ["responsible_ai_practice", "fairness_talk"],
    "AI Governance, Law and Accountability": ["responsible_ai_practice", "cs50_law"],
    "Documentation: Model Cards and Datasheets": ["ethics_bias_real", "mlflow_gems"],
    "Human Oversight and Safe Failure": ["fei_fei", "bias_explain_guide"],
    "Planning Your Capstone Project": ["baseline_nlp", "stanford_ml1"],
    "Capstone Build: An End-to-End Reference Project": ["painless_ml_prod", "mlops_bridge"],
    "Capstone Presentation, Final Exam and Certificate": ["cs50x_ai_2026", "responsible_ai_practice"],
})
