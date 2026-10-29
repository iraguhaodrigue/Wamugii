"""
WAMUGII AI Program — Course 3: "Machine Learning Fundamentals".
University-level, original WAMUGII content in simple English.
Run:  python -m app.seed_ai_c3_ml_fundamentals
"""

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.models.course import CourseStatus
from app.schemas.course import CourseCreate, LessonCreate

COURSE_SLUG = "machine-learning-fundamentals"

COURSE = CourseCreate(
    title="Machine Learning Fundamentals",
    slug=COURSE_SLUG,
    category="Artificial Intelligence",
    is_free=True,
    status=CourseStatus.PUBLISHED,
    display_order=4,
    description=(
        "Course 3 of the WAMUGII AI Program. Build and evaluate real machine "
        "learning models using Python and scikit-learn. You will learn the core "
        "algorithms — linear and logistic regression, decision trees and random "
        "forests, k-nearest neighbours and k-means clustering — plus feature "
        "preparation, honest model evaluation, and how to avoid overfitting. "
        "Simple English, runnable code, and exercises throughout. By the end you "
        "can take prepared data and build a model you can actually trust."
    ),
)

LESSONS = [
    {
        "title": "3.1 The ML Mindset and scikit-learn",
        "content": """\
**Learning objective:** Understand how every scikit-learn model follows the same
simple pattern, so new algorithms become easy to learn.

## One pattern for every model

The biggest secret of practical ML: **almost every model in scikit-learn works
the same way.** Learn the pattern once and you can use dozens of algorithms.

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# 1. Split data into features (X) and label (y)
X = df[["attendance", "assignments", "study_hours"]]
y = df["passed"]

# 2. Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 3. Choose a model
model = DecisionTreeClassifier()

# 4. Train it (fit)
model.fit(X_train, y_train)

# 5. Predict
predictions = model.predict(X_test)

# 6. Score it
print(model.score(X_test, y_test))
```

Every model has `.fit()` (learn) and `.predict()` (use). To try a different
algorithm, you change **one line** — the model you choose.

## Features (X) and label (y)

- **X** — the inputs, a table of features (always a 2-D structure).
- **y** — the target you want to predict (one column).

## Train and test, always

Remember Course 1: we **always** test on data the model never trained on
(`train_test_split`). A score on training data is meaningless — the model could
just be memorising.

## Key terms

**scikit-learn**, **fit**, **predict**, **X / y**, **train_test_split**.

## Practice

Write the 6-step scikit-learn pattern (in pseudo-code or real code) for predicting
house price from `size`, `bedrooms`, `location`. Mark clearly which part is X and
which is y.
""",
    },
    {
        "title": "3.2 Linear Regression — Predicting Numbers",
        "content": """\
**Learning objective:** Understand and use linear regression to predict a
continuous number.

## The idea

Linear regression draws the **best straight line (or flat surface)** through your
data. It predicts a number by multiplying each feature by a **weight** and adding
them up — exactly the dot product from Course 2.

```
predicted_price = w1*size + w2*bedrooms + w3*age + b
```

The model **learns** the weights (`w1, w2, w3`) and the bias (`b`) by using
gradient descent to make its line fit the data as closely as possible.

## In code

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)
print(model.coef_)        # the learned weights
print(model.intercept_)   # the bias
predictions = model.predict(X_test)
```

## Reading the weights

The weights tell you the story: a weight of **+500** on `size_m2` means each extra
square metre adds about 500 to the predicted price. A **negative** weight means
that feature pushes the prediction down. This makes linear regression
**interpretable** — you can explain its decisions.

## When to use it

- The target is a **number** (price, temperature, demand).
- You want a simple, explainable baseline. **Always start simple** — a linear
  model is often a strong first attempt.

## Evaluating it

Use regression metrics from Course 1: **MAE** and **RMSE** (lower is better).

```python
from sklearn.metrics import mean_absolute_error
print(mean_absolute_error(y_test, predictions))
```

## Key terms

**Linear regression**, **Weight / coefficient**, **Bias / intercept**, **MAE**,
**Baseline model**.

## Practice

A linear model predicts monthly electricity cost from `[appliances, people,
house_size]` and learns weights `[300, 1500, 40]` with bias 2000. Predict the cost
for a house with 10 appliances, 4 people, 90 m². Then say which feature has the
biggest effect per unit.
""",
    },
    {
        "title": "3.3 Logistic Regression and Classification",
        "content": """\
**Learning objective:** Use logistic regression to predict categories, and
understand how a model outputs a probability.

## From numbers to categories

Linear regression predicts a number. **Classification** predicts a **category**
(spam/not, pass/fail, disease/healthy). **Logistic regression** is the classic
starting model for classification.

## How it works

It first computes a number like linear regression, then squashes it through an
**S-shaped (sigmoid) function** into a **probability between 0 and 1**.

- Output **0.9** → very likely the positive class.
- Output **0.2** → unlikely.
- We pick a **threshold** (usually 0.5): above it → class 1, below → class 0.

Despite the name "regression," it is a **classifier**.

## In code

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression()
model.fit(X_train, y_train)

model.predict(X_test)          # 0 or 1
model.predict_proba(X_test)    # the probabilities behind the decision
```

## Why probabilities are powerful

A probability lets you act with nuance. For fraud, you might **investigate**
anything above 0.3 rather than only above 0.5 — because missing fraud is costly.
You tune the threshold to match the real-world cost of mistakes (recall vs
precision, Course 1).

## Evaluating it

Use **precision, recall, F1** and the **confusion matrix** from Course 1 — not
just accuracy, especially on imbalanced data.

```python
from sklearn.metrics import classification_report
print(classification_report(y_test, model.predict(X_test)))
```

## Key terms

**Classification**, **Logistic regression**, **Sigmoid**, **Probability**,
**Threshold**, **predict_proba**.

## Practice

A model gives these spam probabilities: [0.9, 0.4, 0.6, 0.1]. With a 0.5
threshold, which are spam? If you *lowered* the threshold to 0.3 to catch more
spam, what would change — and what is the cost of doing that?
""",
    },
    {
        "title": "3.4 Decision Trees and Random Forests",
        "content": """\
**Learning objective:** Understand decision trees and why combining many of them
(a random forest) is one of the most useful tools in ML.

## Decision trees — asking questions

A **decision tree** predicts by asking a series of yes/no questions, like a
flowchart:

```
Is attendance >= 50%?
├── No  -> predict Fail
└── Yes -> Is assignments >= 5?
           ├── No  -> predict Fail
           └── Yes -> predict Pass
```

The model **learns which questions to ask**, and in what order, to separate the
classes best.

```python
from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier(max_depth=4)
model.fit(X_train, y_train)
```

**Strengths:** easy to understand, handles numbers and categories, needs little
data preparation.
**Weakness:** a single deep tree **overfits** — it memorises the training data.
That is why we limit depth (`max_depth`) and why we use forests.

## Random forests — wisdom of the crowd

A **random forest** trains **many different trees** on random slices of the data
and features, then has them **vote**. No single tree is perfect, but their
combined vote is far more accurate and stable. This is called **ensemble
learning**.

```python
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
```

Random forests are a reliable, strong default for many real problems — often the
best thing to try after a simple baseline.

## Feature importance

A trained forest can tell you **which features mattered most** — valuable insight
on its own:

```python
model.feature_importances_
```

## Key terms

**Decision tree**, **max_depth**, **Overfitting**, **Random forest**,
**Ensemble**, **Feature importance**.

## Practice

Explain in your own words why one very deep decision tree can score 100% on
training data but do badly on new data — and how a random forest reduces that
problem.
""",
    },
    {
        "title": "3.5 k-NN and k-Means Clustering",
        "content": """\
**Learning objective:** Use k-nearest neighbours for classification and k-means
for clustering — and tell supervised from unsupervised learning in practice.

## k-Nearest Neighbours (k-NN) — "who are your neighbours?"

k-NN is a **supervised** classifier with a simple idea: to classify a new point,
look at the **k closest examples** and take the **majority vote**.

- New student looks most like 5 past students → predict what most of them were.
- **k** is how many neighbours to check (e.g. 5). Small k is sensitive to noise;
  large k is smoother.

```python
from sklearn.neighbors import KNeighborsClassifier
model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)
```

Because it measures distance, k-NN needs features on a **similar scale** (see
Lesson 3.6).

## k-Means Clustering — finding groups without labels

k-means is **unsupervised**: there are **no labels**. It finds **k natural
groups** in the data by placing k centres and pulling similar points together.

- Segment customers into groups by behaviour.
- Group villages by farming pattern.
- You choose **k** (how many groups), then the algorithm finds them.

```python
from sklearn.cluster import KMeans
model = KMeans(n_clusters=3)
groups = model.fit_predict(X)   # a group number for each point
```

## The key difference

- **k-NN** uses neighbours to **predict a known label** → supervised.
- **k-means** groups data with **no labels at all** → unsupervised.

Both use "distance" and both have a "k", which is why beginners confuse them —
but their jobs are completely different.

## Key terms

**k-NN**, **k-means**, **Supervised vs unsupervised**, **Cluster**, **Centroid**,
**Distance / scale**.

## Practice

For each task, say whether you'd use k-NN or k-means, and why: (a) group 5,000
mobile-money users into spending segments with no labels; (b) decide if a new loan
applicant is "low risk" based on similar past applicants whose outcome is known.
""",
    },
    {
        "title": "3.6 Feature Engineering and Preparation",
        "content": """\
**Learning objective:** Prepare features so models can learn from them —
scaling, encoding categories, and creating useful new features.

## Models are only as good as their features

A famous saying: *"Better features beat better algorithms."* Preparing your
features well often helps more than switching models.

## Scaling numbers

Features on very different scales confuse distance-based models (k-NN, k-means)
and slow down others. **Scaling** puts them on a comparable range.

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)   # note: transform only
```

**Important:** fit the scaler on **training data only**, then apply it to test
data — fitting on all data is a form of data leakage (Course 1).

## Encoding categories

Models need numbers, not text. Turn categories into numbers with **one-hot
encoding**:

```
Location: [Kigali, Huye, Musanze]  ->  three 0/1 columns
```

```python
df = pd.get_dummies(df, columns=["location"])
```

## Creating new features

Often the best feature is one you build from others:

- From a date → "day of week", "is weekend".
- From `price` and `quantity` → `total`.
- From `height` and `weight` → BMI.

Good new features encode knowledge the model can't discover alone.

## Handling missing values

Fill numeric blanks with the **mean/median**, or categorical blanks with the most
common value — or drop rows if there are few. Always decide deliberately.

## Key terms

**Feature engineering**, **Scaling / StandardScaler**, **One-hot encoding**,
**get_dummies**, **Data leakage**.

## Practice

You have columns `age` (0–90), `salary` (0–5,000,000), and `city` (text). Say what
preparation each one needs before a k-NN model, and write the one rule that stops
scaling from causing data leakage.
""",
    },
    {
        "title": "3.7 Evaluating and Validating Models",
        "content": """\
**Learning objective:** Judge a model honestly using the right metric and
cross-validation, so your results hold up in the real world.

## A single test score can mislead

Your 20% test set gives one score — but if you were lucky or unlucky with that
split, the score could be off. **Cross-validation** gives a more trustworthy
picture.

## k-fold cross-validation

Split the data into **k parts (folds)**. Train on k−1 of them and test on the
one left out — then repeat so every fold gets a turn as the test set. Average the
scores.

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)
print(scores.mean(), scores.std())
```

A high mean **and** a low spread means the model is both good and stable.

## Choose the metric that matches the goal (Course 1)

- **Classification:** precision, recall, F1 — not just accuracy, especially with
  imbalance.
- **Regression:** MAE, RMSE.
- Always ask: *what does a mistake cost in this problem?* That decides the metric.

## Compare against a baseline

Always compare your model to a **dumb baseline** — e.g. "always predict the most
common class" or "always predict the average." If your model can't beat that, it
isn't learning anything useful.

## Don't touch the final test set until the end

Use training + validation (or cross-validation) to build and tune. Keep the real
**test set for one final, honest score.** Peeking at it while tuning quietly
inflates your results.

## Key terms

**Cross-validation**, **Fold**, **Baseline**, **Metric choice**, **Validation vs
test**.

## Practice

Your classifier gets 92% accuracy, but 90% of the data is the "No" class. Explain
why 92% might be unimpressive, name a better metric to check, and describe the
baseline you'd compare against.
""",
    },
    {
        "title": "3.8 Overfitting and How to Beat It",
        "content": """\
**Learning objective:** Recognise overfitting and apply the main techniques to
build models that generalise.

## The central problem of ML

Remember from Course 1:

- **Overfitting** — the model memorises training data (including noise). Great on
  training, poor on new data.
- **Underfitting** — the model is too simple to capture the pattern. Poor on both.

The whole craft is finding the balance: a model complex enough to learn the real
pattern, simple enough to ignore the noise.

## How to spot overfitting

Compare training score to test score:

- Training 99%, test 70% → **overfitting** (big gap).
- Training 65%, test 64% → **underfitting** (both low).
- Training 88%, test 85% → **healthy** (close and high).

## How to reduce overfitting

1. **More data** — the single best cure, when you can get it.
2. **Simpler model** — limit `max_depth` on trees; fewer features.
3. **Regularisation** — gently penalise large weights so the model stays simple
   (e.g. `Ridge`/`Lasso` for linear models, the `C` setting in logistic
   regression).
4. **Cross-validation** — to choose settings honestly (Lesson 3.7).
5. **Dropout / early stopping** — for neural networks (Course 4).

## How to reduce underfitting

- Use a **more powerful model**, add **better features**, or train longer.

## The goal: generalisation

A model is only useful if it works on data it has never seen. Everything in this
course — splitting, validation, regularisation — exists to protect
**generalisation**.

## Key terms

**Overfitting**, **Underfitting**, **Generalisation**, **Regularisation**,
**Early stopping**, **Train-test gap**.

## Practice

For each case, say overfitting, underfitting, or healthy, and one thing to try:
(a) train 97%, test 72%; (b) train 60%, test 59%; (c) train 90%, test 88%.
""",
    },
    {
        "title": "3.9 Project — Build and Evaluate a Model (Assessment)",
        "content": """\
**This is your Course 3 assessment.** You will build a complete, trustworthy
machine-learning model from prepared data — the core skill of this course.

## The task

Take a dataset (ideally the one you cleaned in Course 2, or a new one) and build a
model that predicts something useful. Produce your code and a short report.

## Required steps

1. **Define the problem** and its type (classification or regression) and say why
   it matters.
2. **Prepare the features**: handle missing values, **scale** numeric features,
   **one-hot encode** categories, and create at least **one new feature** you
   think will help (Lesson 3.6).
3. **Split** the data into train and test sets.
4. **Train at least two different models** (for example logistic regression *and*
   a random forest) so you can compare.
5. **Evaluate honestly**: use the **right metric** for the problem (precision/
   recall/F1 or MAE/RMSE), use **cross-validation**, and compare against a simple
   **baseline** (Lesson 3.7).
6. **Check for overfitting**: report both training and test scores and comment on
   the gap (Lesson 3.8).
7. **Choose a winner** and explain, in plain language, *why* you trust it and what
   its limitations are.

## What good work looks like

- Your preparation avoids **data leakage** (scaler fit on train only).
- You compare models **fairly** on the same data and metric.
- You pick a metric that **matches the real cost** of mistakes.
- You are honest about overfitting and about what the model **cannot** do.

## Submit

Keep your code and report together. Finishing this means you can build a model and,
more importantly, **know whether to trust it** — the difference between someone who
runs ML code and someone who does ML well. Next, Course 4 opens up neural networks
and deep learning.
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
