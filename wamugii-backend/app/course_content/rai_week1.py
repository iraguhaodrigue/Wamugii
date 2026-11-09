"""Responsible AI & Deployment -- Week 1: From Notebook to Product. Original WAMUGII content."""

from app.course_content.rai_data import fill

WEEK1 = fill({
    "title": "Week 1 · From Notebook to Product",
    "lessons": [
        # ------------------------------------------------------------------ 1
        {
            "title": "The Deployment Gap: From Notebook to Product",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=wRnKcWIZEvk",
            "content": r"""
**Learning objective:** Explain why a model that works in a notebook is not yet a product, name the parts of a real machine-learning system, and save a model with the information needed to use it safely later.

## Welcome to the capstone course

In the earlier courses you built models that predict, classify and generate. In this course you learn to **deliver** them: put a model behind an API, test it, ship it, watch it in production, check it is fair, protect people's data, document it — and finish with your own end-to-end capstone project.

All course long we use one realistic story: a savings and credit cooperative (SACCO) wants a model that predicts whether a loan applicant will **repay**. Loans change lives, so mistakes and unfairness matter. The data is made up — no real people.

{APPLICANTS}

## The notebook model

{MODEL}

An AUC of about **0.88** is a good model. In a notebook, the job looks done. It is not.

## What changes in production

| In the notebook | In production |
|---|---|
| You run the code once | It answers requests all day, every day |
| Clean, known data | Missing fields, typing mistakes, new kinds of applicants |
| You are the only user | Loan officers and applicants rely on the answer |
| Errors show up as red text | Errors are silent: a wrong number looks like a right number |
| The world is frozen | Prices, incomes and behaviour change every month |
| No rules | Data protection law, fairness, appeals, audits |

A famous Google paper, "Hidden Technical Debt in Machine Learning Systems" (2015), showed that in real systems the model code is only a **small part**. Around it you need data collection and checks, feature code, serving, monitoring, configuration and process.

## The parts of an ML system

1. **Data pipeline** — collects and checks the data.
2. **Training pipeline** — turns data into a model in a repeatable way.
3. **Model artifact** — the saved model file plus its information (version, features, metrics).
4. **Serving** — an API or batch job that makes predictions.
5. **Monitoring** — watches inputs, outputs, speed, errors and quality.
6. **Feedback** — real outcomes come back and trigger retraining.
7. **People and rules** — owners, reviewers, documentation, appeals, law.

## Save the model with its "passport"

A model file alone is dangerous: later nobody knows which features it expects, how good it was, or which data trained it. Save a small metadata file next to it:

```python
import datetime
import hashlib
import json

import joblib
import sklearn

joblib.dump(model, "loan_model_v1.joblib")

data_hash = hashlib.sha256(pd.util.hash_pandas_object(train, index=False).values.tobytes()).hexdigest()[:16]
meta = {
    "name": "loan-repayment",
    "version": "1.0.0",
    "trained_on": datetime.date.today().isoformat(),
    "features": FEATURES,
    "target": TARGET,
    "threshold": 0.5,
    "metrics": {"auc": round(roc_auc_score(test[TARGET], proba), 3),
                "accuracy": round(accuracy_score(test[TARGET], proba >= 0.5), 3)},
    "training_rows": len(train),
    "data_fingerprint": data_hash,
    "sklearn_version": sklearn.__version__,
}
with open("loan_model_v1.json", "w") as f:
    json.dump(meta, f, indent=2)
print(json.dumps(meta, indent=2))
```

The **data fingerprint** proves which data trained the model. The **sklearn version** matters because a model saved with one version may not load in another.

## A silent production bug

Load the model the way a server would, and send one applicant:

```python
loaded = joblib.load("loan_model_v1.joblib")
info = json.load(open("loan_model_v1.json"))

def predict_one(applicant):
    row = pd.DataFrame([applicant])[info["features"]]
    p = float(loaded.predict_proba(row)[0, 1])
    return {"repay_probability": round(p, 3), "approve": p >= info["threshold"]}

good = {"income_rwf": 350_000, "loan_rwf": 200_000, "years_member": 5,
        "late_payments": 0, "salaried": 1, "momo_tx_month": 40}
print("correct units:   ", predict_one(good))

mistake = dict(good, income_rwf=350)          # a form that asks for income "in thousands"
print("income in 1,000s:", predict_one(mistake))
```

The second answer is badly wrong — but the code raised **no error**. This is called **training–serving skew**: the data at serving time does not look like the training data. Real systems stop this with input checks:

```python
LIMITS = {"income_rwf": (10_000, 20_000_000), "loan_rwf": (10_000, 5_000_000),
          "years_member": (0, 60), "late_payments": (0, 50), "salaried": (0, 1), "momo_tx_month": (0, 1000)}

def check_input(applicant):
    problems = []
    for name, (low, high) in LIMITS.items():
        value = applicant.get(name)
        if value is None:
            problems.append(f"{name} is missing")
        elif not low <= value <= high:
            problems.append(f"{name}={value} is outside {low}..{high}")
    return problems

print(check_input(good))
print(check_input(mistake))
```

Rejecting a strange request with a clear message is far better than returning a confident wrong answer.

## Key terms

- **Deployment** — making a model available to real users or systems.
- **Model artifact** — the saved model plus its metadata.
- **Metadata** — information about the model: version, features, metrics, data, library versions.
- **Training–serving skew** — serving data that differs from training data, causing silent errors.
- **Input validation** — checking requests before predicting.

**Takeaway:** A notebook model becomes a product only with everything around it: versioned artifacts with metadata, input checks, serving, monitoring, people and rules.

## Try it yourself

1. Send an applicant with `late_payments` missing to `predict_one`. What happens? Then try `check_input`.
2. Add a check that the loan is not more than 20 times the income.
3. Change the version to `1.0.1`, save again, and list everything that should change in the metadata.
4. Draw the seven parts of an ML system for a problem in your own organisation.
""",
            "quiz": [
                ("Why is a good notebook model not yet a product?",
                 ["Notebooks cannot train models", "Production needs serving, checks, monitoring, people and rules around the model", "The AUC is too low", "Products never use Python"],
                 1, "The model is only a small part of the system."),
                ("What should be saved next to the model file?",
                 ["Nothing", "Metadata: version, features, metrics, data fingerprint and library versions", "The whole internet", "Only the accuracy"],
                 1, "Its 'passport' makes it safe to use later."),
                ("What is training–serving skew?",
                 ["A slow server", "Serving data that differs from training data, causing silent errors", "A type of chart", "A fairness metric"],
                 1, "Income in thousands instead of RWF is an example."),
                ("Why are production errors often dangerous?",
                 ["They are loud", "They are silent: a wrong number looks like a right number", "They delete the model", "They only happen at night"],
                 1, "So you must check inputs and monitor outputs."),
                ("What should the API do with an income of 350 RWF for a salaried worker?",
                 ["Predict anyway", "Reject it with a clear message", "Double it", "Ignore the field"],
                 1, "A clear rejection beats a confident wrong answer."),
                ("Why record the scikit-learn version?",
                 ["For marketing", "A model saved with one version may not load in another", "It sets the threshold", "It is required by law"],
                 1, "Versions matter for reproducibility."),
            ],
        },
        # ------------------------------------------------------------------ 2
        {
            "title": "Reproducible Machine Learning",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=UY2WFPeEVN0",
            "content": r"""
**Learning objective:** Make training repeatable with fixed seeds, configuration, pipelines, data fingerprints and pinned library versions, and prove it with a check.

## Why reproducibility matters

Six months from now someone asks: "Why did the model refuse my loan? Which data and code made it?" If you cannot rebuild the exact same model, you cannot answer, debug or defend it. **Reproducible** means: same data + same code + same settings = same model.

{APPLICANTS}

## Hidden randomness

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

FEATURES = ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried", "momo_tx_month"]

def train_once(seed=None):
    tr, te = train_test_split(applicants, test_size=0.25, random_state=seed)
    forest = RandomForestClassifier(n_estimators=50, random_state=seed).fit(tr[FEATURES], tr["repaid"])
    return round(roc_auc_score(te["repaid"], forest.predict_proba(te[FEATURES])[:, 1]), 4)

print("no seed:   ", [train_once() for _ in range(3)])
print("seed = 42: ", [train_once(42) for _ in range(3)])
```

Without a seed, every run gives a different score — so you cannot tell whether a change helped or you were just lucky. With a fixed seed, the runs are identical.

## Put every setting in one config

```python
import hashlib
import json

CONFIG = {
    "data": {"test_size": 0.25, "split_seed": 0},
    "features": FEATURES,
    "target": "repaid",
    "model": {"type": "logistic_regression", "C": 1.0, "max_iter": 1000},
    "threshold": 0.5,
}

def config_id(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:10]

print("config id:", config_id(CONFIG))
```

The **config id** is a short fingerprint: if any setting changes, the id changes.

## A pipeline keeps preprocessing with the model

If you scale the data in one cell and train in another, it is easy to forget the scaling at serving time. A scikit-learn **Pipeline** stores both together, so the saved file always does the same steps:

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def train(config, data):
    tr, te = train_test_split(data, test_size=config["data"]["test_size"],
                              random_state=config["data"]["split_seed"], stratify=data[config["target"]])
    pipe = Pipeline([("scale", StandardScaler()),
                     ("model", LogisticRegression(C=config["model"]["C"], max_iter=config["model"]["max_iter"]))])
    pipe.fit(tr[config["features"]], tr[config["target"]])
    p = pipe.predict_proba(te[config["features"]])[:, 1]
    metrics = {"auc": round(roc_auc_score(te[config["target"]], p), 4),
               "accuracy": round(accuracy_score(te[config["target"]], p >= config["threshold"]), 4)}
    return pipe, metrics

_, first = train(CONFIG, applicants)
_, second = train(CONFIG, applicants)
print(first, second)
assert first == second, "training is not reproducible!"
print("reproducible: the same config and data give the same model")
```

That `assert` is a tiny **reproducibility test**. Put it in your test suite (Lesson 4).

## Fingerprint the data

```python
def data_fingerprint(df):
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes()).hexdigest()[:16]

print("original data:", data_fingerprint(applicants))
changed = applicants.copy()
changed.loc[0, "income_rwf"] += 1000          # change ONE number
print("one value changed:", data_fingerprint(changed))
```

One changed value gives a completely different fingerprint. Store the fingerprint with every model — and keep the data itself in a safe, versioned place (a dated folder, object storage, or tools such as DVC).

## Pin your library versions

```python
import importlib.metadata as md

packages = ["scikit-learn", "pandas", "numpy", "joblib"]
pinned = [f"{p}=={md.version(p)}" for p in packages]
with open("requirements.txt", "w") as f:
    f.write("\n".join(pinned) + "\n")
print(open("requirements.txt").read())
```

`requirements.txt` with exact versions (`==`) lets anyone install the same libraries later.

## A tidy folder layout

```text
loan-model/
  data/            raw and processed data (or links to where it is stored)
  src/             train.py, features.py, serve.py
  tests/           test_data.py, test_model.py, test_api.py
  configs/         train.json
  models/          saved models + metadata (or a model registry)
  requirements.txt
  README.md        how to train, test and run
```

## Key terms

- **Reproducible** — the same inputs always give the same model and results.
- **Random seed** — a number that fixes "random" choices.
- **Config** — one place that holds every training setting.
- **Pipeline** — preprocessing and model saved together.
- **Data fingerprint** — a hash that identifies the exact data.
- **Pinned versions** — exact library versions in requirements.txt.

**Takeaway:** Fix seeds, keep settings in a config, use pipelines, fingerprint the data and pin library versions — then prove reproducibility with a test.

## Try it yourself

1. Change `C` to 0.1 in `CONFIG`. Does the config id change? Does the AUC change?
2. Remove `stratify` from `train`. Is it still reproducible?
3. Write a function `save_run(config, metrics, data)` that stores the config, metrics and data fingerprint in one JSON file.
4. Create the folder layout above for one of your own projects.
""",
            "quiz": [
                ("What does reproducible mean in ML?",
                 ["The model is fast", "Same data, code and settings give the same model and results", "The model is accurate", "The code is short"],
                 1, "You can rebuild and explain it later."),
                ("Why fix a random seed?",
                 ["To make the model better", "So results do not change from run to run and comparisons are fair", "To save memory", "It hides errors"],
                 1, "Otherwise you cannot tell luck from improvement."),
                ("Why use a scikit-learn Pipeline?",
                 ["It is faster", "Preprocessing and model are saved together, so serving does the same steps", "It removes the need for data", "It tunes the threshold"],
                 1, "No forgotten scaling at serving time."),
                ("What happens to a data fingerprint when one value changes?",
                 ["Nothing", "It becomes completely different", "It increases by one", "It is deleted"],
                 1, "That is how it proves which data was used."),
                ("What does requirements.txt with == versions do?",
                 ["Installs the newest versions", "Lets anyone install exactly the same library versions later", "Trains the model", "Removes old models"],
                 1, "Pinned versions avoid surprise changes."),
                ("Where should every training setting live?",
                 ["Spread across many cells", "In one config", "Only in your memory", "In the model name"],
                 1, "One config, one fingerprint."),
            ],
        },
        # ------------------------------------------------------------------ 3
        {
            "title": "Serving a Model with FastAPI",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=mMQ6mGQtwX8",
            "content": r"""
**Learning objective:** Serve a trained model as a web API with FastAPI, validate inputs automatically, return versioned answers, support batch requests, and test the API in code.

## Why an API?

A web or mobile app, a loan officer's dashboard or a USSD menu cannot run your notebook. They send an **HTTP request** with the applicant's data and get back JSON. FastAPI is a popular Python library for this: fast, simple, and it checks inputs for you using **pydantic** models. (FastAPI is already installed in Google Colab.)

{APPLICANTS}

{MODEL}

```python
import joblib
joblib.dump(model, "loan_model.joblib")
MODEL_VERSION = "1.0.0"
```

## Describe the input once

```python
from pydantic import BaseModel, Field

class Applicant(BaseModel):
    income_rwf: float = Field(..., ge=10_000, le=20_000_000, description="Monthly income in RWF")
    loan_rwf: float = Field(..., ge=10_000, le=5_000_000)
    years_member: int = Field(..., ge=0, le=60)
    late_payments: int = Field(..., ge=0, le=50)
    salaried: int = Field(..., ge=0, le=1)
    momo_tx_month: int = Field(..., ge=0, le=1000)

class Decision(BaseModel):
    repay_probability: float
    approve: bool
    model_version: str
```

`ge` means "greater than or equal", `le` "less than or equal". Any request outside these limits is rejected **before** the model sees it — the input checks from Lesson 1, written once.

Notice what is **not** in `Applicant`: gender, area, name, phone number. The model does not need them, so the API does not accept them. Collecting less data is safer (Week 3).

## The API

```python
from fastapi import FastAPI

app = FastAPI(title="SACCO loan scoring", version=MODEL_VERSION)
scorer = joblib.load("loan_model.joblib")          # load once at start-up, not on every request
THRESHOLD = 0.5

@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}

@app.post("/predict", response_model=Decision)
def predict(applicant: Applicant):
    row = pd.DataFrame([applicant.model_dump()])[FEATURES]
    p = float(scorer.predict_proba(row)[0, 1])
    return Decision(repay_probability=round(p, 3), approve=p >= THRESHOLD, model_version=MODEL_VERSION)

@app.post("/predict/batch", response_model=list[Decision])
def predict_batch(applicants: list[Applicant]):
    rows = pd.DataFrame([a.model_dump() for a in applicants])[FEATURES]
    ps = scorer.predict_proba(rows)[:, 1]
    return [Decision(repay_probability=round(float(p), 3), approve=bool(p >= THRESHOLD), model_version=MODEL_VERSION)
            for p in ps]
```

Every answer includes the **model version**, so later you know which model made each decision.

## Test it without a server

FastAPI's `TestClient` sends real HTTP requests to the app inside your notebook:

```python
from fastapi.testclient import TestClient

client = TestClient(app)
print(client.get("/health").json())

applicant = {"income_rwf": 350_000, "loan_rwf": 200_000, "years_member": 5,
             "late_payments": 0, "salaried": 1, "momo_tx_month": 40}
r = client.post("/predict", json=applicant)
print(r.status_code, r.json())

bad = dict(applicant, income_rwf=350)
r = client.post("/predict", json=bad)
print(r.status_code, r.json()["detail"][0]["msg"])

r = client.post("/predict/batch", json=[applicant, dict(applicant, late_payments=4, loan_rwf=900_000)])
print(r.status_code, r.json())
```

- A good request returns **200** with the decision.
- The income of 350 RWF returns **422 Unprocessable Entity** with a clear message — the model never ran.
- The batch endpoint scores many applicants in one call (faster than one call each).

## Run it for real

Save the code as `main.py` and start it on your computer or server:

```bash
pip install fastapi uvicorn scikit-learn pandas joblib
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000/docs`: FastAPI creates an interactive documentation page where you can try every endpoint.

## Good serving habits

- **Load the model once** at start-up, not on every request.
- **Validate inputs** with pydantic; accept only the fields you need.
- **Version every answer**.
- **Never log personal data** in plain text (Week 3).
- **Add a /health endpoint** so your server, Docker and monitoring can check the service is alive.

## Key terms

- **API** — a way for programs to talk over HTTP.
- **Endpoint** — one URL and method, such as POST /predict.
- **pydantic model** — a class that describes and validates data.
- **422** — the status code for input that fails validation.
- **TestClient** — sends requests to a FastAPI app inside Python, for testing.
- **Batch endpoint** — scores many items in one request.

**Takeaway:** FastAPI turns a model into a validated, versioned, testable web service in a few dozen lines — load once, check every input, version every answer.

## Try it yourself

1. Send a request with `salaried` set to 2. Read the error message.
2. Add a field `reason` to `Decision` that says "high loan-to-income" when the loan is more than 3 times the income.
3. Add a `GET /model` endpoint that returns the features and threshold.
4. Time 100 single requests and one batch request of 100. Which is faster?
""",
            "quiz": [
                ("What does FastAPI use to check request data automatically?",
                 ["SQL", "pydantic models", "pandas", "Docker"],
                 1, "Field limits reject bad input before the model runs."),
                ("Which status code does FastAPI return for input that fails validation?",
                 ["200", "422", "404", "500"],
                 1, "422 Unprocessable Entity."),
                ("Why load the model at start-up?",
                 ["It is required by law", "Loading on every request would be slow", "To change it each time", "To hide it"],
                 1, "Load once, predict many times."),
                ("Why return the model version with each answer?",
                 ["For decoration", "So you later know which model made each decision", "To slow down attackers", "It improves accuracy"],
                 1, "Essential for audits and debugging."),
                ("Why does the Applicant model not accept gender or phone number?",
                 ["They are too long", "The model does not need them, and collecting less personal data is safer", "FastAPI forbids it", "They are always missing"],
                 1, "Data minimisation."),
                ("What does TestClient let you do?",
                 ["Deploy to the cloud", "Send real HTTP requests to the app inside Python, for testing", "Train the model", "Write documentation"],
                 1, "Test the API without starting a server."),
            ],
        },
        # ------------------------------------------------------------------ 4
        {
            "title": "Testing Machine Learning Systems",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=CU0C4MtrQMU",
            "content": r"""
**Learning objective:** Write automated tests for data, model quality and model behaviour, and run them with pytest so problems are caught before users see them.

## What can go wrong — and which test catches it

| Problem | Test |
|---|---|
| A column is missing or has impossible values | **Data validation** test |
| A new model is worse than the old one | **Quality gate** (minimum AUC) |
| The model behaves strangely: more late payments → more likely to repay | **Directional** test |
| Tiny, meaningless changes flip the decision | **Invariance** test |
| Training is not repeatable | **Reproducibility** test (Lesson 2) |
| The API accepts bad input | **API** test (Lesson 3) |

Accuracy alone is not enough: a model can score well and still behave in ways that are wrong or unfair.

{APPLICANTS}

{MODEL}

## Data validation

```python
EXPECTED = {
    "income_rwf": (10_000, 20_000_000), "loan_rwf": (10_000, 5_000_000), "years_member": (0, 60),
    "late_payments": (0, 50), "salaried": (0, 1), "momo_tx_month": (0, 1000), "repaid": (0, 1),
}

def validate(df):
    problems = []
    for col, (low, high) in EXPECTED.items():
        if col not in df.columns:
            problems.append(f"missing column {col}")
            continue
        if df[col].isna().any():
            problems.append(f"{col} has {df[col].isna().sum()} missing values")
        bad = ((df[col] < low) | (df[col] > high)).sum()
        if bad:
            problems.append(f"{col} has {bad} values outside {low}..{high}")
    if len(df) < 500:
        problems.append(f"only {len(df)} rows")
    return problems

print("clean data:", validate(applicants))
broken = applicants.drop(columns="momo_tx_month").head(300).copy()
broken.loc[broken.index[:5], "income_rwf"] = -1
print("broken data:", validate(broken))
```

Run validation **before** training and on new data before scoring. Libraries such as Great Expectations and pandera do the same job at scale.

## Behaviour tests

```python
base = pd.DataFrame([{"income_rwf": 300_000, "loan_rwf": 250_000, "years_member": 4,
                      "late_payments": 1, "salaried": 1, "momo_tx_month": 35}])

def p_repay(df):
    return float(model.predict_proba(df[FEATURES])[0, 1])

print("base:                 ", round(p_repay(base), 3))
print("3 more late payments: ", round(p_repay(base.assign(late_payments=4)), 3))
print("loan doubled:         ", round(p_repay(base.assign(loan_rwf=500_000)), 3))
print("5 more member years:  ", round(p_repay(base.assign(years_member=9)), 3))
print("income + 1 RWF:       ", round(p_repay(base.assign(income_rwf=300_001)), 3))
```

- **Directional:** more late payments and a bigger loan should **lower** the probability; more years of membership should **raise** it.
- **Invariance:** adding 1 RWF to income should change almost nothing.

These tests come from domain knowledge. A model that fails them is suspicious, even with a high AUC.

## Turn checks into pytest tests

pytest finds functions whose names start with `test_` and runs them. We save the model and test data, write a test file, and run pytest:

```python
import joblib
joblib.dump(model, "model.joblib")
test.to_csv("test_data.csv", index=False)

tests = '''
import joblib
import pandas as pd
from sklearn.metrics import roc_auc_score

FEATURES = ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried", "momo_tx_month"]
model = joblib.load("model.joblib")
data = pd.read_csv("test_data.csv")
base = pd.DataFrame([{"income_rwf": 300000, "loan_rwf": 250000, "years_member": 4,
                      "late_payments": 1, "salaried": 1, "momo_tx_month": 35}])

def p(df):
    return model.predict_proba(df[FEATURES])[:, 1]

def test_no_missing_values():
    assert not data[FEATURES].isna().any().any()

def test_quality_gate():
    assert roc_auc_score(data["repaid"], p(data)) >= 0.80

def test_more_late_payments_lowers_probability():
    assert p(base.assign(late_payments=4))[0] < p(base)[0]

def test_bigger_loan_lowers_probability():
    assert p(base.assign(loan_rwf=500000))[0] < p(base)[0]

def test_tiny_income_change_does_not_matter():
    assert abs(p(base.assign(income_rwf=300001))[0] - p(base)[0]) < 0.001

def test_probabilities_are_valid():
    assert ((p(data) >= 0) & (p(data) <= 1)).all()
'''
with open("test_model.py", "w") as f:
    f.write(tests)

import subprocess, sys
result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_model.py"],
                        capture_output=True, text=True)
print(result.stdout[-400:])
```

All **6 passed**. In a real project these tests run automatically every time someone changes the code or retrains the model (Week 2, CI/CD).

## A test that catches a bad model

Train a "broken" model on shuffled labels — like a bug that mixes up rows — and run the quality gate again:

```python
from sklearn.utils import shuffle
bad_labels = shuffle(train[TARGET], random_state=1).values
bad_model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(train[FEATURES], bad_labels)
joblib.dump(bad_model, "model.joblib")

result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_model.py"],
                        capture_output=True, text=True)
print(result.stdout.strip().splitlines()[-1])
joblib.dump(model, "model.joblib")                 # put the good model back
```

**Two of the six tests fail** — including the quality gate — so the broken model would never reach users. Notice that the other four still pass: one test is never enough, you need several kinds.

## Key terms

- **Data validation** — checking columns, types, ranges and missing values.
- **Quality gate** — a minimum score a model must reach to be released.
- **Directional test** — a change in an input should move the prediction in a known direction.
- **Invariance test** — a meaningless change should not change the prediction.
- **pytest** — the standard Python test runner.

**Takeaway:** Test data, quality and behaviour automatically; a model that passes accuracy but fails behaviour tests should not be released.

## Try it yourself

1. Add a test that a salaried applicant has a higher probability than the same applicant without salary.
2. Add a data test that `loan_rwf` is never more than 50 times `income_rwf`.
3. Raise the quality gate to 0.95. What happens, and is that a sensible gate?
4. Write an API test file `test_api.py` for Lesson 3's app with three tests (good request, bad request, health).
""",
            "quiz": [
                ("Why is accuracy alone not enough to test a model?",
                 ["Accuracy is always wrong", "A model can score well but still behave strangely or unfairly", "Accuracy is too slow", "Tests are not needed"],
                 1, "Behaviour tests catch what scores miss."),
                ("What does a directional test check?",
                 ["Speed", "That changing an input moves the prediction in the expected direction", "File names", "The colour of charts"],
                 1, "More late payments should lower the repay probability."),
                ("What is an invariance test?",
                 ["A meaningless change, like +1 RWF, should not change the prediction", "The model never changes", "Testing on Sundays", "A fairness law"],
                 0, "Small irrelevant changes must not flip decisions."),
                ("What is a quality gate?",
                 ["A door", "A minimum score a model must reach before release", "A firewall", "A type of chart"],
                 1, "For example AUC ≥ 0.80."),
                ("How does pytest find tests?",
                 ["It guesses", "It runs functions whose names start with test_", "It reads comments", "It needs a GPU"],
                 1, "A simple naming rule."),
                ("What happened when the model trained on shuffled labels was tested?",
                 ["All tests passed", "The tests failed, so it would not be released", "pytest crashed", "Accuracy went up"],
                 1, "That is exactly what tests are for."),
            ],
        },
        # ------------------------------------------------------------------ 5
        {
            "title": "Packaging with Docker and Configuration",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=Jq68axbKIbg",
            "content": r"""
**Learning objective:** Package a model service so it runs the same everywhere using Docker, keep settings and secrets in environment variables, and produce a ready-to-deploy folder.

## "It works on my computer"

Your service needs a certain Python version, certain libraries, the model file and some settings. On another computer one of these is often different — and the service breaks. **Docker** packages the code, libraries and model into an **image**; a running copy of an image is a **container**. The same image runs the same way on your laptop, a school server or a cloud droplet.

{APPLICANTS}

{MODEL}

## Settings come from the environment

Never write paths, thresholds or secrets inside the code. Read them from **environment variables**, with safe defaults:

```python
import os

def load_settings():
    return {
        "model_path": os.environ.get("MODEL_PATH", "model/loan_model.joblib"),
        "threshold": float(os.environ.get("APPROVE_THRESHOLD", "0.5")),
        "model_version": os.environ.get("MODEL_VERSION", "1.0.0"),
        "api_key": os.environ.get("API_KEY"),            # a secret: no default, never in the code
    }

print(load_settings())
os.environ["APPROVE_THRESHOLD"] = "0.6"
print("after changing the environment:", load_settings()["threshold"])
del os.environ["APPROVE_THRESHOLD"]
```

The same image can now run with different settings (test or production) without changing code. Secrets such as API keys or database passwords are given to the container when it starts — they are **never** stored in the code, the image or Git.

## Build the service folder

This cell writes every file the service needs into a folder `loan_service/`:

```python
import pathlib
import importlib.metadata as md
import joblib

svc = pathlib.Path("loan_service")
(svc / "model").mkdir(parents=True, exist_ok=True)
joblib.dump(model, svc / "model" / "loan_model.joblib")

(svc / "main.py").write_text('''import os

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

MODEL_PATH = os.environ.get("MODEL_PATH", "model/loan_model.joblib")
THRESHOLD = float(os.environ.get("APPROVE_THRESHOLD", "0.5"))
VERSION = os.environ.get("MODEL_VERSION", "1.0.0")
FEATURES = ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried", "momo_tx_month"]

app = FastAPI(title="SACCO loan scoring", version=VERSION)
model = joblib.load(MODEL_PATH)


class Applicant(BaseModel):
    income_rwf: float = Field(..., ge=10_000, le=20_000_000)
    loan_rwf: float = Field(..., ge=10_000, le=5_000_000)
    years_member: int = Field(..., ge=0, le=60)
    late_payments: int = Field(..., ge=0, le=50)
    salaried: int = Field(..., ge=0, le=1)
    momo_tx_month: int = Field(..., ge=0, le=1000)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": VERSION}


@app.post("/predict")
def predict(applicant: Applicant):
    p = float(model.predict_proba(pd.DataFrame([applicant.model_dump()])[FEATURES])[0, 1])
    return {"repay_probability": round(p, 3), "approve": p >= THRESHOLD, "model_version": VERSION}
''')

libs = ["fastapi", "uvicorn", "scikit-learn", "pandas", "joblib"]
pins = []
for lib in libs:
    try:
        pins.append(f"{lib}=={md.version(lib)}")
    except md.PackageNotFoundError:
        pins.append(lib)                                  # not installed here: leave unpinned
(svc / "requirements.txt").write_text("\n".join(pins) + "\n")

(svc / "Dockerfile").write_text('''FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home appuser
USER appuser
ENV MODEL_PATH=model/loan_model.joblib
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
''')
(svc / ".dockerignore").write_text("__pycache__/\n*.ipynb\n.env\ndata/\n")

for path in sorted(svc.rglob("*")):
    if path.is_file():
        print(f"{str(path):40s} {path.stat().st_size:>8,} bytes")
```

What the Dockerfile does, line by line:

1. Start from a small official Python image.
2. Install the pinned libraries first (Docker caches this step, so rebuilds are fast).
3. Copy the code and model.
4. Create and switch to a normal user — never run services as root.
5. Declare the port and a **health check** that calls `/health`.
6. Start the API with uvicorn.

`.dockerignore` keeps notebooks, secrets (`.env`) and raw data out of the image.

## Check the service before you ship it

```python
import importlib
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, str(svc.resolve()))
cwd = os.getcwd(); os.chdir(svc)
service = importlib.import_module("main")
client = TestClient(service.app)
print(client.get("/health").json())
print(client.post("/predict", json={"income_rwf": 400_000, "loan_rwf": 150_000, "years_member": 6,
                                    "late_payments": 0, "salaried": 1, "momo_tx_month": 50}).json())
os.chdir(cwd)

import shutil
print("download this file:", shutil.make_archive("loan_service", "zip", svc))
```

In Colab, download `loan_service.zip` from the Files panel.

## Build and run with Docker

On a computer or server with Docker installed:

```bash
cd loan_service
docker build -t loan-service:1.0.0 .
docker run -d --name loan-service -p 8000:8000 \
  -e MODEL_VERSION=1.0.0 -e APPROVE_THRESHOLD=0.5 -e API_KEY="$LOAN_API_KEY" \
  loan-service:1.0.0
curl http://localhost:8000/health
```

Tag images with the version (`1.0.0`), never only `latest`, so you can always go back to a known version.

## Key terms

- **Docker image** — a package of code, libraries and files.
- **Container** — a running copy of an image.
- **Dockerfile** — the recipe for building an image.
- **Environment variable** — a setting given to a program from outside.
- **Secret** — a password or key; never in code, images or Git.
- **Health check** — a regular test that the service is alive.

**Takeaway:** Docker packages the service so it runs the same everywhere; settings and secrets come from environment variables, and every image has a version tag and a health check.

## Try it yourself

1. Start the service code with `APPROVE_THRESHOLD=0.7` and compare decisions for three applicants.
2. Add `MODEL_VERSION` to the `/predict` answer and change it through the environment.
3. If you have Docker, build and run the image, then open `http://localhost:8000/docs`.
4. Explain to a classmate why `API_KEY` has no default value in `load_settings`.
""",
            "quiz": [
                ("What is a Docker container?",
                 ["A Python library", "A running copy of a Docker image", "A database", "A type of model"],
                 1, "Image = package; container = running copy."),
                ("Where should an API key for the service come from?",
                 ["Written in main.py", "An environment variable or secret store given at start-up", "The Docker image", "A public Git repository"],
                 1, "Secrets never live in code, images or Git."),
                ("Why install requirements before copying the code in the Dockerfile?",
                 ["It is required", "Docker caches that step, so rebuilds after code changes are fast", "It makes the image bigger", "To run as root"],
                 1, "Layer caching."),
                ("Why create a normal user in the Dockerfile?",
                 ["For speed", "Services should not run as root, for security", "To save space", "Python needs it"],
                 1, "Least privilege."),
                ("What does .dockerignore do?",
                 ["Deletes Docker", "Keeps files such as notebooks, .env and raw data out of the image", "Ignores errors", "Speeds up the model"],
                 1, "Smaller, safer images."),
                ("Why tag images with a version like 1.0.0?",
                 ["It looks nice", "So you can always run or return to a known version", "Docker requires numbers", "To hide the model"],
                 1, "Avoid relying only on 'latest'."),
            ],
        },
        # ------------------------------------------------------------------ 6
        {
            "title": "Week 1 Project: A Tested Loan-Scoring Service",
            "minutes": 120,
            "video": "https://www.youtube.com/watch?v=8Zn4hV9xE1I",
            "content": r"""
**Learning objective:** Build a complete, reproducible, tested and packaged prediction service from raw data, and check it against a release checklist.

## The brief

The SACCO's IT team asks you for a loan-scoring service they can run on their server. They need: a reproducible model, a validated and versioned API, automated tests, and a Docker package. You will build all of it in this notebook.

{APPLICANTS}

## Part 1 — Validate the data

```python
LIMITS = {"income_rwf": (10_000, 20_000_000), "loan_rwf": (10_000, 5_000_000), "years_member": (0, 60),
          "late_payments": (0, 50), "salaried": (0, 1), "momo_tx_month": (0, 1000), "repaid": (0, 1)}

def validate(df):
    problems = [f"missing column {c}" for c in LIMITS if c not in df.columns]
    for c, (lo, hi) in LIMITS.items():
        if c in df.columns and (df[c].isna().any() or not df[c].between(lo, hi).all()):
            problems.append(f"bad values in {c}")
    return problems

assert validate(applicants) == [], validate(applicants)
print("data OK:", len(applicants), "rows")
```

## Part 2 — Reproducible training with a config

```python
import hashlib, json
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

CONFIG = {"features": ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried", "momo_tx_month"],
          "target": "repaid", "test_size": 0.25, "seed": 0, "C": 1.0, "threshold": 0.5, "version": "1.0.0"}

def train(config, data):
    tr, te = train_test_split(data, test_size=config["test_size"], random_state=config["seed"], stratify=data[config["target"]])
    pipe = Pipeline([("scale", StandardScaler()), ("lr", LogisticRegression(C=config["C"], max_iter=1000))])
    pipe.fit(tr[config["features"]], tr[config["target"]])
    p = pipe.predict_proba(te[config["features"]])[:, 1]
    return pipe, te, {"auc": round(roc_auc_score(te[config["target"]], p), 4),
                      "accuracy": round(accuracy_score(te[config["target"]], p >= config["threshold"]), 4)}

model, test, metrics = train(CONFIG, applicants)
assert train(CONFIG, applicants)[2] == metrics          # reproducibility check
fingerprint = hashlib.sha256(pd.util.hash_pandas_object(applicants, index=False).values.tobytes()).hexdigest()[:16]
print(metrics, "| data", fingerprint)
```

## Part 3 — Save the artifact with metadata

```python
import pathlib, joblib, sklearn
out = pathlib.Path("release"); (out / "model").mkdir(parents=True, exist_ok=True)
joblib.dump(model, out / "model" / "loan_model.joblib")
meta = {**CONFIG, "metrics": metrics, "data_fingerprint": fingerprint, "sklearn_version": sklearn.__version__}
(out / "model" / "metadata.json").write_text(json.dumps(meta, indent=2))
test.to_csv(out / "model" / "test_data.csv", index=False)
print(sorted(p.name for p in (out / "model").iterdir()))
```

## Part 4 — The API

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

class Applicant(BaseModel):
    income_rwf: float = Field(..., ge=10_000, le=20_000_000)
    loan_rwf: float = Field(..., ge=10_000, le=5_000_000)
    years_member: int = Field(..., ge=0, le=60)
    late_payments: int = Field(..., ge=0, le=50)
    salaried: int = Field(..., ge=0, le=1)
    momo_tx_month: int = Field(..., ge=0, le=1000)

app = FastAPI(title="SACCO loan scoring")
scorer = joblib.load(out / "model" / "loan_model.joblib")

@app.get("/health")
def health():
    return {"status": "ok", "model_version": meta["version"]}

@app.post("/predict")
def predict(a: Applicant):
    p = float(scorer.predict_proba(pd.DataFrame([a.model_dump()])[meta["features"]])[0, 1])
    return {"repay_probability": round(p, 3), "approve": p >= meta["threshold"], "model_version": meta["version"]}

client = TestClient(app)
ok = client.post("/predict", json={"income_rwf": 420_000, "loan_rwf": 300_000, "years_member": 3,
                                   "late_payments": 1, "salaried": 1, "momo_tx_month": 30})
bad = client.post("/predict", json={"income_rwf": 420_000})
print(client.get("/health").json(), ok.status_code, ok.json(), bad.status_code)
```

## Part 5 — Automated tests

```python
import subprocess, sys
(out / "test_release.py").write_text('''import json, joblib, pandas as pd
from sklearn.metrics import roc_auc_score
meta = json.load(open("model/metadata.json"))
model = joblib.load("model/loan_model.joblib")
data = pd.read_csv("model/test_data.csv")
F = meta["features"]
base = pd.DataFrame([{"income_rwf": 300000, "loan_rwf": 250000, "years_member": 4,
                      "late_payments": 1, "salaried": 1, "momo_tx_month": 35}])
p = lambda df: model.predict_proba(df[F])[:, 1]

def test_quality_gate():
    assert roc_auc_score(data[meta["target"]], p(data)) >= 0.80

def test_late_payments_direction():
    assert p(base.assign(late_payments=4))[0] < p(base)[0]

def test_salary_direction():
    assert p(base.assign(salaried=1))[0] > p(base.assign(salaried=0))[0]

def test_metadata_complete():
    for key in ["version", "features", "metrics", "data_fingerprint", "sklearn_version"]:
        assert key in meta
''')
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_release.py"],
                   cwd=out, capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1])
```

## Part 6 — Package and check the release

Add `main.py`, `requirements.txt`, `Dockerfile` and `.dockerignore` to `release/` as in Lesson 5. Then run the release checklist:

```python
CHECKLIST = {
    "model file": (out / "model" / "loan_model.joblib").exists(),
    "metadata with version and metrics": "metrics" in meta and "version" in meta,
    "quality gate passed": metrics["auc"] >= 0.80,
    "reproducible": train(CONFIG, applicants)[2] == metrics,
    "API validates input": bad.status_code == 422,
    "tests pass": r.returncode == 0,
}
for item, done in CHECKLIST.items():
    print(("[x] " if done else "[ ] ") + item)
print("READY TO SHIP" if all(CHECKLIST.values()) else "NOT READY")
```

## Your report (one page)

1. Model: features, metrics, data fingerprint, version.
2. API: endpoints, input limits, example request and answer.
3. Tests: what each test checks and the result.
4. Package: how to build and run it, which settings are environment variables.
5. Risks you already see (we tackle many of them in Weeks 2 and 3).

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Reproducibility | Config, seed, fingerprint and a passing reproducibility check |
| API | Validated inputs, versioned answers, health endpoint |
| Tests | Data, quality and behaviour tests that pass |
| Packaging | Dockerfile, pinned requirements, no secrets in files |
| Communication | A clear one-page report |

**Takeaway:** A shippable model is validated data, reproducible training, a versioned artifact, a validated API, automated tests and a clean package — checked with a release checklist.

## Try it yourself

Complete Parts 1–6 and the report. Then change one thing (a feature, `C`, or the threshold), bump the version to 1.1.0, and run the whole release again. Share your checklist output with your instructor in the lesson Q&A.
""",
            "quiz": [
                ("What should happen first in the project?",
                 ["Deploy the API", "Validate the data", "Write the report", "Build the Docker image"],
                 1, "Bad data makes everything after it wrong."),
                ("How does the project prove training is reproducible?",
                 ["By guessing", "Training twice with the same config gives the same metrics", "By using a GPU", "By deleting the data"],
                 1, "A simple check with assert."),
                ("Which file records the version, features and metrics?",
                 ["requirements.txt", "metadata.json", "Dockerfile", ".dockerignore"],
                 1, "The model's passport."),
                ("What does the API return for a request with only income_rwf?",
                 ["A prediction", "422, because required fields are missing", "200 with zeros", "500"],
                 1, "pydantic requires every field."),
                ("When is the release 'READY TO SHIP'?",
                 ["When the code runs once", "When every checklist item is done", "When accuracy is 100%", "Always"],
                 1, "Checklists stop half-finished releases."),
                ("What should you change when you retrain with a new setting?",
                 ["Nothing", "The version number, then run the whole release again", "Only the file name", "Delete the tests"],
                 1, "Every model gets its own version."),
            ],
        },
    ],
})
