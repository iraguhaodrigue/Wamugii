"""
Modern AI: LLMs & Generative AI -- full 4-week course (24 lessons, about 26 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content modern_ai_llms_generative

It replaces the short 6-lesson version created by seed_ai_c5_llms_genai.py:
the old lessons are hidden, students keep their enrolment.
"""

from app.course_content.lectures import attach
from app.course_content.llm_exam import EXAM
from app.course_content.llm_week1 import WEEK1
from app.course_content.llm_week2 import WEEK2
from app.course_content.llm_week3 import WEEK3
from app.course_content.llm_week4 import WEEK4

COURSE = {
    "slug": "modern-ai-llms-generative",
    "title": "Modern AI: LLMs & Generative AI",
    "category": "Artificial Intelligence",
    "display_order": 6,
    "is_free": True,
    "description": (
        "A complete 4-week, hands-on course in large language models and generative AI with "
        "Python — explained in simple English, with every line of code tested. Week 1: how LLMs "
        "work — tokens and BPE, next-token prediction and sampling, building and training your own "
        "tiny GPT, and how a base model becomes an assistant. Week 2: building with LLM APIs — "
        "your first API call, prompt engineering, structured output and tool use, conversations "
        "and streaming, cost, speed and reliability, and a customer-support assistant. Week 3: "
        "embeddings, vector search and retrieval-augmented generation (RAG) with citations, "
        "better retrieval, and evaluating LLM apps properly. Week 4: AI agents, fine-tuning and "
        "LoRA from scratch, diffusion and multimodal AI, open models running locally, safety and "
        "prompt injection, and deploying a responsible AI assistant as a web API.\n\n"
        "Free in Google Colab — nothing to install. For the API lessons you need a free or paid "
        "key from an LLM provider (the course shows Anthropic Claude and Google Gemini's free tier) "
        "or an open model you run yourself. 24 lessons, each with a short video, full lectures to "
        "go deeper, notes with ready-to-run code, a downloadable handout and a quiz, plus a project "
        "every week, a final exam and a certificate. Built by WAMUGII TECH SOLUTIONS for students "
        "and professionals in Rwanda and beyond."
    ),
    "modules": [WEEK1, WEEK2, WEEK3, WEEK4],
    # Final exam: these questions plus every lesson-quiz question (as single answer).
    "exam": EXAM,
}

# "Go deeper" full lectures under the short videos (see lectures.py).
attach(COURSE, {
    "From Chatbots to Large Language Models": ["karpathy_llm", "karpathy_deep_dive"],
    "Tokens: How LLMs Read Text": ["karpathy_tokenizer", "karpathy_deep_dive"],
    "Next-Token Prediction and Sampling": ["karpathy_makemore1", "cs50_one_word"],
    "Build a Tiny GPT": ["karpathy_gpt", "3b1b_attention"],
    "From Base Model to Assistant": ["karpathy_deep_dive", "karpathy_llm"],
    "Week 1 Project: Train and Study Your Own Language Model": ["karpathy_gpt2", "karpathy_makemore1"],
    "Your First LLM API Call": ["karpathy_llm", "cs50_llm_programming"],
    "Prompt Engineering for Developers": ["mastering_llms", "karpathy_how_i_use"],
    "Structured Output and Tool Use": ["agents_python", "mastering_llms"],
    "Conversations, Memory and Streaming": ["karpathy_how_i_use", "karpathy_llm"],
    "Cost, Speed and Reliability": ["mastering_llms", "hacker_guide_llms"],
    "Week 2 Project: A Customer-Support Assistant": ["mastering_llms", "agents_python"],
    "Embeddings: Meaning as Numbers": ["embedding_models", "embeddings_talk"],
    "Vector Search and Vector Databases": ["vectors_visual", "rag_fundamentals"],
    "Retrieval-Augmented Generation (RAG)": ["rag_limits", "facts_hallucination"],
    "Better Retrieval: Chunking, Hybrid Search and Reranking": ["rag_fundamentals", "embedding_models"],
    "Evaluating LLM Applications": ["mastering_llms", "rag_limits"],
    "Week 3 Project: Ask the Handbook": ["rag_fundamentals", "facts_hallucination"],
    "AI Agents: LLMs That Use Tools and Take Steps": ["agents_python", "mastering_llms"],
    "Fine-Tuning, Prompting or RAG? And LoRA from Scratch": ["hacker_guide_llms", "karpathy_deep_dive"],
    "Generative AI Beyond Text: Images, Audio and Diffusion": ["3b1b_clip", "attention_diffusion_talk", "whisper_talk"],
    "Open Models and Running AI Locally": ["finetune_local", "karpathy_llm"],
    "Safety, Security and Responsible Generative AI": ["liveoverflow_injection", "chatgpt_privacy", "cc_bias"],
    "Final Project: Build and Deploy a Responsible AI Assistant": ["facts_hallucination", "multilingual_eval", "karpathy_deep_dive"],
})
