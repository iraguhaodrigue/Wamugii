"""
WAMUGII AI Program — Course 5: "Modern AI: LLMs & Generative AI".
University-level, original WAMUGII content in simple English.
Run:  python -m app.seed_ai_c5_llms_genai
"""

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.models.course import CourseStatus
from app.schemas.course import CourseCreate, LessonCreate

COURSE_SLUG = "modern-ai-llms-generative"

COURSE = CourseCreate(
    title="Modern AI: LLMs & Generative AI",
    slug=COURSE_SLUG,
    category="Artificial Intelligence",
    is_free=True,
    status=CourseStatus.PUBLISHED,
    display_order=6,
    description=(
        "Course 5 of the WAMUGII AI Program. Understand and build with today's "
        "frontier AI: large language models and generative AI. You'll learn the "
        "transformer idea, how LLMs work, embeddings, prompting as engineering, "
        "retrieval-augmented generation (RAG), how to call AI through APIs, "
        "generative models beyond text, and the real limits and safety issues. "
        "Simple English with practical code. By the end you can build a simple, "
        "useful AI application."
    ),
)

LESSONS = [
    {
        "title": "5.1 What Changed — The Transformer",
        "content": """\
**Learning objective:** Understand, in plain language, the transformer idea that
started the modern AI era.

## The breakthrough of 2017

For decades, handling language was slow and limited (RNNs, Course 4). In 2017 a
new design called the **Transformer** changed everything. Nearly every modern AI
system — ChatGPT, Claude, Gemini, image generators — is built on it.

## The key idea: attention

The transformer's superpower is **attention**: when processing a word, the model
**looks at all the other words at once** and decides which ones matter most for
meaning.

*Example:* in "the trophy didn't fit in the suitcase because **it** was too big,"
what is "it"? Attention lets the model weigh every word and link "it" to "trophy."
This is how transformers understand **context**.

## Why it beat RNNs

- RNNs read one word at a time and forgot distant words.
- Transformers see the **whole sequence together**, so they handle long text and
  long-range context far better.
- They also **train much faster** because the work can be done in parallel.

## Scale did the rest

Researchers found that making transformers **bigger** (more layers, more data,
more compute) kept making them **smarter**, in surprising ways. Trained on huge
amounts of text, they became the **large language models** we use today.

You don't need the maths of attention to use LLMs well — but knowing that "the
model weighs every word to understand context" explains much of their behaviour.

## Key terms

**Transformer**, **Attention**, **Context**, **Parallel training**, **Scale**.

## Practice

In the sentence "Ana told Maria that she passed the exam," the word "she" is
ambiguous. Explain how "attention" helps a model guess who "she" is — and why even
a strong model might still get it wrong.
""",
    },
    {
        "title": "5.2 How Large Language Models Work",
        "content": """\
**Learning objective:** Understand what an LLM actually does, so you can use it
wisely and know its limits.

## At heart: predict the next token

An LLM does one simple thing extremely well: **predict the next piece of text
(token).** Given "The capital of Rwanda is," it predicts "Kigali" because that is
the most likely continuation it learned from vast text.

Everything else — answering questions, writing code, summarising — is this same
next-token prediction, repeated again and again, each new token added and fed back
in.

## Tokens

Models don't see whole words; they see **tokens** — common chunks of text (a
short word may be one token; a long word several). This is why models have length
limits measured in tokens, and why you sometimes pay per token.

## Training in two stages

1. **Pre-training** — read enormous amounts of text to learn language, facts, and
   reasoning patterns. This is where most capability comes from.
2. **Fine-tuning / alignment** — further training (often with human feedback) to
   make the model helpful, honest, and safe to talk to.

## Why they "hallucinate"

Because an LLM predicts *likely* text, not *true* text, it can produce a confident
answer that is **wrong or invented** — a **hallucination**. It has no built-in
fact-checker. This is the single most important limit to remember: **an LLM sounds
authoritative whether or not it is correct.** Always verify anything that matters.

## What they don't have (by default)

- **Live knowledge** — they know only up to their training cutoff unless given
  tools or search.
- **Real memory of you** — unless the app is built to keep it.
- **True understanding or intent** — they model patterns of language.

## Key terms

**LLM**, **Token**, **Next-token prediction**, **Pre-training**, **Fine-tuning**,
**Hallucination**, **Knowledge cutoff**.

## Practice

Explain to a non-technical friend, in 3–4 sentences, why a chatbot can write a
beautiful, confident paragraph that contains a completely made-up "fact" — and what
that means for how they should use it.
""",
    },
    {
        "title": "5.3 Embeddings — Meaning as Numbers",
        "content": """\
**Learning objective:** Understand embeddings and why they power search,
recommendations, and RAG.

## Turning meaning into vectors

An **embedding** turns a piece of text (a word, sentence, or document) into a
**vector of numbers** that captures its **meaning**. Texts with similar meaning get
vectors that are **close together**; unrelated texts are far apart.

- "doctor" and "nurse" → close.
- "doctor" and "banana" → far.

This is powerful because, once meaning is numbers, the computer can **measure how
similar two texts are** — using distance, like in Course 3.

## Why this is useful

- **Semantic search** — find documents by *meaning*, not just matching keywords. A
  search for "cheap places to eat" can find a page about "affordable restaurants"
  even with no shared words.
- **Recommendations** — suggest items similar to what someone liked.
- **Clustering** — group similar documents (Course 3's k-means on embeddings).
- **RAG** — the key to giving an LLM your own documents (next lesson).

## In practice

```python
# Pseudocode: get an embedding from a model API
vector = embed("affordable restaurants in Kigali")
# Then compare vectors with cosine similarity to find the closest matches.
```

You store many document embeddings in a **vector database** and, given a query
embedding, quickly find the closest ones.

## Key terms

**Embedding**, **Vector**, **Semantic similarity**, **Semantic search**, **Vector
database**, **Cosine similarity**.

## Practice

You run a help centre with 500 articles. Explain how embeddings would let a user
find the right article by describing their problem in their own words, even if they
don't use the same words as the article title.
""",
    },
    {
        "title": "5.4 Prompting as Engineering",
        "content": """\
**Learning objective:** Write effective prompts using proven techniques — the core
skill for getting real value from LLMs.

## Prompting is a skill, not luck

The same model gives weak or excellent answers depending entirely on the prompt.
This lesson builds on the basics (role, task, details, format) with the techniques
professionals use.

## Core techniques

- **Give a role and context.** "You are a financial analyst reviewing a small
  business…" sets the right frame.
- **Be specific about the output.** Say the length, format, tone, and audience.
- **Give examples (few-shot).** Show one or two examples of the input→output you
  want; the model copies the pattern. This is one of the most powerful techniques.
- **Ask for step-by-step reasoning.** For hard problems, "think step by step
  before giving the final answer" improves accuracy.
- **Set constraints.** "Use only the information I provide." "If you are not sure,
  say so." This reduces hallucination.
- **Iterate.** Treat the first answer as a draft; refine with follow-ups.

## A strong prompt, assembled

```
You are an experienced IT lecturer.
Task: explain "overfitting" to a first-year student.
Constraints: use one everyday analogy, under 120 words, simple English.
If the concept has a common misunderstanding, point it out.
```

## Verify, always

Prompting well gets better *drafts*, not guaranteed truth. Everything from Course
5.2 still holds: **check important facts.** Ask the model to "list the claims I
should verify."

## Key terms

**Prompt engineering**, **Role/context**, **Few-shot examples**, **Step-by-step
reasoning**, **Constraints**, **Iteration**.

## Practice

Take a vague prompt — "help me write a business plan" — and rewrite it into a
strong prompt using at least **four** of the techniques above (role, specifics,
an example or constraint, and desired format).
""",
    },
    {
        "title": "5.5 Retrieval-Augmented Generation (RAG)",
        "content": """\
**Learning objective:** Understand RAG — how to make an LLM answer accurately from
*your own* documents.

## The problem RAG solves

An LLM only knows its training data, which is general and frozen at a cutoff. It
doesn't know **your** company handbook, **your** course notes, or **today's**
information — and if you ask, it may hallucinate. **RAG** fixes this by giving the
model the right information at the moment you ask.

## How RAG works (the recipe)

1. **Prepare** — split your documents into chunks and create an **embedding**
   (Lesson 5.3) for each. Store them in a **vector database**.
2. **Retrieve** — when a user asks a question, embed the question and find the
   **most similar chunks** from your documents.
3. **Augment** — put those chunks into the prompt as context.
4. **Generate** — ask the LLM to answer **using only that provided context**.

```
User question
   → find relevant chunks from YOUR docs (by embedding similarity)
   → prompt: "Using the context below, answer the question. Context: ...”
   → grounded, accurate answer (with sources)
```

## Why RAG is so important

- The answer is **grounded** in real, current, private information — far less
  hallucination.
- You can show **sources**, so users can verify.
- You don't need to retrain the model; just update the documents.

This is how most real business AI assistants are built — a customer-support bot
that answers from the company's actual help articles, a study assistant that
answers from the actual course notes.

## Key terms

**RAG**, **Chunking**, **Vector database**, **Retrieval**, **Grounding**,
**Context window**.

## Practice

Design (in words) a RAG assistant for your WAMUGII courses that answers students'
questions from the lesson content. List the four RAG steps for your case and say
what the "documents" and the "chunks" would be.
""",
    },
    {
        "title": "5.6 Building with AI — Using APIs",
        "content": """\
**Learning objective:** Call an LLM from your own program through an API, so you
can build real applications.

## From chatbot to building block

Chatting with an AI in a browser is useful, but to build a **product** you call
the model from your **own code** through an **API** (Application Programming
Interface). Your program sends a prompt and gets back the model's answer, which you
then use however you like.

## The basic shape (pseudocode)

```python
response = ai_client.chat(
    model="some-model",
    messages=[
        {"role": "system", "content": "You are a helpful study assistant."},
        {"role": "user", "content": "Explain overfitting simply."},
    ],
)
answer = response.text
```

- **system message** — sets the role/behaviour (your prompt engineering lives
  here).
- **user message** — the actual request, often built from user input + retrieved
  context (RAG).
- The response is just text your app can display, store, or act on.

## Key practical points

- **API keys are secrets.** Never put them in your frontend code or public repos;
  keep them on your server (like WAMUGII keeps its keys in an env file).
- **It costs money per token.** Keep prompts tight; cache repeated answers.
- **It can fail or be slow.** Handle errors and timeouts gracefully.
- **Never trust output blindly.** Validate anything used for an action; never let
  raw model output run code or commands unchecked.

## What you can build

- A support assistant (LLM + RAG over your docs).
- A tool that summarises documents, drafts emails, or extracts data.
- A tutor that answers from your course content.

These are real, buildable projects — exactly the kind WAMUGII can offer clients.

## Key terms

**API**, **API key**, **System / user message**, **Token cost**, **Error
handling**, **Server-side secret**.

## Practice

Sketch (in words or pseudocode) how a "summarise this document" feature would work
in an app: what the user sends, what your server adds to the prompt, what the API
returns, and where you'd keep the API key safe.
""",
    },
    {
        "title": "5.7 Generative AI Beyond Text",
        "content": """\
**Learning objective:** Understand generative models for images, audio and more —
and where they're useful.

## Generative AI generates new content

So far we've focused on text, but the same idea — a model trained to generate
likely content — applies to other media.

## Images

**Image generators** (such as diffusion models) create pictures from a text
description ("a rose-gold logo on a black background"). They work by learning to
turn random noise into a coherent image that matches the prompt, step by step.

- **Uses:** mock-ups, illustrations, concept art, marketing images.
- **Limits:** they invent details, struggle with text-in-images and exact
  likenesses, and raise copyright and authenticity questions.

## Audio and speech

- **Text-to-speech** turns text into natural-sounding voice.
- **Speech-to-text** transcribes recordings (useful for notes, subtitles).
- **Music and sound generation** is emerging.

## Video

Text-to-video is advancing fast — generating short clips from a description — but
is still expensive and imperfect.

## Multimodal models

The newest models are **multimodal**: one model handles **text, images, and audio
together**. You can show it a photo and ask a question about it, or have it read a
chart. This is quickly becoming the norm.

## Using it responsibly

Generative media brings real risks: **deepfakes**, misinformation, and using
someone's likeness or copyrighted work without permission. Label AI-generated
content honestly, and never use it to deceive. (More in Lesson 5.8 and Course 6.)

## Key terms

**Generative AI**, **Diffusion model**, **Text-to-image**, **Text-to-speech**,
**Multimodal**, **Deepfake**.

## Practice

Name one task in your work or studies where **image generation** would genuinely
help, and one where it would be **inappropriate or risky**. Explain the difference.
""",
    },
    {
        "title": "5.8 Limits, Hallucination and Safety",
        "content": """\
**Learning objective:** Know the real limits of generative AI and how to use it
safely and honestly.

## The honest truth about today's AI

Modern AI is powerful but **not reliable on its own**. Using it professionally
means understanding exactly where it breaks.

## The main limits

- **Hallucination.** It can state false things with full confidence. Never publish
  AI facts, figures, names, quotes, or citations without checking them.
- **No real-time knowledge.** It doesn't know recent events unless given search or
  tools.
- **Bias.** It learned from human text and can reproduce stereotypes and unfair
  patterns.
- **No true understanding.** It predicts language; it can be tripped up by simple
  logic or arithmetic, and can be confidently inconsistent.
- **Sensitivity to wording.** Small prompt changes can change the answer a lot.

## Safety and security risks

- **Prompt injection.** If your app feeds untrusted text (a web page, an email) to
  the model, that text can contain hidden instructions that hijack it. Treat
  outside content as **data, not commands**.
- **Data leakage.** Don't paste real secrets, passwords, or private personal data
  into public AI tools.
- **Over-reliance.** If you let AI do all the thinking, your own skill fades, and
  you can't catch its mistakes.

## How to use it well

1. **Verify** anything that matters against a real source.
2. **Keep a human in charge** of important decisions.
3. **Protect private data** — remove or fake sensitive details.
4. **Be honest** — tell people when content is AI-generated.
5. **Design for failure** — assume it will sometimes be wrong, and build checks.

## Key terms

**Hallucination**, **Bias**, **Prompt injection**, **Data leakage**,
**Over-reliance**, **Human oversight**.

## Practice

You're building an AI assistant that reads customer emails and drafts replies.
Name two risks from this lesson that apply, and one concrete safeguard for each.
""",
    },
    {
        "title": "5.9 Project — Build a Simple AI App (Assessment)",
        "content": """\
**This is your Course 5 assessment.** You will design and build a small but real
AI-powered application using an LLM.

## The task

Build a simple app or script that solves a **real problem** for you or your
community using an LLM through an API. It doesn't need a fancy interface — a
working command-line script or a small web page is fine. Produce the working code
and a short report.

## Good project ideas

- A **study assistant** that answers questions from your course notes (use **RAG**,
  Lesson 5.5).
- A **document summariser** that turns a long PDF or text into key points.
- A **support reply drafter** that reads a customer message and drafts a response.
- A **data extractor** that pulls structured fields (name, date, amount) from messy
  text.

## Required steps

1. **Define the problem** and who it helps.
2. **Design the solution**: plain LLM call, or LLM + RAG if it needs your own
   documents. Explain your choice.
3. **Engineer the prompt** using the techniques from Lesson 5.4 (role, specifics,
   constraints, and "use only the provided context" where relevant).
4. **Build it**: call the model through an API; **keep the API key safe**
   (server-side / env file, never in public code).
5. **Handle reality**: deal with errors, and **validate or verify** the output
   before showing or using it.
6. **Address safety**: name the main risk (hallucination, data leakage, prompt
   injection) and how you handled it (Lesson 5.8).

## What good work looks like

- The solution **fits the problem** (you justified plain LLM vs RAG).
- The prompt is **well-engineered**, not a one-liner.
- Secrets are **protected**, and output is **not blindly trusted**.
- You are honest about the app's **limits**.

## Submit

Keep your code and report together. You have now built something real with frontier
AI — the exact kind of work in highest demand. The final course, Course 6, takes a
project like this and makes it **responsible and ready for the real world**.
""",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        existing = course_crud.get_course_by_slug(db, COURSE_SLUG)
        if existing:
            print(f"Course already exists: {existing.title}")
            return
        course = course_crud.create_course(db, COURSE)
        print(f"Created course: {course.title} (status: {course.status.value})")
        for order, lesson in enumerate(LESSONS, start=1):
            created = course_crud.create_lesson(
                db, course.id,
                LessonCreate(title=lesson["title"], content=lesson["content"], display_order=order),
            )
            print(f"  + {created.title}")
        print(f"Done. {len(LESSONS)} lessons added. '{course.title}' is live.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
