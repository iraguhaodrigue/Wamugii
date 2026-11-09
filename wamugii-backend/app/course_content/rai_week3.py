"""Responsible AI & Deployment -- Week 3: Fairness, Explainability, Privacy and Security. Original WAMUGII content."""

from app.course_content.rai_data import fill

FAIRNESS_TOOLS = r"""
```python
def group_report(data, group, decision, outcome="repaid"):
    rows = []
    for name, g in data.groupby(group):
        rows.append({
            group: name, "people": len(g),
            "approval_rate": g[decision].mean(),                              # selection rate
            "approved_if_would_repay": g.loc[g[outcome] == 1, decision].mean(), # true positive rate
            "approved_if_would_default": g.loc[g[outcome] == 0, decision].mean(), # false positive rate
            "repay_rate": g[outcome].mean(),
        })
    return pd.DataFrame(rows).set_index(group).round(3)

def fairness_summary(report):
    a, t = report["approval_rate"], report["approved_if_would_repay"]
    return {"approval_gap": round(float(a.max() - a.min()), 3),
            "disparate_impact": round(float(a.min() / a.max()), 3),
            "equal_opportunity_gap": round(float(t.max() - t.min()), 3)}
```
""".strip()

WEEK3 = fill({
    "title": "Week 3 · Fairness, Explainability, Privacy and Security",
    "lessons": [
        # ------------------------------------------------------------------ 13
        {
            "title": "Measuring Fairness",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=-YXOVspBWpo",
            "content": r"""
**Learning objective:** Measure how a model treats different groups with approval rates, true and false positive rates, disparate impact and equal opportunity, and explain why different fairness definitions can disagree.

## Why measure fairness?

A model can be accurate **on average** and still treat a group of people worse — rural applicants, women, older people, speakers of one language. In lending, that means some people are refused credit they would have repaid. You cannot fix what you do not measure.

Our model does **not** use gender or area as inputs. Does that make it fair? Let us measure.

{APPLICANTS}

{MODEL}

## Group metrics

{FAIRNESS_TOOLS}

```python
audit = test.copy()
audit["approved"] = (model.predict_proba(audit[FEATURES])[:, 1] >= 0.5).astype(int)

for group in ["area", "gender"]:
    report = group_report(audit, group, "approved")
    print(report.to_string()); print(fairness_summary(report), "\n")
```

What each column means:

- **approval_rate** — share of the group approved (also called selection rate).
- **approved_if_would_repay** — among people who really would repay, the share approved (the **true positive rate**). Low values mean good borrowers are being refused.
- **approved_if_would_default** — among people who would default, the share approved (the **false positive rate**).
- **repay_rate** — how often the group really repays.

## Three fairness measures

| Measure | Question | Our model, by area |
|---|---|---|
| **Approval gap** (demographic parity difference) | Are groups approved at similar rates? | Large |
| **Disparate impact ratio** | Lowest approval rate ÷ highest | Below 0.8 |
| **Equal opportunity gap** | Are people who would repay approved at similar rates? | Several points |

The "**four-fifths rule**" from US employment guidelines treats a disparate-impact ratio below **0.8** as a warning sign. It is a rule of thumb, not a law of nature — but a useful alarm.

For **gender**, all measures are small: women and men repay at the same rate and the model treats them alike. For **area**, rural applicants are approved much less often.

## Is that unfair? It depends on the definition

Rural applicants in our data **do** repay less often (lower incomes, fewer salaried jobs). So:

- By **demographic parity**, the model is unfair: approval rates differ a lot.
- By **equal opportunity**, it is partly unfair: rural people who **would** repay are still refused more often than urban people who would repay.
- By **calibration** (a 70% score means 70% repay, in every group), it may be fair.

Researchers have proved that when groups have different repay rates, these definitions **cannot all be satisfied at once** (except with a perfect model). Choosing the definition is not a technical choice: it is a decision about values, made with the SACCO's leaders, the people affected, and the law — and written down (Week 4).

```python
import matplotlib.pyplot as plt
report = group_report(audit, "area", "approved")
report[["approval_rate", "approved_if_would_repay", "repay_rate"]].plot.bar(figsize=(7, 3.5), rot=0)
plt.title("Loan model by area"); plt.ylim(0, 1); plt.show()
```

## Good habits

- Measure fairness for **every group** that matters — even when the group is not a model input.
- Keep group labels (gender, area) in a **separate, protected** table used only for auditing.
- Look at **several** measures, and at small groups' sample sizes (a rate from 20 people is noisy).
- Report results honestly, including where the model is unfair.

## Key terms

- **Selection rate** — share of a group that gets the positive decision.
- **True positive rate** — share of truly positive cases that are approved.
- **Demographic parity** — equal selection rates across groups.
- **Disparate impact ratio** — lowest selection rate ÷ highest; below 0.8 is a warning.
- **Equal opportunity** — equal true positive rates across groups.
- **Calibration** — scores mean the same probability in every group.

**Takeaway:** Leaving gender and area out of the model does not guarantee fairness; measure group metrics, know that fairness definitions conflict, and decide the definition openly with the people affected.

## Try it yourself

1. Add an age group column (under 30, 30–45, over 45) and run `group_report` for it.
2. Change the approval threshold to 0.6. What happens to the area gaps?
3. Check calibration: for applicants with scores between 0.6 and 0.8, what share repaid in each area?
4. Write two sentences for the SACCO board explaining the difference between demographic parity and equal opportunity.
""",
            "quiz": [
                ("If a model does not use gender or area as inputs, is it automatically fair?",
                 ["Yes, always", "No — you must measure how it treats each group", "Only on Mondays", "Only if accuracy is high"],
                 1, "Other features can carry group differences."),
                ("What is the disparate impact ratio?",
                 ["Accuracy ÷ AUC", "The lowest group approval rate ÷ the highest", "The number of groups", "Errors per day"],
                 1, "Below 0.8 is a common warning sign."),
                ("What does equal opportunity compare?",
                 ["Ages", "Approval rates among people who would really repay, across groups", "Income levels", "Number of loans"],
                 1, "Are good borrowers treated alike?"),
                ("Why can fairness definitions disagree?",
                 ["Because of bugs", "When groups have different outcome rates, they cannot all be satisfied at once", "They never disagree", "Python rounds numbers"],
                 1, "A proven impossibility result."),
                ("Who should choose the fairness definition?",
                 ["Only the programmer", "Leaders, affected people and the law, decided openly and written down", "Nobody", "The model itself"],
                 1, "It is a values decision."),
                ("Where should gender and area labels be kept?",
                 ["In public logs", "In a separate, protected table used for auditing", "Inside the model", "On the website"],
                 1, "Needed to audit, protected from misuse."),
            ],
        },
        # ------------------------------------------------------------------ 14
        {
            "title": "Where Bias Comes From and How to Reduce It",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=vq8mDiDODhc",
            "content": r"""
**Learning objective:** Show how historical bias and proxy features enter a model, apply three mitigation methods, and compare their effects on fairness and accuracy.

## Sources of bias

| Source | Example in lending |
|---|---|
| **Historical bias** | Training on past officers' decisions, which were unfair |
| **Proxy features** | Mobile-money activity is much lower in rural areas, so it "stands in" for area |
| **Representation bias** | Few applicants from one district, so the model learns little about them |
| **Measurement bias** | "Late payments" recorded more strictly in some branches |
| **Feedback loops** | Refused people never get loans, so they never build a repayment record |

{APPLICANTS}

{MODEL}

{FAIRNESS_TOOLS}

## Historical bias: copying unfair decisions

Many organisations train on **past decisions** because real outcomes are missing for refused people. Our data has `approved_before`: past loan-officer decisions that were secretly unfair to rural applicants and women.

```python
past = applicants.groupby(["area", "gender"])[["approved_before", "repaid"]].mean().round(3)
print(past)
```

Women and men repay at the **same** rate, yet women were approved less often. Rural applicants were approved far less than their repay rate justifies. Now train a model to copy those decisions:

```python
def fit_and_audit(target, features, label, weights=None):
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    m.fit(train[features], train[target], logisticregression__sample_weight=weights)
    out = test.copy()
    out["approved"] = (m.predict_proba(out[features])[:, 1] >= 0.5).astype(int)
    auc = roc_auc_score(out["repaid"], m.predict_proba(out[features])[:, 1])     # judged on real repayment
    area, gender = fairness_summary(group_report(out, "area", "approved")), fairness_summary(group_report(out, "gender", "approved"))
    return {"model": label, "auc_vs_real_repayment": round(auc, 3),
            "area_eq_opp_gap": area["equal_opportunity_gap"], "area_disparate_impact": area["disparate_impact"],
            "gender_eq_opp_gap": gender["equal_opportunity_gap"]}

train = train.assign(is_female=(train["gender"] == "female").astype(int), is_rural=(train["area"] == "rural").astype(int))
test = test.assign(is_female=(test["gender"] == "female").astype(int), is_rural=(test["area"] == "rural").astype(int))

results = [
    fit_and_audit("approved_before", FEATURES + ["is_female", "is_rural"], "copy officers, with gender+area"),
    fit_and_audit("approved_before", FEATURES, "copy officers, gender+area removed"),
]
print(pd.DataFrame(results).to_string(index=False))
```

- **With** gender and area as inputs, the model copies both unfair patterns.
- **Removing** them fixes the gender gap — but **not** the area gap. Why?

## Proxies

```python
from sklearn.model_selection import cross_val_score
for target in ["is_rural", "is_female"]:
    auc = cross_val_score(LogisticRegression(max_iter=1000), StandardScaler().fit_transform(train[FEATURES]),
                          train[target], cv=5, scoring="roc_auc").mean()
    print(f"can the other features guess {target}? AUC {auc:.2f}")
print(train.groupby("area")[["momo_tx_month", "salaried", "income_rwf"]].mean().round({"momo_tx_month": 0, "salaried": 2, "income_rwf": -3}))
```

The other features predict **area** very well (mobile-money activity, salary and income all differ by area) but cannot predict **gender**. So the model learns "low mobile money → refuse", which is really "rural → refuse". Removing a sensitive column is **not enough** when proxies exist.

## Three ways to reduce bias

```python
# 1. Better labels: learn from real repayment, not from past decisions
results.append(fit_and_audit("repaid", FEATURES, "train on real repayment"))

# 2. Reweighing: give each (group, label) combination equal total weight
grp = train["area"] + "_" + train["approved_before"].astype(str)
weights = (1.0 / grp.map(grp.value_counts())).values * len(train) / grp.nunique()
results.append(fit_and_audit("approved_before", FEATURES, "copy officers + reweighing", weights))

# 3. Remove the strongest proxy
no_momo = [f for f in FEATURES if f != "momo_tx_month"]
results.append(fit_and_audit("repaid", no_momo, "real repayment, no mobile-money feature"))

print(pd.DataFrame(results).to_string(index=False))
```

Read the table row by row:

- **Better labels** help the most. When real outcomes exist, learn from them — not from people's past judgements.
- **Reweighing** reduces the area gap of the "copy officers" model, at little cost.
- **Removing the strongest proxy** helps further here: disparate impact rises above 0.8 at almost no accuracy cost, because the model barely relied on mobile-money activity (Lesson 15 shows this). That is not always so — proxies often carry real, legitimate information, and removing them can cost accuracy. Measure before deciding.

A fourth method, **different thresholds per group**, can equalise approval rates, but it means treating people differently by group at decision time, which may be unlawful discrimination in many places. Get legal advice before using it.

## Mitigation is a decision, not a button

There is no free lunch: each method moves accuracy and different fairness measures in different ways. Put the options in a table like the one above, discuss them with the decision-makers, choose, and **document why** (Week 4). Then keep monitoring fairness in production — it can drift too.

## Key terms

- **Historical bias** — unfairness carried in from past decisions in the data.
- **Proxy** — a feature that stands in for a sensitive attribute.
- **Reweighing** — giving training examples weights to balance groups and labels.
- **Pre-, in-, post-processing** — fixing bias in the data, in training, or in the decisions.
- **Feedback loop** — model decisions shape the future data the model learns from.

**Takeaway:** Bias enters through past decisions and proxies; removing sensitive columns is not enough — compare mitigations openly, prefer better labels, and document the choice.

## Try it yourself

1. Which single feature is the strongest proxy for area? Remove each feature in turn and measure.
2. Change the reweighing to balance gender instead of area. What happens?
3. Explain the feedback loop in lending in three sentences. How could the SACCO break it?
4. Make a table of the five rows above for gender as well as area.
""",
            "quiz": [
                ("What is historical bias?",
                 ["Old computers", "Unfairness carried in from past decisions recorded in the data", "Slow training", "A history lesson"],
                 1, "Copying past officers copies their unfairness."),
                ("Why did removing the area column not remove the area gap?",
                 ["It was a bug", "Other features act as proxies for area", "The model ignored all features", "Area was never in the data"],
                 1, "Mobile money, salary and income differ by area."),
                ("Why did removing gender fix the gender gap here?",
                 ["Luck", "No other feature could stand in for gender", "Women were removed", "The model used age"],
                 1, "No proxy for gender in this data."),
                ("Which mitigation helped most in the lesson?",
                 ["Adding more features", "Training on real repayment instead of past decisions", "Deleting rural applicants", "Raising the threshold"],
                 1, "Better labels beat copying biased judgements."),
                ("What is reweighing?",
                 ["Weighing applicants", "Giving training examples weights so groups and labels are balanced", "Changing the threshold", "Removing data"],
                 1, "A pre-processing method."),
                ("Why be careful with different thresholds per group?",
                 ["They are slow", "Treating people differently by group at decision time may be unlawful", "They always fail", "They need a GPU"],
                 1, "Get legal advice first."),
            ],
        },
        # ------------------------------------------------------------------ 15
        {
            "title": "Explaining Model Decisions",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=Wl9L592ycc4",
            "content": r"""
**Learning objective:** Explain what drives a model overall and why it made one decision, give people clear reasons and actionable "what would change the decision" answers, and know the limits of explanations.

## Who needs explanations?

- **The applicant**: "Why was I refused, and what can I do?"
- **The loan officer**: "Can I trust this score?"
- **The developer and auditor**: "Is the model using sensible signals?"
- **The regulator**: "Can you justify decisions that affect people?"

{APPLICANTS}

{MODEL}

## Global explanations: what matters overall

```python
from sklearn.inspection import permutation_importance

coefs = pd.Series(model[-1].coef_[0], index=FEATURES)                   # on standardised features
perm = permutation_importance(model, test[FEATURES], test[TARGET], scoring="roc_auc", n_repeats=10, random_state=0)
importance = pd.DataFrame({"weight (standardised)": coefs.round(2),
                           "AUC lost when shuffled": pd.Series(perm.importances_mean, index=FEATURES).round(3)})
print(importance.sort_values("AUC lost when shuffled", ascending=False).to_string())
```

- **Weights** of a logistic regression on standardised data show direction (+ helps repayment, − hurts) and strength.
- **Permutation importance** works for **any** model: shuffle one column and see how much the score drops. A big drop means the model relies on it.

Check these against common sense: income, loan size and late payments should matter most — and they do.

## Local explanations: why this applicant?

For a logistic regression, each feature's contribution to the score is simply weight × (standardised value). Compared with an average applicant, that gives clear **reason codes**:

```python
scaler, lr = model[0], model[-1]
REASONS = {"income_rwf": "income", "loan_rwf": "loan amount", "years_member": "years as a member",
           "late_payments": "late payments", "salaried": "salary status", "momo_tx_month": "mobile-money activity"}

def explain(applicant, top=2):
    row = pd.DataFrame([applicant])[FEATURES]
    p = float(model.predict_proba(row)[0, 1])
    contrib = pd.Series(lr.coef_[0] * scaler.transform(row)[0], index=FEATURES)
    hurts = contrib.sort_values().head(top)
    helps = contrib.sort_values(ascending=False).head(top)
    print(f"repay probability {p:.0%} -> {'APPROVE' if p >= 0.5 else 'REFER / DECLINE'}")
    print("  main reasons against:", ", ".join(f"{REASONS[f]} ({v:+.2f})" for f, v in hurts.items() if v < 0) or "none")
    print("  main reasons for:    ", ", ".join(f"{REASONS[f]} ({v:+.2f})" for f, v in helps.items() if v > 0) or "none")

aline = {"income_rwf": 180_000, "loan_rwf": 520_000, "years_member": 2, "late_payments": 2, "salaried": 0, "momo_tx_month": 20}
explain(aline)
```

## Counterfactuals: what would change the decision?

People find "what could I change?" more useful than numbers:

```python
def smallest_change(applicant, feature, values):
    for v in values:
        trial = dict(applicant, **{feature: v})
        if model.predict_proba(pd.DataFrame([trial])[FEATURES])[0, 1] >= 0.5:
            return v
    return None

loan_ok = smallest_change(aline, "loan_rwf", range(520_000, 0, -10_000))
late_ok = smallest_change(dict(aline, loan_rwf=300_000), "late_payments", [1, 0])
print(f"Approved if the loan were {loan_ok:,} RWF or less (instead of 520,000)." if loan_ok else "No loan amount works alone.")
print(f"With a 300,000 RWF loan: approved if late payments drop to {late_ok}." if late_ok is not None
      else "With a 300,000 RWF loan, fewer late payments alone would not be enough.")
```

A good message to Aline: "We could approve a loan of up to the amount above today. Paying on time for the next months would also improve your result." Only suggest changes a person **can** make — never "change your age or area".

## SHAP and the limits of explanations

For complex models (forests, boosting, neural networks), the **SHAP** library computes similar per-feature contributions using game theory. Limits to remember:

- An explanation describes the **model**, not the real world: "late payments" explains the score, it does not prove causation.
- Explanations can be **misleading** for correlated features (income and salary move together).
- A clear explanation of an unfair model is still an unfair model.
- Simple, explainable models are often nearly as accurate (Lesson 8) — prefer them for high-stakes decisions.

## Key terms

- **Global explanation** — what drives the model overall.
- **Local explanation** — why the model gave one particular answer.
- **Permutation importance** — score lost when one feature is shuffled.
- **Reason codes** — the top factors behind a decision, in plain words.
- **Counterfactual explanation** — the smallest realistic change that would change the decision.
- **SHAP** — a method and library for per-feature contributions in any model.

**Takeaway:** Explain models globally and individually, give people reasons and realistic counterfactuals in plain language, and remember that explanations describe the model, not the truth.

## Try it yourself

1. Explain three applicants of your own design, including one who is approved.
2. Find the smallest increase in `years_member` that would approve Aline (keep the 520,000 loan).
3. Rewrite the reason codes as one friendly SMS of under 160 characters.
4. Compute permutation importance with accuracy instead of AUC. Does the order change?
""",
            "quiz": [
                ("What does permutation importance measure?",
                 ["Training time", "How much the score drops when one feature is shuffled", "The number of features", "Model size"],
                 1, "Works for any model."),
                ("What is a local explanation?",
                 ["An explanation in the local language only", "Why the model gave one particular answer", "A summary of all data", "A server log"],
                 1, "Reason codes for one applicant."),
                ("What is a counterfactual explanation?",
                 ["A false statement", "The smallest realistic change that would change the decision", "A random example", "A legal document"],
                 1, "'Approved if the loan were 400,000 RWF or less.'"),
                ("Which change should never be suggested to an applicant?",
                 ["Borrow less", "Pay on time", "Change your age or area", "Save more"],
                 2, "Only suggest changes people can make."),
                ("What is a limit of explanations?",
                 ["They are always causal", "They describe the model, not proof of cause in the real world", "They make models fair", "They need no data"],
                 1, "A clear explanation of an unfair model is still unfair."),
                ("What does SHAP do?",
                 ["Encrypts data", "Computes per-feature contributions for any model", "Trains models faster", "Draws maps"],
                 1, "Game-theory-based explanations."),
            ],
        },
        # ------------------------------------------------------------------ 16
        {
            "title": "Privacy and Data Protection",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=NUk6QN02UxQ",
            "content": r"""
**Learning objective:** Apply Rwanda's data-protection principles to an ML system with data minimisation, pseudonymisation, k-anonymity checks, differential privacy for statistics, and deletion and retention rules.

## The law and the principles

Rwanda's **Law No. 058/2021 relating to the protection of personal data and privacy**, supervised by the National Cyber Security Authority (NCSA), sets rules for anyone who processes personal data. Key ideas you must design for:

- **Lawful basis and purpose** — collect data for a clear, stated purpose (for example consent or a contract).
- **Data minimisation** — collect and keep only what you need.
- **Accuracy and storage limits** — keep data correct and only as long as needed.
- **Security** — protect data against loss and misuse.
- **Rights of the data subject** — people can ask to see, correct or delete their data, and to object.
- **Storage outside Rwanda** — allowed only under conditions in the law.

This lesson is not legal advice: check the current law and NCSA guidance for your project. Many other countries have similar laws (for example the EU's GDPR).

{APPLICANTS}

## 1. Minimise

```python
raw = applicants.assign(
    full_name=[f"Applicant {i}" for i in applicants["applicant_id"]],
    phone=["07" + str(8_800_000_00 + i)[-8:] for i in applicants["applicant_id"]],
)
MODEL_NEEDS = ["income_rwf", "loan_rwf", "years_member", "late_payments", "salaried", "momo_tx_month", "repaid"]
AUDIT_NEEDS = ["age", "gender", "area"]                      # kept apart, for fairness checks only
print("collected:", list(raw.columns))
print("model table:", MODEL_NEEDS)
print("dropped for modelling:", [c for c in raw.columns if c not in MODEL_NEEDS + AUDIT_NEEDS + ["applicant_id"]])
```

The model never needs names or phone numbers, so they never enter the modelling data.

## 2. Pseudonymise

Replace IDs with a **keyed hash** (HMAC). Without the secret key, nobody can reverse it or recompute it — but you can still join tables:

```python
import hashlib
import hmac
import os

KEY = os.environ.get("PSEUDONYM_KEY", "demo-key-use-a-real-secret").encode()

def pseudonym(value):
    return hmac.new(KEY, str(value).encode(), hashlib.sha256).hexdigest()[:16]

model_table = raw[MODEL_NEEDS].assign(pid=raw["applicant_id"].map(pseudonym))
audit_table = raw[AUDIT_NEEDS].assign(pid=raw["applicant_id"].map(pseudonym))
print(model_table.head(3).to_string(index=False))
print("plain SHA-256 of ID 1 (anyone can recompute it!):", hashlib.sha256(b"1").hexdigest()[:16])
```

A plain hash of an ID is **not** private: someone can hash all possible IDs and match them. The secret key prevents that. Pseudonymised data is still personal data under the law — but much safer.

## 3. Check re-identification risk with k-anonymity

Even without names, a rare combination (a 62-year-old rural man) can identify someone. **k-anonymity** asks: is every combination of "quasi-identifiers" shared by at least k people?

```python
def smallest_group(df, columns):
    return int(df.groupby(columns).size().min())

print("exact age + gender + area: smallest group =", smallest_group(audit_table, ["age", "gender", "area"]))
banded = audit_table.assign(age_band=pd.cut(audit_table["age"], [0, 30, 45, 120], labels=["<30", "30-45", "45+"]))
print("age band + gender + area:  smallest group =", smallest_group(banded, ["age_band", "gender", "area"]))
```

With exact ages, some combinations have only a handful of people — risky to share. With age **bands**, every group has many people. Generalise data before sharing it for research or reports.

## 4. Differential privacy for published statistics

When you publish counts ("how many rural borrowers defaulted"), adding carefully sized random noise protects each individual: the result barely changes whether any one person is in the data or not.

```python
rng = np.random.default_rng(0)

def private_count(true_count, epsilon):
    return true_count + rng.laplace(0, 1 / epsilon)          # one person changes a count by at most 1

defaults = applicants.groupby("area")["repaid"].apply(lambda s: int((s == 0).sum()))
for eps in [0.1, 1.0]:
    noisy = {a: round(private_count(c, eps)) for a, c in defaults.items()}
    print(f"epsilon {eps}: true {defaults.to_dict()} -> published {noisy}")
```

Smaller **epsilon** = more noise = more privacy. For large counts the noise hardly matters; for small groups it protects people strongly.

## 5. Deletion and retention

```python
def delete_person(applicant_id, *tables):
    p = pseudonym(applicant_id)
    return [t[t["pid"] != p] for t in tables]

model_table, audit_table = delete_person(17, model_table, audit_table)
print("rows left:", len(model_table), len(audit_table))

RETENTION = {"raw application forms": "5 years after the loan closes (check your legal obligations)",
             "model training tables": "until the next retraining, then replaced",
             "prediction logs": "12 months, pseudonymised"}
for item, rule in RETENTION.items():
    print(f"- {item}: {rule}")
```

Remember: deleting a person from the data does not remove them from an **already trained** model. Plan regular retraining so deletions take effect, and record when each request was handled.

## Key terms

- **Personal data** — information about an identifiable person.
- **Data minimisation** — collecting and keeping only what is needed.
- **Pseudonymisation** — replacing identifiers with codes that need a secret to link back.
- **k-anonymity** — every combination of quasi-identifiers is shared by at least k people.
- **Differential privacy** — adding calibrated noise so results barely depend on any one person.
- **Retention policy** — how long each kind of data is kept.

**Takeaway:** Design privacy in: collect less, separate audit data, pseudonymise with a secret key, check re-identification risk, add noise to published statistics, and honour deletion and retention rules under Rwanda's data-protection law.

## Try it yourself

1. Find the age-band boundaries that give a smallest group of at least 100 people.
2. Publish the number of defaulters per area and gender with epsilon 0.5. Which counts change most, relatively?
3. Write a one-paragraph privacy notice an applicant could understand.
4. List every place personal data appears in your Week 1 service (logs, backups, test files…).
""",
            "quiz": [
                ("Which Rwandan law protects personal data and privacy?",
                 ["Law No. 058/2021", "The Road Traffic Law", "The Tax Code", "There is none"],
                 0, "Supervised by the National Cyber Security Authority."),
                ("What is data minimisation?",
                 ["Compressing files", "Collecting and keeping only the data you need", "Deleting the model", "Using small fonts"],
                 1, "Names and phone numbers never enter the model table."),
                ("Why is a plain SHA-256 hash of an ID not private?",
                 ["It is too long", "Anyone can hash all possible IDs and match them", "It is random", "It cannot be stored"],
                 1, "A secret key (HMAC) prevents this."),
                ("What does k-anonymity check?",
                 ["Encryption strength", "That every combination of quasi-identifiers is shared by at least k people", "Model accuracy", "Password length"],
                 1, "Rare combinations can identify people."),
                ("In differential privacy, what does a smaller epsilon mean?",
                 ["Less noise", "More noise and more privacy", "Faster code", "No effect"],
                 1, "Privacy budget."),
                ("Does deleting a person's data remove them from an already trained model?",
                 ["Yes, instantly", "No — retraining is needed for the deletion to take effect", "Only on Fridays", "Models never contain data"],
                 1, "Plan retraining for deletions."),
            ],
        },
        # ------------------------------------------------------------------ 17
        {
            "title": "Security for AI Systems",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=nErkn4Na7ZE",
            "content": r"""
**Learning objective:** Identify the main attacks on ML systems, see poisoning, gaming and model copying in action, and protect a model API with authentication, rate limits and safe loading.

## The threat model

| Attack | What the attacker does | Defence |
|---|---|---|
| **Data poisoning** | Inserts false training data or labels | Control and validate data sources, track changes |
| **Evasion / gaming** | Changes inputs cheaply to get approved | Use verified, hard-to-fake features; monitor |
| **Model extraction** | Queries the API many times to copy the model | Authentication, rate limits, coarse outputs |
| **Membership inference** | Learns whether a person was in the training data | Less overfitting, differential privacy |
| **Unsafe model files** | Sends a model file that runs code when loaded | Only load trusted files; prefer safe formats |
| **Prompt injection** (LLM apps) | Hides instructions in input text | Course 6, Lesson 23 |
| **Classic attacks** | Stolen keys, open ports, old libraries | Secrets management, updates, least privilege |

{APPLICANTS}

{MODEL}

## Poisoning: an insider flips labels

Someone with access to the training data marks many rural repayers as "defaulted":

```python
rng = np.random.default_rng(3)
poisoned = train.copy()
targets = poisoned.index[(poisoned["area"] == "rural") & (poisoned[TARGET] == 1)]
flip = rng.choice(targets, size=int(0.6 * len(targets)), replace=False)
poisoned.loc[flip, TARGET] = 0

bad = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(poisoned[FEATURES], poisoned[TARGET])
for name, m in [("clean model", model), ("poisoned model", bad)]:
    approved = m.predict_proba(test[FEATURES])[:, 1] >= 0.5
    rural = (test["area"] == "rural").values
    print(f"{name:15s} AUC {roc_auc_score(test[TARGET], m.predict_proba(test[FEATURES])[:, 1]):.3f} | "
          f"rural approval {approved[rural].mean():.1%} | urban approval {approved[~rural].mean():.1%}")
```

The overall AUC drops only a little — it would still pass a 0.80 quality gate — but rural approvals collapse to about a third of what they were. Defences: restrict who can change training data, keep a change log, compare label rates per group between data versions, and run the fairness audit (Lessons 13–14) before every release.

## Gaming: cheap features can be faked

Mobile-money activity is easy to inflate: someone can make many tiny transfers before applying.

```python
applicant = {"income_rwf": 200_000, "loan_rwf": 420_000, "years_member": 1, "late_payments": 1, "salaried": 0, "momo_tx_month": 15}
for tx in [15, 60, 120]:
    p = model.predict_proba(pd.DataFrame([dict(applicant, momo_tx_month=tx)])[FEATURES])[0, 1]
    print(f"{tx:3d} transactions/month -> repay probability {p:.0%}")
```

Defences: prefer features that are verified or costly to fake (repayment history, verified salary), cap how much one feature can add, and watch for sudden jumps in a feature before applications.

## Model extraction: copying through the API

```python
from sklearn.tree import DecisionTreeClassifier

queries = make_applicants(n=2000, seed=77)[FEATURES]                 # attacker invents applicants
answers = model.predict(queries)                                     # ... and records the API's decisions
copy = DecisionTreeClassifier(max_depth=6, random_state=0).fit(queries, answers)
fresh = make_applicants(n=2000, seed=78)[FEATURES]
print(f"the copied model agrees with ours on {(copy.predict(fresh) == model.predict(fresh)).mean():.1%} of new applicants")
```

With 2,000 free queries, an attacker gets a close copy — which they can use to find exactly how to game it. Defences: require an **API key**, **rate-limit** each key, return only the decision (not the exact probability) to outside users, and watch for unusual query patterns.

## A protected API

```python
import secrets
import time
from collections import defaultdict, deque
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

API_KEYS = {"branch-kigali": "kgl-" + secrets.token_hex(8)}          # in real life: from a secret store
calls = defaultdict(deque)
LIMIT, WINDOW = 5, 60

def check_key(x_api_key: str = Header(default="")):
    for client_name, key in API_KEYS.items():
        if secrets.compare_digest(x_api_key, key):                  # constant-time comparison
            now = time.time(); q = calls[client_name]
            while q and now - q[0] > WINDOW:
                q.popleft()
            if len(q) >= LIMIT:
                raise HTTPException(429, "Too many requests")
            q.append(now)
            return client_name
    raise HTTPException(401, "Missing or wrong API key")

class Applicant(BaseModel):
    income_rwf: float = Field(..., ge=10_000, le=20_000_000)
    loan_rwf: float = Field(..., ge=10_000, le=5_000_000)
    years_member: int = Field(..., ge=0, le=60)
    late_payments: int = Field(..., ge=0, le=50)
    salaried: int = Field(..., ge=0, le=1)
    momo_tx_month: int = Field(..., ge=0, le=1000)

app = FastAPI()

@app.post("/decide")
def decide(a: Applicant, client_name: str = Depends(check_key)):
    p = model.predict_proba(pd.DataFrame([a.model_dump()])[FEATURES])[0, 1]
    return {"decision": "approve" if p >= 0.5 else "refer to officer"}     # no raw probability outside

api = TestClient(app)
body = dict(applicant, momo_tx_month=15)
print("no key:   ", api.post("/decide", json=body).status_code)
key = {"X-API-Key": API_KEYS["branch-kigali"]}
print("with key: ", [api.post("/decide", json=body, headers=key).status_code for _ in range(7)])
```

No key → **401**. With a key, the sixth call within a minute → **429 Too Many Requests**.

## Never load untrusted model files

`joblib` and `pickle` files can run code when loaded. This harmless demo only prints a message — a real attacker could do anything:

```python
import pickle

class Surprise:
    def __reduce__(self):
        return (print, ("!!! code ran while loading this file — it could have been anything !!!",))

data = pickle.dumps(Surprise())
pickle.loads(data)
```

Only load model files you created or that come from a trusted, checked source; verify a checksum before loading; and prefer safe formats (for example ONNX or safetensors) when sharing models.

## Key terms

- **Threat model** — a list of who might attack, how, and the defences.
- **Data poisoning** — corrupting training data to change the model.
- **Evasion / gaming** — changing inputs to get a desired output.
- **Model extraction** — copying a model by querying it.
- **Rate limiting** — capping requests per client per time window.
- **Constant-time comparison** — comparing secrets without leaking timing information.

**Takeaway:** AI systems face poisoning, gaming, copying and unsafe files on top of classic attacks — defend with controlled data, robust features, authentication, rate limits, coarse outputs and trusted artifacts.

## Try it yourself

1. Poison only 20% of rural repayer labels. Would your Week 2 quality gate notice? Would the fairness audit?
2. Make the copied model with 200 queries instead of 2,000. How much does agreement drop?
3. Add a second API key for another branch and check each branch has its own limit.
4. Write a threat model table for a USSD loan application service.
""",
            "quiz": [
                ("What is data poisoning?",
                 ["Food safety", "Corrupting training data or labels to change the model", "A slow database", "Deleting logs"],
                 1, "An insider flipping labels is one example."),
                ("Why was the poisoning hard to notice from AUC alone?",
                 ["AUC went to zero", "Overall AUC dropped only a little while one group was harmed a lot", "AUC is not computed", "The model crashed"],
                 1, "Group-level checks catch it."),
                ("Why is mobile-money activity a risky feature?",
                 ["It is always missing", "It is cheap to inflate, so people can game the model", "It is illegal", "It has no values"],
                 1, "Prefer verified, costly-to-fake features."),
                ("How can attackers copy a model through an API?",
                 ["By guessing the password", "By sending many queries and training on the answers", "By reading the logo", "They cannot"],
                 1, "Model extraction."),
                ("Which status code means too many requests?",
                 ["200", "401", "429", "422"],
                 2, "401 means missing or wrong key."),
                ("Why never load untrusted pickle or joblib files?",
                 ["They are large", "They can run code when loaded", "They are slow", "They lose accuracy"],
                 1, "Only load trusted, checked files."),
            ],
        },
        # ------------------------------------------------------------------ 18
        {
            "title": "Week 3 Project: A Responsible AI Audit",
            "minutes": 120,
            "video": "https://www.youtube.com/watch?v=FkCb7345Hj8",
            "content": r"""
**Learning objective:** Audit a deployed model for performance, fairness, explainability, privacy and security, and produce a written audit report with findings and recommendations.

## The brief

The SACCO board asks: "Is our loan model safe and fair to use?" You will run a complete audit and write the report the board will read. The audit must be **repeatable**: one function that can run again after every retraining.

{APPLICANTS}

{MODEL}

{FAIRNESS_TOOLS}

## Part 1 — Performance

```python
p = model.predict_proba(test[FEATURES])[:, 1]
audit = test.assign(score=p, approved=(p >= 0.5).astype(int))
performance = {"AUC": round(roc_auc_score(audit[TARGET], p), 3),
               "accuracy": round(accuracy_score(audit[TARGET], audit["approved"]), 3),
               "approval rate": round(float(audit["approved"].mean()), 3)}
print(performance)
```

## Part 2 — Fairness

```python
fair = {}
for group in ["area", "gender"]:
    report = group_report(audit, group, "approved")
    fair[group] = (report, fairness_summary(report))
    print(report.to_string()); print(fair[group][1], "\n")
```

## Part 3 — Explainability

```python
from sklearn.inspection import permutation_importance
perm = permutation_importance(model, test[FEATURES], test[TARGET], scoring="roc_auc", n_repeats=5, random_state=0)
drivers = pd.Series(perm.importances_mean, index=FEATURES).sort_values(ascending=False).round(3)
print(drivers.to_string())
```

## Part 4 — Privacy and security checks

```python
SENSITIVE = {"full_name", "phone", "national_id", "gender", "area", "age"}
checks = {
    "model uses no sensitive or identifying columns": not (set(FEATURES) & SENSITIVE),
    "fairness gap on equal opportunity below 0.10 for every group":
        all(s["equal_opportunity_gap"] < 0.10 for _, s in fair.values()),
    "disparate impact at least 0.8 for every group": all(s["disparate_impact"] >= 0.8 for _, s in fair.values()),
    "top drivers are financial, not proxies": drivers.index[0] in {"income_rwf", "loan_rwf", "late_payments"},
    "API requires a key and rate limit (Lesson 17)": True,          # confirm from the service code
    "prediction logs pseudonymised (Lesson 9)": True,               # confirm from the logging code
}
for name, ok in checks.items():
    print(("PASS  " if ok else "ISSUE ") + name)
```

## Part 5 — Write the report

```python
def table(df):
    return "\n".join("    " + line for line in df.to_string().splitlines())   # indented = shown as a table

issues = [name for name, ok in checks.items() if not ok]
lines = ["# Loan model audit report", "",
         f"Model: logistic regression, features: {', '.join(FEATURES)}", "",
         "## 1. Performance", *[f"- {k}: {v}" for k, v in performance.items()], "",
         "## 2. Fairness"]
for group, (report, summary) in fair.items():
    lines += [f"### By {group}", table(report), "", f"Summary: {summary}", ""]
lines += ["## 3. What drives the model", table(drivers.to_frame("AUC lost when shuffled")), "",
          "## 4. Checks", *[f"- [{'x' if ok else ' '}] {n}" for n, ok in checks.items()], "",
          "## 5. Findings and recommendations"]
if issues:
    lines += [f"- ISSUE: {i}" for i in issues]
    lines += ["- Recommendation: keep human review for refused rural applicants until the gap is reduced.",
              "- Recommendation: test mitigations from Lesson 14 and re-run this audit.",
              "- Recommendation: re-audit monthly in production and after every retraining."]
else:
    lines += ["- No blocking issues found. Re-audit monthly and after every retraining."]
open("audit_report.md", "w").write("\n".join(lines))
print("\n".join(lines[:12])); print("...")
print("issues:", issues)
```

The audit finds that the model is accurate and does not use sensitive data, but it **fails** the disparate-impact check for area: rural applicants are approved at only about 76% of the urban rate, below the 0.8 warning line. Rural applicants who would repay are also refused a little more often (a gap of about 5 points, inside our 0.10 limit). That is exactly the kind of finding a board must see before deciding.

## Your report (three pages)

1. Summary for the board in five sentences: is the model safe to use, under which conditions?
2. Performance, fairness (by area and gender), drivers — with tables.
3. Privacy and security status.
4. Findings ranked by severity, each with an owner and a date.
5. Recommendation: deploy, deploy with conditions (for example human review), or do not deploy.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Coverage | Performance, fairness, explanations, privacy and security all checked |
| Evidence | Every claim backed by a number or a test |
| Honesty | Problems reported clearly, not hidden |
| Recommendations | Concrete, owned, dated |
| Repeatability | The audit runs again with one call |

**Takeaway:** A responsible AI audit is repeatable, evidence-based and honest — and its findings lead to concrete decisions, not just a report on a shelf.

## Try it yourself

Complete Parts 1–5 and the board report. Then re-run the audit for the "train on real repayment, no mobile-money feature" model from Lesson 14 and compare the two reports side by side.
""",
            "quiz": [
                ("Why must an audit be repeatable?",
                 ["To make it longer", "So it can run again after every retraining and in production", "Boards like code", "It is not needed"],
                 1, "Models change; audits must keep up."),
                ("What did the audit find for area?",
                 ["Perfect fairness", "Rural applicants are approved at under 80% of the urban rate", "No rural applicants", "The model uses area as an input"],
                 1, "It fails the disparate-impact check — an important finding for the board."),
                ("Which is a good recommendation format?",
                 ["'Be fairer'", "A concrete action with an owner and a date", "No recommendations", "Only technical words"],
                 1, "Owned and dated actions get done."),
                ("What should happen to problems found in an audit?",
                 ["Hide them", "Report them clearly with evidence", "Delete the data", "Retrain until they disappear silently"],
                 1, "Honesty builds trust."),
                ("Which option can be safer than full deployment or no deployment?",
                 ["Deploy with conditions, such as human review of refused rural applicants", "Deploy to everyone instantly", "Turn off logging", "Remove the audit"],
                 0, "Conditions reduce harm while issues are fixed."),
                ("What should every audit claim be backed by?",
                 ["Opinions", "A number or a test", "Colours", "Rumours"],
                 1, "Evidence-based reporting."),
            ],
        },
    ],
})

for _lesson in WEEK3["lessons"]:
    _lesson["content"] = _lesson["content"].replace("{FAIRNESS_TOOLS}", FAIRNESS_TOOLS)
