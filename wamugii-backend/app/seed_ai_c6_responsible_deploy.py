"""
WAMUGII AI Program — Course 6: "Responsible AI & Deployment (Capstone)".
University-level, original WAMUGII content in simple English.
Run:  python -m app.seed_ai_c6_responsible_deploy
"""

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.models.course import CourseStatus
from app.schemas.course import CourseCreate, LessonCreate

COURSE_SLUG = "responsible-ai-deployment"

COURSE = CourseCreate(
    title="Responsible AI & Deployment (Capstone)",
    slug=COURSE_SLUG,
    category="Artificial Intelligence",
    is_free=True,
    status=CourseStatus.PUBLISHED,
    display_order=7,
    description=(
        "Course 6 and capstone of the WAMUGII AI Program. Take a model from a "
        "notebook to a responsible, working product. You'll learn how to serve a "
        "model through an API, the basics of MLOps, how to monitor for model "
        "drift, how to audit for fairness and bias, privacy and security, AI "
        "governance and law, and documentation for reproducibility. The course "
        "ends in a full capstone: plan and build an end-to-end AI project. "
        "Simple English, practical focus. By the end you can deliver AI "
        "responsibly and complete a real project start to finish."
    ),
)

LESSONS = [
    {
        "title": "6.1 From Notebook to Product — The Deployment Gap",
        "content": """\
**Learning objective:** Understand why a model that works in a notebook is only
the beginning, and what it takes to make it real.

## A trained model is not a product

Most AI courses stop at "the model gets 90% accuracy." In the real world that is
roughly **10% of the work.** A model only creates value when real people can use
it reliably, safely, and over time. Closing that distance is called the
**deployment gap**.

## What a real AI system needs beyond the model

- **A way to be used** — an API or app that takes new input and returns a
  prediction (Lesson 6.2).
- **Reliability** — it must handle bad input, errors, and load without crashing.
- **Monitoring** — the world changes; the model must be watched (Lesson 6.3).
- **Fairness and safety checks** — it affects people (Lessons 6.4–6.5).
- **Documentation** — so others (and future you) can understand and maintain it
  (Lesson 6.7).
- **Governance** — accountability and compliance with the law (Lesson 6.6).

## MLOps — operating ML in the real world

**MLOps** (Machine Learning Operations) is the practice of building, deploying, and
maintaining ML systems reliably — the same discipline that software engineering
brought to normal code, applied to models that also depend on **data** and can
**decay over time**.

## The mindset shift

- Notebook thinking: *"Does the model predict well on my test set?"*
- Product thinking: *"Will this still work, safely and fairly, on real users six
  months from now — and can someone else maintain it?"*

This course is about that second question.

## Key terms

**Deployment gap**, **MLOps**, **Reliability**, **Monitoring**, **Maintainability**.

## Practice

List three things (beyond model accuracy) that a real deployed AI system needs that
a notebook model does not. For each, write one sentence on what could go wrong if
it's missing.
""",
    },
    {
        "title": "6.2 Serving a Model",
        "content": """\
**Learning objective:** Understand how a trained model is made available to
applications through an API.

## Save the model, then serve it

After training, you **save** the model to a file so it can be loaded later without
retraining.

```python
import joblib
joblib.dump(model, "model.pkl")      # save
model = joblib.load("model.pkl")     # load later
```

## Wrap it in an API

To let apps use it, you put the model behind a small **web API**. A request comes
in with the input features; the API returns the prediction. (WAMUGII's own backend
is a FastAPI service — the same idea.)

```python
from fastapi import FastAPI
import joblib

app = FastAPI()
model = joblib.load("model.pkl")

@app.post("/predict")
def predict(features: list[float]):
    prediction = model.predict([features])
    return {"prediction": prediction[0].item()}
```

Now any app — web, mobile, another service — can send data and get a prediction.

## Containerising with Docker

To run the same way everywhere, the service is usually packaged in a **Docker
container** — the model, the code, and its exact dependencies in one box. (This is
exactly how WAMUGII's backend runs.) It removes "it worked on my machine" problems
and makes deployment repeatable.

## Key practical concerns

- **Input validation** — reject malformed or out-of-range inputs.
- **The same preparation** — apply the *exact* scaling/encoding used in training,
  or predictions will be wrong (save the scaler too).
- **Speed** — cache where possible; keep the model loaded in memory.
- **Versioning** — know which model version is live, so you can roll back.

## Key terms

**Serialisation (save/load)**, **API endpoint**, **FastAPI**, **Docker /
container**, **Input validation**, **Model versioning**.

## Practice

Explain why you must save and reuse the **training scaler** when serving a model,
not fit a new one on incoming data. (Hint: connect it to data leakage and to
getting consistent predictions.)
""",
    },
    {
        "title": "6.3 Monitoring and Model Drift",
        "content": """\
**Learning objective:** Understand why deployed models get worse over time and how
to catch it.

## Models decay — this is the big surprise

Normal software keeps working until the code changes. **A model can silently get
worse even though its code never changed**, because the **world** changed. This is
the most important idea in operating AI.

## Two kinds of drift

- **Data drift** — the incoming data starts to look different from the training
  data. *Example:* a spending-prediction model trained before a price shock now
  sees very different amounts.
- **Concept drift** — the relationship itself changes. *Example:* what counts as
  "fraud" evolves as fraudsters change tactics, so old patterns no longer apply.

Either way, accuracy quietly drops while everything *looks* fine.

## What to monitor

- **Inputs** — are the feature values drifting away from the training range?
- **Predictions** — is the mix of predictions shifting (e.g. far more "approve"
  than before)?
- **Outcomes** — where you can later learn the true answer, track real accuracy
  over time.
- **System health** — errors, latency, and usage.

## What to do about it

- **Set alerts** for drift and accuracy drops.
- **Retrain** the model regularly on fresh data.
- **Keep a human review** for important or low-confidence decisions.
- **Log predictions** so you can investigate problems later.

## Key terms

**Model drift**, **Data drift**, **Concept drift**, **Monitoring**, **Retraining**,
**Logging**.

## Practice

A loan-approval model worked well for a year, then its approvals quietly became
less accurate — with no code change. Name the two kinds of drift that could cause
this, give an example of each for this case, and say what you'd put in place to
catch it next time.
""",
    },
    {
        "title": "6.4 Fairness and Bias in Practice",
        "content": """\
**Learning objective:** Move from knowing bias exists (Course 1) to actually
checking and reducing it in a real system.

## Why fairness needs active work

Bias doesn't announce itself. A model can have great overall accuracy and still
treat some groups unfairly. You only find this if you **look for it on purpose.**

## Where bias comes from

- **Biased data** — the training data reflects past unfair patterns (Course 1's
  hiring example).
- **Biased labels** — the "right answers" themselves were decided unfairly.
- **Missing groups** — some groups are under-represented, so the model serves them
  worse.
- **Proxy features** — a feature that secretly stands in for a protected
  attribute (e.g. a neighbourhood acting as a proxy for ethnicity).

## How to audit for fairness

1. **Measure performance by group.** Don't just report overall accuracy — report
   precision/recall **for each group** (by gender, region, age, etc.). Big gaps are
   a red flag.
2. **Check error types by group.** Who gets more false rejections? Who gets more
   false approvals? The *kind* of error matters.
3. **Question your features.** Could any feature be a proxy for something you must
   not discriminate on?

## How to reduce bias

- **Fix the data** — collect more balanced, representative data.
- **Remove or handle proxy features** carefully.
- **Set fairness constraints** or adjust thresholds per the situation.
- **Keep human oversight** for decisions that seriously affect people.

## No single definition of "fair"

Fairness can mean different things (equal accuracy across groups, equal error
rates, equal outcomes) and they can **conflict**. There is no purely technical
answer — it's a decision that needs people, context, and often the affected
community's voice.

## Key terms

**Fairness audit**, **Performance by group**, **Proxy feature**, **False
positive/negative by group**, **Fairness trade-off**.

## Practice

A hiring model is 88% accurate overall. Describe exactly what you would measure to
check whether it is fair to men and women — and what result would make you refuse
to deploy it.
""",
    },
    {
        "title": "6.5 Privacy, Security and Data Protection",
        "content": """\
**Learning objective:** Protect people's data and secure your AI system —
responsibilities, not optional extras.

## AI runs on data — often personal

Most useful AI uses data about real people. Handling it carelessly causes real harm
and can break the law. Responsible practice protects data at every stage.

## Privacy principles

- **Collect only what you need** (data minimisation). More data is more risk.
- **Get consent** and be clear about how data will be used.
- **Anonymise / pseudonymise** where possible — remove names and direct
  identifiers.
- **Limit access** — only those who need the data should reach it.
- **Have a retention plan** — delete data when it's no longer needed.
- **Respect rights** — people may have the right to see or delete their data.

Rwanda's **Data Protection Law (2021)** and frameworks like the EU's **GDPR** set
these as legal duties, not just good manners.

## Security of the AI system

- **Protect secrets** — API keys, credentials, and model files. Keep them
  server-side and out of public code (as WAMUGII keeps keys in an env file).
- **Validate all inputs** — never trust incoming data.
- **Guard against prompt injection** (Course 5) when feeding untrusted text to an
  LLM — treat it as data, not instructions.
- **Protect the model** — trained models can leak information about their training
  data; be careful what you expose.
- **Log and audit access** — know who did what.

## The simple test

*Would the person whose data this is be comfortable with how you're storing and
using it?* If not, change your design.

## Key terms

**Data minimisation**, **Consent**, **Anonymisation**, **Data retention**, **Data
protection law (Rwanda 2021 / GDPR)**, **Secret management**, **Access control**.

## Practice

You're building a health-screening model using patient data. List three specific
privacy steps and two security steps you would put in place before it touches real
patient records.
""",
    },
    {
        "title": "6.6 Governance, Law and Accountability",
        "content": """\
**Learning objective:** Understand who is responsible for an AI system and the
rules that increasingly govern it.

## "The algorithm did it" is never an answer

When an AI system causes harm — an unfair rejection, a dangerous mistake — a
**person or organisation is accountable**, never the software. Good governance makes
that responsibility clear *before* anything goes wrong.

## What governance means in practice

- **A named owner.** Someone is responsible for each AI system's behaviour and
  outcomes.
- **Clear purpose and limits.** Write down what the system is for and, just as
  importantly, what it must **not** be used for.
- **Human-in-the-loop for high stakes.** Decisions that seriously affect people
  (health, money, jobs, justice) keep a human making or approving the final call.
- **Approval and review.** High-risk systems are reviewed before launch and
  re-checked over time.
- **A way to contest decisions.** People affected should be able to question a
  decision and reach a human.

## The legal landscape is growing

- **Risk-based regulation** (like the **EU AI Act**) puts stricter rules on
  higher-risk uses (biometrics, hiring, credit, health).
- **Data protection law** (Rwanda 2021, GDPR) governs the personal data AI uses.
- **Sector rules** (finance, health, education) still apply on top of AI-specific
  ones.

Even where local AI law is still forming, these principles are becoming the global
standard — and clients increasingly expect them.

## Transparency to users

People generally have a right to **know when they're dealing with AI** and to get a
**meaningful explanation** of decisions that affect them. Build this in rather than
bolting it on.

## Key terms

**Governance**, **Accountability**, **Named owner**, **Human-in-the-loop**,
**Risk-based regulation (EU AI Act)**, **Right to explanation**, **Auditability**.

## Practice

For an AI system that recommends which students get a scholarship, write a short
governance note: who is accountable, where a human must stay in the loop, what it
must never be used for, and how a rejected student could contest the decision.
""",
    },
    {
        "title": "6.7 Documentation and Reproducibility",
        "content": """\
**Learning objective:** Document AI work so it can be understood, trusted,
reproduced, and maintained.

## If you can't reproduce it, you can't trust it

An AI result that can't be repeated is not science or engineering — it's luck.
**Reproducibility** means someone else (or future you) can run your work and get
the same result. It is the foundation of trustworthy AI.

## What makes work reproducible

- **The code**, in version control (Git).
- **The data** (or a clear description and source of it), and exactly how it was
  prepared.
- **The environment** — the exact library versions (a `requirements.txt`), ideally
  in a container.
- **Random seeds** — set them so "random" steps repeat the same way.
- **The configuration** — settings, thresholds, model version.

## Documenting the model itself

A short **model card** records, in plain language:

- **What** the model does and **who** it's for.
- **The data** it was trained on and any known gaps or biases.
- **How well** it performs — and on which groups.
- **Its limits** — where it should **not** be used.
- **Ethical considerations** and the responsible owner.

This is what lets others use your model safely and know its boundaries.

## Documenting the system

- A clear **README**: what it is, how to set it up, how to run it.
- How to **retrain** and **redeploy**.
- How it is **monitored**, and what to do when something breaks.

Good documentation is a gift to the next person — who is very often **you**, six
months later, having forgotten everything.

## Key terms

**Reproducibility**, **Version control (Git)**, **requirements.txt**, **Random
seed**, **Model card**, **README**.

## Practice

Write a short **model card** (6–8 lines) for the model you built in Course 3:
what it does, its data, its performance, its limits, and who is responsible.
""",
    },
    {
        "title": "6.8 Capstone — Build an End-to-End AI Project (Assessment)",
        "content": """\
**This is your capstone — the final assessment of the whole AI Program.** It brings
together every course: foundations, Python and maths, machine learning, deep
learning, modern AI, and responsible deployment.

## The task

Plan and build a **complete, end-to-end AI project** that solves a **real problem**
you care about — ideally in your own field or community (education, agriculture,
health, security, finance, local services). Deliver the working project and a full
report.

## The project must go from problem to responsible product

1. **Problem & analysis** (Course 1) — the real problem, who it helps, the problem
   type, and an honest judgement that AI is the right tool.
2. **Data** (Courses 2–3) — collect/choose data; clean, explore, and prepare it;
   document what you did and its quality and limits.
3. **Model** (Courses 3–4) — build at least one model (classic ML or a neural
   network, whichever fits); train it and **evaluate it honestly** with the right
   metric and a baseline.
4. **(If suitable) Modern AI** (Course 5) — if your problem suits an LLM/RAG
   solution, build that instead or as well, with safe API use.
5. **Make it usable** (Course 6) — serve the model or app so it can actually be
   used (an API, a script, or a small interface).
6. **Make it responsible** (Course 6) — a **fairness/bias check**, **privacy and
   security** measures, a **governance note** (owner, human-in-the-loop, limits),
   and a plan for **monitoring/drift**.
7. **Document it** (Course 6) — a **README**, a **model card**, and reproducible
   code (Git, pinned dependencies, seeds).

## The report (your defense)

Write it as if presenting to a panel or a client:

- The problem and why it matters.
- Your data, method, and results — with honest numbers.
- The responsible-AI measures you took.
- The **limits** of your system and what you'd do next.

## What excellent work looks like

- It solves a **real** problem, not a toy one.
- Every claim is backed by **honest evidence**.
- It is **responsible by design**, not as an afterthought.
- Someone else could **run and understand** it from your documentation.
- You can clearly explain and **defend** every choice.

## You made it

Finishing this capstone means you can take an AI project from a real-world problem
all the way to a responsible, working, documented product — the complete skill set
of a modern AI practitioner. **Congratulations on completing the WAMUGII AI
Program.** Build something that helps people. 🎓
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
