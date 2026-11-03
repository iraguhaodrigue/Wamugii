"""Machine Learning Fundamentals -- Week 4: Unsupervised Learning and Real Projects. Original WAMUGII content."""

from app.course_content.ml_data import fill_data

CUSTOMERS = r"""
```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(3)
def group(n, tx, amount, airtime):
    return np.column_stack([rng.normal(*tx, n), rng.normal(*amount, n), rng.normal(*airtime, n)])

data = np.vstack([group(250, (8, 3), (4000, 1500), (0.6, 0.1)),
                  group(150, (45, 10), (15000, 4000), (0.15, 0.08)),
                  group(100, (20, 6), (60000, 15000), (0.05, 0.04))])
customers = pd.DataFrame(data, columns=["tx_per_month", "avg_amount_rwf", "airtime_share"])
customers["tx_per_month"] = customers["tx_per_month"].clip(1).round()
customers["avg_amount_rwf"] = customers["avg_amount_rwf"].clip(500).round(-2)
customers["airtime_share"] = customers["airtime_share"].clip(0, 1).round(2)
customers = customers.sample(frac=1, random_state=1).reset_index(drop=True)   # shuffle
print(customers.shape)
customers.head()
```
""".strip()

WEEK4 = {
    "title": "Week 4 · Unsupervised Learning and Real Projects",
    "lessons": [
        # ------------------------------------------------------------------ 19
        {
            "title": "k-Means Clustering: Finding Customer Groups",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=4b5d3muPQmA",
            "content": r"""
**Learning objective:** Explain how k-means groups data without labels, choose the number of clusters with the elbow method and silhouette score, and describe each cluster in business terms.

## Learning without answers

Until now every example had a label (rent, default). In **unsupervised learning** there is no answer column. The model looks for **structure** by itself. The most common task is **clustering**: putting similar examples into groups.

A mobile-money company has 500 customers and wants to design different offers. Nobody has labelled the customers — the company wants the data to suggest the groups.

{CUSTOMERS}

The three features are transactions per month, average transaction amount and the share of transactions spent on airtime.

## How k-means works

1. Choose **k**, the number of clusters.
2. Place k **centroids** (centre points) at random.
3. **Assign** every customer to the nearest centroid.
4. **Move** each centroid to the average of its customers.
5. Repeat steps 3–4 until nothing changes.

Because the start is random, scikit-learn runs the whole thing several times (`n_init=10`) and keeps the best result. k-means uses **distances**, so scale first.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

X_scaled = StandardScaler().fit_transform(customers)
kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
customers["segment"] = kmeans.fit_predict(X_scaled)
print(customers["segment"].value_counts())
```

## Describe the clusters

A cluster number means nothing until you describe it:

```python
profile = customers.groupby("segment").mean().round(1)
print(profile)
```

You should find three clear groups:

| Segment (your numbers may differ) | Behaviour | A name for the business |
|---|---|---|
| About 250 customers | ~8 transactions a month, ~4,000 RWF each, mostly airtime | **Occasional airtime users** |
| About 150 customers | ~44 transactions, ~15,000 RWF each | **Busy everyday users** (small traders) |
| About 100 customers | ~20 transactions, ~60,000 RWF each, little airtime | **Big-ticket payers** (businesses, school fees) |

Cluster numbers (0, 1, 2) are arbitrary — they can change between runs. The **descriptions** are what matter. Naming the clusters is a human job.

## How many clusters? The elbow method

```python
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score

ks = range(2, 8)
inertias, silhouettes = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, km.labels_))

plt.plot(ks, inertias, marker="o")
plt.xlabel("k")
plt.ylabel("inertia (within-cluster spread)")
plt.title("Elbow method")
plt.show()
for k, s in zip(ks, silhouettes):
    print(k, round(s, 3))
```

- **Inertia** is the total squared distance from each point to its centroid. It always falls as k grows, so look for the **elbow** — where the drop suddenly slows. Here the elbow is clearly at **k = 3**.
- The **silhouette score** (−1 to 1) measures how well each point fits its own cluster compared with the next one. Higher is better. It peaks at **k = 3** (about **0.74**).

Always combine the numbers with **business sense**: 3 offers may be practical, 12 may not.

## See the clusters

```python
plt.scatter(customers["tx_per_month"], customers["avg_amount_rwf"],
            c=customers["segment"], s=12)
plt.xlabel("Transactions per month")
plt.ylabel("Average amount (RWF)")
plt.title("Customer segments")
plt.show()
```

## Limits of k-means

- You must choose k.
- It finds **round**, similar-sized groups; it struggles with long, curved or very unequal clusters.
- Outliers pull centroids away.
- **DBSCAN** (density-based) finds clusters of any shape and marks outliers; **hierarchical clustering** builds a tree of clusters. Both are in `sklearn.cluster`.

## Other unsupervised uses

- **Anomaly detection** — `IsolationForest` flags unusual transactions (possible fraud) without fraud labels.
- **Dimensionality reduction** — PCA, next lesson.

## Key terms

- **Unsupervised learning** — finding structure in data without labels.
- **Clustering** — grouping similar examples.
- **Centroid** — the centre of a cluster.
- **Inertia** — within-cluster squared distances.
- **Elbow method / silhouette score** — ways to choose k.

**Takeaway:** k-means groups similar customers around centroids; choose k with the elbow, the silhouette score and business sense, then describe each group in plain words.

## Try it yourself

1. Run k-means with k = 4. Which segment splits in two? Is the split useful for the business?
2. Run k-means on the **unscaled** data. Compare the segment sizes with the scaled result and explain the difference.
3. Use `IsolationForest(random_state=42)` on the scaled data and look at the 10 most unusual customers.
4. Write one marketing idea for each of the three segments.
""",
            "quiz": [
                ("What makes clustering unsupervised?",
                 ["It uses no data", "There are no labels; the model finds groups by itself", "It needs a test set", "It predicts rent"],
                 1, "No answer column is given."),
                ("In k-means, what happens after customers are assigned to the nearest centroid?",
                 ["The model stops", "Each centroid moves to the average of its customers", "Labels are added", "Features are deleted"],
                 1, "Assign and move are repeated until stable."),
                ("Why scale features before k-means?",
                 ["Distances would be dominated by the feature with the biggest numbers", "To add labels", "k-means requires text", "It is not needed"],
                 0, "Amounts in RWF would swamp a 0–1 share."),
                ("What does the elbow method look for?",
                 ["The k where inertia stops falling quickly", "The highest inertia", "k = 1", "The largest cluster"],
                 0, "After the elbow, more clusters add little."),
                ("A silhouette score close to 1 means…",
                 ["Points fit their own cluster well", "Clusters overlap badly", "There is one cluster", "The model failed"],
                 0, "Higher silhouette means clearer clusters."),
                ("Which method finds clusters of any shape and marks outliers?",
                 ["Linear regression", "DBSCAN", "Naive Bayes", "Ridge"],
                 1, "DBSCAN is density-based."),
            ],
        },
        # ------------------------------------------------------------------ 20
        {
            "title": "PCA: Seeing Many Features in Two",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=FgakZw6K1QQ",
            "content": r"""
**Learning objective:** Explain what principal component analysis does, read explained variance, plot high-dimensional data in 2-D, and use PCA inside a model pipeline.

## Too many features to look at

The wine dataset in scikit-learn has **13** chemical measurements for 178 wines from three grape varieties (cultivars). You cannot draw a 13-dimensional chart. **Principal component analysis (PCA)** finds new axes — **principal components** — that keep as much of the spread (variance) as possible in as few dimensions as possible.

- **PC1** is the direction in which the data varies most.
- **PC2** is the next most varied direction, at a right angle to PC1.
- And so on. Each component is a **weighted mix** of the original features.

It is like taking the best photo of a 3-D object: you choose the angle that shows the most detail.

## PCA on the wine data

PCA is driven by variance, so features must be **standardised** first — otherwise the feature with the biggest units (proline, in the hundreds) would dominate.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

wine = load_wine(as_frame=True)
X_wine = StandardScaler().fit_transform(wine.data)

pca = PCA().fit(X_wine)
print(pca.explained_variance_ratio_.round(3))
print(pca.explained_variance_ratio_.cumsum().round(3))
```

- PC1 explains about **36%** of the variance and PC2 about **19%**: together about **55%** with only two numbers per wine instead of 13.
- About 10 components are needed to keep 95% of the variance.

## Plot 13 features in 2-D

```python
pca2 = PCA(n_components=2)
coords = pca2.fit_transform(X_wine)
plt.scatter(coords[:, 0], coords[:, 1], c=wine.target, s=15)
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.title("178 wines, 13 measurements, shown in 2-D")
plt.show()
```

The three varieties form three clearly separated clouds — even though PCA **never saw the labels**. That shows the 13 measurements really contain the information needed to tell them apart.

## What does a component mean?

```python
loadings = pd.Series(pca2.components_[0], index=wine.data.columns).sort_values()
print(loadings.round(2))
```

PC1 has large positive weights for flavanoids and total phenols and negative weights for non-flavanoid phenols and malic acid — so PC1 is roughly a "phenol richness" axis. Components are mixtures, so their meaning is often fuzzy. That is the price of PCA.

## PCA before a model

PCA can make data smaller and remove noise before a model. Let's try it on the breast-cancer data (30 features):

```python
from sklearn.datasets import load_breast_cancer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

cancer = load_breast_cancer()
for n in [2, 5, 10]:
    pipe = make_pipeline(StandardScaler(), PCA(n_components=n), LogisticRegression(max_iter=1000))
    print(n, "components:", cross_val_score(pipe, cancer.data, cancer.target, cv=5).mean().round(3))
full = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
print("all 30 features:", cross_val_score(full, cancer.data, cancer.target, cv=5).mean().round(3))
```

With just **2** components the model already scores about **0.95**; with 10 it matches all 30 features (about **0.98**). You can also ask for a share of variance: `PCA(n_components=0.95)` keeps as many components as needed for 95%.

## When to use PCA

| Good for | Be careful |
|---|---|
| Visualising many features | Components are hard to explain |
| Compressing data, speeding up models | Throws away some information |
| Removing correlated, noisy features | Needs scaling first |
| Image and gene data with thousands of features | Tree models rarely need it |

For pictures of complex data, **t-SNE** and **UMAP** often show clusters more clearly, but they are only for visualisation.

## Key terms

- **Dimensionality reduction** — representing data with fewer features.
- **Principal component** — a new axis that captures as much variance as possible.
- **Explained variance ratio** — the share of the total variance kept by each component.
- **Loadings** — the weights of the original features in a component.

**Takeaway:** PCA rotates the data so the first few components keep most of the information; it is excellent for 2-D pictures and compression, at the cost of easy interpretation.

## Try it yourself

1. Plot the cumulative explained variance of the wine data (`plt.plot(...cumsum())`) and mark the 90% line.
2. Run PCA on the wine data **without** scaling. How much does PC1 explain now, and which feature dominates it? Why?
3. Use `PCA(n_components=0.95)` in the cancer pipeline. How many components does it keep (`pipe[1].n_components_`)?
4. Run PCA with 2 components on the customer data from Lesson 19 and colour the plot by k-means segment.
""",
            "quiz": [
                ("What does PCA do?",
                 ["Adds labels", "Finds new axes that keep the most variance in fewer dimensions", "Predicts rent", "Removes rows"],
                 1, "It is dimensionality reduction."),
                ("Why must features be standardised before PCA?",
                 ["Otherwise features with big units dominate the components", "To add noise", "PCA needs text", "It is not needed"],
                 0, "Variance depends on units."),
                ("PC1 explains 36% and PC2 19% of the variance. How much do they explain together?",
                 ["17%", "36%", "55%", "100%"],
                 2, "Explained variance adds up."),
                ("Did PCA use the wine labels to separate the varieties?",
                 ["Yes", "No — it is unsupervised; the separation comes from the measurements", "Only for PC2", "Only after scaling"],
                 1, "PCA never sees the target."),
                ("What is the main cost of using PCA?",
                 ["Components are mixtures that are hard to explain", "It needs labels", "It always lowers accuracy to 50%", "It only works on images"],
                 0, "Interpretability is lost."),
                ("What does PCA(n_components=0.95) do?",
                 ["Keeps 95 components", "Keeps as many components as needed to explain 95% of the variance", "Removes 95% of rows", "Sets a threshold of 0.95"],
                 1, "A fraction asks for a share of variance."),
            ],
        },
        # ------------------------------------------------------------------ 21
        {
            "title": "Feature Engineering and Pipelines",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=C0_bh_5C5ro",
            "content": r"""
**Learning objective:** Create better features from domain knowledge, and build a single scikit-learn Pipeline with a ColumnTransformer that imputes, encodes, scales and models — safely and repeatably.

## Better features beat fancier models

**Feature engineering** means creating new inputs that make the pattern easier to learn. It uses **domain knowledge** — what you know about the real world.

Any loan officer will tell you that the **size of a loan compared with income** matters more than either number alone. Let's check:

{LOANS}

```python
loans["loan_to_income"] = loans["loan_rwf"] / loans["income_rwf"]
bands = pd.cut(loans["loan_to_income"], [0, 0.5, 1, 1.5, 10])
print(loans.groupby(bands, observed=True)["defaulted"].agg(["mean", "count"]).round(3))
```

Borrowers asking for less than half their monthly income default about **4%** of the time; those asking for more than 1.5 times their income default about **68%** of the time. One new column tells a very clear story.

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

cv = StratifiedKFold(5, shuffle=True, random_state=42)
model = make_pipeline(StandardScaler(), LogisticRegression())
y = loans["defaulted"]
before = loans.drop(columns=["defaulted", "loan_to_income"])
after = loans.drop(columns=["defaulted"])
print("AUC before:", cross_val_score(model, before, y, cv=cv, scoring="roc_auc").mean().round(3))
print("AUC after: ", cross_val_score(model, after, y, cv=cv, scoring="roc_auc").mean().round(3))
```

AUC rises from about **0.866** to about **0.875** — a bigger gain than all the tuning in Lesson 17, from one sensible column.

## Common feature ideas

| Idea | Example |
|---|---|
| Ratios | loan ÷ income, price per m² |
| Dates | month, day of week, "is it a holiday?", days since last payment |
| Counts and totals | transactions in the last 30 days |
| Logs of skewed numbers | log(income) |
| Groups | district average rent (computed on training data only!) |
| Text | word counts, message length |

Every feature must be available **at prediction time**. "Number of reminders sent after the due date" would be leakage for predicting default at approval time.

## The problem pipelines solve

A real dataset mixes number and text columns, with missing values. Each needs different preparation, and every step must be learned from training data only — in every cross-validation fold. Doing this by hand is where most leakage bugs come from.

Let's make the homes data realistically messy:

{HOMES}

```python
rng = np.random.default_rng(5)
messy = homes.copy()
messy.loc[rng.choice(len(messy), 30, replace=False), "size_m2"] = np.nan
messy.loc[rng.choice(len(messy), 15, replace=False), "district"] = np.nan
print(messy.isna().sum())
```

## ColumnTransformer + Pipeline

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

numbers = ["bedrooms", "size_m2", "km_to_centre"]
categories = ["district"]

prepare = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numbers),
    ("cat", make_pipeline(SimpleImputer(strategy="most_frequent"),
                          OneHotEncoder(handle_unknown="ignore")), categories),
    ("flag", "passthrough", ["furnished"]),
])
pipe = Pipeline([("prepare", prepare), ("model", LinearRegression())])

X = messy.drop(columns="rent_rwf")
y = messy["rent_rwf"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipe.fit(X_train, y_train)
print("Test MAE:", round(mean_absolute_error(y_test, pipe.predict(X_test))))
print(pipe.named_steps["prepare"].get_feature_names_out())
```

Read it from the inside out:

- **Number columns**: fill gaps with the median, then standardise.
- **District**: fill gaps with the most common district, then one-hot encode (unknown districts become zeros).
- **furnished**: passed through unchanged.
- Then the model.

`fit` learns every step from the training data; `predict` applies the same steps to new data. The test MAE is about **22,000 RWF** — close to the clean-data result, despite the gaps.

## One object does everything

```python
new_homes = pd.DataFrame({
    "district": ["Gasabo", "Musanze"],        # Musanze never appeared in training
    "bedrooms": [2, 3],
    "size_m2": [80, np.nan],                   # missing size
    "km_to_centre": [3.0, 6.0],
    "furnished": [True, False],
})
print(pipe.predict(new_homes).round(-3))

scores = cross_val_score(pipe, X, y, cv=5, scoring="neg_mean_absolute_error")
print("Cross-validated MAE:", round(-scores.mean()))
```

Raw rows go in, predictions come out — missing values and unknown districts included. And `cross_val_score` re-fits the imputers, scaler and encoder inside every fold automatically: **no leakage, by design**. You can also put the pipeline straight into `GridSearchCV` and tune preparation choices (for example `prepare__num__simpleimputer__strategy`).

## Key terms

- **Feature engineering** — creating new, more useful inputs from existing data.
- **Domain knowledge** — understanding of the real-world problem.
- **Pipeline** — a chain of steps that is fitted and applied as one model.
- **ColumnTransformer** — applies different preparation to different columns.
- **SimpleImputer** — fills missing values (median, mean, most frequent).

**Takeaway:** Good features come from understanding the problem; a Pipeline with a ColumnTransformer turns all preparation and the model into one leak-proof object.

## Try it yourself

1. Add `log_income = np.log(income_rwf)` to the loans data. Does AUC improve further?
2. Swap `LinearRegression()` in the homes pipeline for `RandomForestRegressor(300, random_state=42)`. Which has the lower cross-validated MAE?
3. Add a `price_per_m2`-style feature to the homes data. Why would that be **leakage**?
4. Put the homes pipeline in `GridSearchCV` and compare median and mean imputation.
""",
            "quiz": [
                ("Why did loan_to_income help the model?",
                 ["It is a longer column", "It captures what really drives risk: the loan compared with income", "It removes missing values", "It scales the data"],
                 1, "Domain knowledge creates a stronger signal."),
                ("Which feature would be leakage when predicting default at approval time?",
                 ["Monthly income", "Number of reminders sent after the due date", "Loan amount", "Months as a customer"],
                 1, "It is only known after the outcome."),
                ("What does ColumnTransformer do?",
                 ["Trains several models", "Applies different preparation steps to different columns", "Deletes columns", "Draws charts"],
                 1, "Numbers and categories get their own steps."),
                ("What does SimpleImputer(strategy='median') do?",
                 ["Deletes rows with gaps", "Fills missing values with the column's median", "Scales the data", "Encodes text"],
                 1, "Imputation fills gaps."),
                ("Why is cross-validating a whole Pipeline leak-proof?",
                 ["All preparation is re-fitted on the training folds only", "It uses the test set", "It skips preparation", "Pipelines cannot leak by magic"],
                 0, "Every step is learned inside each fold."),
                ("A new home arrives with a missing size and a district never seen in training. What does the pipeline do?",
                 ["Crashes", "Imputes the size and encodes the district as zeros, then predicts", "Deletes the home", "Asks the user"],
                 1, "The imputer and handle_unknown='ignore' deal with both."),
            ],
        },
        # ------------------------------------------------------------------ 22
        {
            "title": "Imbalanced Data and Fairness",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=6M2d2n-QXCc",
            "content": r"""
**Learning objective:** Handle rare-event problems with the right metrics, class weights and thresholds, and check a model's results across groups of people for fairness.

## Part 1 — When the positive class is rare

Fraud, disease outbreaks and machine failures are **rare**. Suppose only about **2%** of mobile-money transactions are fraud. A "model" that says "never fraud" is **98% accurate** — and worthless. This is the **accuracy paradox**.

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X_f, y_f = make_classification(n_samples=20_000, n_features=8, n_informative=5,
                               weights=[0.98], class_sep=1.0, flip_y=0.005, random_state=42)
print("Fraud rate:", round(y_f.mean(), 4))
X_tr, X_te, y_tr, y_te = train_test_split(X_f, y_f, test_size=0.25, random_state=42, stratify=y_f)
print("Accuracy of 'never fraud':", round(1 - y_te.mean(), 3))
```

## Compare approaches with the right metrics

```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, average_precision_score

def report(name, model):
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    score = model.predict_proba(X_te)[:, 1]
    print(f"{name:28s} precision {precision_score(y_te, pred, zero_division=0):.2f}  "
          f"recall {recall_score(y_te, pred):.2f}  avg precision {average_precision_score(y_te, score):.2f}")

report("Logistic regression", LogisticRegression())
report("Logistic, balanced weights", LogisticRegression(class_weight="balanced"))
report("Random forest", RandomForestClassifier(300, random_state=42, n_jobs=-1))
report("Random forest, balanced", RandomForestClassifier(300, class_weight="balanced_subsample",
                                                        min_samples_leaf=5, random_state=42, n_jobs=-1))
```

What you should see:

- **Plain logistic regression** flags **no** fraud at all (recall 0) — it learned that "no" is almost always right.
- **class_weight="balanced"** makes each fraud case count about 45 times more in training. Recall jumps to about **0.75** — but precision is only about **0.07**: 13 false alarms for every real fraud.
- **The random forest** finds the fraud pattern much better (average precision about **0.79**), catching about half the fraud with almost no false alarms; balanced weights raise its recall to about **0.58**.

**Average precision** (the area under the precision–recall curve) is a good single number for rare events: it ignores the huge number of easy negatives.

## The tools for rare events

1. **Use the right metrics** — recall, precision, F1, average precision; never accuracy alone.
2. **Stratify** every split and cross-validation.
3. **Class weights** — `class_weight="balanced"` in most scikit-learn classifiers.
4. **Move the threshold** — choose it from costs (Lesson 15).
5. **Resampling** — undersample the majority class or oversample the minority (the `imbalanced-learn` library has SMOTE). Resample **only the training data**, never the test set.
6. **Get more positive examples** — often the best fix of all.

## Part 2 — Is the model fair?

A model can be accurate overall and still treat groups of people differently. Let's add a **region** to the loans data. In our simulation, rural borrowers tend to earn less (as in many countries) — but the model is **not** given the region.

{LOANS}

```python
rng = np.random.default_rng(21)
rural_chance = np.where(loans["income_rwf"] < 180_000, 0.6, 0.25)
loans["region"] = np.where(rng.random(len(loans)) < rural_chance, "rural", "urban")
print(loans.groupby("region")["defaulted"].agg(["count", "mean"]).round(3))
```

Train the usual model **without** the region, then audit it **by** region:

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X = loans.drop(columns=["defaulted", "region"])
y, group = loans["defaulted"], loans["region"]
X_train, X_test, y_train, y_test, g_train, g_test = train_test_split(
    X, y, group, test_size=0.25, random_state=42, stratify=y)

model = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_train, y_train)
refuse = (model.predict_proba(X_test)[:, 1] >= 0.25).astype(int)

audit = pd.DataFrame({"actual": y_test.to_numpy(), "refused": refuse, "region": g_test.to_numpy()})
def rates(df):
    good, bad = df[df["actual"] == 0], df[df["actual"] == 1]
    return pd.Series({"applicants": len(df),
                      "refusal rate": df["refused"].mean(),
                      "good borrowers refused": good["refused"].mean(),
                      "defaulters caught": bad["refused"].mean()})
print(audit.groupby("region")[["actual", "refused"]].apply(rates).round(2))
```

You should see that rural applicants are refused far more often (about **42%** vs **30%**), and that about **25%** of good rural borrowers are refused, compared with about **20%** of good urban borrowers.

## Why — and is it unfair?

- The model never saw the region, but **income acts as a proxy**: removing a sensitive column does not remove its effect.
- Part of the gap reflects a real difference in default rates. Part is a heavier burden on good rural borrowers.

There is no single definition of fairness, and some cannot all be met at once:

| Fairness idea | Asks | Here |
|---|---|---|
| **Demographic parity** | Are refusal rates similar across groups? | No: 42% vs 30% |
| **Equal opportunity** | Are good borrowers refused at similar rates? | Closer: 25% vs 20% |
| **Calibration** | Does a score of 0.3 mean the same risk in each group? | Check with real data |

Deciding which matters is an **ethical and legal** question for the organisation, not only a technical one. Rwanda's data protection law (Law No. 058/2021) and the National AI Policy both expect AI systems to be responsible and accountable.

## What you can do

- **Audit** every model by group before launch, and again regularly.
- Look for **proxies** and for missing or under-represented groups in the data.
- Adjust **thresholds** or retrain with better data if a group carries an unfair burden.
- Give people a **human appeal** and clear reasons for decisions.
- Document everything in a **model card** (next lesson).

## Key terms

- **Imbalanced data** — one class is much rarer than the other.
- **Accuracy paradox** — high accuracy from always predicting the majority class.
- **Class weights** — making errors on the rare class count more.
- **Average precision** — area under the precision–recall curve.
- **Proxy** — a feature that indirectly reveals a sensitive attribute.
- **Demographic parity / equal opportunity** — two different fairness checks.

**Takeaway:** For rare events, use recall, precision and average precision with class weights and cost-based thresholds; for people, audit results by group, because a model can be unfair even without sensitive columns.

## Try it yourself

1. For the plain fraud logistic regression, lower the threshold to 0.1. What happens to precision and recall?
2. Undersample the training data so there are 5 normal transactions for every fraud, retrain logistic regression and compare.
3. In the fairness audit, try thresholds 0.2 and 0.35. Does the gap between regions grow or shrink?
4. Write a half-page memo to a SACCO board explaining the regional differences and what you recommend.
""",
            "quiz": [
                ("Only 2% of transactions are fraud. What accuracy does 'never fraud' get?",
                 ["2%", "50%", "About 98%", "100%"],
                 2, "This is the accuracy paradox."),
                ("What does class_weight='balanced' do?",
                 ["Deletes rare examples", "Makes errors on the rare class count more in training", "Balances the test set", "Sets the threshold to 0.5"],
                 1, "Rare-class mistakes are weighted up."),
                ("Which metric is a good single number for rare-event problems?",
                 ["Accuracy", "Average precision (area under the precision–recall curve)", "Training error", "Number of rows"],
                 1, "It focuses on the rare positive class."),
                ("When resampling, which data should be resampled?",
                 ["Only the training data", "Only the test data", "Both", "Neither"],
                 0, "The test set must stay realistic."),
                ("The model never saw 'region' but treats regions differently. Why?",
                 ["A bug in scikit-learn", "Income acts as a proxy for region", "Random chance only", "The test set is too big"],
                 1, "Removing a column does not remove its influence."),
                ("Equal opportunity asks…",
                 ["Are refusal rates the same in every group?", "Are good borrowers (true negatives) treated similarly across groups?", "Is accuracy above 90%?", "Are groups the same size?"],
                 1, "It compares error rates for people who deserve approval."),
            ],
        },
        # ------------------------------------------------------------------ 23
        {
            "title": "Saving, Sharing and Monitoring Models",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=URdnFlZnlaE",
            "content": r"""
**Learning objective:** Save a trained pipeline with joblib, load it to make predictions, document it with a model card, and check new data for drift.

## A model is only useful when it is used

A notebook model helps nobody. To be useful it must be **saved**, **loaded** by an app (a website, a USSD service, a mobile app) and **watched** over time. This step is called **deployment**, and the wider practice is **MLOps**.

{LOANS}

## Train the final pipeline on all development data

```python
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

X = loans.drop(columns="defaulted")
y = loans["defaulted"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

pipe = make_pipeline(StandardScaler(), LogisticRegression(C=1.0))
pipe.fit(X_train, y_train)
test_auc = roc_auc_score(y_test, pipe.predict_proba(X_test)[:, 1])
print("Test AUC:", round(test_auc, 3))
```

Save the **whole pipeline**, not just the model — the scaler is part of the model. Saving only the model is a classic bug: the app then feeds it unscaled numbers.

## Save and load with joblib

```python
import joblib

joblib.dump(pipe, "loan_model_v1.joblib")

loaded = joblib.load("loan_model_v1.joblib")
same = (loaded.predict_proba(X_test) == pipe.predict_proba(X_test)).all()
print("Loaded model gives identical predictions:", same)
```

In Colab, download the file from the Files panel or save it to Google Drive.

Rules for model files:

- Load files only from sources you **trust** — a joblib/pickle file can run code when opened.
- Record the **scikit-learn version**: a model saved with one version may not load in a very different one.
- Use clear names with versions: `loan_model_v1.joblib`, `v2`…

## A prediction function for the app

```python
import pandas as pd

FEATURES = ["income_rwf", "loan_rwf", "months_customer", "late_payments", "salaried"]
THRESHOLD = 0.25

def decide(application: dict) -> dict:
    row = pd.DataFrame([application])[FEATURES]
    risk = float(loaded.predict_proba(row)[0, 1])
    return {"risk": round(risk, 3),
            "decision": "refer to officer" if risk >= THRESHOLD else "approve"}

print(decide({"income_rwf": 180_000, "loan_rwf": 90_000, "months_customer": 24,
              "late_payments": 0, "salaried": 1}))
print(decide({"income_rwf": 120_000, "loan_rwf": 250_000, "months_customer": 2,
              "late_payments": 3, "salaried": 0}))
```

Notice the decision for risky cases is **"refer to officer"**, not "refuse": a person reviews them. A web framework such as **FastAPI** (which powers the WAMUGII website) can wrap a function like this as an API.

## Write a model card

A **model card** is a short document that travels with the model:

```python
import json
import sklearn
from datetime import date

card = {
    "name": "Micro-loan default risk",
    "version": "v1",
    "date": str(date.today()),
    "sklearn_version": sklearn.__version__,
    "intended_use": "Rank mobile micro-loan applications by default risk; risky cases go to a loan officer.",
    "not_for": "Automatic refusal without human review; loans above 300,000 RWF.",
    "training_data": "2,000 simulated past borrowers (practice data).",
    "features": FEATURES,
    "threshold": THRESHOLD,
    "test_auc": round(test_auc, 3),
    "fairness_check": "Refusal rates audited by region (see Lesson 22).",
    "retrain": "Every 3 months, or when drift is detected.",
}
with open("loan_model_v1_card.json", "w") as f:
    json.dump(card, f, indent=2)
print(json.dumps(card, indent=2)[:400])
```

## Monitor for drift

The world changes: inflation raises incomes and loan sizes, a new competitor changes who applies. When new data looks different from the training data — **data drift** — the model's accuracy can quietly fall.

```python
new_month = X_test.copy()
new_month["loan_rwf"] = (new_month["loan_rwf"] * 1.4).round(-3)    # loans grew 40%

comparison = pd.DataFrame({"training mean": X_train.mean(), "this month": new_month.mean()})
comparison["change %"] = ((comparison["this month"] / comparison["training mean"] - 1) * 100).round(1)
print(comparison.round(0))

before = (loaded.predict_proba(X_test)[:, 1] >= THRESHOLD).mean()
after = (loaded.predict_proba(new_month)[:, 1] >= THRESHOLD).mean()
print("Share referred: test data", round(before, 3), "-> this month", round(after, 3))
```

Loan sizes jumped about 40%, and the share of applicants referred to an officer rises from about a third to about half. That is an alarm: investigate, collect new labelled outcomes, and **retrain**.

What to monitor every month:

1. Input features — averages, ranges, missing values.
2. Predictions — the share approved or referred.
3. Real outcomes once known — recall, precision, AUC.
4. Fairness by group.

## Key terms

- **Deployment** — putting a model into real use.
- **joblib** — a library to save and load Python objects such as pipelines.
- **Model card** — a short document describing a model's use, data, performance and limits.
- **Data drift** — new data that differs from the training data.
- **MLOps** — the practice of deploying, monitoring and maintaining models.

**Takeaway:** Save the whole pipeline with joblib, wrap it in a simple prediction function with human review, document it in a model card and watch for drift so you know when to retrain.

## Try it yourself

1. Save the homes pipeline from Lesson 21, load it, and predict the rent of three new homes.
2. Add `"limitations"` and `"contact"` fields to the model card.
3. Simulate a month where incomes rise 20% and loan sizes stay the same. Does the referral rate go up or down? Why?
4. Write a one-paragraph monitoring plan for the SACCO: what you check, how often, and what triggers retraining.
""",
            "quiz": [
                ("Why save the whole pipeline instead of only the model?",
                 ["Files are smaller", "The preparation steps (like the scaler) are part of the model and must be applied to new data", "Models cannot be saved", "It is faster to train"],
                 1, "Without the scaler, the app would feed wrong numbers."),
                ("Which library is commonly used to save scikit-learn pipelines?",
                 ["joblib", "matplotlib", "seaborn", "requests"],
                 0, "joblib.dump and joblib.load."),
                ("Why only load model files from trusted sources?",
                 ["They are large", "Loading a pickle/joblib file can run code", "They expire", "They contain passwords"],
                 1, "Untrusted files are a security risk."),
                ("What is a model card?",
                 ["A credit card for AI", "A short document describing a model's purpose, data, performance and limits", "The model file", "A chart"],
                 1, "It helps people use the model responsibly."),
                ("Loan sizes rise 40% after training. What is this called?",
                 ["Overfitting", "Data drift", "Regularisation", "Clustering"],
                 1, "New data no longer looks like the training data."),
                ("Why does the app say 'refer to officer' instead of 'refuse'?",
                 ["To keep a human in the loop for risky decisions", "Because the model cannot refuse", "To make it slower", "It is a bug"],
                 0, "High-stakes decisions should be reviewed by people."),
            ],
        },
        # ------------------------------------------------------------------ 24
        {
            "title": "Final Project: An End-to-End Model and Certificate",
            "minutes": 120,
            "video": "https://www.youtube.com/watch?v=nKW8Ndu7Mjw",
            "content": r"""
**Learning objective:** Combine everything in the course — preparation, several algorithms, cross-validation, tuning, honest testing, fairness, saving and documentation — in one professional project, and earn your certificate.

## Choose your track

- **Track A — Kigali rents (regression).** The full starter code is below.
- **Track B — Micro-loans (classification).** Use the loans data from Week 3, with the region audit from Lesson 22 and a cost-based threshold.
- **Track C — Your own data.** A public dataset you care about (for example from the National Institute of Statistics of Rwanda, Kaggle or your workplace — anonymised). Agree the target with a classmate or mentor first.

Whatever the track, follow the same seven parts and write one report.

## Track A starter

{HOMES}

### Part 1 — Make it realistic and explore

```python
rng = np.random.default_rng(5)
data = homes.copy()
data.loc[rng.choice(len(data), 30, replace=False), "size_m2"] = np.nan
data.loc[rng.choice(len(data), 15, replace=False), "district"] = np.nan
print(data.isna().sum())
print(data.groupby("district")["rent_rwf"].median())
```

Add at least two charts and three sentences of findings.

### Part 2 — Lock away the test set and build the pipeline

```python
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

X = data.drop(columns="rent_rwf")
y = data["rent_rwf"]
X_dev, X_test, y_dev, y_test = train_test_split(X, y, test_size=0.2, random_state=11)

prepare = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
     ["bedrooms", "size_m2", "km_to_centre"]),
    ("cat", make_pipeline(SimpleImputer(strategy="most_frequent"),
                          OneHotEncoder(handle_unknown="ignore")), ["district"]),
    ("flag", "passthrough", ["furnished"]),
])
```

### Part 3 — Compare models with cross-validation

```python
candidates = {
    "Baseline": DummyRegressor(),
    "Linear regression": LinearRegression(),
    "Ridge": Ridge(alpha=1.0),
    "Random forest": RandomForestRegressor(300, min_samples_leaf=3, random_state=11, n_jobs=-1),
    "Gradient boosting": GradientBoostingRegressor(random_state=11),
}
for name, model in candidates.items():
    pipe = Pipeline([("prepare", prepare), ("model", model)])
    mae = -cross_val_score(pipe, X_dev, y_dev, cv=5, scoring="neg_mean_absolute_error")
    print(f"{name:18s} MAE {mae.mean():8.0f} +/- {mae.std():6.0f}")
```

The linear models should lead (MAE around 22,000–23,000 RWF), the tree ensembles follow, and the baseline is far behind (about 85,000). Explain **why** linear models suit this data.

### Part 4 — Tune and test once

```python
pipe = Pipeline([("prepare", prepare), ("model", Ridge())])
search = GridSearchCV(pipe, {"model__alpha": [0.01, 0.1, 1, 10, 100],
                             "prepare__num__simpleimputer__strategy": ["median", "mean"]},
                      cv=5, scoring="neg_mean_absolute_error")
search.fit(X_dev, y_dev)
print(search.best_params_, "CV MAE:", round(-search.best_score_))

from sklearn.metrics import mean_absolute_error, r2_score
final = search.best_estimator_
pred = final.predict(X_test)
print("Test MAE:", round(mean_absolute_error(y_test, pred)), " Test R²:", round(r2_score(y_test, pred), 3))
```

### Part 5 — Check errors by group

```python
errors = pd.DataFrame({"district": X_test["district"].fillna("missing"),
                       "abs_error": (y_test - pred).abs()})
print(errors.groupby("district")["abs_error"].agg(["count", "mean"]).round(0))
```

Is the model much worse for any district? For homes with missing size? Say what you would do about it.

### Part 6 — Save and document

```python
import joblib, json, sklearn
joblib.dump(final, "rent_model_v1.joblib")
card = {"name": "Kigali rent estimate", "version": "v1",
        "sklearn_version": sklearn.__version__,
        "test_mae_rwf": round(mean_absolute_error(y_test, pred)),
        "intended_use": "Guide price shown to visitors of a property website",
        "limits": "Simulated practice data; no information on building quality, water or security"}
json.dump(card, open("rent_model_v1_card.json", "w"), indent=2)
print(json.load(open("rent_model_v1_card.json")))
```

### Part 7 — Report (two pages)

1. **Problem and data** — target, features, data problems found.
2. **Method** — pipeline steps, models compared, cross-validation, tuning.
3. **Results** — CV table, final test MAE and R², a predicted-vs-real chart.
4. **Errors and fairness** — results by group, and what you would change.
5. **Deployment plan** — saved file, model card, what you would monitor and when you would retrain.
6. **Limits and next steps.**

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Data | Problems found and handled inside a pipeline |
| Method | Several models compared with cross-validation, one tuned |
| Honesty | Test set used once; baseline reported |
| Responsibility | Errors checked by group; limits stated |
| Engineering | Pipeline saved, model card written, monitoring plan |
| Communication | Clear charts and plain-English conclusions |

## Getting your certificate

1. Complete **every lesson** in the course (the progress bar shows 100%).
2. The **final exam** then unlocks on the course page: 60 questions (single answer, multiple answers, true/false and fill in the blank), 90 minutes, 60% to pass, 3 attempts. The exam opens in full screen; leaving the exam screen is counted, and the third time ends the exam automatically.
3. Pass the exam and your **WAMUGII Certificate** appears on the course page, showing your exam score. Add it — and a link to your final project notebook — to your CV and LinkedIn.

## What you can do now

You can take a real table of data and turn it into a trustworthy model: prepare it in a pipeline, choose among linear models, k-NN, trees, forests, boosting, SVMs and Naive Bayes, evaluate with cross-validation, precision, recall and AUC, tune, find groups with clustering and PCA, check fairness, and deploy with a model card. Next in the WAMUGII AI Program: **deep learning**, where neural networks learn from images, sound and text.

**Takeaway:** Professional machine learning is a disciplined process — honest evaluation, clear communication and responsibility matter as much as the algorithm.

## Try it yourself

Complete Parts 1–7 for your chosen track in one notebook and share the notebook link with your instructor in the lesson Q&A below. Challenge: add one engineered feature and show, with cross-validation, whether it helps.
""",
            "quiz": [
                ("What is the correct order for an honest project?",
                 ["Test, tune, split", "Split off the test set, develop with cross-validation, test once", "Tune on the test set, then split", "Train on everything, then test on the training data"],
                 1, "The test set is locked away until the end."),
                ("Why are preparation steps inside the Pipeline in the final project?",
                 ["So they are learned from training folds only and saved with the model", "To make the code longer", "Because models need text", "To remove the target"],
                 0, "Pipelines prevent leakage and simplify deployment."),
                ("Why check the errors by district?",
                 ["To find groups the model serves badly", "To increase R²", "Because the baseline needs it", "It is not useful"],
                 0, "Overall scores can hide problems for groups."),
                ("Why might linear models win on the rent data?",
                 ["Rents were built from a mostly straight-line rule", "Trees cannot do regression", "Linear models always win", "The data has no numbers"],
                 0, "Model shape should match the data."),
                ("What does the final exam require to pass?",
                 ["50%", "60%", "80%", "100%"],
                 1, "The pass mark is 60%."),
                ("What should a model card include?",
                 ["Intended use, data, performance and limits", "Only the file name", "The test set", "Passwords"],
                 0, "It lets others use the model responsibly."),
            ],
        },
    ],
}

for _lesson in WEEK4["lessons"]:
    _lesson["content"] = _lesson["content"].replace("{CUSTOMERS}", CUSTOMERS)
fill_data(WEEK4)
