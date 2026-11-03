"""Machine Learning Fundamentals -- Week 3: Evaluating and Improving Models. Original WAMUGII content."""

from app.course_content.ml_data import fill_data

SPLIT = r"""
```python
from sklearn.model_selection import train_test_split

X = loans.drop(columns="defaulted")
y = loans["defaulted"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
```
""".strip()

MODEL = r"""
```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

model = make_pipeline(StandardScaler(), LogisticRegression())
model.fit(X_train, y_train)
```
""".strip()

WEEK3 = {
    "title": "Week 3 · Evaluating and Improving Models",
    "lessons": [
        # ------------------------------------------------------------------ 13
        {
            "title": "Cross-Validation: Testing Without Luck",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=fSytzGwwBVw",
            "content": r"""
**Learning objective:** Show why one train/test split can mislead, use k-fold cross-validation to compare models, and keep a final test set untouched.

## One split is one roll of the dice

In Week 2 you saw that a model's test score changes when the split changes. Let's measure how much:

{LOANS}

```python
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X = loans.drop(columns="defaulted")
y = loans["defaulted"]

scores = []
for seed in range(10):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25,
                                              random_state=seed, stratify=y)
    m = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_tr, y_tr)
    scores.append(m.score(X_te, y_te))
print(np.round(scores, 3))
print("lowest", min(scores), "highest", max(scores))
```

The **same model** scores anywhere from about **0.82 to 0.89** depending only on which borrowers landed in the test set. If you compared two models on one lucky split, you could pick the wrong one.

## k-fold cross-validation

**Cross-validation** uses every row for testing once:

1. Split the training data into **k** equal parts (folds), for example k = 5.
2. Train on 4 folds and test on the 5th.
3. Repeat 5 times, so each fold is the test fold once.
4. Report the **average** score and its **spread** (standard deviation).

| Round | Fold 1 | Fold 2 | Fold 3 | Fold 4 | Fold 5 |
|---|---|---|---|---|---|
| 1 | test | train | train | train | train |
| 2 | train | test | train | train | train |
| 3 | train | train | test | train | train |
| 4 | train | train | train | test | train |
| 5 | train | train | train | train | test |

## Three sets, three jobs

Professionals keep a **final test set** locked away and use cross-validation on the rest:

- **Training folds** — the model learns.
- **Validation folds** (inside cross-validation) — you compare models and settings.
- **Test set** — used **once**, at the very end, to report the final score.

{SPLIT}

```python
from sklearn.model_selection import cross_val_score

model = make_pipeline(StandardScaler(), LogisticRegression())
cv_scores = cross_val_score(model, X_train, y_train, cv=5)
print(cv_scores.round(3))
print("mean", cv_scores.mean().round(3), "+/-", cv_scores.std().round(3))
```

You should see five scores between about 0.84 and 0.87, with a mean of about **0.86 ± 0.01**. That "± 0.01" is valuable: it tells you how much the score wobbles.

Because the scaler is inside the pipeline, it is re-fitted on the training folds in every round — no leakage.

## Compare models fairly

```python
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
candidates = {
    "Logistic regression": make_pipeline(StandardScaler(), LogisticRegression()),
    "k-NN (k=15)": make_pipeline(StandardScaler(), KNeighborsClassifier(15)),
    "Random forest": RandomForestClassifier(300, min_samples_leaf=5, random_state=42, n_jobs=-1),
    "Gradient boosting": GradientBoostingClassifier(random_state=42),
}
for name, m in candidates.items():
    s = cross_val_score(m, X_train, y_train, cv=cv)
    print(f"{name:20s} {s.mean():.3f} +/- {s.std():.3f}")
```

**StratifiedKFold** keeps the 21% default rate in every fold; `shuffle=True` mixes the rows first. Logistic regression comes out on top (about 0.86), but the others are within about 0.015 — roughly one standard deviation. When scores are that close, prefer the **simpler** model.

## Choosing k

- **k = 5 or 10** is standard.
- More folds = more training data per round but more computing time.
- **Leave-one-out** (k = number of rows) is only for tiny datasets.

For data in **time order** (sales per month, exchange rates), never shuffle: use `TimeSeriesSplit`, which always trains on the past and tests on the future.

## Key terms

- **Cross-validation** — repeated training and testing on different folds.
- **Fold** — one of the k equal parts of the data.
- **Validation set** — data used to compare models and settings.
- **Stratified k-fold** — folds that keep the class proportions.
- **TimeSeriesSplit** — cross-validation that respects time order.

**Takeaway:** One split is luck; cross-validation gives an average and a spread, and the final test set is opened only once.

## Try it yourself

1. Run `cross_val_score` with `cv=10`. Does the mean change? Does the spread change?
2. Use `cross_validate(model, X_train, y_train, cv=5, return_train_score=True)` and compare train and validation scores. Is the model overfitting?
3. Add a `DecisionTreeClassifier()` with no depth limit to the comparison. Where does it rank?
4. Explain to a classmate why you must not tune a model by looking at the test set.
""",
            "quiz": [
                ("Why can a single train/test split be misleading?",
                 ["It is too slow", "The score depends on which rows happened to land in the test set", "It uses no data", "It always overfits"],
                 1, "Scores changed from about 0.82 to 0.89 with the split alone."),
                ("In 5-fold cross-validation, how many times is the model trained?",
                 ["1", "4", "5", "10"],
                 2, "Once per fold."),
                ("What does the ± value after a cross-validation mean tell you?",
                 ["The training time", "How much the score varies between folds", "The number of features", "The learning rate"],
                 1, "A small spread means a stable estimate."),
                ("When should the final test set be used?",
                 ["Many times while tuning", "Once, at the end, to report the final score", "Never", "Before cleaning"],
                 1, "Using it repeatedly turns it into another validation set."),
                ("Why use StratifiedKFold for the loans data?",
                 ["To keep the default rate the same in every fold", "To sort by income", "To remove defaulters", "To scale data"],
                 0, "Stratified folds keep class shares equal."),
                ("Which cross-validation suits monthly sales data?",
                 ["Shuffled KFold", "TimeSeriesSplit", "Leave-one-out with shuffling", "No validation"],
                 1, "Time-ordered data must train on the past and test on the future."),
            ],
        },
        # ------------------------------------------------------------------ 14
        {
            "title": "Confusion Matrix, Precision and Recall",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=Kdsp6soqA7o",
            "content": r"""
**Learning objective:** Build and read a confusion matrix, calculate precision, recall and F1, and decide which matters more for a real problem.

## Accuracy is not enough

In Lesson 4 a model that said "nobody defaults" scored 79% accuracy and caught **zero** defaulters. To see what a classifier really does, count its four kinds of answers.

{LOANS}

{SPLIT}

{MODEL}

## The confusion matrix

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

pred = model.predict(X_test)
print(confusion_matrix(y_test, pred))
ConfusionMatrixDisplay.from_predictions(y_test, pred, display_labels=["repaid", "default"])
plt.show()
```

You should see:

|  | Predicted repaid | Predicted default |
|---|---|---|
| **Really repaid** | 366 (TN) | 28 (FP) |
| **Really defaulted** | 54 (FN) | 52 (TP) |

- **True positives (TP) = 52** — defaulters correctly flagged.
- **True negatives (TN) = 366** — good borrowers correctly approved.
- **False positives (FP) = 28** — good borrowers wrongly flagged (a lost customer).
- **False negatives (FN) = 54** — defaulters the model missed (lost money).

"Positive" simply means the class we are looking for (default), not something good.

## Precision and recall

> **Precision** = TP ÷ (TP + FP) — of the borrowers we flagged, how many really defaulted?
> **Recall** = TP ÷ (TP + FN) — of all real defaulters, how many did we catch?

```python
from sklearn.metrics import precision_score, recall_score, f1_score

print("Precision:", round(precision_score(y_test, pred), 3))   # 52 / 80
print("Recall:   ", round(recall_score(y_test, pred), 3))      # 52 / 106
print("F1:       ", round(f1_score(y_test, pred), 3))
```

- Precision is about **0.65**: when the model says "default", it is right 65% of the time.
- Recall is about **0.49**: it catches only **half** of the real defaulters.

The 84% accuracy hid this weakness completely.

## F1: one number for both

> F1 = 2 × precision × recall ÷ (precision + recall)

F1 (here about **0.56**) is high only when **both** precision and recall are high. It is useful when the positive class is rare.

## The full report

```python
from sklearn.metrics import classification_report

print(classification_report(y_test, pred, target_names=["repaid", "default"], digits=3))
```

It shows precision, recall and F1 for each class, plus their averages. **Support** is the number of real examples of each class.

## Which matters more?

| Situation | Worse mistake | Focus on |
|---|---|---|
| Cancer screening | Missing a cancer (FN) | **Recall** |
| Fraud alerts on mobile money | Missing fraud (FN), but too many alerts annoy customers | Recall, while watching precision |
| Spam filter | Hiding a real email (FP) | **Precision** |
| Approving micro-loans | Depends on the money lost vs earned | Both — choose with costs (next lesson) |

There is almost always a **trade-off**: catching more positives (higher recall) usually means more false alarms (lower precision). The decision threshold controls it — next lesson.

## Sensitivity and specificity

Doctors use other names:

- **Sensitivity** = recall = TP ÷ (TP + FN).
- **Specificity** = TN ÷ (TN + FP) — how many healthy people are correctly cleared. Here 366 ÷ 394 ≈ **0.93**.

## Key terms

- **Confusion matrix** — table of TP, TN, FP and FN.
- **Precision** — share of predicted positives that are correct.
- **Recall (sensitivity)** — share of real positives that are found.
- **F1 score** — balance of precision and recall.
- **Specificity** — share of real negatives correctly identified.

**Takeaway:** Always look at the confusion matrix; precision and recall show which mistakes a model makes, and the right balance depends on what each mistake costs.

## Try it yourself

1. Compute precision and recall by hand from the confusion matrix, then check with scikit-learn.
2. Build the confusion matrix for the "nobody defaults" `DummyClassifier`. What are its precision and recall?
3. Train a random forest and compare its precision and recall with logistic regression.
4. For a mobile-money fraud detector, write two sentences on whether you would favour precision or recall, and why.
""",
            "quiz": [
                ("A model flags 80 borrowers as defaulters and 52 really defaulted. What is its precision?",
                 ["0.49", "0.52", "0.65", "0.80"],
                 2, "52 ÷ 80 = 0.65."),
                ("There were 106 real defaulters and the model caught 52. What is its recall?",
                 ["About 0.49", "0.65", "0.84", "1.0"],
                 0, "52 ÷ 106 ≈ 0.49."),
                ("In cancer screening, which measure matters most?",
                 ["Precision", "Recall: catch as many real cancers as possible", "Training accuracy", "Number of features"],
                 1, "Missing a cancer is the worst mistake."),
                ("What is a false negative in the loan problem?",
                 ["A good borrower wrongly flagged", "A defaulter the model approved", "A correct approval", "A correct flag"],
                 1, "The model said 'no default' but the borrower defaulted."),
                ("When is F1 high?",
                 ["Only when precision is high", "Only when recall is high", "When both precision and recall are high", "When accuracy is low"],
                 2, "F1 balances the two."),
                ("For a spam filter, why is precision usually more important?",
                 ["A real email hidden as spam is costly", "Spam is harmless", "Recall cannot be computed", "Spam filters have no false positives"],
                 0, "Losing an important email is worse than seeing one spam message."),
            ],
        },
        # ------------------------------------------------------------------ 15
        {
            "title": "ROC Curves and Choosing a Threshold",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=4jRBRDbJemM",
            "content": r"""
**Learning objective:** Move the decision threshold to trade precision for recall, read a ROC curve and AUC, and choose a threshold from real business costs.

## The threshold is a business decision

`predict()` says "default" when the probability is above **0.5**. Nothing forces that. A lender who fears losses can refuse anyone above 0.3; one who wants more customers can use 0.7.

{LOANS}

{SPLIT}

{MODEL}

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score

proba = model.predict_proba(X_test)[:, 1]
for t in [0.5, 0.4, 0.3, 0.2, 0.1]:
    pred_t = (proba >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred_t).ravel()
    print(f"threshold {t}: caught {tp} of 106 defaulters, wrongly refused {fp}, "
          f"precision {precision_score(y_test, pred_t):.2f}, recall {recall_score(y_test, pred_t):.2f}")
```

Lowering the threshold from 0.5 to 0.2 raises recall from about **0.49 to 0.84** (89 of 106 defaulters caught) — but wrongly refuses 110 good borrowers instead of 28. Every threshold is a different trade-off.

## The ROC curve

The **ROC curve** shows every threshold at once:

- x-axis: **false positive rate** = FP ÷ (FP + TN) — good borrowers wrongly refused.
- y-axis: **true positive rate** = recall — defaulters caught.

```python
import matplotlib.pyplot as plt
from sklearn.metrics import RocCurveDisplay, roc_auc_score

RocCurveDisplay.from_predictions(y_test, proba, name="Logistic regression")
plt.plot([0, 1], [0, 1], "--", color="grey", label="random guessing")
plt.legend()
plt.show()
print("AUC:", round(roc_auc_score(y_test, proba), 3))
```

- A perfect model goes straight up to the top-left corner.
- The diagonal is random guessing.
- The **AUC** (area under the curve) summarises the whole curve: 1.0 is perfect, 0.5 is random. Our model has an AUC of about **0.86**.

AUC has a friendly meaning: pick one random defaulter and one random good borrower — AUC is the chance the model gives the defaulter the **higher** risk score.

## Compare models with AUC

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(300, min_samples_leaf=5, random_state=42, n_jobs=-1).fit(X_train, y_train)
print("Random forest AUC:", round(roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1]), 3))
```

The forest's AUC (about 0.84) is a little lower. AUC does not depend on any threshold, so it is a fair way to compare rankings. For very rare positives (fraud at 1%), also look at the **precision–recall curve** (`PrecisionRecallDisplay`), which is more sensitive to the rare class.

## Choose the threshold with money

Suppose the lender **earns a 15% fee** on each repaid loan and **loses 60%** of each defaulted loan (after some recovery). Let's compute the profit for every threshold on the test borrowers:

```python
import numpy as np

amount = X_test["loan_rwf"].to_numpy()
actual = y_test.to_numpy()

def profit(threshold):
    approve = proba < threshold
    earned = 0.15 * amount[approve & (actual == 0)].sum()
    lost = 0.60 * amount[approve & (actual == 1)].sum()
    return earned - lost

for t in [0.15, 0.25, 0.35, 0.5, 0.7, 1.01]:
    print(f"threshold {t}: profit {profit(t) / 1e6:.2f} million RWF")
```

- Approving **everyone** (threshold above 1) **loses** about 5.3 million RWF.
- The default threshold of 0.5 earns about 1.4 million.
- A threshold around **0.25** earns about **3.9 million** — almost three times more.

The best threshold came from the **costs**, not from accuracy. In a real project you choose it on validation data, then confirm it once on the test set.

## Key terms

- **Decision threshold** — the probability above which we predict the positive class.
- **ROC curve** — true positive rate against false positive rate for every threshold.
- **AUC** — area under the ROC curve; 0.5 = random, 1.0 = perfect.
- **Precision–recall curve** — precision against recall; better for rare positives.
- **Cost-based threshold** — the threshold that gives the best result in money or harm.

**Takeaway:** A model gives scores; people choose the threshold. ROC/AUC compares how well models rank cases, and real costs decide where to draw the line.

## Try it yourself

1. Plot the profit for thresholds from 0.05 to 0.95 in steps of 0.05. Where is the peak?
2. Change the costs: a 25% fee and a 50% loss. How does the best threshold move? Why?
3. Draw `PrecisionRecallDisplay.from_predictions(y_test, proba)` and describe its shape.
4. Write a short note to the lender's manager recommending a threshold, in plain words and RWF.
""",
            "quiz": [
                ("What happens to recall when you lower the threshold from 0.5 to 0.2?",
                 ["It goes down", "It goes up: more defaulters are caught", "It stays the same", "It becomes zero"],
                 1, "More cases are flagged, so more real positives are found."),
                ("What is on the y-axis of a ROC curve?",
                 ["Precision", "True positive rate (recall)", "Accuracy", "Threshold"],
                 1, "ROC plots TPR against FPR."),
                ("What does an AUC of 0.5 mean?",
                 ["A perfect model", "No better than random guessing", "50% accuracy is excellent", "The model is overfitting"],
                 1, "The diagonal has area 0.5."),
                ("Our model has AUC 0.86. What is a correct reading?",
                 ["86% accuracy", "An 86% chance it ranks a random defaulter above a random good borrower", "86 defaulters caught", "Threshold 0.86"],
                 1, "AUC measures ranking quality."),
                ("Why did a threshold of about 0.25 earn more than 0.5?",
                 ["Defaults cost much more than one fee earns, so refusing riskier borrowers pays", "Lower thresholds always win", "It increases accuracy", "Because AUC changed"],
                 0, "Costs, not accuracy, decide the best threshold."),
                ("Which curve is more informative when positives are very rare?",
                 ["Precision–recall curve", "Histogram", "Learning curve", "Pie chart"],
                 0, "It focuses on the rare positive class."),
            ],
        },
        # ------------------------------------------------------------------ 16
        {
            "title": "Bias, Variance and Regularisation",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=EuBBz3bI-aA",
            "content": r"""
**Learning objective:** Recognise underfitting and overfitting from train and test errors, explain the bias–variance trade-off, and use Ridge and Lasso regularisation to tame complex models.

## Two ways to be wrong

- **Bias** — the model is too **simple** to capture the pattern. It is wrong on training **and** test data. (**Underfitting.**)
- **Variance** — the model is too **flexible** and learns the noise. It is excellent on training data and poor on new data. (**Overfitting.**)

The best model sits in between: complex enough to learn the real pattern, simple enough to ignore the noise. This is the **bias–variance trade-off**.

## See it with curves

Twenty noisy points follow a wave. We fit polynomials of degree 1 (a straight line), 3 and 15:

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error

rng = np.random.default_rng(2)
x = rng.uniform(0, 1, 20)
y = np.sin(2 * np.pi * x) + rng.normal(0, 0.3, 20)
x_new = rng.uniform(0, 1, 200)                       # new data from the same wave
y_new = np.sin(2 * np.pi * x_new) + rng.normal(0, 0.3, 200)

grid = np.linspace(0, 1, 300).reshape(-1, 1)
for degree in [1, 3, 15]:
    m = make_pipeline(PolynomialFeatures(degree), LinearRegression()).fit(x.reshape(-1, 1), y)
    train_mse = mean_squared_error(y, m.predict(x.reshape(-1, 1)))
    new_mse = mean_squared_error(y_new, m.predict(x_new.reshape(-1, 1)))
    print(f"degree {degree:2d}: train MSE {train_mse:.3f}, new-data MSE {new_mse:.3f}")
    plt.plot(grid, m.predict(grid), label=f"degree {degree}")
plt.scatter(x, y, color="black")
plt.ylim(-2, 2)
plt.legend()
plt.show()
```

| Degree | Train error | New-data error | Diagnosis |
|---|---|---|---|
| 1 | high (about 0.28) | high (about 0.30) | Underfitting — high bias |
| 3 | low (about 0.08) | low (about 0.11) | Good balance |
| 15 | lowest (about 0.06) | very high (about 1.8) | Overfitting — high variance |

The degree-15 curve wiggles through almost every training point and goes wild between them.

## How to diagnose your own model

| You see | Problem | Try |
|---|---|---|
| Train error high, test error high | Underfitting | A more flexible model, better features |
| Train error low, test error much higher | Overfitting | More data, a simpler model, **regularisation** |
| Both low and close | Good fit | Ship it (after the final test) |

## Regularisation: a penalty for complexity

**Regularisation** adds a penalty for big coefficients, so the model prefers simple explanations.

- **Ridge (L2)** — penalty = alpha × (sum of squared coefficients). Shrinks all coefficients towards zero.
- **Lasso (L1)** — penalty = alpha × (sum of absolute coefficients). Can push some coefficients **exactly to zero**, removing useless features.

**alpha** sets the strength: 0 means plain linear regression; larger values mean simpler models. Features must be **scaled** first, so the penalty treats them fairly.

```python
ridge15 = make_pipeline(PolynomialFeatures(15), StandardScaler(), Ridge(alpha=0.1))
ridge15.fit(x.reshape(-1, 1), y)
print("Ridge degree 15, new-data MSE:",
      round(mean_squared_error(y_new, ridge15.predict(x_new.reshape(-1, 1))), 3))
```

The same degree-15 model, with a Ridge penalty, drops from about **1.8** to about **0.11** — as good as the degree-3 model.

## Regularisation on the homes data

Now a realistic danger: only **40** homes to learn from, and 20 extra columns of pure random noise (in real projects, many columns turn out to be useless).

{HOMES}

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_error

X = pd.get_dummies(homes.drop(columns="rent_rwf"), columns=["district"], dtype=int)
X["furnished"] = X["furnished"].astype(int)
noise = np.random.default_rng(1).normal(size=(len(X), 20))
X = pd.concat([X, pd.DataFrame(noise, columns=[f"noise_{i}" for i in range(20)])], axis=1)
y = homes["rent_rwf"]

X_small, X_rest, y_small, y_rest = train_test_split(X, y, train_size=40, random_state=42)
for name, reg in [("Linear", LinearRegression()), ("Ridge", Ridge(alpha=10)),
                  ("Lasso", Lasso(alpha=4000, max_iter=10_000))]:
    m = make_pipeline(StandardScaler(), reg).fit(X_small, y_small)
    print(f"{name:6s} train MAE {mean_absolute_error(y_small, m.predict(X_small)):8.0f}"
          f"   test MAE {mean_absolute_error(y_rest, m.predict(X_rest)):8.0f}")
```

- Plain linear regression: train MAE about **10,000**, test MAE about **48,500** — badly overfitted.
- Ridge: test MAE about **33,000**.
- Lasso: test MAE about **27,000** — and it switched off most of the noise columns completely (only about 6 of the 20 keep a non-zero coefficient). It also dropped `bedrooms`, which size already explains:

```python
lasso = make_pipeline(StandardScaler(), Lasso(alpha=4000, max_iter=10_000)).fit(X_small, y_small)
coefs = pd.Series(lasso[-1].coef_, index=X.columns)
print("Noise columns kept:", int((coefs.filter(like="noise") != 0).sum()), "of 20")
```

## Regularisation is everywhere

- `LogisticRegression` is regularised by default; **C** is the inverse strength (small C = strong penalty).
- Trees are regularised by `max_depth` and `min_samples_leaf`; boosting by the learning rate; neural networks by dropout and weight decay.

## Key terms

- **Bias** — error from a model that is too simple (underfitting).
- **Variance** — error from a model that is too sensitive to the training data (overfitting).
- **Regularisation** — a penalty that discourages complexity.
- **Ridge (L2)** — shrinks all coefficients.
- **Lasso (L1)** — shrinks and can set coefficients to zero (feature selection).
- **alpha / C** — the strength of the penalty (C is the inverse).

**Takeaway:** Compare train and test errors to tell bias from variance; regularisation trades a little training accuracy for much better results on new data.

## Try it yourself

1. Repeat the curve experiment with degrees 2, 5 and 9. Which degree gives the lowest new-data error?
2. Try Ridge alphas 0.001, 0.1, 1 and 10 on the degree-15 model. What happens when alpha is too big?
3. On the 40-home experiment, try Lasso alphas 1000, 4000 and 15000. Which features survive at 15000, and what happens to the test MAE?
4. Train the 40-home models again with all 480 remaining homes as training data. Does regularisation still matter as much? Why?
""",
            "quiz": [
                ("A model has high error on both training and test data. What is the problem?",
                 ["Overfitting", "Underfitting (high bias)", "Data leakage", "Too much data"],
                 1, "Too simple to capture the pattern."),
                ("A model has train MAE 10,000 and test MAE 48,500. What is the problem?",
                 ["Underfitting", "Overfitting (high variance)", "Perfect fit", "Wrong units"],
                 1, "A big gap between train and test means overfitting."),
                ("What does Lasso do that Ridge does not?",
                 ["Uses no penalty", "Can set some coefficients exactly to zero", "Needs no scaling", "Only works for trees"],
                 1, "L1 can remove features completely."),
                ("What happens as alpha in Ridge gets very large?",
                 ["The model becomes more complex", "Coefficients shrink towards zero and the model can underfit", "Nothing", "Training stops"],
                 1, "Too strong a penalty makes the model too simple."),
                ("Why must features be scaled before Ridge or Lasso?",
                 ["So the penalty treats every feature fairly", "To make training slower", "Because Lasso needs text", "It is not needed"],
                 0, "Unscaled features would be penalised unequally."),
                ("In LogisticRegression, what does a small C mean?",
                 ["Weak regularisation", "Strong regularisation", "No model", "A high threshold"],
                 1, "C is the inverse of the penalty strength."),
            ],
        },
        # ------------------------------------------------------------------ 17
        {
            "title": "Hyperparameter Tuning with Grid Search",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=Gol_qOgRqfA",
            "content": r"""
**Learning objective:** Tell parameters from hyperparameters, tune a model with GridSearchCV and RandomizedSearchCV, and avoid tuning on the test set.

## Parameters vs hyperparameters

- **Parameters** are learned from data during `fit`: the coefficients of a regression, the questions in a tree.
- **Hyperparameters** are settings **you** choose before training: k in k-NN, `max_depth` of a tree, C in an SVM, the learning rate in boosting.

Choosing hyperparameters by hand is slow and easy to get wrong. **Grid search** tries every combination with cross-validation and keeps the best.

{LOANS}

{SPLIT}

## GridSearchCV

```python
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

pipe = make_pipeline(StandardScaler(), KNeighborsClassifier())
grid = {
    "kneighborsclassifier__n_neighbors": [5, 15, 25, 35, 51],
    "kneighborsclassifier__weights": ["uniform", "distance"],
}
search = GridSearchCV(pipe, grid, cv=5, scoring="roc_auc")
search.fit(X_train, y_train)
print(search.best_params_)
print("Best cross-validated AUC:", round(search.best_score_, 3))
```

- The grid has 5 × 2 = **10 combinations**; with 5 folds that is **50 trainings**.
- Inside a pipeline, a setting is named **step name + two underscores + setting** (`kneighborsclassifier__n_neighbors`).
- `scoring="roc_auc"` tells the search what "best" means. Choose the measure that matches your goal (accuracy, recall, f1, roc_auc, neg_mean_absolute_error…).

The best k-NN uses about **51 neighbours** weighted by distance, with a cross-validated AUC of about **0.86**.

## Tune a random forest

```python
from sklearn.ensemble import RandomForestClassifier

rf_grid = {
    "max_depth": [3, 6, None],
    "min_samples_leaf": [1, 5, 20],
    "max_features": ["sqrt", None],
}
rf_search = GridSearchCV(RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
                         rf_grid, cv=5, scoring="roc_auc", n_jobs=-1)
rf_search.fit(X_train, y_train)
print(rf_search.best_params_, round(rf_search.best_score_, 3))

results = pd.DataFrame(rf_search.cv_results_)
print(results[["params", "mean_test_score", "rank_test_score"]]
      .sort_values("rank_test_score").head(5))
```

18 combinations × 5 folds = 90 forests. The winner limits depth to 6 with at least 5 borrowers per leaf (AUC about **0.87**) — a regularised forest. Looking at the top five shows how **flat** the top is: several settings are almost equally good.

## Random search: faster for big grids

Grids explode: 5 settings with 5 values each = 3,125 combinations. **RandomizedSearchCV** tries a fixed number of random combinations instead — usually almost as good, much faster.

```python
from scipy.stats import randint
from sklearn.model_selection import RandomizedSearchCV

rand = RandomizedSearchCV(
    RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
    {"max_depth": randint(2, 15), "min_samples_leaf": randint(1, 40)},
    n_iter=15, cv=5, scoring="roc_auc", random_state=42, n_jobs=-1)
rand.fit(X_train, y_train)
print(rand.best_params_, round(rand.best_score_, 3))
```

## Finally — and only once — the test set

```python
from sklearn.metrics import roc_auc_score

best = rf_search.best_estimator_          # already re-trained on all training data
print("Test AUC:", round(roc_auc_score(y_test, best.predict_proba(X_test)[:, 1]), 3))
```

The test AUC (about **0.85**) is a little below the cross-validated 0.87. That is normal: picking the best of many settings is slightly optimistic. If you went back and tuned again after seeing the test score, the test set would no longer be honest.

## Good habits

- Start with a **coarse** grid (0.01, 0.1, 1, 10, 100), then zoom in around the best value.
- Tune the settings that matter most (k for k-NN; depth and leaf size for trees; learning rate and number of trees for boosting; C for SVM and logistic regression).
- Put **all** preparation inside a pipeline so it is redone in every fold.
- Remember the gains are often small — better **data and features** usually beat better tuning.

## Key terms

- **Hyperparameter** — a setting chosen before training.
- **Grid search** — try every combination with cross-validation.
- **Random search** — try a set number of random combinations.
- **best_params_ / best_score_ / best_estimator_** — the winning settings, their CV score and the re-trained model.
- **Scoring** — the measure the search optimises.

**Takeaway:** Let GridSearchCV or RandomizedSearchCV choose hyperparameters by cross-validation, then report the winner's score on the untouched test set exactly once.

## Try it yourself

1. Tune `LogisticRegression` C over [0.01, 0.1, 1, 10, 100] inside a pipeline. Does tuning help much?
2. Tune `GradientBoostingClassifier` over `learning_rate` [0.05, 0.1] and `n_estimators` [100, 300] with `max_depth=2`.
3. Change `scoring` to `"recall"` for the forest search. Do the best settings change? Why?
4. Explain to a teammate the difference between a parameter and a hyperparameter, with one example of each.
""",
            "quiz": [
                ("Which of these is a hyperparameter?",
                 ["A regression coefficient", "max_depth of a decision tree", "The questions inside a trained tree", "The predicted probability"],
                 1, "You choose it before training."),
                ("A grid has 3 × 3 × 2 combinations and cv=5. How many models are trained during the search?",
                 ["18", "45", "90", "5"],
                 2, "18 combinations × 5 folds = 90."),
                ("How do you name k-NN's n_neighbors inside make_pipeline for a grid?",
                 ["n_neighbors", "kneighborsclassifier__n_neighbors", "knn.n_neighbors", "pipeline_k"],
                 1, "Step name, two underscores, setting name."),
                ("When is RandomizedSearchCV better than GridSearchCV?",
                 ["When the grid would be very large", "Never", "Only for regression", "When there is no data"],
                 0, "Random combinations save a lot of time on big grids."),
                ("Why is the final test score often a little below the best CV score?",
                 ["Choosing the best of many settings is slightly optimistic", "The test set is wrong", "CV leaks data", "Random forests are unstable"],
                 0, "Selecting the maximum of noisy scores adds optimism."),
                ("What should you NOT do after seeing the final test score?",
                 ["Write the report", "Go back and tune again using the test set", "Save the model", "Explain the results"],
                 1, "That would turn the test set into a validation set."),
            ],
        },
        # ------------------------------------------------------------------ 18
        {
            "title": "Week 3 Project: Build a Trustworthy Loan Model",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=85dtiMz9tSo",
            "content": r"""
**Learning objective:** Deliver a complete, honest classification project: compare and tune models with cross-validation, choose a threshold from business costs, and report results from a single final test.

## The brief

A Rwandan savings and credit cooperative (SACCO) wants to approve mobile micro-loans automatically. The board asks three questions:

1. Which model should we use, and how good is it really?
2. At what risk level should we refuse a loan?
3. What are the risks of using this model?

{LOANS}

## Step 1 — Lock the test set away

```python
from sklearn.model_selection import train_test_split

X = loans.drop(columns="defaulted")
y = loans["defaulted"]
X_dev, X_test, y_dev, y_test = train_test_split(
    X, y, test_size=0.25, random_state=7, stratify=y)
print(len(X_dev), "rows to develop with,", len(X_test), "rows locked away")
```

Everything until Step 5 uses **X_dev** only.

## Step 2 — Compare candidates with cross-validation

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

cv = StratifiedKFold(5, shuffle=True, random_state=7)
candidates = {
    "Baseline": DummyClassifier(strategy="prior"),
    "Logistic regression": make_pipeline(StandardScaler(), LogisticRegression()),
    "Random forest": RandomForestClassifier(300, min_samples_leaf=5, random_state=7, n_jobs=-1),
    "Gradient boosting": GradientBoostingClassifier(learning_rate=0.05, n_estimators=200,
                                                    max_depth=2, random_state=7),
}
for name, m in candidates.items():
    s = cross_val_score(m, X_dev, y_dev, cv=cv, scoring="roc_auc")
    print(f"{name:20s} AUC {s.mean():.3f} +/- {s.std():.3f}")
```

The baseline has an AUC of **0.5** (it gives everyone the same score). The three real models should all be around **0.85–0.87**.

## Step 3 — Tune the leader

Tune the strongest simple model (or your favourite) with `GridSearchCV`:

```python
from sklearn.model_selection import GridSearchCV

search = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression()),
                      {"logisticregression__C": [0.01, 0.1, 1, 10, 100]},
                      cv=cv, scoring="roc_auc")
search.fit(X_dev, y_dev)
print(search.best_params_, round(search.best_score_, 3))
model = search.best_estimator_
```

## Step 4 — Choose the threshold on development data

Use cross-validated probabilities, so each development row is scored by a model that did not train on it:

```python
import numpy as np
from sklearn.model_selection import cross_val_predict

dev_proba = cross_val_predict(model, X_dev, y_dev, cv=cv, method="predict_proba")[:, 1]
amount, actual = X_dev["loan_rwf"].to_numpy(), y_dev.to_numpy()

def profit(proba, amount, actual, t, fee=0.15, loss=0.60):
    ok = proba < t
    return fee * amount[ok & (actual == 0)].sum() - loss * amount[ok & (actual == 1)].sum()

thresholds = np.arange(0.05, 0.96, 0.05)
profits = [profit(dev_proba, amount, actual, t) for t in thresholds]
best_t = round(float(thresholds[int(np.argmax(profits))]), 2)
print("Best threshold on development data:", best_t)
```

## Step 5 — Open the test set once

```python
from sklearn.metrics import roc_auc_score, precision_score, recall_score

test_proba = model.predict_proba(X_test)[:, 1]
refuse = (test_proba >= best_t).astype(int)
print("Test AUC:", round(roc_auc_score(y_test, test_proba), 3))
print("Recall (defaulters refused):", round(recall_score(y_test, refuse), 3))
print("Precision (refused who would default):", round(precision_score(y_test, refuse), 3))
print("Approved:", int((refuse == 0).sum()), "of", len(refuse))
print("Profit: %.2f million RWF" % (profit(test_proba, X_test["loan_rwf"].to_numpy(),
                                           y_test.to_numpy(), best_t) / 1e6))
print("Profit if everyone is approved: %.2f million RWF" % (profit(test_proba, X_test["loan_rwf"].to_numpy(),
                                                                   y_test.to_numpy(), 1.01) / 1e6))
```

## Step 6 — Board report (one page)

1. **Recommendation** — the model, the threshold, and the expected profit compared with approving everyone.
2. **How good** — cross-validated AUC with its ± spread, and the single test AUC.
3. **What it means for customers** — how many good borrowers are refused per 100 applicants.
4. **What drives risk** — the logistic coefficients, in plain words.
5. **Risks and safeguards** — data drift (incomes change), fairness (check results by group, Week 4), a human appeal process for refused customers, and retraining every few months.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Honesty | Test set opened once, after all choices |
| Method | Cross-validation and tuning inside pipelines |
| Business sense | Threshold chosen from costs on development data |
| Customers | Effect on good borrowers stated clearly |
| Responsibility | Drift, fairness and appeals discussed |

**Takeaway:** A trustworthy model comes from an honest process: develop with cross-validation, decide the threshold from real costs, and open the test set only once.

## Try it yourself

Complete Steps 1–6. Then repeat Step 4 with a 25% fee and a 50% loss and explain to the board how the recommended threshold would change.
""",
            "quiz": [
                ("Why is the test set split off before anything else?",
                 ["So no choice is influenced by it and the final score stays honest", "To train faster", "Because it is bigger", "To scale it"],
                 0, "Every decision must be made without seeing the test set."),
                ("What AUC does the DummyClassifier baseline get?",
                 ["0.5", "0.79", "1.0", "0.0"],
                 0, "Giving everyone the same score is like random ranking."),
                ("Why use cross_val_predict to choose the threshold?",
                 ["Each development row gets a probability from a model that did not train on it", "It is faster", "It changes the labels", "It removes the test set"],
                 0, "Out-of-fold probabilities are honest."),
                ("How was the threshold chosen?",
                 ["Always 0.5", "The value that maximised profit on development data", "The value that maximised test accuracy", "At random"],
                 1, "Costs decide; the test set only confirms."),
                ("Which safeguard belongs in the board report?",
                 ["Never retrain the model", "A human appeal process and regular retraining", "Hide the model from staff", "Remove the threshold"],
                 1, "People affected need recourse, and models drift."),
                ("Why report the effect on good borrowers?",
                 ["Refusing good customers has a real cost to them and to the SACCO", "It is not important", "Because accuracy is 100%", "To increase AUC"],
                 0, "Decisions affect people, not just numbers."),
            ],
        },
    ],
}

for _lesson in WEEK3["lessons"]:
    _lesson["content"] = _lesson["content"].replace("{SPLIT}", SPLIT).replace("{MODEL}", MODEL)
fill_data(WEEK3)
