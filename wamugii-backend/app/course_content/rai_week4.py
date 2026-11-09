"""Responsible AI & Deployment -- Week 4: Governance, Documentation and the Capstone. Original WAMUGII content."""

from app.course_content.rai_data import fill

WEEK4 = fill({
    "title": "Week 4 · Governance, Documentation and the Capstone",
    "lessons": [
        # ------------------------------------------------------------------ 19
        {
            "title": "AI Governance, Law and Accountability",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=FLUd0k2ctJE",
            "content": r"""
**Learning objective:** Describe the main AI rules and policies that apply in Rwanda and internationally, decide who is accountable for what, and build a risk register and impact assessment for an AI system.

## Why governance?

Technology alone cannot make AI responsible. Somebody must decide **whether** to use AI for a task, **who** answers when it goes wrong, **how** people can complain, and **when** to stop. That system of roles, rules and records is **AI governance**.

## The rules you should know

| Rule or policy | What it means for builders |
|---|---|
| **Rwanda's Law No. 058/2021** on personal data and privacy | Lawful basis, minimisation, security, data-subject rights, conditions for storing data abroad (Lesson 16) |
| **Rwanda's National AI Policy** (adopted 2023) | Rwanda's plan to use AI for development responsibly: skills, data, infrastructure, investment, and trustworthy AI. In 2026 the Cabinet also approved a **National AI Agency** to coordinate this work |
| **EU AI Act** | A risk-based law: some uses are banned, **high-risk** uses (including credit scoring of people, hiring, education, essential services) have strict duties. It matters if you serve EU customers or partners — and many countries copy its ideas |
| **Sector rules** | Banks, SACCOs, health and telecom have their own regulators and rules (for example the National Bank of Rwanda for financial services) |
| **International principles** | OECD AI Principles, UNESCO Recommendation on the Ethics of AI |

Laws change: before a real project, read the current texts and get legal advice. In the EU AI Act, for example, the duties for high-risk systems such as credit scoring were moved by a 2026 amendment to apply from December 2027.

## Risk levels

The EU AI Act's idea of **risk tiers** is useful everywhere:

| Tier | Examples | What to do |
|---|---|---|
| Unacceptable | Social scoring of citizens, manipulation of vulnerable people | Do not build |
| High | Credit decisions, hiring, school admissions, medical triage | Full documentation, testing, human oversight, monitoring, registration where required |
| Limited | Chatbots, AI-generated content | Tell people they are dealing with AI; label generated content |
| Minimal | Spam filters, game AI | Normal good practice |

Our loan model is **high-risk**: it affects people's access to money.

## Who is accountable?

Every AI system needs named people, not just "the team":

| Role | Responsible for |
|---|---|
| **System owner** (a manager) | The decision to use AI, its purpose and limits; final accountability |
| **Model developer** | Building, testing and documenting the model |
| **Data protection officer** | Lawful use of personal data, privacy reviews, data-subject requests |
| **Operations / IT** | Running, monitoring and securing the service |
| **Reviewers** (loan officers) | Human oversight of decisions and handling appeals |
| **Independent auditor** | Periodic checks of fairness, performance and compliance |

## A risk register

List what could go wrong, how likely and how bad it is, and what you do about it:

```python
import pandas as pd

risks = pd.DataFrame([
    {"risk": "Rural applicants approved less often than fair", "likelihood": 4, "impact": 4,
     "control": "Monthly fairness audit; human review of refused rural applicants", "owner": "Model developer"},
    {"risk": "Concept drift lowers accuracy", "likelihood": 3, "impact": 4,
     "control": "Monthly outcome monitoring; retrain trigger at 5-point drop", "owner": "Operations"},
    {"risk": "Personal data leaked from logs", "likelihood": 2, "impact": 5,
     "control": "Pseudonymised logs; access control; 12-month retention", "owner": "Data protection officer"},
    {"risk": "Applicants game mobile-money activity", "likelihood": 3, "impact": 3,
     "control": "Cap feature effect; monitor sudden jumps", "owner": "Model developer"},
    {"risk": "Service down at month end", "likelihood": 2, "impact": 3,
     "control": "Health checks; fallback to manual process", "owner": "Operations"},
    {"risk": "Staff trust the score blindly", "likelihood": 3, "impact": 4,
     "control": "Training; reason codes; review band (Lesson 21)", "owner": "System owner"},
])
risks["score"] = risks["likelihood"] * risks["impact"]
risks["level"] = pd.cut(risks["score"], [0, 6, 12, 25], labels=["low", "medium", "high"])
print(risks.sort_values("score", ascending=False)[["risk", "score", "level", "owner"]].to_string(index=False))
```

Scores use 1–5 scales: **score = likelihood × impact**. High risks need strong controls before launch; every risk has an **owner**.

## An AI impact review

Before building, answer in writing:

```python
ASSESSMENT = {
    "Purpose": "Help loan officers judge repayment risk faster and more consistently.",
    "Decision supported": "Approve, or refer to an officer. The model never refuses on its own.",
    "People affected": "SACCO loan applicants, including rural members and women.",
    "Data used": "Income, loan amount, membership years, late payments, salary status, mobile-money activity.",
    "Data NOT used": "Name, phone, national ID, gender, area, age (kept separately for audits only).",
    "Risk tier": "High (credit decision).",
    "Main risks": ", ".join(risks.sort_values("score", ascending=False)["risk"].head(3)),
    "Human oversight": "Officers review every refused or borderline case; applicants can appeal.",
    "Go/no-go criteria": "AUC >= 0.80, disparate impact >= 0.8 by area and gender, all high risks controlled.",
    "Review date": "Every 3 months and after every retraining.",
}
for k, v in ASSESSMENT.items():
    print(f"{k}: {v}")
```

## Key terms

- **AI governance** — the roles, rules and records that control how AI is used.
- **Risk-based regulation** — stricter rules for higher-risk uses.
- **High-risk system** — AI that affects important life decisions such as credit, jobs or health.
- **Accountability** — named people answer for outcomes.
- **Risk register** — a list of risks with likelihood, impact, controls and owners.
- **Impact assessment** — a written review of purpose, people affected, risks and safeguards before deployment.

**Takeaway:** Responsible AI needs governance: know the laws and policies, classify the risk, name accountable owners, keep a risk register, and assess impact before you deploy.

## Try it yourself

1. Add two risks of your own to the register and give each an owner.
2. Classify these by risk tier: a school timetable optimiser, a CV-screening tool, a crop-disease photo app, a chatbot for a bank.
3. Read Rwanda's National AI Policy summary and list three priorities that relate to your capstone idea.
4. Write the impact assessment for your own capstone idea.
""",
            "quiz": [
                ("What is AI governance?",
                 ["A type of neural network", "The roles, rules and records that control how AI is used", "A programming language", "A server setting"],
                 1, "Technology alone cannot make AI responsible."),
                ("In the EU AI Act's approach, what tier is credit scoring of people?",
                 ["Minimal", "Limited", "High-risk", "Banned"],
                 2, "It affects access to essential services."),
                ("Which Rwandan policy sets the national direction for AI?",
                 ["The National AI Policy, adopted in 2023", "The Road Traffic Policy", "There is none", "The Tax Policy"],
                 0, "A National AI Agency was also approved in 2026."),
                ("How is a risk score calculated in the register?",
                 ["Likelihood + impact", "Likelihood × impact", "Impact ÷ likelihood", "Random"],
                 1, "Each on a 1–5 scale."),
                ("Why must every risk have an owner?",
                 ["For decoration", "So a named person is accountable for controlling it", "Laws forbid teams", "To save money"],
                 1, "'The team' is not accountable."),
                ("In the impact assessment, what does the model never do on its own?",
                 ["Compute scores", "Refuse a loan", "Log requests", "Use income"],
                 1, "Refusals go to a human officer."),
            ],
        },
        # ------------------------------------------------------------------ 20
        {
            "title": "Documentation: Model Cards and Datasheets",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=dQHjntrqrFQ",
            "content": r"""
**Learning objective:** Write a datasheet for a dataset and a model card for a model, generate them automatically from real metrics, and keep them up to date with every release.

## Why documentation?

Imagine a new developer, an auditor or a regulator in two years. They need to know: what is this model for, what data built it, how good is it, for whom does it work less well, and what must it **not** be used for? Two widely used formats answer these questions:

- **Datasheets for Datasets** (Gebru and colleagues, 2018): how a dataset was collected, what it contains, its limits and allowed uses.
- **Model Cards for Model Reporting** (Mitchell and colleagues, 2019): a short document about one model — intended use, performance broken down by group, limitations and ethical considerations.

Hugging Face shows a model card on every model page — you have seen them in Course 6.

{APPLICANTS}

{MODEL}

## A datasheet, generated from the data

```python
def datasheet(df, name):
    lines = [f"# Datasheet: {name}", "",
             "## Motivation", "Created to train and audit a loan-repayment model for a SACCO (practice data, no real people).", "",
             "## Composition", f"- Rows: {len(df):,}", f"- Columns: {len(df.columns)}"]
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            info = f"min {s.min():,.0f}, median {s.median():,.0f}, max {s.max():,.0f}"
        else:
            info = ", ".join(f"{k} {v:.0%}" for k, v in s.value_counts(normalize=True).items())
        lines.append(f"- `{col}`: {info}; missing {s.isna().mean():.0%}")
    lines += ["", "## Known issues",
              "- `approved_before` records past officer decisions that were unfair to rural applicants and women.",
              "- Rural applicants have lower incomes and fewer salaried jobs; several features act as proxies for area.",
              "", "## Allowed uses", "Training and auditing credit-risk models with human review. Not for marketing or for decisions without review.",
              "", "## Personal data", "Contains no names or contact details. Gender, area and age are kept for fairness audits only."]
    return "\n".join(lines)

sheet = datasheet(applicants, "SACCO loan applications v1")
open("DATASHEET.md", "w").write(sheet)
print(sheet)
```

## A model card, generated from the metrics

```python
def group_metrics(data, group, approved):
    out = []
    for name, g in data.assign(approved=approved).groupby(group):
        out.append(f"| {group} = {name} | {len(g)} | {g['approved'].mean():.1%} | "
                   f"{g.loc[g[TARGET] == 1, 'approved'].mean():.1%} | {roc_auc_score(g[TARGET], g['score']):.3f} |")
    return out

scored = test.assign(score=model.predict_proba(test[FEATURES])[:, 1])
approved = (scored["score"] >= 0.5).astype(int)

card = "\n".join([
    "# Model card: loan-repayment v1.0.0", "",
    "## Intended use",
    "- Supports SACCO loan officers by estimating the probability that an applicant repays.",
    "- Output: approve, or refer to an officer. **The model never refuses a loan on its own.**", "",
    "## Out-of-scope uses",
    "- Fully automatic refusals; marketing; employment or insurance decisions; applicants outside the SACCO.", "",
    "## Model", f"- Logistic regression on standardised features: {', '.join(FEATURES)}.",
    "- Gender, area and age are NOT inputs.", "",
    "## Data", "- Trained on 2,250 applications; tested on 750. See DATASHEET.md.", "",
    "## Performance (test set)",
    f"- AUC {roc_auc_score(test[TARGET], scored['score']):.3f}, accuracy {accuracy_score(test[TARGET], approved):.3f}", "",
    "## Performance by group",
    "| Group | People | Approval rate | Approved if would repay | AUC |", "|---|---|---|---|---|",
    *group_metrics(scored, "area", approved), *group_metrics(scored, "gender", approved), "",
    "## Limitations and ethical considerations",
    "- Rural applicants are approved less often (disparate impact below 0.8); human review of refused rural applicants is required.",
    "- Performance will fall under concept drift; outcomes are monitored monthly.",
    "- Mobile-money activity can be inflated by applicants; its effect is monitored.", "",
    "## Owners", "- System owner: SACCO credit manager. Developer: data team. Next review: in 3 months.",
])
open("MODEL_CARD.md", "w").write(card)
print(card)
```

Because the card is **generated by code** from the real metrics, it cannot become out of date: regenerate it in CI for every release (Lesson 7) and store it next to the model in the registry (Lesson 8).

## What makes good documentation

- **Honest:** includes weaknesses and groups where the model works less well.
- **Specific:** numbers, dates, versions, owners — not "the model is fair".
- **For its readers:** a short summary for managers, details for auditors.
- **Versioned:** one card per model version.

## Key terms

- **Datasheet** — documentation of a dataset's origin, contents, limits and uses.
- **Model card** — documentation of a model's use, performance by group, limits and ethics.
- **Intended use / out-of-scope use** — what the model is and is not for.
- **Disaggregated metrics** — performance reported separately for each group.

**Takeaway:** Document datasets with datasheets and models with model cards, generate them from real metrics in every release, and be honest about limits.

## Try it yourself

1. Add an "age band" section to the model card's group table.
2. Add a "Change log" section listing what changed since the previous version.
3. Write a five-sentence summary of the model card for the SACCO board.
4. Find a model card on Hugging Face and list which of our sections it has and which it misses.
""",
            "quiz": [
                ("What is a model card?",
                 ["A business card", "A short document about a model's use, performance by group, limits and ethics", "A graphics card", "A data table"],
                 1, "Mitchell and colleagues, 2019."),
                ("What does a datasheet describe?",
                 ["A spreadsheet's colours", "How a dataset was collected, what it contains, its limits and allowed uses", "Model weights", "Server specifications"],
                 1, "Gebru and colleagues, 2018."),
                ("Why generate the model card with code?",
                 ["It looks nicer", "It always uses the real, current metrics and cannot go out of date", "Laws require Python", "To hide limits"],
                 1, "Regenerate it in CI for every release."),
                ("What is an out-of-scope use?",
                 ["The main use", "A use the model is not designed or approved for", "A test", "A server error"],
                 1, "For example, fully automatic refusals."),
                ("Why report performance by group?",
                 ["To make the card longer", "Average performance can hide groups for whom the model works less well", "It is faster", "Groups never differ"],
                 1, "Disaggregated metrics."),
                ("Which is a sign of good documentation?",
                 ["It hides weaknesses", "It is honest, specific and versioned", "It says 'the model is fair' with no numbers", "It is never updated"],
                 1, "Honesty and specifics build trust."),
            ],
        },
        # ------------------------------------------------------------------ 21
        {
            "title": "Human Oversight and Safe Failure",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=EUXevpbMFHU",
            "content": r"""
**Learning objective:** Design how people and models work together: a review band for uncertain cases, appeals, overrides, fallbacks when the model fails, and measures of whether oversight really works.

## Humans in the loop — for real

"A human checks the decisions" often means a tired person clicking "approve" on 300 scores a day. Real oversight needs design:

- The model decides only where it is **confident**; uncertain cases go to people.
- People get **reasons** (Lesson 15), not just a number.
- People have time, training and the **authority to disagree**.
- Applicants can **appeal**, and appeals are tracked.
- When the model is down or wrong, there is a **fallback**.

{APPLICANTS}

{MODEL}

## A review band

```python
scores = model.predict_proba(test[FEATURES])[:, 1]

def route(score, low, high):
    if score >= high:
        return "approve"
    if score <= low:
        return "decline"                      # in our policy: decline means "refer with reasons", never silent
    return "human review"

rows = []
for low, high in [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8)]:
    routes = np.array([route(s, low, high) for s in scores])
    auto = routes != "human review"
    correct = (routes[auto] == "approve") == (test[TARGET].values[auto] == 1)
    rows.append({"band": f"{low}-{high}", "automated": f"{auto.mean():.0%}",
                 "accuracy on automated cases": f"{correct.mean():.1%}",
                 "cases for people per 1,000": int(round((~auto).mean() * 1000))})
print(pd.DataFrame(rows).to_string(index=False))
```

Wider bands mean the automated decisions are more accurate — but people must review more cases. Choose the band from your staff's real capacity, and give reviewers the hard cases with reasons attached.

## Which group lands in the review band?

```python
band = (scores > 0.3) & (scores < 0.7)
print(test.assign(in_band=band).groupby("area")["in_band"].mean().round(3).to_dict())
```

Here rural applicants land in the review band more often than urban ones (about 27% against 20%). If one group is sent to review much more often, they wait longer — another fairness question to watch.

## Overrides teach you something

When reviewers disagree with the model, record it:

```python
rng = np.random.default_rng(5)
reviewed = test[band].assign(score=scores[band])
reviewed["officer_decision"] = np.where(rng.random(len(reviewed)) < 0.5 + (reviewed["score"] - 0.5), "approve", "decline")
reviewed["model_suggestion"] = np.where(reviewed["score"] >= 0.5, "approve", "decline")
override = reviewed["officer_decision"] != reviewed["model_suggestion"]
print(f"override rate: {override.mean():.0%} of {len(reviewed)} reviewed cases")
for who in ["model_suggestion", "officer_decision"]:
    acc = ((reviewed[who] == "approve") == (reviewed[TARGET] == 1)).mean()
    print(f"accuracy of {who}: {acc:.1%}")
```

In this simulation the officers' decisions are **less** accurate than the model's suggestions on the reviewed cases — a sign they need better reasons or training. Track overrides and their outcomes. If officers are often right when they override, learn why — maybe the model misses information. If they are often wrong, they may need training or better reasons. An override rate near **0%** can mean "rubber-stamping": people no longer think.

## Safe failure

```python
def decide(applicant, model_available=True):
    try:
        if not model_available:
            raise RuntimeError("model service unreachable")
        p = float(model.predict_proba(pd.DataFrame([applicant])[FEATURES])[0, 1])
        return {"route": route(p, 0.3, 0.7), "source": "model", "score": round(p, 2)}
    except Exception as exc:
        # fallback: simple, written rules + a person; never a silent refusal
        risky = applicant["loan_rwf"] > 3 * applicant["income_rwf"] or applicant["late_payments"] >= 3
        return {"route": "human review", "source": f"fallback ({exc})", "flag": "high risk" if risky else "normal"}

a = {"income_rwf": 300_000, "loan_rwf": 250_000, "years_member": 4, "late_payments": 1, "salaried": 1, "momo_tx_month": 35}
print(decide(a))
print(decide(a, model_available=False))
```

When the model fails, the service still works — with simple written rules and a person. Never let a technical failure turn into automatic refusals.

## Appeals

Every applicant who is declined should receive: the main reasons, how to appeal, and the time limit for an answer. Track appeals: how many, how long they take, and how many change the decision — by group.

## Key terms

- **Human oversight** — people able to understand, check and override AI decisions.
- **Review band** — scores where the model does not decide and a person does.
- **Override** — a person changes the model's suggestion.
- **Automation bias** — trusting a machine's answer too much.
- **Fallback** — what happens when the model is unavailable or unreliable.
- **Appeal** — a person's right to ask for a decision to be reviewed.

**Takeaway:** Design oversight on purpose — a review band sized to real capacity, reasons for reviewers, tracked overrides and appeals, and a safe fallback that never refuses silently.

## Try it yourself

1. With 20 officers reviewing 15 cases each per day and 1,000 applications per day, which band can you afford?
2. Make the simulated officers better than the model and check what the numbers show.
3. Add an "appeal" field to `decide` that tells declined applicants how to appeal.
4. Write the fallback rules for your own capstone system.
""",
            "quiz": [
                ("What is a review band?",
                 ["A music group", "A range of scores where a person, not the model, decides", "A server limit", "A data column"],
                 1, "Uncertain cases go to people."),
                ("What happens when the review band gets wider?",
                 ["Automated decisions get less accurate", "Automated decisions get more accurate but people review more cases", "Nothing", "The model retrains"],
                 1, "Choose it from real staff capacity."),
                ("What can an override rate near 0% suggest?",
                 ["Perfect model", "Rubber-stamping: people no longer really check", "Too many officers", "A network error"],
                 1, "Automation bias."),
                ("What should happen if the model service is down?",
                 ["Refuse everyone", "Fall back to simple written rules and a person", "Approve everyone", "Shut the SACCO"],
                 1, "Never turn a failure into silent refusals."),
                ("What should a declined applicant receive?",
                 ["Nothing", "The main reasons, how to appeal and the time limit", "Only the score", "An advert"],
                 1, "Appeals are part of oversight."),
                ("What is automation bias?",
                 ["A faster computer", "Trusting a machine's answer too much", "A type of drift", "A fairness metric"],
                 1, "Real oversight needs time, training and authority to disagree."),
            ],
        },
        # ------------------------------------------------------------------ 22
        {
            "title": "Planning Your Capstone Project",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=4mGvH3ms6B8",
            "content": r"""
**Learning objective:** Choose a valuable, feasible and responsible capstone problem, define success measures and baselines, plan data, risks and timeline, and get your plan approved.

## What the capstone is

Your capstone is one end-to-end AI project that brings the whole WAMUGII AI Program together: a real problem, real or realistic data, a model (classic ML, deep learning or an LLM application), an API, tests, monitoring, a fairness and privacy review, documentation and a presentation.

## Choosing the problem

A good capstone problem is:

1. **Valuable** — someone real has this problem and would use the result.
2. **Feasible** — you can get the data and build it in about two weeks.
3. **Measurable** — you can tell whether it works.
4. **Responsible** — you can manage its risks; avoid unacceptable uses.

Ideas that fit Rwanda and the region:

| Idea | Type | Data |
|---|---|---|
| Crop-disease detection from leaf photos | Image classification (Course 5) | Public plant-disease image sets + your own photos |
| Support-ticket router for a company or school | Text classification or LLM (Courses 4–6) | Anonymised past tickets |
| Ask-the-handbook assistant for a school or SACCO | RAG (Course 6) | Policies you are allowed to use |
| Mobile-money transaction anomaly alerts | Anomaly detection (Course 4) | Synthetic or anonymised data |
| Student drop-out early warning | Classification + fairness (this course) | Anonymised school records, with permission |
| Clinic appointment no-show prediction | Classification | Anonymised records, with permission |

## The one-page canvas

```python
CANVAS = {
    "Problem": "Small clinics lose time when patients miss appointments.",
    "Users": "Clinic receptionists, who call patients the day before.",
    "Decision supported": "Which patients to call first (never: refuse care).",
    "Success measure": "Recall of no-shows in the top 20% called, compared with calling at random.",
    "Baseline to beat": "Call the patients with the most past no-shows.",
    "Data": "Anonymised appointment records from one partner clinic, with written permission.",
    "Model": "Logistic regression first; gradient boosting if clearly better.",
    "Delivery": "FastAPI service + simple daily call list.",
    "Risks": "Privacy of health data; unfair targeting by area; staff over-trust.",
    "Ethics checks": "Fairness by area and age; data protection review; human always decides.",
}
missing = [k for k, v in CANVAS.items() if not v.strip()]
print("canvas complete" if not missing else f"missing: {missing}")
for k, v in CANVAS.items():
    print(f"{k:20s} {v}")
```

## Always beat a baseline

Before any model, compute what a simple rule achieves. If your model cannot beat it, it is not worth deploying:

{APPLICANTS}

```python
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried", "momo_tx_month"]
tr, te = train_test_split(applicants, test_size=0.25, random_state=0, stratify=applicants["repaid"])

majority = DummyClassifier(strategy="most_frequent").fit(tr[FEATURES], tr["repaid"])
rule = ((te["loan_rwf"] <= 2 * te["income_rwf"]) & (te["late_payments"] <= 1)).astype(int)
lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(tr[FEATURES], tr["repaid"])

print(f"always 'repays':        accuracy {accuracy_score(te['repaid'], majority.predict(te[FEATURES])):.3f}")
print(f"simple written rule:    accuracy {accuracy_score(te['repaid'], rule):.3f}")
print(f"logistic regression:    accuracy {accuracy_score(te['repaid'], lr.predict(te[FEATURES])):.3f} "
      f"(AUC {roc_auc_score(te['repaid'], lr.predict_proba(te[FEATURES])[:, 1]):.3f})")
```

Guessing "everyone repays" is already right two times out of three, so "67% accuracy" would be worthless. Our model clearly beats both baselines — that is the evidence a project needs.

## Plan the two weeks

```python
plan = pd.DataFrame([
    ("Day 1-2", "Canvas approved, data access and permissions, datasheet draft"),
    ("Day 3-4", "Data cleaning and validation, baselines"),
    ("Day 5-7", "Models, experiment tracking, choose the simplest good model"),
    ("Day 8", "Fairness, explainability and privacy review"),
    ("Day 9-10", "API, tests, Docker package, monitoring plan"),
    ("Day 11", "Model card, risk register, impact assessment"),
    ("Day 12-13", "Report and presentation; rehearse the demo"),
    ("Day 14", "Present; submit code, report and documents"),
], columns=["When", "What"])
print(plan.to_string(index=False))
```

## Get approval before you build

Send your instructor the canvas, data source and permission, the baseline, and your top three risks with controls. If a project uses personal data, health data or affects important decisions, extra care is needed — or choose synthetic data.

## Key terms

- **Capstone** — a final project that combines everything you learned.
- **Project canvas** — a one-page plan of problem, users, data, measures and risks.
- **Baseline** — the result of a simple method your model must beat.
- **Success measure** — the number that shows whether the project works.
- **Feasibility** — whether the project can be done with the time and data available.

**Takeaway:** Choose a valuable, feasible, measurable and responsible problem, define success and a baseline first, plan the two weeks, and get approval before building.

## Try it yourself

1. Fill in the canvas for your own capstone idea.
2. Write your success measure and baseline in one sentence each.
3. List your data source, who owns it, and what permission you have.
4. Post your canvas in the lesson Q&A and ask a classmate for one improvement.
""",
            "quiz": [
                ("Which is NOT one of the four qualities of a good capstone problem?",
                 ["Valuable", "Feasible", "Measurable", "As complex as possible"],
                 3, "Valuable, feasible, measurable and responsible."),
                ("Why compute a baseline first?",
                 ["To slow the project", "Your model is only worth deploying if it beats a simple method", "Baselines are always best", "It is required by Docker"],
                 1, "Evidence that the model adds value."),
                ("Guessing 'everyone repays' gave about what accuracy?",
                 ["10%", "About 67%", "100%", "50% exactly"],
                 1, "So 67% accuracy alone would be worthless."),
                ("What should you send your instructor before building?",
                 ["Nothing", "Canvas, data permission, baseline and top risks", "Only the final code", "Your password"],
                 1, "Approval before effort."),
                ("What should you do if your project needs sensitive personal data you cannot protect?",
                 ["Use it anyway", "Take extra care and get permission — or use synthetic data", "Post it online", "Ignore privacy"],
                 1, "Responsible by design."),
                ("Which model should you try first in most capstones?",
                 ["The biggest neural network", "A simple model such as logistic regression", "No model", "A random guess"],
                 1, "Then move up only if clearly better."),
            ],
        },
        # ------------------------------------------------------------------ 23
        {
            "title": "Capstone Build: An End-to-End Reference Project",
            "minutes": 150,
            "video": "https://www.youtube.com/watch?v=KGpg8jwAda4",
            "content": r"""
**Learning objective:** Follow a complete reference implementation — validated data, tracked training, quality and fairness gates, documentation, a secure API with monitoring, and tests — and adapt it to your own capstone.

## The reference system

This notebook builds the whole SACCO system in one run. Use it as a **template**: replace the data and features with your own, keep the structure.

{APPLICANTS}

## Step 1 — Settings and data checks

```python
import hashlib, json, os, pathlib, secrets, time
import joblib
from collections import defaultdict, deque
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CONFIG = {"version": "2.0.0", "features": ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried"],
          "target": "repaid", "seed": 0, "threshold": 0.5, "review_band": [0.35, 0.65],
          "gates": {"min_auc": 0.80, "min_disparate_impact": 0.80}}
F, T = CONFIG["features"], CONFIG["target"]
OUT = pathlib.Path("capstone"); OUT.mkdir(exist_ok=True)

assert applicants[F + [T]].notna().all().all(), "missing values"
assert applicants["income_rwf"].gt(0).all() and applicants["loan_rwf"].gt(0).all(), "bad amounts"
print("data checks passed")
```

## Step 2 — Train and track

```python
tr, te = train_test_split(applicants, test_size=0.25, random_state=CONFIG["seed"], stratify=applicants[T])
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(tr[F], tr[T])
scores = model.predict_proba(te[F])[:, 1]
approved = (scores >= CONFIG["threshold"]).astype(int)
metrics = {"auc": round(roc_auc_score(te[T], scores), 3), "accuracy": round(accuracy_score(te[T], approved), 3)}
fingerprint = hashlib.sha256(pd.util.hash_pandas_object(tr, index=False).values.tobytes()).hexdigest()[:16]
with open(OUT / "runs.jsonl", "a") as f:
    f.write(json.dumps({"config": CONFIG, "metrics": metrics, "data": fingerprint}) + "\n")
print(metrics)
```

Notice version 2.0.0 drops mobile-money activity, following the Week 3 audit.

## Step 3 — Quality and fairness gates

```python
def disparate_impact(data, group, decision):
    rates = data.assign(d=decision).groupby(group)["d"].mean()
    return round(float(rates.min() / rates.max()), 3)

fair = {g: disparate_impact(te, g, approved) for g in ["area", "gender"]}
gates = {f"AUC {metrics['auc']} >= {CONFIG['gates']['min_auc']}": metrics["auc"] >= CONFIG["gates"]["min_auc"]}
gates.update({f"disparate impact by {g} {v} >= {CONFIG['gates']['min_disparate_impact']}": v >= CONFIG["gates"]["min_disparate_impact"]
              for g, v in fair.items()})
for name, ok in gates.items():
    print("PASS" if ok else "FAIL", name)
RELEASE = all(gates.values())
print("release allowed" if RELEASE else "release BLOCKED")
```

## Step 4 — Save the artifact and the model card

```python
joblib.dump(model, OUT / "model.joblib")
meta = {**CONFIG, "metrics": metrics, "fairness": fair, "data_fingerprint": fingerprint, "released": RELEASE}
(OUT / "metadata.json").write_text(json.dumps(meta, indent=2))
(OUT / "MODEL_CARD.md").write_text("\n".join([
    f"# Model card: loan-repayment v{CONFIG['version']}",
    "Intended use: support loan officers; scores in the review band go to a person; no automatic refusals.",
    f"Features: {', '.join(F)} (no gender, area, age or mobile-money activity).",
    f"Performance: AUC {metrics['auc']}, accuracy {metrics['accuracy']}.",
    f"Disparate impact: {fair}.",
    "Limits: monitor concept drift monthly; human review of all refusals.",
]))
print(sorted(p.name for p in OUT.iterdir()))
```

## Step 5 — A secure, monitored API

```python
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

KEY = os.environ.get("CAPSTONE_API_KEY") or secrets.token_hex(16)
SALT = os.environ.get("LOG_SALT", "demo-salt").encode()
LOGS, calls = [], defaultdict(deque)
scorer = joblib.load(OUT / "model.joblib")

class Applicant(BaseModel):
    applicant_id: int
    income_rwf: float = Field(..., ge=10_000, le=20_000_000)
    loan_rwf: float = Field(..., ge=10_000, le=5_000_000)
    years_member: int = Field(..., ge=0, le=60)
    late_payments: int = Field(..., ge=0, le=50)
    salaried: int = Field(..., ge=0, le=1)

def auth(x_api_key: str = Header(default="")):
    if not secrets.compare_digest(x_api_key, KEY):
        raise HTTPException(401, "Missing or wrong API key")
    q, now = calls[x_api_key], time.time()
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= 30:
        raise HTTPException(429, "Too many requests")
    q.append(now)

app = FastAPI(title="SACCO loan support", version=CONFIG["version"])

@app.get("/health")
def health():
    return {"status": "ok", "version": CONFIG["version"]}

@app.post("/decide", dependencies=[Depends(auth)])
def decide(a: Applicant):
    start = time.perf_counter()
    p = float(scorer.predict_proba(pd.DataFrame([a.model_dump()])[F])[0, 1])
    low, high = CONFIG["review_band"]
    route = "approve" if p >= high else "human review"           # no automatic refusals
    LOGS.append({"who": hashlib.sha256(SALT + str(a.applicant_id).encode()).hexdigest()[:12],
                 "score": round(p, 3), "route": route, "ms": round((time.perf_counter() - start) * 1000, 2),
                 "version": CONFIG["version"]})
    return {"route": route, "version": CONFIG["version"]}

@app.get("/metrics", dependencies=[Depends(auth)])
def metrics_endpoint():
    df = pd.DataFrame(LOGS)
    if df.empty:
        return {"requests": 0}
    return {"requests": len(df), "approve_rate": round(float((df["route"] == "approve").mean()), 3),
            "p95_ms": round(float(df["ms"].quantile(0.95)), 2)}
```

## Step 6 — Test everything

```python
api = TestClient(app)
H = {"X-API-Key": KEY}
sample = te.head(20)
for _, r in sample.iterrows():
    body = {"applicant_id": int(r["applicant_id"]), **{f: (int(r[f]) if f in ("years_member", "late_payments", "salaried") else float(r[f])) for f in F}}
    api.post("/decide", json=body, headers=H)

tests = {
    "health works": api.get("/health").status_code == 200,
    "no key is refused": api.post("/decide", json=body).status_code == 401,
    "bad input is refused": api.post("/decide", json={**body, "income_rwf": 5}, headers=H).status_code == 422,
    "no automatic refusals": all(l["route"] in ("approve", "human review") for l in LOGS),
    "logs hold no raw IDs": all(str(int(r["applicant_id"])) != l["who"] for l, (_, r) in zip(LOGS, sample.iterrows())),
    "metrics endpoint works": api.get("/metrics", headers=H).json()["requests"] == 20,
    "gates passed": RELEASE,
}
for name, ok in tests.items():
    print(("PASS  " if ok else "FAIL  ") + name)
print(api.get("/metrics", headers=H).json())
```

## Adapting it to your capstone

| Keep | Replace |
|---|---|
| The seven-step structure | Data, features, target |
| Gates (quality + fairness) | Thresholds that fit your problem |
| Model card, metadata, run log | The text describing your use and limits |
| API key, rate limit, validation, pseudonymised logs | Field names and limits |
| Tests | Add tests for your own behaviour rules |

Then add the Docker package from Lesson 5 and the CI workflow from Lesson 7.

**Takeaway:** A capstone-quality AI system is a chain — checked data, tracked training, gates, documentation, a secure monitored API and tests — and this template gives you every link.

## Try it yourself

1. Run the template with the mobile-money feature added back. Which gate changes?
2. Change the review band to 0.45–0.55. What happens to the approve rate in `/metrics`?
3. Replace the SACCO data with your own capstone data and get all tests to pass.
4. Add a Dockerfile and a GitHub Actions workflow to the `capstone/` folder.
""",
            "quiz": [
                ("Why does version 2.0.0 drop the mobile-money feature?",
                 ["To save memory", "Following the Week 3 audit findings on fairness and gaming", "It was always missing", "By accident"],
                 1, "Audit findings should change the next version."),
                ("What happens if a gate fails in Step 3?",
                 ["The model is released anyway", "The release is blocked", "The data is deleted", "The API restarts"],
                 1, "Gates stop unsafe releases."),
                ("What does the capstone API return for uncertain or low scores?",
                 ["Decline", "Human review", "An error", "Nothing"],
                 1, "No automatic refusals."),
                ("Why do the logs store a salted hash instead of the applicant ID?",
                 ["Hashes are shorter", "To protect privacy while still allowing linking", "IDs are wrong", "It is faster"],
                 1, "Pseudonymised logs."),
                ("Which status code does the API return without an API key?",
                 ["200", "401", "422", "429"],
                 1, "401 Unauthorized."),
                ("What should you keep when adapting the template?",
                 ["Only the SACCO data", "The structure: checks, gates, documentation, secure API and tests", "Nothing", "Only the model"],
                 1, "Replace data and thresholds, keep the chain."),
            ],
        },
        # ------------------------------------------------------------------ 24
        {
            "title": "Capstone Presentation, Final Exam and Certificate",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=9B02MzWwkSo",
            "content": r"""
**Learning objective:** Present your capstone clearly and honestly, check your submission is complete, prepare for the final exam, and plan your next steps after the WAMUGII AI Program.

## The capstone report

Write 6–10 pages, in simple English, with these sections:

1. **Summary** — the problem, what you built, the result in one number, and your recommendation.
2. **Problem and users** — who has the problem and how it is solved today.
3. **Data** — source, permission, datasheet summary, cleaning and validation.
4. **Approach** — baselines, models tried (from your run log), the chosen model and why.
5. **Results** — metrics on unseen data, compared with the baseline.
6. **Responsible AI** — fairness by group, explanations, privacy, security, human oversight.
7. **Deployment** — API, tests, Docker, monitoring plan and alert rules.
8. **Governance** — risk register, impact assessment, model card, owners.
9. **Limitations and next steps** — what does not work yet, and what you would do with more time.

## The ten-minute presentation

| Minutes | Content |
|---|---|
| 1 | The problem, told as a short story about one user |
| 2 | Data and approach — one slide, no code |
| 2 | **Live demo**: one good case, one hard case, one refused input |
| 2 | Results vs baseline, and fairness by group |
| 2 | Risks, controls and limitations — honestly |
| 1 | What you recommend and what you need |

Tips: practise the demo twice, have screenshots ready in case the internet fails, and answer "I don't know yet — here is how I would find out" when you do not know.

## Check your submission

```python
import pathlib

REQUIRED = {
    "README.md": "how to install, train, test and run",
    "requirements.txt": "pinned library versions",
    "Dockerfile": "packaging",
    "DATASHEET.md": "dataset documentation",
    "MODEL_CARD.md": "model documentation",
    "RISK_REGISTER.csv": "risks, controls and owners",
    "tests": "automated tests (folder)",
    "report.pdf": "the written report",
}

def check_submission(folder):
    root = pathlib.Path(folder)
    missing = [name for name in REQUIRED if not (root / name).exists()]
    for name, why in REQUIRED.items():
        print(("[x] " if name not in missing else "[ ] ") + f"{name:18s} {why}")
    return missing

demo = pathlib.Path("my_capstone"); (demo / "tests").mkdir(parents=True, exist_ok=True)
for name in ["README.md", "requirements.txt", "Dockerfile", "MODEL_CARD.md"]:
    (demo / name).write_text("draft\n")
missing = check_submission(demo)
print("\nREADY TO SUBMIT" if not missing else f"\nstill missing: {', '.join(missing)}")
```

Run `check_submission` on your own project folder before you submit.

## Marking rubric

| Area | Weight | Excellent work |
|---|---|---|
| Problem and value | 10% | Real users, clear success measure, beats a baseline |
| Technical quality | 25% | Clean data, sound modelling, reproducible, tested |
| Deployment | 20% | Working API, Docker, CI, monitoring plan |
| Responsible AI | 25% | Fairness, privacy, security, oversight — measured and honest |
| Documentation | 10% | Datasheet, model card, risk register, README |
| Communication | 10% | Clear report and confident demo |

## Final exam and certificate

When you have finished all 24 lessons and their quizzes, take the **final exam** for this course. It covers deployment, MLOps, fairness, explainability, privacy, security, governance and the capstone. With a passing score you receive your **WAMUGII certificate in Responsible AI & Deployment**.

Completing all seven courses of the WAMUGII AI Program means you can now:

1. Use AI tools well and explain how AI works (Courses 1–2).
2. Program in Python and use the maths behind AI (Course 3).
3. Build and evaluate machine-learning and deep-learning models (Courses 4–5).
4. Build LLM and generative-AI applications (Course 6).
5. Deploy, monitor and govern AI systems responsibly (Course 7).

## What next?

- **Build in public:** put your capstone on GitHub with a clear README and a short demo video.
- **Contribute:** open-source projects, Kaggle competitions, local hackathons and AI communities in Kigali.
- **Specialise:** MLOps engineering, data science, NLP for African languages, computer vision for agriculture or health, AI policy and governance.
- **Keep learning responsibly:** every new model you build deserves the same questions — does it work, for whom, what can go wrong, and who is accountable?

**Takeaway:** A great capstone is useful, working, honest and well documented — present it clearly, pass the final exam, and keep building AI that serves people.

## Try it yourself

Finish your capstone, run `check_submission` on your folder until it says READY TO SUBMIT, rehearse your ten-minute presentation, and share your project link with your instructor in the lesson Q&A. Congratulations on completing the WAMUGII AI Program!
""",
            "quiz": [
                ("What should the first minute of the presentation cover?",
                 ["The code", "The problem, told as a short story about one user", "Your hobbies", "The library versions"],
                 1, "Start with the person and the problem."),
                ("What should you prepare in case the live demo fails?",
                 ["Nothing", "Screenshots of the demo", "An excuse", "A different project"],
                 1, "Always have a backup."),
                ("Which area carries the highest weight in the rubric, together with technical quality?",
                 ["Communication", "Responsible AI", "Documentation", "Problem and value"],
                 1, "25% each."),
                ("What should you say when you do not know an answer?",
                 ["Make something up", "'I don't know yet — here is how I would find out'", "Nothing", "Change the subject"],
                 1, "Honesty builds trust."),
                ("What does check_submission do?",
                 ["Grades the project", "Lists required files and shows which are missing", "Trains the model", "Uploads the report"],
                 1, "Run it before you submit."),
                ("Which question should you ask about every model you build?",
                 ["Is it the biggest?", "Does it work, for whom, what can go wrong, and who is accountable?", "Is it the newest?", "Can it run without data?"],
                 1, "The heart of responsible AI."),
            ],
        },
    ],
})
