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
    # Deep Learning & Neural Networks
    "3b1b_nn": ("3Blue1Brown: But what is a neural network?", YT + "aircAruvnKk", None),
    "3b1b_backprop_calc": ("3Blue1Brown: Backpropagation calculus", YT + "tIeHLnjs5U8", None),
    "karpathy_micrograd": ("Andrej Karpathy: Neural networks and backpropagation, step by step (building micrograd)", YT + "VMj-3S1tku0", 146),
    "karpathy_makemore3": ("Andrej Karpathy: Activations, gradients and BatchNorm", YT + "P6sfmUTpUmc", None),
    "karpathy_gpt": ("Andrej Karpathy: Let's build GPT from scratch, in code", YT + "kCc8FmEb1nY", 116),
    "fcc_pytorch": ("freeCodeCamp: PyTorch for Deep Learning & Machine Learning — full course", YT + "V_xro1bcAuA", None),
    "pytorch_autograd_talk": ("EuroPython: An introduction to PyTorch and autograd", YT + "rrekAv9Fml4", 32),
    "pytorch_image_talk": ("EuroPython: How to train an image classifier using PyTorch", YT + "eDRck258bnw", 42),
    "pytorch2_talk": ("EuroPython 2023: PyTorch 2.0 — why should you care?", YT + "B_KXmhCffzQ", 28),
    "mit_cnn_2024": ("MIT 6.S191 (2024): Convolutional Neural Networks", YT + "2xqkSUhmmXU", None),
    "mit_cnn_2023": ("MIT 6.S191 (2023): Convolutional Neural Networks", YT + "NmLK_WQBxB4", None),
    "mit_rnn_2024": ("MIT 6.S191 (2024): Recurrent Neural Networks, Transformers and Attention", YT + "dqoEU9Ac3ek", None),
    "mit_wild_2024": ("MIT 6.S191 (2024): Building AI Models in the Wild", YT + "ZAGiinWiFsE", None),
    "computerphile_cnn": ("Computerphile: CNNs — Convolutional Neural Networks Explained", YT + "py5byOOHZM8", None),
    "keras_cnn_talk": ("PyData London: Introduction to Convolutional Neural Networks (TensorFlow and Keras)", YT + "WIhI1W6NoZ0", 93),
    "transfer_talk": ("PyData: Transfer Learning and Fine-tuning Deep Convolutional Networks", YT + "nB15sW-mkHA", 52),
    "embeddings_talk": ("PyCon Italia: Word Embeddings for Natural Language Processing in Python", YT + "c8QF1FJjPG8", 42),
    "rnn_talk": ("EuroPython: Understanding and Implementing Recurrent Neural Networks using Python", YT + "bSdBG7hToOg", 40),
    "conv1d_ts_talk": ("PyData LA: 1D Convolutional Neural Networks for Time Series Modelling", YT + "nMkqWxMjWzg", 36),
    "vae_talk": ("PyData Tel Aviv: Generative Models and Variational Autoencoders Explained", YT + "bbOFvxbMIV0", 37),
    "gans_talk": ("EuroSciPy: Deep Diving into GANs — from Theory to Production", YT + "CePrdabdtxw", 80),
    "onnx_talk": ("PyParis: Deep Learning Model Deployment with ONNX", YT + "cswXUNtUfuI", 20),
    "deploy_nlp_talk": ("EuroPython: Train, Serve, Deploy — an NLP model with PyTorch and Docker", YT + "BSDW8PWUVF0", 30),
    # Modern AI: LLMs & Generative AI
    "karpathy_tokenizer": ("Andrej Karpathy: Let's build the GPT Tokenizer", YT + "zduSFxRajkE", 134),
    "karpathy_deep_dive": ("Andrej Karpathy: Deep Dive into LLMs like ChatGPT", YT + "7xTGNNLPyMI", 211),
    "karpathy_how_i_use": ("Andrej Karpathy: How I use LLMs", YT + "EWvNQjAaOHw", 131),
    "karpathy_makemore1": ("Andrej Karpathy: The spelled-out intro to language modeling — building makemore", YT + "PaCmpygFfXo", None),
    "karpathy_gpt2": ("Andrej Karpathy: Let's reproduce GPT-2 (124M)", YT + "l8pRSuU81PU", None),
    "3b1b_llm_brief": ("3Blue1Brown: Large Language Models explained briefly", YT + "LPZh9BOjkQs", None),
    "3b1b_gpt": ("3Blue1Brown: Transformers, the tech behind LLMs", YT + "wjZofJX0v4M", None),
    "3b1b_attention": ("3Blue1Brown: Attention in transformers, step by step", YT + "eMlx5fFNoYc", None),
    "3b1b_clip": ("3Blue1Brown: How AI connects text and images", YT + "j5h9dBtWZXM", None),
    "diffusion_welch": ("3Blue1Brown (guest video by Welch Labs): But how do AI images and videos actually work?", YT + "iv-5mZ_9CPY", None),
    "liveoverflow_injection": ("LiveOverflow: Attacking LLM — Prompt Injection", YT + "Sv5OLj2nVAQ", 13),
    "rag_fundamentals": ("EuroPython 2024: Fundamentals of Retrieval Augmented Generation", YT + "vSwK5sBpD2c", 31),
    "rag_limits": ("EuroPython 2024: Is RAG all you need? A look at the limits of retrieval augmented generation", YT + "9wk7mGB_Gp4", 44),
    "embedding_models": ("EuroPython 2024: Deconstructing the text embedding models", YT + "Lha_QCkXxm0", 44),
    "vectors_visual": ("North Bay Python 2024: A visual exploration of vectors (Pamela Fox)", YT + "Q_slEpNuhMc", 21),
    "agents_python": ("PyOhio 2025: Demystifying AI Agents with Python Code", YT + "jOEdb9HnwsQ", None),
    "mastering_llms": ("PyData Virginia 2025: Mastering LLMs — from Prompt Engineering to Agentic AI", YT + "jmwLzX_ltbQ", 99),
    "multilingual_eval": ("PyTorch Day 2025: Best Practices for Open Multilingual LLM Evaluation", YT + "6u996P09EZE", 16),
    "finetune_local": ("EuroPython 2024: Fine-tuning large models on local hardware", YT + "hdHKCjhF68U", 28),
    "hacker_guide_llms": ("posit::conf 2023: A hacker's guide to open source LLMs (Jeremy Howard)", YT + "sYliwvml9Es", 62),
    "facts_hallucination": ("PyData Berlin 2023: How to Feed Facts to Large Language Models and Reduce Hallucination", YT + "-eRjgj1zww4", 29),
    "attention_diffusion_talk": ("EuroPython 2023: Understanding Neural Network Architectures with Attention and Diffusion", YT + "Clh0nJRMvNs", 38),
    "whisper_talk": ("EuroPython 2023: Whisper AI — Live English Subtitles for 96 Languages", YT + "WpKzFqrQXdw", 30),
    "chatgpt_privacy": ("PyCon US 2023: The ChatGPT Privacy Tango — Data Security and Large Language Models", YT + "sGn6BuldvIk", None),
    # Responsible AI & Deployment
    "mlops_bridge": ("PyCascades 2024: Embracing MLOps — Bridging the Gap Between Machine Learning and DevOps", YT + "wRnKcWIZEvk", 23),
    "painless_ml_prod": ("EuroPython 2020: Painless Machine Learning in Production", YT + "8Zn4hV9xE1I", 42),
    "reproducible_ml": ("PyCon DE 2022: Reproducible machine learning and science with Python", YT + "0ShpadTHsro", 75),
    "reproducible_experiments": ("Python Web Conf 2022: Using Reproducible Experiments to Create Better Machine Learning Models", YT + "DY8LpArCulI", 42),
    "fastapi_keynote": ("PyCon India 2021 keynote: Modern Python through FastAPI and friends (Sebastián Ramírez)", YT + "3qTBLhnS4to", 63),
    "continuous_testing_ml": ("PyCon DE 2023: Staying Alert — How to Implement Continuous Testing for Machine Learning Models", YT + "4BgmBtsS0iA", 30),
    "docker_best": ("EuroPython 2020: Best practices for production-ready Docker packaging", YT + "H0UPw-ILiz4", 32),
    "can_we_deploy": ("EuroPython 2020: Can we deploy yet?", YT + "Fgyk8P0IJsU", 23),
    "mlflow_lifecycle": ("PyData Eindhoven 2019: Managing the Machine Learning Lifecycle with MLflow", YT + "hm3HIZ5mns0", 56),
    "mlflow_gems": ("PyCon US 2024: Trust Fall — Three Hidden Gems in MLflow", YT + "cAgrIilgP4A", None),
    "mlflow_serverless": ("PyCon Italia 2022: Managing large-scale ML pipelines with MLflow and serverless computing", YT + "8AkqF99tkXg", 30),
    "ml_monitoring": ("EuroPython 2021: Production ML Monitoring — Outliers, Drift, Explainers and Statistical Performance", YT + "n0bR0IArJDo", 25),
    "logging_module": ("EuroPython 2023: Stop using print! Understanding and using the logging module", YT + "5f4o3nyAz5w", 29),
    "detecting_drift": ("PyCon DE 2022: Detecting drift — how to evaluate and explore data drift in ML systems", YT + "0wdCMvU1vCQ", 29),
    "ab_python": ("PyBay 2019: A/B Testing in Python", YT + "QWeMYnlNtzY", None),
    "debias_ml": ("PyBay 2019: DebiasML", YT + "VCyk0_I-8BM", None),
    "bias_explain_guide": ("PyData London 2019: A practical guide towards algorithmic bias and explainability in machine learning", YT + "vq8mDiDODhc", 38),
    "interpretability_tutorial": ("PyCon US 2019 tutorial: Open the Black Box — an Introduction to Model Interpretability in Python", YT + "d66ttkMY9zE", 218),
    "shap_beyond": ("PyData Amsterdam 2019: SHAP and Beyond", YT + "xwl8WhtJNs0", 31),
    "privacy_methods": ("PyCon US 2020: Privacy-preserving methods — Building secure projects", YT + "jKlJEPSZAYo", 29),
    "privacy_tools": ("PyCon US 2022: Open Source, Python Based Tools For Data Privacy", YT + "tuhJiz9_V6o", 29),
    "poisoned_pickles": ("EuroPython 2023: Poisoned pickles make you ill", YT + "c2c9lqKb39I", 27),
    "responsible_ai_practice": ("SciPy 2023: Responsible AI in Practice (Rumman Chowdhury)", YT + "dQHjntrqrFQ", 49),
    "ethics_bias_real": ("PyGotham 2019: Ethics & Bias Detection in the Real World", YT + "FkCb7345Hj8", 25),
    "baseline_nlp": ("PyData Berlin 2023: How to baseline in NLP and where to go from there", YT + "oc_p0ZgoyA8", 30),
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
