"""
Seed Course 1 of the WAMUGII AI Program: "AI Foundations".

University-level, rigorous, original WAMUGII content written in simple English.
Safe to re-run (skips if the course already exists):

    python -m app.seed_ai_foundations

On the droplet, run it inside the backend container:

    docker exec wamugii-backend python -m app.seed_ai_foundations
"""

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.models.course import CourseStatus
from app.schemas.course import CourseCreate, LessonCreate

COURSE_SLUG = "ai-foundations"

COURSE = CourseCreate(
    title="AI Foundations",
    slug=COURSE_SLUG,
    category="Artificial Intelligence",
    is_free=True,  # change to a paid course in the admin panel any time
    status=CourseStatus.PUBLISHED,
    display_order=2,  # after AI Career Essentials (1)
    description=(
        "Course 1 of the WAMUGII AI Program. A rigorous, university-level "
        "foundation in artificial intelligence — explained in simple English. "
        "You will learn exactly what AI, machine learning and deep learning are, "
        "how intelligent agents work, the types of AI problems, the full "
        "machine-learning workflow, the role of data, how AI performance is "
        "measured, where AI is used in the real world (including Africa), and "
        "the ethics every AI practitioner must understand. Each lesson has a "
        "clear objective, worked examples, key terms and practice. The course "
        "ends with an AI problem-analysis project. By the end you can explain "
        "AI concepts precisely and correctly categorise any AI problem."
    ),
)

LESSONS = [
    {
        "title": "1.1 What Artificial Intelligence Really Is",
        "content": """\
**Learning objective:** Define AI precisely, tell AI, machine learning and deep
learning apart, and place today's systems on the map.

## A precise definition

Artificial Intelligence (AI) is the study and engineering of **agents that
perceive their environment and take actions to achieve goals** — doing tasks
that normally require human intelligence, such as reasoning, learning,
perception, and decision-making.

Notice what this definition does *not* say: it does not say "a computer that
thinks like a human." AI systems reach goals; *how* they do it need not resemble
human thought at all.

## AI, ML and DL — three circles inside each other

- **Artificial Intelligence (AI)** — the whole field: any technique that makes
  machines act intelligently, including rules written by hand.
- **Machine Learning (ML)** — a *part* of AI where the system **learns patterns
  from data** instead of being told every rule.
- **Deep Learning (DL)** — a *part* of ML that learns using **neural networks
  with many layers**. It powers image recognition, speech, and large language
  models.

So: **DL is inside ML, and ML is inside AI.** All deep learning is machine
learning; not all AI is machine learning.

## Narrow vs General AI

- **Narrow (weak) AI** — built for one task: translation, face recognition,
  playing chess. **Every AI system that exists today is narrow AI.**
- **General AI (AGI)** — a single system as capable as a human across *any*
  task. It does **not** exist yet.
- **Superintelligence** — hypothetical AI beyond human ability. Theory only.

## How we got here (the short history)

- **1950** — Alan Turing asks "Can machines think?" and proposes the Turing Test.
- **1956** — the term "Artificial Intelligence" is coined at the Dartmouth
  workshop.
- **1970s–80s** — "AI winters": progress and funding stall.
- **2012** — deep learning wins the ImageNet image contest by a huge margin; the
  modern boom begins.
- **2017** — the *Transformer* architecture is invented.
- **2020s** — large language models (ChatGPT, Claude, Gemini) reach the public.

**Why now?** Three things arrived together: lots of **data**, powerful
**compute** (GPUs), and better **algorithms**.

## Worked example — classify the technology

| Technology | What is it? |
|---|---|
| A thermostat that switches on at 20°C | Not AI (a fixed rule) |
| A chess engine using search | AI, but not ML |
| A spam filter trained on real emails | AI and ML |
| ChatGPT | AI, ML, and DL |

## Key terms

**AI**, **Machine Learning**, **Deep Learning**, **Narrow AI**, **AGI**,
**Agent**, **Turing Test**.

## Practice

List **three** technologies you use in a normal week. For each, decide: is it
AI? If yes, is it machine learning? Is it deep learning? Write one sentence
explaining your choice.
""",
    },
    {
        "title": "1.2 Intelligent Agents",
        "content": """\
**Learning objective:** Describe any AI system using the agent framework, judge
whether an agent is rational, and classify agent and environment types.

## What is an agent?

An **agent** is anything that **perceives** its environment through **sensors**
and **acts** on that environment through **actuators**.

- A robot: cameras (sensors) and motors (actuators).
- A spam filter: the incoming email (sensor) and the "move to spam" action
  (actuator).

The agent sits in a loop: *perceive → decide → act → perceive again.*

## Rationality

A **rational agent** chooses, for each situation, the action **expected to do
best** according to its **performance measure**, given what it has perceived and
knows.

Rational is **not** the same as perfect or all-knowing. A rational agent can
still fail if the world is unpredictable — it only has to make the best decision
with the information available.

## PEAS — how to describe any agent

Before building an AI system, describe it with **PEAS**:

- **P**erformance measure — how do we score success?
- **E**nvironment — where does it operate?
- **A**ctuators — what can it do?
- **S**ensors — what can it perceive?

## Worked example — PEAS for a self-driving car

- **Performance:** safety, reaching the destination, obeying traffic law,
  comfort, time.
- **Environment:** roads, other cars, pedestrians, weather, signs.
- **Actuators:** steering, accelerator, brakes, indicators.
- **Sensors:** cameras, radar, LiDAR, GPS, speedometer.

## Environment types (know these)

- **Fully vs partially observable** — can the agent see everything it needs?
- **Deterministic vs stochastic** — is the next state certain, or does chance
  play a part?
- **Static vs dynamic** — does the world change while the agent thinks?
- **Discrete vs continuous** — a fixed set of states/actions, or a smooth range?
- **Single vs multi-agent** — is the agent alone, or competing/cooperating?

## Five kinds of agents (simplest to smartest)

1. **Simple reflex** — acts only on the current perception ("if smoke, sound
   alarm").
2. **Model-based reflex** — keeps an internal model of the world it can't fully
   see.
3. **Goal-based** — chooses actions that move it toward a stated goal.
4. **Utility-based** — weighs *how good* each outcome is, not just goal/no-goal.
5. **Learning** — improves its own behaviour over time from experience.

## Key terms

**Agent**, **Sensor**, **Actuator**, **Rational agent**, **Performance
measure**, **PEAS**, **Observable/partial**, **Deterministic/stochastic**.

## Practice

Choose one system (an ATM, a delivery drone, a recommendation feed). Write its
full **PEAS**, then say which **environment types** and which **agent type** it
is. Justify each choice in one line.
""",
    },
    {
        "title": "1.3 The Types of AI Problems",
        "content": """\
**Learning objective:** Recognise which *category* of AI problem you are facing —
the single most useful skill before choosing any tool.

## Why this matters

Beginners ask "which algorithm should I use?" far too early. The right first
question is **"what *type* of problem is this?"** Get that right and the tools
follow. Here are the main categories.

## 1. Classification

Put an input into one of a **fixed set of categories**.
*Example:* is this email spam or not? Is this photo a cat, dog, or bird?

## 2. Regression

Predict a **number** on a continuous scale.
*Example:* what will this house sell for? How many customers tomorrow?

## 3. Clustering

**Group** similar items together **without being told the groups** in advance.
*Example:* segment customers into natural groups from their behaviour.

## 4. Search & Optimisation

Find the **best option** among many possibilities, often under constraints.
*Example:* the shortest delivery route; the best timetable.

## 5. Planning & Sequential Decision-Making

Choose a **sequence of actions** over time to reach a goal, where each action
changes the situation.
*Example:* a robot navigating a warehouse; a game-playing agent.

## 6. Perception (Vision, Speech, Language)

Make sense of **raw signals** — images, sound, text.
*Example:* reading a number plate; transcribing speech; understanding a question.

## 7. Reasoning & Knowledge

Draw **conclusions from facts and rules**.
*Example:* a medical system that infers likely causes from symptoms.

## Worked example — categorise these tasks

| Task | Type |
|---|---|
| Predict a student's final mark (0–100) | Regression |
| Decide if a transaction is fraud | Classification |
| Group villages by farming pattern | Clustering |
| Plan the cheapest bus route across Kigali | Search / Optimisation |
| Transcribe a Kinyarwanda voice note | Perception (speech) |

Some real problems are a **mix** — e.g. a self-driving car does perception *and*
sequential decision-making. Naming the parts is still the first step.

## Key terms

**Classification**, **Regression**, **Clustering**, **Optimisation**,
**Planning**, **Perception**, **Reasoning**.

## Practice

Write down **four** real problems from your studies, work, or community. Label
each with its problem type. If one is a mix, name both parts.
""",
    },
    {
        "title": "1.4 How Machines Learn — The ML Workflow",
        "content": """\
**Learning objective:** Explain the three ways machines learn and walk through
the full machine-learning workflow from problem to deployment.

## Three ways machines learn

- **Supervised learning** — the data has **labels** (the right answers). The
  model learns the mapping from input to answer. *Most practical ML is here.*
  *Example:* emails labelled spam / not-spam.
- **Unsupervised learning** — the data has **no labels**. The model finds
  structure on its own. *Example:* clustering customers.
- **Reinforcement learning** — an agent learns by **trial and error**, receiving
  **rewards** for good actions. *Example:* a game-playing agent.

## The machine-learning workflow (the pipeline)

Real ML work follows these steps, in order. Skipping steps is the most common
beginner mistake.

1. **Define the problem.** What are we predicting? What type is it (Lesson 1.3)?
   What would success look like?
2. **Collect data.** Gather examples relevant to the problem.
3. **Prepare and clean the data.** Fix missing values, remove errors, format
   features. *This is usually the biggest part of the job.*
4. **Split the data.** Set aside a **test set** the model never sees in training
   (more in Lesson 1.5).
5. **Choose a model.** Pick an algorithm suited to the problem type.
6. **Train the model.** Let it learn patterns from the training data.
7. **Evaluate.** Measure performance on the unseen test set (Lesson 1.6).
8. **Tune.** Adjust settings and repeat to improve results.
9. **Deploy.** Put the model to work on real new data.
10. **Monitor.** Watch it over time — the world changes, and models go stale.

## Worked example — predicting if a student will pass

1. **Problem:** predict pass/fail (classification).
2. **Data:** past students' attendance, assignment scores, study hours, result.
3. **Clean:** fill missing attendance, fix wrong entries.
4. **Split:** 80% to train, 20% to test.
5. **Model:** a decision tree.
6. **Train** on the 80%.
7. **Evaluate** on the 20% — say 85% accuracy.
8. **Tune** the tree depth to reduce errors.
9. **Deploy** to flag at-risk students early.
10. **Monitor** each term as teaching changes.

## Key terms

**Supervised**, **Unsupervised**, **Reinforcement learning**, **Label**,
**Training set**, **Test set**, **Model**, **Deployment**.

## Practice

Take one problem you named in Lesson 1.3. Write the **10 workflow steps** for it
in one short line each. Say which of the three learning types it uses.
""",
    },
    {
        "title": "1.5 Data — The Fuel of AI",
        "content": """\
**Learning objective:** Understand features, labels, data quality, and why the
train/validation/test split exists — the ideas that make or break any model.

## Data decides everything

A famous rule: **"garbage in, garbage out."** The best algorithm trained on bad
data gives bad results. In practice, good data matters more than a clever model.

## Features and labels

- A **feature** is one input column — a measurable property of an example
  (age, price, number of logins).
- A **label** is the answer we want to predict (pass/fail, the sale price).

**Example dataset:**

| Attendance % | Assignments done | Study hours | Result (label) |
|---|---|---|---|
| 90 | 8 | 12 | Pass |
| 40 | 3 | 2 | Fail |

Here the first three columns are **features**; "Result" is the **label**.

## Structured vs unstructured data

- **Structured** — neat rows and columns (a spreadsheet, a database table).
- **Unstructured** — text, images, audio, video. More powerful, harder to use.

## Data quality problems to watch for

- **Missing values** — blanks that must be filled or removed.
- **Noise / errors** — wrong or inconsistent entries.
- **Imbalance** — one class is rare (e.g. 1% fraud). This fools "accuracy"
  (Lesson 1.6).
- **Bias** — if the data reflects unfair patterns, the model repeats them.

## The train / validation / test split

We **never** judge a model on the same data it learned from — it could simply
memorise. So we split the data:

- **Training set** (~70%) — the model learns from this.
- **Validation set** (~15%) — used to tune settings while building.
- **Test set** (~15%) — touched **only once, at the end**, to get an honest
  score on data the model has never seen.

**Data leakage** is the dangerous mistake of letting test information sneak into
training. It makes a model look great in testing and fail in the real world.

## Key terms

**Feature**, **Label**, **Structured/Unstructured data**, **Missing values**,
**Class imbalance**, **Bias**, **Training/Validation/Test split**, **Data
leakage**.

## Practice

For a problem of your choice, list the **features** you would collect and the
**label** you would predict. Then write how you would **split** 1,000 examples
into train/validation/test, and name one **data-quality risk** you'd watch for.
""",
    },
    {
        "title": "1.6 Measuring Intelligence and Performance",
        "content": """\
**Learning objective:** Measure a model honestly using the right metric, and spot
overfitting — so you are never fooled by a good-looking but useless model.

## Why "accuracy" can lie

**Accuracy** = correct predictions ÷ total predictions. It sounds perfect, but
it is dangerous with **imbalanced data**.

*Example:* if only 1% of transactions are fraud, a model that says "never fraud"
is **99% accurate** — and completely useless. We need better tools.

## The confusion matrix

For a classification problem, every prediction falls into one of four boxes:

|  | Predicted Positive | Predicted Negative |
|---|---|---|
| **Actually Positive** | True Positive (TP) | False Negative (FN) |
| **Actually Negative** | False Positive (FP) | True Negative (TN) |

From these we build the metrics that matter:

- **Precision** = TP ÷ (TP + FP) — *of the ones we flagged, how many were
  right?* (Few false alarms → high precision.)
- **Recall** = TP ÷ (TP + FN) — *of all the real positives, how many did we
  catch?* (Miss few → high recall.)
- **F1 score** — the balance of precision and recall in one number.

There is usually a **trade-off**: catching more real cases (recall) often means
more false alarms (lower precision). Which matters more depends on the problem —
for disease screening you want high recall; for flagging spam you may want high
precision.

## Metrics for regression (predicting numbers)

- **MAE** (Mean Absolute Error) — average size of the mistakes.
- **RMSE** (Root Mean Squared Error) — like MAE but punishes big mistakes more.

## Overfitting vs underfitting

- **Overfitting** — the model **memorises** the training data, including its
  noise. It scores high on training but **fails on new data**.
- **Underfitting** — the model is too simple to capture the pattern. It does
  **poorly on both** training and new data.
- The goal is **generalisation** — doing well on data it has never seen. This is
  exactly why we keep a test set (Lesson 1.5).

## Worked example — compute precision and recall

A fraud model gives: TP = 80, FP = 20, FN = 40, TN = 860.

- Precision = 80 ÷ (80 + 20) = **0.80**
- Recall = 80 ÷ (80 + 40) = **0.67**

So 80% of flagged transactions really were fraud, but it caught only 67% of all
fraud.

## Key terms

**Accuracy**, **Confusion matrix**, **Precision**, **Recall**, **F1**, **MAE**,
**RMSE**, **Overfitting**, **Underfitting**, **Generalisation**.

## Practice

A disease test gives TP = 45, FP = 15, FN = 5, TN = 135. Compute **accuracy**,
**precision**, and **recall**. Then write one sentence: for a disease test, is
precision or recall more important, and why?
""",
    },
    {
        "title": "1.7 The AI Landscape and Real Applications",
        "content": """\
**Learning objective:** Map the subfields of AI and recognise real applications,
including in Africa — so you can see where AI creates value.

## The main subfields of AI

- **Machine Learning (ML)** — learning patterns from data (the engine of most
  modern AI).
- **Deep Learning (DL)** — ML with multi-layer neural networks; powers vision,
  speech and language.
- **Natural Language Processing (NLP)** — understanding and generating human
  language (translation, chatbots, LLMs).
- **Computer Vision (CV)** — understanding images and video (face recognition,
  medical scans, crop monitoring).
- **Robotics** — agents that sense and act in the physical world.
- **Reinforcement Learning (RL)** — learning by reward through trial and error
  (games, control, logistics).
- **Expert / Knowledge Systems** — reasoning from rules and facts.

## Where AI is used (by sector)

- **Health** — reading X-rays and scans, triage, drug discovery.
- **Agriculture** — detecting crop disease from leaf photos, yield prediction,
  weather-smart advice. *(Very relevant across Africa.)*
- **Finance** — fraud detection, credit scoring, mobile-money security.
- **Education** — at-risk student detection, personalised practice, tutoring.
- **Security** — threat detection, anomaly spotting on networks and IoT devices.
- **Transport** — routing, demand prediction, driver-assist.

## AI in Africa — concrete examples

- **Crop-disease apps** let farmers photograph a leaf and get a diagnosis.
- **Mobile-money fraud detection** protects millions of transactions daily.
- **Health diagnostics** extend scarce specialists to rural clinics.
- **Local-language NLP** (including Kinyarwanda) brings AI to more people.

These show the point: AI is most valuable when pointed at a **real local
problem** with **real local data**.

## The practical toolkit

- **Language:** Python (the standard for AI).
- **Classic ML:** scikit-learn.
- **Deep learning:** TensorFlow, PyTorch.
- **Modern AI / LLMs:** Hugging Face, and model APIs (OpenAI, Anthropic, Google).

You will use these later in the programme — for now, just know the map.

## Key terms

**NLP**, **Computer Vision**, **Robotics**, **Reinforcement Learning**, **Expert
system**, **scikit-learn**, **TensorFlow**, **PyTorch**.

## Practice

Find **one** real AI application in your country or field (ask around, or search).
Write: what problem it solves, which **subfield** it uses, what **data** it needs,
and who benefits. Three or four sentences is enough.
""",
    },
    {
        "title": "1.8 AI Ethics and Responsibility",
        "content": """\
**Learning objective:** Identify the main ethical risks of AI and apply the
principles of responsible AI — because a system that works is not the same as a
system that is right.

## Why ethics is part of the engineering

AI makes decisions that affect real people — who gets a loan, a job, a diagnosis.
If the system is unfair, opaque, or careless with data, it causes real harm, even
when no one intended it. Responsible AI is not an add-on; it is part of building
the system well.

## The main ethical risks

- **Bias and unfairness.** A model learns from data. If the data carries human
  bias (for example past hiring that favoured one group), the model repeats and
  even amplifies it.
- **Lack of transparency.** Many models are "black boxes" — they give an answer
  but can't explain why. For high-stakes decisions, people deserve an
  explanation.
- **Privacy.** AI is hungry for data, often personal. Collecting, storing and
  using it must respect people's rights and the law.
- **Accountability.** When an AI system causes harm, *who is responsible?* It is
  always a person or organisation — never "the algorithm."
- **Safety and misuse.** Powerful tools can be misused (deepfakes,
  misinformation, surveillance). Builders must consider how their work could be
  abused.
- **Impact on work and society.** AI changes jobs and concentrates power.
  Thinking about who gains and who loses is part of responsible practice.

## Principles of responsible AI

1. **Fairness** — test for and reduce bias; check how the system treats
   different groups.
2. **Transparency** — be able to explain what the system does and its limits.
3. **Privacy** — collect only what you need; protect it; get consent.
4. **Accountability** — a named human stays responsible for outcomes.
5. **Safety and reliability** — test thoroughly; plan for failure.
6. **Human oversight** — keep a person in charge of decisions that affect people.

## Worked example — a biased hiring model

A company trains a CV-screening model on 10 years of past hires. Historically it
hired mostly men for technical roles. The model "learns" that pattern and starts
rejecting women's CVs — not because anyone told it to, but because the **data was
biased**. The fix is not just technical (balance the data, test by group); it is
also a decision to keep **human oversight** on hiring.

## Key terms

**Bias**, **Fairness**, **Transparency / explainability**, **Privacy**,
**Accountability**, **Human oversight**, **Responsible AI**.

## Practice

Think of one AI system you know or use. Name **one ethical risk** it carries
(bias, privacy, transparency, misuse…). Then write **one concrete step** its
builders could take to reduce that risk.
""",
    },
    {
        "title": "1.9 Project — AI Problem Analysis (Assessment)",
        "content": """\
**This is your Course 1 assessment.** It brings together everything you have
learned. There is no new theory here — your task is to *apply* the course to a
real problem and produce a clear written analysis.

## The task

Choose **one real problem** from your studies, work, or community that you think
AI could help with. Then write a structured **AI Problem Analysis** (about 1–2
pages) with the sections below. Write in simple, clear language — imagine you are
explaining it to a manager who must decide whether to fund it.

## Required sections

1. **The problem.** What is the real problem, and who has it? Why does it matter?
2. **Is AI the right tool?** Honestly: does this need AI, or would a simple rule
   or better process solve it? (Saying "AI is not needed here" is a valid, strong
   answer if you justify it.)
3. **Problem type.** Classify it using Lesson 1.3 (classification, regression,
   clustering, optimisation, perception, planning, reasoning — or a mix).
4. **The data.** What **features** would you need, and what **label** would you
   predict (Lesson 1.5)? Where would the data come from? Name one data-quality
   risk.
5. **The approach.** Which **learning type** (supervised / unsupervised /
   reinforcement) and roughly what the **ML workflow** would look like
   (Lesson 1.4).
6. **How you'd measure success.** Which **metric** fits, and why (Lesson 1.6)?
7. **Risks and ethics.** Name the main **ethical risks** (Lesson 1.8) and how you
   would reduce them.
8. **Expected impact.** If it worked, what would change, and for whom?

## What good work looks like

- You correctly **name the problem type** and justify it.
- Your **features and label** make sense for the prediction.
- You choose a **sensible metric** and explain the choice (not just "accuracy").
- You identify a **real ethical risk**, not a generic one.
- You are **honest** — including about when AI is *not* the answer.

## Submit

Write it up as a short document and keep it. If you are taking this course with a
WAMUGII tutor, submit it for feedback. Completing this project means you can now
look at almost any real situation and reason clearly about whether and how AI
applies — the true goal of AI Foundations.

**Congratulations on finishing Course 1.** Course 2, *Math & Python for AI*, turns
these ideas into working code.
""",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        existing = course_crud.get_course_by_slug(db, COURSE_SLUG)
        if existing:
            print(f"Course already exists: {existing.title} (slug: {existing.slug})")
            return

        course = course_crud.create_course(db, COURSE)
        print(f"Created course: {course.title} (slug: {course.slug}, status: {course.status.value})")

        for order, lesson in enumerate(LESSONS, start=1):
            created = course_crud.create_lesson(
                db,
                course.id,
                LessonCreate(
                    title=lesson["title"],
                    content=lesson["content"],
                    display_order=order,
                ),
            )
            print(f"  + {created.title}")

        print(
            f"Done. {len(LESSONS)} lessons added. "
            f"AI Foundations is PUBLISHED and live in the catalog."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
