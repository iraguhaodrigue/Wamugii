"""Responsible AI & Deployment -- Week 2: MLOps, Running Models in Production. Original WAMUGII content."""

from app.course_content.rai_data import fill

WEEK2 = fill({
    "title": "Week 2 · MLOps: Running Models in Production",
    "lessons": [
        # ------------------------------------------------------------------ 7
        {
            "title": "CI/CD for Machine Learning",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=HMlXSiDKWrg",
            "content": r"""
**Learning objective:** Explain continuous integration and continuous delivery for ML, write a quality-gate script that blocks bad models, and read a GitHub Actions workflow that runs it automatically.

## From "I ran it on my laptop" to automatic checks

**Continuous integration (CI)** means: every time someone pushes code, a server automatically installs everything and runs the tests. **Continuous delivery (CD)** means: when the tests pass, the new version is packaged (and possibly deployed) automatically. For ML we add one more step — a **quality gate** that checks the model itself, not just the code.

| Step | What runs | Stops the release if… |
|---|---|---|
| Lint and unit tests | Code checks, feature tests | The code is broken |
| Data validation | Schema and range checks | The training data is wrong |
| Train | The training script with the config | Training crashes |
| Quality gate | Metrics and behaviour tests | The model is worse than required or than production |
| Package | Docker build with a version tag | The image does not build |
| Deploy | To staging first, then production | Smoke tests on staging fail |

{APPLICANTS}

{MODEL}

## A quality-gate script

A gate is a small program that **exits with code 0 when everything is fine and 1 when not**. CI systems read that exit code.

```python
import joblib, json, subprocess, sys

joblib.dump(model, "candidate.joblib")
test.to_csv("holdout.csv", index=False)
json.dump({"auc": 0.87}, open("production_metrics.json", "w"))      # what the live model achieves

gate = '''
import json, sys
import joblib, pandas as pd
from sklearn.metrics import roc_auc_score

FEATURES = ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried", "momo_tx_month"]
MIN_AUC = 0.80          # absolute minimum
MAX_DROP = 0.01         # may not be more than 0.01 worse than production

model = joblib.load(sys.argv[1])
data = pd.read_csv("holdout.csv")
production = json.load(open("production_metrics.json"))
p = model.predict_proba(data[FEATURES])[:, 1]
auc = roc_auc_score(data["repaid"], p)

base = data[FEATURES].iloc[[0]].copy()
worse = base.assign(late_payments=base["late_payments"] + 3)
checks = {
    f"AUC {auc:.3f} >= {MIN_AUC}": auc >= MIN_AUC,
    f"AUC not more than {MAX_DROP} below production ({production['auc']})": auc >= production["auc"] - MAX_DROP,
    "more late payments lowers the probability": model.predict_proba(worse)[0, 1] < model.predict_proba(base)[0, 1],
}
for name, ok in checks.items():
    print("PASS" if ok else "FAIL", name)
sys.exit(0 if all(checks.values()) else 1)
'''
open("quality_gate.py", "w").write(gate)

result = subprocess.run([sys.executable, "quality_gate.py", "candidate.joblib"], capture_output=True, text=True)
print(result.stdout, "exit code:", result.returncode)
```

## The gate blocks a weaker model

A colleague "simplifies" the model by dropping three features:

```python
from sklearn.compose import ColumnTransformer

few = ["income_rwf", "loan_rwf", "salaried"]
small = make_pipeline(ColumnTransformer([("keep", "passthrough", few)]),   # uses only 3 columns
                      StandardScaler(), LogisticRegression(max_iter=1000))
small.fit(train[FEATURES], train[TARGET])
joblib.dump(small, "candidate_small.joblib")

result = subprocess.run([sys.executable, "quality_gate.py", "candidate_small.joblib"], capture_output=True, text=True)
print(result.stdout, "exit code:", result.returncode)
```

The smaller model's AUC (about 0.87) is still good enough — but it **ignores late payments completely**, so the behaviour check fails and the gate returns exit code **1**. CI stops the release automatically. A score-only gate would have let this model through; that is why gates check behaviour too.

## A GitHub Actions workflow

Save this as `.github/workflows/ml.yml` in your repository. GitHub runs it on every push:

```yaml
name: train-and-check
on: [push, pull_request]
jobs:
  ml:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python -m pytest -q tests/            # code, data and API tests
      - run: python src/train.py --config configs/train.json --out candidate.joblib
      - run: python quality_gate.py candidate.joblib
      - run: docker build -t loan-service:${{ github.sha }} .
```

If any step fails, the workflow shows a red cross and the later steps (like building the image) do not run.

## Good CI/CD habits

- Keep the pipeline **fast**: train on a sample in CI, the full data on a schedule.
- Deploy to **staging** first and run smoke tests (call `/health` and one `/predict`).
- Keep the previous image so you can **roll back** in one command.
- Store gate thresholds in the repository, so changing them is visible and reviewed.

## Key terms

- **Continuous integration (CI)** — automatic tests on every change.
- **Continuous delivery (CD)** — automatic packaging and release after tests pass.
- **Quality gate** — a script that blocks models that are not good enough.
- **Exit code** — 0 means success, any other number means failure.
- **Staging** — a copy of production for final checks.
- **Rollback** — going back to the previous version.

**Takeaway:** CI/CD for ML runs tests, trains, and passes every model through an automatic quality gate before packaging — bad models are stopped by machines, not memory.

## Try it yourself

1. Add a check to the gate that the share of approved applicants is between 40% and 90%.
2. Set `MAX_DROP` to 0.05. Does the small model pass now? Is that a good idea?
3. Write the smoke test that staging should pass, as a short Python function using TestClient.
4. Create a free GitHub repository with the workflow above and watch it run.
""",
            "quiz": [
                ("What is continuous integration (CI)?",
                 ["Training once a year", "Automatically running tests on every code change", "Writing documentation", "Buying servers"],
                 1, "Every push is checked."),
                ("What does a quality gate do?",
                 ["Speeds up training", "Blocks models that are not good enough from being released", "Encrypts data", "Draws charts"],
                 1, "Machines check, not memory."),
                ("What exit code means success?",
                 ["0", "1", "200", "422"],
                 0, "Any non-zero exit code means failure."),
                ("Why did the smaller model fail the gate, even with a good AUC?",
                 ["It was too big", "It ignores late payments, so the behaviour check failed", "It had no name", "It used too many features"],
                 1, "Score-only gates miss this; behaviour checks catch it."),
                ("Where should a new version go before production?",
                 ["Nowhere", "Staging, for smoke tests", "Directly to all users", "A USB stick"],
                 1, "Staging catches surprises safely."),
                ("Why keep gate thresholds in the repository?",
                 ["They are secret", "Changes to them become visible and reviewed", "Git needs them", "To make CI slower"],
                 1, "Lowering a threshold should never be silent."),
            ],
        },
        # ------------------------------------------------------------------ 8
        {
            "title": "Experiment Tracking and the Model Registry",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=hm3HIZ5mns0",
            "content": r"""
**Learning objective:** Record every training run with its settings and results, compare runs fairly, and manage model versions with a registry that supports promotion and rollback.

## The spreadsheet problem

After a week of experiments: "Which settings gave AUC 0.89? Was that before or after we fixed the data?" **Experiment tracking** saves, for every run, the config, data fingerprint, metrics and time. A **model registry** keeps the approved model versions and which one is in production.

{APPLICANTS}

## A tiny tracker

```python
import hashlib, json, time
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried", "momo_tx_month"]
train, test = train_test_split(applicants, test_size=0.25, random_state=0, stratify=applicants["repaid"])
fingerprint = hashlib.sha256(pd.util.hash_pandas_object(train, index=False).values.tobytes()).hexdigest()[:12]
open("runs.jsonl", "w").close()

def build(kind, **params):
    if kind == "logreg":
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, **params))
    if kind == "forest":
        return RandomForestClassifier(n_estimators=200, random_state=0, **params)
    return GradientBoostingClassifier(random_state=0, **params)

def run(kind, **params):
    start = time.perf_counter()
    m = build(kind, **params).fit(train[FEATURES], train["repaid"])
    p = m.predict_proba(test[FEATURES])[:, 1]
    record = {"kind": kind, "params": params, "data": fingerprint,
              "auc": round(roc_auc_score(test["repaid"], p), 4),
              "accuracy": round(accuracy_score(test["repaid"], p >= 0.5), 4),
              "seconds": round(time.perf_counter() - start, 2)}
    with open("runs.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
    return m

for C in [0.01, 1.0, 100.0]:
    run("logreg", C=C)
for depth in [3, 8, None]:
    run("forest", max_depth=depth)
run("boosting", max_depth=2, n_estimators=150)

runs = pd.read_json("runs.jsonl", lines=True)
print(runs.sort_values("auc", ascending=False).to_string(index=False))
```

Now every result can be traced back to its exact settings and data. Notice:

- The **simple logistic regression** is as good as the bigger models here — the data is close to linear.
- Every forest is worse than the logistic regression, and the forest with no depth limit is worse than the one limited to depth 8: it overfits.
- Time matters too: a model 20 times slower for the same AUC is not an improvement.

When results are this close, choose the **simplest** model: easier to explain (Week 3), faster and cheaper.

## A model registry

```python
import datetime
import joblib

REGISTRY = "registry.json"
json.dump({"models": []}, open(REGISTRY, "w"))

def register(model, version, metrics, notes=""):
    reg = json.load(open(REGISTRY))
    path = f"model_{version}.joblib"
    joblib.dump(model, path)
    reg["models"].append({"version": version, "path": path, "metrics": metrics, "stage": "staging",
                          "data": fingerprint, "registered": datetime.date.today().isoformat(), "notes": notes})
    json.dump(reg, open(REGISTRY, "w"), indent=2)

def promote(version):
    reg = json.load(open(REGISTRY))
    for m in reg["models"]:
        if m["stage"] == "production":
            m["stage"] = "archived"
        if m["version"] == version:
            m["stage"] = "production"
    json.dump(reg, open(REGISTRY, "w"), indent=2)

def production():
    return next(m for m in json.load(open(REGISTRY))["models"] if m["stage"] == "production")

def show():
    for m in json.load(open(REGISTRY))["models"]:
        print(f"  {m['version']:6s} {m['stage']:11s} AUC {m['metrics']['auc']}  {m['notes']}")

best = runs.sort_values("auc", ascending=False).iloc[0]
register(build("logreg", C=1.0).fit(train[FEATURES], train["repaid"]), "1.0.0", {"auc": 0.88}, "logistic regression")
promote("1.0.0")
register(build("boosting", max_depth=2, n_estimators=150).fit(train[FEATURES], train["repaid"]), "1.1.0",
         {"auc": float(runs.loc[runs.kind == "boosting", "auc"].iloc[0])}, "gradient boosting")
promote("1.1.0")
print("after promoting 1.1.0:"); show()

promote("1.0.0")                        # a problem was found: roll back in one step
print("after rollback:"); show()
print("serving:", production()["version"], production()["path"])
```

The serving code only ever asks the registry "which model is in production?". Promotion and rollback become one small, recorded action — not copying files by hand at midnight.

## Real tools

- **MLflow** (open source) tracks runs and has a model registry with stages; it runs on your own server.
- Other options: Weights & Biases, DVC, cloud ML platforms.
- Whatever you use: record config, data fingerprint, code version (Git commit), metrics and who approved each promotion.

## Key terms

- **Experiment tracking** — recording settings, data and results of every run.
- **Run** — one training attempt.
- **Model registry** — the list of model versions with their stage.
- **Stage** — staging, production or archived.
- **Promotion** — moving a version to production.
- **Rollback** — returning to a previous version.

**Takeaway:** Track every run with its config, data and metrics; keep model versions in a registry so promotion and rollback are single, recorded steps.

## Try it yourself

1. Add a `git_commit` field to each run record (use any text for now).
2. Add three more runs and find the fastest model whose AUC is within 0.005 of the best.
3. Add an `approved_by` field to `promote` and refuse promotion when it is empty.
4. Read the MLflow quick-start guide and list which of our functions it replaces.
""",
            "quiz": [
                ("What should experiment tracking record for every run?",
                 ["Only the best score", "Config, data fingerprint, metrics and time", "The programmer's mood", "Nothing"],
                 1, "So every result can be traced."),
                ("What does a model registry keep?",
                 ["Training data", "Model versions and which stage each is in", "User passwords", "Videos"],
                 1, "Staging, production, archived."),
                ("Why was the forest with no depth limit worse?",
                 ["It was too simple", "It overfitted the training data", "It had no data", "Random forests never work"],
                 1, "Unlimited depth memorises noise."),
                ("When two models have almost the same AUC, which should you usually choose?",
                 ["The most complex", "The simplest, easier to explain and cheaper", "The newest", "The slowest"],
                 1, "Simplicity wins ties."),
                ("What is a rollback?",
                 ["Deleting all models", "Returning production to a previous version", "Training again", "A type of chart"],
                 1, "One recorded step with a registry."),
                ("Which open-source tool tracks runs and has a model registry?",
                 ["MLflow", "Excel", "Paint", "Zoom"],
                 0, "MLflow can run on your own server."),
            ],
        },
        # ------------------------------------------------------------------ 9
        {
            "title": "Monitoring Models in Production",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=n0bR0IArJDo",
            "content": r"""
**Learning objective:** Log predictions safely, compute service and model health metrics over time, and set alert rules that catch problems quickly.

## What to watch

| Layer | Metrics | Example alert |
|---|---|---|
| Service | Requests, errors, latency (p50, p95) | Error rate above 2% |
| Inputs | Missing values, ranges, distribution (drift) | Income distribution moved (next lesson) |
| Outputs | Approval rate, average probability | Approval rate jumps from 70% to 40% |
| Quality | Accuracy when real outcomes arrive | Accuracy 5 points below launch |
| Fairness | Approval rate by group (Week 3) | Gap between groups grows |

Outcomes (did they repay?) arrive **months** later, so service, input and output metrics are your early warning.

## Log every prediction — safely

```python
import hashlib
import hmac
import json

SECRET = b"replace-with-a-secret-from-the-environment"

def log_line(applicant_id, features, probability, latency_ms, status, version="1.0.0"):
    return json.dumps({
        "ts": "2026-11-09T10:15:02Z",
        "applicant": hmac.new(SECRET, str(applicant_id).encode(), hashlib.sha256).hexdigest()[:16],
        "version": version, "status": status, "latency_ms": latency_ms,
        "probability": probability, "features": features,
    })

print(log_line(1042, {"income_rwf": 350000, "loan_rwf": 200000}, 0.91, 38, 200))
```

The applicant's ID is replaced by a keyed hash (Week 3 explains why): you can still link a log line to a later outcome, but someone reading the logs cannot see who it was. Never log names, phone numbers or national IDs. Structured **JSON lines** are easy to search and analyse.

## Two weeks of traffic

{APPLICANTS}

{MODEL}

We simulate 14 days of requests. On day 10 the database becomes slow; on day 12 a new app version sends some broken requests:

```python
rng = np.random.default_rng(0)
logs = []
for day in range(1, 15):
    batch = make_applicants(n=300, seed=1000 + day)
    p = model.predict_proba(batch[FEATURES])[:, 1]
    latency = rng.lognormal(np.log(40), 0.35, len(batch)) * (3.0 if day == 10 else 1.0)
    status = np.where(rng.random(len(batch)) < (0.08 if day == 12 else 0.005), 422, 200)
    logs.append(pd.DataFrame({"day": day, "latency_ms": latency.round(1), "status": status,
                              "probability": np.where(status == 200, p, np.nan)}))
logs = pd.concat(logs, ignore_index=True)

daily = logs.groupby("day").agg(
    requests=("status", "size"),
    error_rate=("status", lambda s: (s != 200).mean()),
    p50_ms=("latency_ms", "median"),
    p95_ms=("latency_ms", lambda s: s.quantile(0.95)),
    approve_rate=("probability", lambda s: (s.dropna() >= 0.5).mean()),
).round(3)
print(daily.to_string())
```

**p95 latency** means 95% of requests were faster than this. Averages hide slow requests; percentiles show what your slowest users feel.

## Alert rules

```python
RULES = {
    "error rate above 2%": lambda d: d["error_rate"] > 0.02,
    "p95 latency above 150 ms": lambda d: d["p95_ms"] > 150,
    "approval rate outside 60%-80%": lambda d: not 0.60 <= d["approve_rate"] <= 0.80,
}
for day, row in daily.iterrows():
    fired = [name for name, rule in RULES.items() if rule(row)]
    if fired:
        print(f"day {day}: ALERT -> {', '.join(fired)}")
```

```python
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 3, figsize=(13, 3.2))
for ax, col, limit in zip(axes, ["error_rate", "p95_ms", "approve_rate"], [0.02, 150, None]):
    ax.plot(daily.index, daily[col], marker="o"); ax.set_title(col); ax.set_xlabel("day")
    if limit: ax.axhline(limit, color="red", linestyle="--")
plt.tight_layout(); plt.show()
```

The alerts fire on exactly the bad days, and the approval-rate rule stays quiet because the model itself is fine. A good alert is **specific** (says what broke), **actionable** (someone knows what to do) and **rare** (people ignore alerts that fire every day).

## In real systems

- Send logs to a central place (for example the ELK stack, Grafana Loki or a cloud service).
- Show dashboards with Grafana or similar, and send alerts to email, Slack or SMS.
- Write a **runbook** for each alert: what it means and the first three things to check.

## Key terms

- **Monitoring** — continuously measuring a system's health.
- **Structured logging** — logs as machine-readable records such as JSON lines.
- **Latency** — time to answer a request.
- **p95** — the value 95% of measurements are below.
- **Alert rule** — a condition that notifies a person.
- **Runbook** — instructions for responding to an alert.

**Takeaway:** Log every prediction safely, watch service, input, output and quality metrics with percentiles, and set few, specific, actionable alerts.

## Try it yourself

1. Add a rule "requests below 200 per day" and simulate a day with only 100 requests.
2. Make day 13 have 30% more rural applicants. Does the approval-rate alert fire?
3. Add a p99 column. How different is it from p95?
4. Write a three-line runbook for the "p95 latency" alert.
""",
            "quiz": [
                ("Why monitor inputs and outputs, not only accuracy?",
                 ["Accuracy is useless", "Real outcomes arrive months later, so inputs and outputs are early warnings", "They are cheaper to print", "It is required by Docker"],
                 1, "You cannot wait months to notice a problem."),
                ("Why replace the applicant ID with a keyed hash in logs?",
                 ["To save space", "To link logs to outcomes without showing who the person is", "To make logs faster", "Hashes are prettier"],
                 1, "Privacy-preserving linkage."),
                ("What does p95 latency mean?",
                 ["Average speed", "95% of requests were faster than this value", "95 requests per second", "The slowest request"],
                 1, "Percentiles show what slow users feel."),
                ("Which is a good alert?",
                 ["One that fires every hour", "Specific, actionable and rare", "Vague and frequent", "Sent to nobody"],
                 1, "Noisy alerts get ignored."),
                ("What should never be written to logs?",
                 ["Latency", "Names, phone numbers and national IDs", "Model version", "Status codes"],
                 1, "Logs are often widely accessible."),
                ("What is a runbook?",
                 ["A training plan for runners", "Instructions for responding to an alert", "A model file", "A log format"],
                 1, "So anyone on duty knows what to do."),
            ],
        },
        # ------------------------------------------------------------------ 10
        {
            "title": "Data Drift and Concept Drift",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=0wdCMvU1vCQ",
            "content": r"""
**Learning objective:** Measure data drift with PSI and the KS test, understand concept drift, and see why you need both input monitoring and outcome monitoring.

## The world does not stand still

- **Data drift:** the inputs change. Prices rise, so loans get bigger; a new mobile-money product changes transaction counts.
- **Concept drift:** the **link** between inputs and outcome changes. A large employer closes, so "has a salary" no longer protects against default.

A model trained on last year can be wrong this year in either case.

{APPLICANTS}

{MODEL}

## Measuring drift: PSI

The **Population Stability Index** compares how a feature is spread across bins in the training data and in new data:

> PSI = sum over bins of (new% − old%) × ln(new% ÷ old%)

A common rule of thumb: **below 0.1** no real change, **0.1–0.25** some change (watch), **above 0.25** big change (investigate).

```python
from scipy.stats import ks_2samp

def psi(reference, current, bins=10):
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    ref = np.histogram(reference, edges)[0] / len(reference)
    cur = np.histogram(current, edges)[0] / len(current)
    ref, cur = np.clip(ref, 1e-4, None), np.clip(cur, 1e-4, None)
    return float(np.sum((cur - ref) * np.log(cur / ref)))

def drift_report(reference, current):
    rows = []
    for f in FEATURES:
        value = psi(reference[f], current[f])
        rows.append({"feature": f, "psi": round(value, 3),
                     "ks_p_value": round(ks_2samp(reference[f], current[f]).pvalue, 4),
                     "status": "BIG CHANGE" if value > 0.25 else "watch" if value > 0.1 else "ok"})
    return pd.DataFrame(rows)

same_world = make_applicants(n=1000, seed=21)
later = make_applicants(n=1000, seed=22, drift=0.4)
print("new data from the same world:"); print(drift_report(train, same_world).to_string(index=False))
print("\na year later (prices and late payments up):"); print(drift_report(train, later).to_string(index=False))
```

The **KS test** asks "could these two samples come from the same distribution?"; a tiny p-value says no. Look at income in the first table: the KS test gives p ≈ 0.03 although the data comes from the **same** world — a false alarm. With large samples it flags even unimportant changes, so PSI's size is usually more useful for decisions.

## Does data drift hurt the model?

```python
def evaluate(data):
    p = model.predict_proba(data[FEATURES])[:, 1]
    return {"accuracy": round(accuracy_score(data[TARGET], p >= 0.5), 3),
            "auc": round(roc_auc_score(data[TARGET], p), 3), "approve_rate": round(float((p >= 0.5).mean()), 3)}

print("same world:", evaluate(same_world))
print("a year later:", evaluate(later))
```

Surprise: the inputs moved a lot (loan size PSI far above 0.25) but accuracy is **about the same**. The model still applies the same, correct rules — it just approves fewer people because loans really are riskier. Data drift is an **alarm to investigate**, not automatic proof that the model is broken.

## Concept drift: the silent killer

Now the rules of the world change, but the inputs look the same:

```python
changed = make_applicants(n=1000, seed=21, concept=1.5)
print("max PSI:", drift_report(train, changed)["psi"].max())
print("same world:   ", evaluate(same_world))
print("concept drift:", evaluate(changed))
```

PSI sees **nothing**, the approval rate is **identical** — but accuracy falls by about **12 points** (from 0.82 to 0.70). Only one thing reveals concept drift: comparing predictions with **real outcomes** when they arrive.

## A monitoring plan that covers both

1. **Inputs:** PSI per feature every week; investigate above 0.25.
2. **Outputs:** approval rate and probability distribution every day.
3. **Outcomes:** as repayments come in, accuracy and AUC per month — the only defence against concept drift.
4. **Early outcome signals:** in lending, "missed first payment" arrives sooner than "fully repaid".
5. **Response:** investigate → retrain on recent data → test → promote through the registry (Lesson 8).

## Key terms

- **Data drift** — input distributions change.
- **Concept drift** — the relationship between inputs and outcome changes.
- **PSI** — Population Stability Index, a size of distribution change.
- **KS test** — a statistical test for whether two samples have the same distribution.
- **Label delay** — the time until real outcomes are known.

**Takeaway:** Measure input drift with PSI, but remember that data drift does not always hurt and concept drift can hurt without any data drift — so always monitor real outcomes too.

## Try it yourself

1. Compute PSI for `drift=0.1`, `0.2` and `0.3`. At which value does loan size cross 0.25?
2. Try `concept=0.5` and `concept=1.0`. How much accuracy is lost?
3. Retrain the model on 2,000 rows of `make_applicants(seed=30, concept=1.5)` and evaluate it on `changed`.
4. Write a short message to the SACCO manager explaining concept drift in three sentences.
""",
            "quiz": [
                ("What is data drift?",
                 ["The model file moves", "The distribution of inputs changes", "Accuracy improves", "Data is deleted"],
                 1, "For example, loans get bigger."),
                ("What is concept drift?",
                 ["Inputs change colour", "The relationship between inputs and outcome changes", "A slow server", "A bug in pandas"],
                 1, "For example, salary stops protecting against default."),
                ("By a common rule of thumb, what does PSI above 0.25 mean?",
                 ["No change", "A big change: investigate", "The model is perfect", "Delete the data"],
                 1, "Below 0.1 ok, 0.1–0.25 watch, above 0.25 investigate."),
                ("In the lesson, what happened to accuracy under strong data drift?",
                 ["It collapsed", "It stayed about the same", "It reached 100%", "It became negative"],
                 1, "Drift is an alarm to investigate, not proof of failure."),
                ("Why is concept drift called silent?",
                 ["It makes no noise", "Inputs and approval rate can look unchanged while accuracy falls", "It only happens at night", "It deletes logs"],
                 1, "Only real outcomes reveal it."),
                ("What is the only reliable way to detect concept drift?",
                 ["PSI", "Comparing predictions with real outcomes when they arrive", "Restarting the server", "Counting requests"],
                 1, "Outcome monitoring."),
            ],
        },
        # ------------------------------------------------------------------ 11
        {
            "title": "Releasing Safely: Shadow Mode, Canary and A/B Tests",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=GN5PJXajxKw",
            "content": r"""
**Learning objective:** Release a new model with low risk using shadow mode, canary releases and A/B tests, decide with statistics instead of feelings, and choose between batch and real-time scoring.

## Never switch everyone at once

A new model can pass every test and still surprise you with real traffic. Release in steps:

| Strategy | What happens | Risk to users |
|---|---|---|
| **Shadow mode** | The new model scores every request, but only the old model's answer is used | None |
| **Canary** | A small share (say 5–10%) of requests use the new model | Small |
| **A/B test** | Two groups get different models; you compare outcomes | Controlled |
| **Full rollout** | Everyone uses the new model; the old one stays ready for rollback | Watched closely |

{APPLICANTS}

{MODEL}

## Shadow mode

```python
from sklearn.ensemble import GradientBoostingClassifier

challenger = GradientBoostingClassifier(max_depth=2, n_estimators=150, random_state=0).fit(train[FEATURES], train[TARGET])
traffic = make_applicants(n=2000, seed=40)

old = model.predict_proba(traffic[FEATURES])[:, 1] >= 0.5          # the answer users get
new = challenger.predict_proba(traffic[FEATURES])[:, 1] >= 0.5     # logged only
print(f"agreement: {(old == new).mean():.1%}")
print(f"approval rate  old {old.mean():.1%}  new {new.mean():.1%}")
diff = traffic[old != new]
print(f"{len(diff)} applicants would get a different decision; review a sample by hand:")
print(diff[FEATURES].head(3).to_string(index=False))
```

Shadow mode shows **how different** the new model is on real requests, at zero risk. Look at the disagreements by hand: are the new decisions sensible?

## Canary routing

Send a fixed share of applicants to the new model. A hash of the ID keeps each person on the same model every time they apply:

```python
import hashlib

def use_new_model(applicant_id, share=0.10):
    bucket = int(hashlib.sha256(f"canary-v2:{applicant_id}".encode()).hexdigest(), 16) % 100
    return bucket < share * 100

routed = traffic["applicant_id"].map(use_new_model)
print(f"share on the new model: {routed.mean():.1%}")
print("same answer for the same person every time:", use_new_model(123) == use_new_model(123))
```

If canary metrics look bad (errors, strange approval rate), turn the share back to 0% — one setting.

## A/B test: is the difference real?

The SACCO tests a new approval policy. In group A (old policy) 640 of 800 approved loans were repaid; in group B, 668 of 800. Is B really better, or is it luck?

```python
from scipy.stats import norm

def two_proportion_test(success_a, n_a, success_b, n_b):
    pa, pb = success_a / n_a, success_b / n_b
    pooled = (success_a + success_b) / (n_a + n_b)
    se = np.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = (pb - pa) / se
    return pa, pb, z, 2 * (1 - norm.cdf(abs(z)))

pa, pb, z, p_value = two_proportion_test(640, 800, 668, 800)
print(f"A {pa:.1%}  B {pb:.1%}  difference {pb - pa:+.1%}  p-value {p_value:.3f}")

pa, pb, z, p_value = two_proportion_test(3200, 4000, 3340, 4000)
print(f"same rates, 5x more loans: p-value {p_value:.4f}")
```

With 800 loans per group the p-value is about **0.07** — not quite convincing at the usual 0.05 level. With five times more loans, the same difference gives a tiny p-value. **Decide the sample size before the test**, and do not stop early just because the numbers look good — that is how many A/B tests go wrong.

## Batch or real-time?

```python
import time

start = time.perf_counter()
for i in range(200):
    model.predict_proba(traffic[FEATURES].iloc[[i]])
one_by_one = (time.perf_counter() - start) / 200

start = time.perf_counter()
model.predict_proba(traffic[FEATURES])
batch = (time.perf_counter() - start) / len(traffic)
print(f"one at a time: {one_by_one * 1000:.2f} ms each | batch: {batch * 1000:.4f} ms each "
      f"({one_by_one / batch:.0f}x faster per applicant)")
```

| | Real-time (API) | Batch |
|---|---|---|
| When | An applicant waits for an answer | Scoring many records on a schedule (every night) |
| Speed per item | Slower | Much faster |
| Example | Loan decision at the counter | Monthly risk review of all active loans |

## Key terms

- **Shadow mode** — the new model runs on real traffic but its answers are not used.
- **Canary release** — a small share of traffic gets the new version.
- **A/B test** — a controlled comparison of two versions on two groups.
- **p-value** — how surprising the result would be if there were no real difference.
- **Batch scoring** — scoring many records together on a schedule.

**Takeaway:** Release new models in steps — shadow, canary, A/B, full rollout — decide with pre-planned statistics, and pick batch or real-time scoring by how fast an answer is needed.

## Try it yourself

1. Change the canary share to 25% and check the real share.
2. Find the smallest group size (try 1,000, 1,500, 2,000…) at which 80% vs 83.5% has a p-value below 0.05.
3. List three things you would check by hand in the shadow-mode disagreements.
4. Decide batch or real-time for: SMS reminders to late payers, a USSD loan request, an annual portfolio report.
""",
            "quiz": [
                ("In shadow mode, whose answers do users get?",
                 ["The new model's", "The old model's; the new model is only logged", "Both", "Neither"],
                 1, "Zero risk to users."),
                ("Why route canary traffic with a hash of the applicant ID?",
                 ["It is faster", "The same person always gets the same model", "To hide the model", "Hashes are random every time"],
                 1, "Consistent experience and clean comparison."),
                ("What did a p-value of about 0.07 with 800 loans per group mean?",
                 ["B is certainly better", "Not quite convincing at the usual 0.05 level", "A is better", "The test failed to run"],
                 1, "More data was needed."),
                ("What is a common mistake in A/B tests?",
                 ["Planning the sample size", "Stopping early because the numbers look good", "Using two groups", "Recording results"],
                 1, "Decide the size before you start."),
                ("Which is a good use of batch scoring?",
                 ["A loan decision at the counter", "A nightly review of all active loans", "A chat reply", "A login page"],
                 1, "No one is waiting for each answer."),
                ("What should stay ready during a full rollout?",
                 ["Nothing", "The old model, for rollback", "A new dataset", "A second office"],
                 1, "Always be able to go back."),
            ],
        },
        # ------------------------------------------------------------------ 12
        {
            "title": "Week 2 Project: Monitor, Detect and Retrain",
            "minutes": 120,
            "video": "https://www.youtube.com/watch?v=4BgmBtsS0iA",
            "content": r"""
**Learning objective:** Run a model through six simulated months of production, detect drift and quality loss, retrain on recent data, and decide on promotion with evidence.

## The brief

The loan model went live in January. Each month you receive the new applications, and — later — whether they repaid. The economy slowly changes (data drift), and from March the rules of repayment also change (concept drift). Your job: monitor, decide when to act, retrain, and prove the new model is better before promoting it.

{APPLICANTS}

{MODEL}

## Part 1 — A monthly health check

```python
from scipy.stats import ks_2samp

def psi(reference, current, bins=10):
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    ref = np.clip(np.histogram(reference, edges)[0] / len(reference), 1e-4, None)
    cur = np.clip(np.histogram(current, edges)[0] / len(current), 1e-4, None)
    return float(np.sum((cur - ref) * np.log(cur / ref)))

BASELINE_ACC = accuracy_score(test[TARGET], proba >= 0.5)

def health(model, month_data, reference):
    p = model.predict_proba(month_data[FEATURES])[:, 1]
    psis = {f: psi(reference[f], month_data[f]) for f in FEATURES}
    worst = max(psis, key=psis.get)
    return {"approve_rate": round((p >= 0.5).mean(), 3), "max_psi": round(psis[worst], 3), "worst_feature": worst,
            "accuracy": round(accuracy_score(month_data[TARGET], p >= 0.5), 3)}
```

## Part 2 — Six months in production

```python
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
DRIFT = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25]
CONCEPT = [0.0, 0.0, 0.4, 0.8, 1.2, 1.5]

history, months = [], {}
for i, name in enumerate(MONTHS):
    data = make_applicants(n=1200, seed=500 + i, drift=DRIFT[i], concept=CONCEPT[i])
    months[name] = data
    h = health(model, data, train)
    h["accuracy_drop"] = round(BASELINE_ACC - h["accuracy"], 3)
    reasons = []
    if h["max_psi"] > 0.25:
        reasons.append(f"input drift in {h['worst_feature']}")
    if h["accuracy_drop"] > 0.05:
        reasons.append("accuracy down more than 5 points")
    h["action"] = "RETRAIN: " + " and ".join(reasons) if reasons else "ok"
    history.append({"month": name, **h})

report = pd.DataFrame(history)
print(f"baseline accuracy {BASELINE_ACC:.3f}")
print(report.to_string(index=False))
```

```python
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots(figsize=(8, 3.5))
ax1.plot(report["month"], report["accuracy"], marker="o", label="accuracy")
ax1.axhline(BASELINE_ACC - 0.05, color="red", linestyle="--", label="retrain line")
ax2 = ax1.twinx(); ax2.bar(report["month"], report["max_psi"], alpha=0.25, color="gray", label="max PSI")
ax1.set_ylabel("accuracy"); ax2.set_ylabel("max PSI"); ax1.legend(loc="lower left"); plt.show()
```

Read the table: when did input drift appear, and when did accuracy cross the retrain line? Remember the outcomes for a month are only known later — in real life you would see June's accuracy months after June.

## Part 3 — Retrain on recent data

```python
from sklearn.base import clone

recent = pd.concat([months["May"], months["Jun"]])
recent_train, recent_check = train_test_split(recent, test_size=0.3, random_state=0, stratify=recent[TARGET])
candidate = clone(model).fit(recent_train[FEATURES], recent_train[TARGET])

july = make_applicants(n=1500, seed=600, drift=0.3, concept=1.6)      # next month, never seen
def score(m, data):
    p = m.predict_proba(data[FEATURES])[:, 1]
    return {"accuracy": round(accuracy_score(data[TARGET], p >= 0.5), 3), "auc": round(roc_auc_score(data[TARGET], p), 3)}

print("current model on July:  ", score(model, july))
print("retrained model on July:", score(candidate, july))
coef = pd.DataFrame({"feature": FEATURES,
                     "old": model[-1].coef_[0].round(2), "new": candidate[-1].coef_[0].round(2)})
print(coef.to_string(index=False))
```

The retrained model learned the new rules — look at how the weights for `salaried` and `late_payments` changed. That is concept drift, visible in the model itself.

## Part 4 — Decide

```python
old_s, new_s = score(model, july), score(candidate, july)
decision = ("PROMOTE 1.1.0 (via shadow mode, then canary)" if new_s["auc"] > old_s["auc"] + 0.01
            else "KEEP 1.0.0 and investigate")
print(decision)
```

## Your report (two pages)

1. The monthly table and chart, with one sentence per month.
2. Which problems were data drift and which concept drift, and how you could tell.
3. The retraining: data used, results on July, how the weights changed.
4. The release plan: shadow mode → canary → full, and the rollback trigger.
5. What you would monitor next, and how often.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Monitoring | Monthly drift and accuracy with clear thresholds |
| Diagnosis | Correctly separates data drift from concept drift |
| Retraining | Recent data, fair comparison on unseen data |
| Decision | Evidence-based promotion with a safe release plan |
| Communication | Short, clear explanations for a manager |

**Takeaway:** Monitoring, diagnosis, retraining and careful promotion form one loop — the heart of running models in production.

## Try it yourself

Complete Parts 1–4 and the report. Then try a different retraining window (only June, or March–June) and explain which works best on July and why.
""",
            "quiz": [
                ("Why can you not see June's accuracy at the end of June in real life?",
                 ["Accuracy is secret", "Repayment outcomes arrive months later", "June is too short", "The model is offline"],
                 1, "Label delay."),
                ("Which data did the project retrain on?",
                 ["Only January", "Recent months (May and June)", "Random internet data", "No data"],
                 1, "Recent data reflects the new rules."),
                ("Why test both models on July data?",
                 ["July is longer", "It is new, unseen data — a fair comparison", "It is easier", "To make the old model win"],
                 1, "Never compare on data the candidate trained on."),
                ("What did the changed weights for salaried and late_payments show?",
                 ["A bug", "Concept drift: the rules of repayment changed", "Data deletion", "Nothing"],
                 1, "The model learned the new relationship."),
                ("How should the retrained model be released?",
                 ["Switch everyone instantly", "Shadow mode, then canary, then full rollout with a rollback trigger", "Email it to customers", "Never"],
                 1, "Safe release steps from Lesson 11."),
                ("What is the main loop of running models in production?",
                 ["Train once and forget", "Monitor, diagnose, retrain and promote carefully", "Only add servers", "Only write reports"],
                 1, "That loop is MLOps."),
            ],
        },
    ],
})
