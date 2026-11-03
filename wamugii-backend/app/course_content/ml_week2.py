"""Machine Learning Fundamentals -- Week 2: Trees, Ensembles and More. Original WAMUGII content."""

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

WEEK2 = {
    "title": "Week 2 · Trees, Ensembles and More",
    "lessons": [
        # ------------------------------------------------------------------ 7
        {
            "title": "Decision Trees: Models You Can Read",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=_L39rN6gz7Y",
            "content": r"""
**Learning objective:** Explain how a decision tree chooses its questions, train and draw one in scikit-learn, and control its depth to stop overfitting.

## A model made of questions

A **decision tree** works like a loan officer with a checklist: "Is the income above 150,000 RWF? Is the loan bigger than 190,000 RWF?" Each question splits the borrowers into two groups, until the groups are pure enough to give an answer. Anyone can read a small tree — that is why trees are loved in banks, hospitals and government.

Run the data and the split:

{LOANS}

{SPLIT}

## Train and read a small tree

```python
from sklearn.tree import DecisionTreeClassifier, export_text

tree = DecisionTreeClassifier(max_depth=2, random_state=42)
tree.fit(X_train, y_train)
print(export_text(tree, feature_names=list(X.columns), show_weights=True))
print("Test accuracy:", tree.score(X_test, y_test))
```

Read the output from the top:

1. The first question is **income ≤ 148,500 RWF?** — the most useful single question.
2. For lower-income borrowers, the next question is **loan ≤ 191,500 RWF?** Of those with bigger loans, 122 of 154 defaulted, so that leaf predicts **1 (default)**.
3. For higher-income borrowers, the loan size is checked again; their leaves predict **0**.

`weights: [32, 122]` means 32 repaid and 122 defaulted in that leaf. With only four leaves, this tree already scores about **0.83** on the test set.

## Draw it

```python
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

plt.figure(figsize=(12, 5))
plot_tree(tree, feature_names=list(X.columns), class_names=["repaid", "default"],
          filled=True, rounded=True)
plt.show()
```

## How the tree chooses a question: Gini impurity

At each step the tree tries **every feature and every threshold** and picks the split that makes the groups **purest**. Purity is measured with **Gini impurity**:

> Gini = 1 − (share of class 0)² − (share of class 1)²

- A group with only one class has Gini **0** (perfectly pure).
- A 50/50 group has Gini **0.5** (as mixed as possible).
- Our whole training set (21% defaulters) has Gini = 1 − 0.79² − 0.21² ≈ **0.33**.

```python
def gini(n0, n1):
    p0, p1 = n0 / (n0 + n1), n1 / (n0 + n1)
    return round(1 - p0**2 - p1**2, 3)

print(gini(1183, 317))   # all training borrowers
print(gini(468, 22))     # high income, small loan: very pure
print(gini(32, 122))     # low income, big loan: mostly defaulters
```

The tree keeps the split that lowers the **weighted average** Gini the most. **Entropy** (`criterion="entropy"`) is another purity measure; results are usually similar.

## The danger: trees love to memorise

```python
for depth in [2, 4, 6, 10, None]:
    t = DecisionTreeClassifier(max_depth=depth, random_state=42).fit(X_train, y_train)
    print(depth, "train", round(t.score(X_train, y_train), 3),
          "test", round(t.score(X_test, y_test), 3), "leaves", t.get_n_leaves())
```

With no limit (`None`) the tree grows until every leaf is pure: **100%** training accuracy, about **0.76** on the test set, and more than 200 leaves. It has memorised the noise — classic **overfitting**. Shallow trees generalise much better here.

Ways to keep a tree in check (called **pruning**):

- `max_depth` — the maximum number of questions in a row.
- `min_samples_leaf` — each leaf must contain at least this many examples (for example 20).
- `max_leaf_nodes` — a limit on the number of leaves.

## Feature importance

```python
print(pd.Series(tree.feature_importances_, index=X.columns).round(2))
```

Importance shows how much each feature reduced impurity. The small tree uses only income and loan size, so every other feature gets 0. Careful: importance tells you what the **model** used, not what **causes** default.

## Trees for numbers

`DecisionTreeRegressor` predicts a number: each leaf gives the **average** value of its training examples. The rent of a home could be predicted by questions such as "size > 100 m²? furnished?".

## Strengths and weaknesses

| Strengths | Weaknesses |
|---|---|
| Easy to read and explain | Overfit easily when deep |
| No scaling needed | Unstable: small data changes can change the whole tree |
| Handle numbers and categories, and curved patterns | A single tree is rarely the most accurate model |

The weaknesses are exactly what **random forests** fix in the next lesson.

## Key terms

- **Decision tree** — a model made of yes/no questions.
- **Node / leaf** — a question / a final answer.
- **Gini impurity** — how mixed a group is (0 = pure).
- **Pruning** — limiting a tree's growth to avoid overfitting.
- **Feature importance** — how much each feature helped the splits.

**Takeaway:** A decision tree asks the questions that make groups purest; it is easy to explain but must be kept shallow to avoid memorising noise.

## Try it yourself

1. Train a tree with `max_depth=3`. Write its rules as three plain-English sentences a loan officer could follow.
2. Try `min_samples_leaf=20` with no depth limit. Compare train and test accuracy with the unlimited tree.
3. Compute by hand the Gini of a leaf with 163 repaid and 48 defaulted. Check with the `gini` function.
4. Train a `DecisionTreeRegressor(max_depth=3)` on the homes data. Which feature does it ask about first?
""",
            "quiz": [
                ("What does each internal node of a decision tree do?",
                 ["Predicts a number", "Asks a yes/no question about a feature", "Scales the data", "Removes rows"],
                 1, "Nodes split data with questions; leaves give answers."),
                ("What is the Gini impurity of a group that contains only one class?",
                 ["0", "0.5", "1", "It depends on the size"],
                 0, "A pure group has Gini 0."),
                ("A tree with no depth limit gets 100% on training data and 76% on test data. What is happening?",
                 ["Underfitting", "Overfitting: it memorised the training data", "Perfect learning", "Data leakage"],
                 1, "A big gap between train and test scores is overfitting."),
                ("Which setting does NOT help limit a tree's growth?",
                 ["max_depth", "min_samples_leaf", "max_leaf_nodes", "random_state"],
                 3, "random_state only makes results repeatable."),
                ("Do decision trees need scaled features?",
                 ["Yes, always", "No, they only compare values against thresholds", "Only for regression", "Only with Gini"],
                 1, "Scaling does not change the order of values."),
                ("What does high feature importance tell you?",
                 ["The feature causes the outcome", "The model relied on that feature for its splits", "The feature has missing values", "The feature should be deleted"],
                 1, "Importance is about the model, not about cause."),
            ],
        },
        # ------------------------------------------------------------------ 8
        {
            "title": "Random Forests: The Wisdom of Many Trees",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=J4Wdy0Wc_xQ",
            "content": r"""
**Learning objective:** Explain bagging and random feature selection, train a random forest, and use out-of-bag scores and feature importance.

## One tree is shaky, many trees are steady

Ask one person to guess the number of beans in a jar and the guess may be far off. Ask 300 people and take the average: the answer is usually close. Errors of different people **cancel out**. A **random forest** uses the same idea: train many different trees and let them **vote**. A group of models working together is called an **ensemble**.

## Two sources of randomness

For the trees to make **different** mistakes, each one is trained differently:

1. **Bootstrap samples (bagging).** Each tree gets its own random sample of the training rows, drawn **with replacement** — some rows appear twice, about a third are left out.
2. **Random features.** At every split, a tree may only choose from a random subset of the features (by default √(number of features) for classification).

The prediction is the **majority vote** of all trees (or the **average** for regression).

{LOANS}

{SPLIT}

## Train a forest

```python
from sklearn.ensemble import RandomForestClassifier

forest = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
forest.fit(X_train, y_train)
print("Train:", round(forest.score(X_train, y_train), 3))
print("Test: ", round(forest.score(X_test, y_test), 3))
```

- `n_estimators` — the number of trees. More trees are never worse, just slower; 100–500 is typical.
- `n_jobs=-1` — use all the computer's processor cores.

Each tree is grown deep, so the forest scores almost **100%** on training data, but averaging makes it far more stable than one deep tree: about **0.83** on the test set instead of **0.76**.

## Make the trees less extreme

```python
forest5 = RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                 random_state=42, n_jobs=-1).fit(X_train, y_train)
print("Train:", round(forest5.score(X_train, y_train), 3),
      "Test:", round(forest5.score(X_test, y_test), 3))
```

Asking for at least 5 borrowers per leaf narrows the train–test gap and nudges the test score up to about **0.84**.

## A free test score: out-of-bag

Each tree never saw about a third of the rows (the ones left out of its bootstrap sample). The forest can test each row using only the trees that did **not** train on it. This **out-of-bag (OOB) score** is an honest estimate without touching the test set:

```python
oob = RandomForestClassifier(n_estimators=300, oob_score=True,
                             random_state=42, n_jobs=-1).fit(X_train, y_train)
print("OOB score:", round(oob.oob_score_, 3))
```

It comes out at about **0.85**, close to the test score.

## What did the forest use?

```python
imp = pd.Series(oob.feature_importances_, index=X.columns).sort_values()
print(imp.round(2))
imp.plot(kind="barh", title="Random forest feature importance")
```

Income and loan size are the most important, then months as a customer. Unlike the single small tree, the forest uses **every** feature a little.

Note: impurity-based importance can favour features with many different values. `sklearn.inspection.permutation_importance` — which shuffles one feature at a time and measures how much the score drops — is a more trustworthy check.

## Random forests for numbers

```python
from sklearn.ensemble import RandomForestRegressor
# RandomForestRegressor(n_estimators=300).fit(X_homes, y_rent) — the average of 300 trees
```

## When to use a random forest

| Good at | Less good at |
|---|---|
| Strong results with little tuning | Explaining a single decision simply |
| No scaling, handles curved patterns and interactions | Very large data (memory and speed) |
| Robust to noisy features | Predicting beyond the range of the training data |

Random forests are one of the best **first models** to try on any table of data.

## Key terms

- **Ensemble** — many models combined into one.
- **Bagging (bootstrap aggregating)** — train each model on a random sample drawn with replacement, then combine.
- **Random forest** — bagged decision trees that also pick features at random.
- **Out-of-bag score** — accuracy measured on rows each tree did not see.
- **Permutation importance** — score drop when a feature is shuffled.

**Takeaway:** A random forest averages many different deep trees, which keeps their power but cancels most of their overfitting.

## Try it yourself

1. Train forests with 10, 50, 100 and 500 trees. Plot the test accuracy. When does adding trees stop helping?
2. Set `max_features=None` (every split may use every feature). Does the forest get better or worse? Why?
3. Run `permutation_importance(oob, X_test, y_test, n_repeats=10, random_state=0)` and compare with the impurity importance.
4. Train a `RandomForestRegressor` on the homes data and compare its MAE with linear regression from Lesson 3.
""",
            "quiz": [
                ("What is an ensemble?",
                 ["One very deep tree", "Many models combined into one prediction", "A type of scaler", "A dataset"],
                 1, "Ensembles combine models so their errors cancel."),
                ("What is a bootstrap sample?",
                 ["The test set", "A random sample of rows drawn with replacement", "The first 100 rows", "The features only"],
                 1, "Some rows appear twice and about a third are left out."),
                ("Why does a random forest also choose features at random at each split?",
                 ["To save memory", "To make the trees different so their mistakes cancel", "To scale the data", "To remove the target"],
                 1, "Different trees make different errors."),
                ("How does a random forest classifier make its final prediction?",
                 ["It uses the first tree", "Majority vote of all trees", "It picks a random tree", "The deepest tree decides"],
                 1, "Classification uses a vote; regression uses the average."),
                ("What is the out-of-bag score?",
                 ["The training accuracy", "Accuracy on rows each tree did not train on", "The test accuracy", "The number of trees"],
                 1, "OOB gives an honest estimate without the test set."),
                ("What usually happens when you add more trees?",
                 ["The forest overfits much more", "Results stabilise; it is never worse, only slower", "Accuracy drops to zero", "Scaling becomes necessary"],
                 1, "More trees reduce variance until the gain levels off."),
            ],
        },
        # ------------------------------------------------------------------ 9
        {
            "title": "Boosting: Learning from Mistakes",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=3CC4N4z3GJc",
            "content": r"""
**Learning objective:** Explain how boosting builds models one after another to fix earlier mistakes, train gradient boosting in scikit-learn, and tune its learning rate and number of trees.

## Bagging vs boosting

A random forest trains its trees **side by side**, independently. **Boosting** trains them **one after another**: each new tree focuses on what the previous trees got wrong. It is like a student who, after every practice test, studies only the questions they missed.

| | Bagging (random forest) | Boosting |
|---|---|---|
| Trees built | In parallel, independently | One after another |
| Each tree | Deep, strong | Small, weak (often 2–3 levels) |
| Main effect | Reduces variance (overfitting) | Reduces bias (underfitting) |
| Risk | Little | Can overfit if it runs too long |

## Gradient boosting in one picture

For a number like rent:

1. Start with a simple guess: the average rent.
2. Compute the **residuals** — the errors (real − predicted) for every home.
3. Train a small tree to predict those **errors**.
4. Add a **small fraction** of that tree's prediction to the model (the **learning rate**, for example 0.1).
5. Repeat hundreds of times.

Each step moves the predictions a little closer to the truth — the same "small steps downhill" idea as gradient descent in Math & Python for AI. For classification the same idea works on the log-odds of the probability.

## See it in code

{LOANS}

{SPLIT}

```python
from sklearn.ensemble import GradientBoostingClassifier

gb = GradientBoostingClassifier(random_state=42)    # 100 trees of depth 3, learning rate 0.1
gb.fit(X_train, y_train)
print("Train:", round(gb.score(X_train, y_train), 3))
print("Test: ", round(gb.score(X_test, y_test), 3))
```

You should see about **0.90** on training data and **0.84** on the test set.

## The two settings that matter most

```python
for lr in [0.05, 0.1, 0.3]:
    m = GradientBoostingClassifier(learning_rate=lr, n_estimators=200, max_depth=2,
                                   random_state=42).fit(X_train, y_train)
    print("learning rate", lr, "test", round(m.score(X_test, y_test), 3))
```

- **learning_rate** — how big each correction is. Small values (0.05) learn slowly but carefully; big values (0.3) rush and overfit.
- **n_estimators** — how many trees. With a small learning rate you need more trees.
- **max_depth** — keep trees small (2–4): each one should be a weak learner.

A rule used by professionals: **lower the learning rate, raise the number of trees**, and stop when the validation score stops improving. `GradientBoostingClassifier(n_iter_no_change=10, validation_fraction=0.1)` does this early stopping for you.

## Watch it learn

```python
import numpy as np
import matplotlib.pyplot as plt

m = GradientBoostingClassifier(learning_rate=0.1, n_estimators=300, max_depth=2,
                               random_state=42).fit(X_train, y_train)
test_acc = [np.mean(p == y_test) for p in m.staged_predict(X_test)]
train_acc = [np.mean(p == y_train) for p in m.staged_predict(X_train)]
plt.plot(train_acc, label="train")
plt.plot(test_acc, label="test")
plt.xlabel("number of trees")
plt.ylabel("accuracy")
plt.legend()
plt.show()
print("Best number of trees on test:", int(np.argmax(test_acc)) + 1)
```

Training accuracy keeps rising; test accuracy rises, then flattens. The gap that opens is overfitting.

## AdaBoost and the famous libraries

- **AdaBoost** (1990s; it powered the first real-time face detectors in 2001) was the first popular boosting method: it gives **more weight** to misclassified examples so the next model concentrates on them. `AdaBoostClassifier` in scikit-learn.
- **HistGradientBoostingClassifier** — scikit-learn's fast version for large data; it also handles missing values.
- **XGBoost, LightGBM and CatBoost** — separate libraries that win many data competitions on tables of data. They follow the same fit/predict pattern.

On this small, simple dataset, boosting is about as good as logistic regression — the loans were simulated with a fairly simple rule. On real, messy tables, gradient boosting is very often the most accurate model.

## Key terms

- **Boosting** — training models in sequence, each fixing the errors of the previous ones.
- **Weak learner** — a small, simple model (a shallow tree).
- **Residual** — real value minus predicted value.
- **Learning rate (shrinkage)** — how much of each new tree is added.
- **Early stopping** — stop adding trees when the validation score stops improving.

**Takeaway:** Boosting adds many small trees one by one, each correcting the last; a small learning rate with enough trees and early stopping gives some of the most accurate models for tables.

## Try it yourself

1. Train `HistGradientBoostingClassifier(random_state=42)` and compare its test accuracy and speed with `GradientBoostingClassifier`.
2. Train `AdaBoostClassifier(n_estimators=200, random_state=42)`. How does it compare?
3. Use early stopping: `GradientBoostingClassifier(n_estimators=1000, learning_rate=0.05, n_iter_no_change=10, random_state=42)`. How many trees did it actually build? (Look at `n_estimators_`.)
4. In two sentences, explain the difference between bagging and boosting to a classmate.
""",
            "quiz": [
                ("How does boosting build its trees?",
                 ["All at the same time, independently", "One after another, each fixing earlier mistakes", "By copying one tree", "At random, without data"],
                 1, "Boosting is sequential."),
                ("In gradient boosting for regression, what does each new tree learn to predict?",
                 ["The original target", "The residuals (errors) of the current model", "The features", "The learning rate"],
                 1, "Each tree models what is still wrong."),
                ("What does a smaller learning rate usually need?",
                 ["Fewer trees", "More trees", "No trees", "Scaled features"],
                 1, "Smaller steps need more of them."),
                ("Why are boosting trees usually kept shallow (depth 2–4)?",
                 ["Deep trees are not allowed", "Each one should be a weak learner adding a small correction", "Shallow trees need scaling", "To make the forest bigger"],
                 1, "Many small corrections generalise well."),
                ("What is early stopping?",
                 ["Stop training when the validation score stops improving", "Train for one tree only", "Stop when accuracy is 100%", "Delete the test set"],
                 0, "It prevents boosting from overfitting."),
                ("Which libraries are famous gradient-boosting tools?",
                 ["XGBoost, LightGBM and CatBoost", "Matplotlib and Seaborn", "Flask and Django", "NumPy and Pandas"],
                 0, "They win many competitions on tabular data."),
            ],
        },
        # ------------------------------------------------------------------ 10
        {
            "title": "Support Vector Machines: The Widest Street",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=efR1C6CvhmE",
            "content": r"""
**Learning objective:** Explain margins, support vectors and kernels, train an SVM in scikit-learn, and tune its C setting.

## The widest possible street

Imagine borrowers drawn as dots on a map, repaid in blue and defaulted in red. Many lines could separate the two colours. A **support vector machine (SVM)** chooses the line that leaves the **widest street** (the **margin**) between the classes. A wide margin means new points near the boundary are less likely to be misclassified.

The few points that touch the edges of the street are the **support vectors** — they alone decide where the line goes. Points far from the boundary do not matter at all.

## Soft margins and C

Real data overlaps, so a perfect street is impossible. The setting **C** decides how strict the SVM is:

- **Small C** — a wide street that allows some points inside it or on the wrong side. Simpler, can underfit.
- **Large C** — a narrow street that tries hard to classify every training point. Can overfit.

## Curved boundaries: the kernel trick

Some patterns cannot be split by a straight line. A **kernel** lets the SVM work as if the data were moved into more dimensions, where a flat boundary does exist — without actually computing those dimensions. The default **RBF kernel** gives smooth curved boundaries.

```python
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

Xm, ym = make_moons(n_samples=400, noise=0.25, random_state=0)
Xm_tr, Xm_te, ym_tr, ym_te = train_test_split(Xm, ym, random_state=0)

print("Logistic regression:", LogisticRegression().fit(Xm_tr, ym_tr).score(Xm_te, ym_te))
print("Linear SVM:         ", SVC(kernel="linear").fit(Xm_tr, ym_tr).score(Xm_te, ym_te))
print("RBF SVM:            ", SVC(kernel="rbf").fit(Xm_tr, ym_tr).score(Xm_te, ym_te))
```

The "moons" are two curved shapes. Straight-line models score about **0.89–0.90**; the RBF kernel bends around the moons and reaches about **0.93**.

## Draw the boundary

```python
import numpy as np
import matplotlib.pyplot as plt

svm = SVC(kernel="rbf", C=1).fit(Xm_tr, ym_tr)
xx, yy = np.meshgrid(np.linspace(-2, 3, 300), np.linspace(-1.5, 2, 300))
zz = svm.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
plt.contourf(xx, yy, zz, alpha=0.3)
plt.scatter(Xm[:, 0], Xm[:, 1], c=ym, s=12)
plt.title("RBF SVM decision boundary")
plt.show()
```

## SVM on the loans

SVMs measure distances, so **scaling is required**.

{LOANS}

{SPLIT}

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler().fit(X_train)
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

for C in [0.1, 1, 10, 100]:
    s = SVC(C=C).fit(X_train_s, y_train)
    print("C =", C, "train", round(s.score(X_train_s, y_train), 3),
          "test", round(s.score(X_test_s, y_test), 3))
```

As C grows, training accuracy rises steadily (from about 0.84 to 0.89) but the test score peaks around C = 10 (about **0.85**) and then falls back — the overfitting pattern again.

## Probabilities and speed

- `SVC` gives labels by default. Use `SVC(probability=True)` if you need probabilities (slower).
- Training time grows quickly with the number of rows. For more than about 50,000 rows, prefer `LinearSVC` or a different model.

## When to use an SVM

Good for medium-sized data with many features (for example text or gene data), and when the boundary is curved but smooth. Less good for very large data, or when you must explain each decision.

## Key terms

- **Margin** — the gap between the boundary and the closest points of each class.
- **Support vectors** — the points on the edge of the margin that define the boundary.
- **C** — how strongly mistakes on training data are punished.
- **Kernel** — a function that lets SVMs draw curved boundaries (linear, RBF, polynomial).
- **Kernel trick** — working in a higher-dimensional space without computing it.

**Takeaway:** An SVM finds the widest street between classes; kernels let that street curve, C sets how strict it is, and features must be scaled.

## Try it yourself

1. Draw the moons boundary for C = 0.1 and C = 100. Describe the difference.
2. Try `SVC(kernel="poly", degree=3)` on the moons. Better or worse than RBF?
3. Train an RBF SVM on the **unscaled** loans data. What happens to the test accuracy?
4. Print `svm.n_support_` for the moons model. How many support vectors does each class have?
""",
            "quiz": [
                ("What does an SVM try to maximise?",
                 ["The number of features", "The margin between the classes", "The training time", "The number of trees"],
                 1, "It looks for the widest street."),
                ("What are support vectors?",
                 ["All the training points", "The points on the edge of the margin that define the boundary", "The test points", "The features"],
                 1, "Only the closest points decide the boundary."),
                ("What does a very large C do?",
                 ["Allows many mistakes with a wide street", "Tries hard to classify every training point, risking overfitting", "Removes the kernel", "Scales the data"],
                 1, "Large C punishes training mistakes heavily."),
                ("Why use the RBF kernel on the moons data?",
                 ["The classes are separated by a curved boundary", "It is faster", "The data has no labels", "It needs no scaling"],
                 0, "Kernels allow curved boundaries."),
                ("Must features be scaled for an SVM?",
                 ["No", "Yes, because SVMs use distances", "Only for linear kernels", "Only for regression"],
                 1, "Unscaled features distort the distances."),
                ("When is an SVM a poor choice?",
                 ["Medium data with many features", "Hundreds of thousands of rows", "Curved boundaries", "Text data"],
                 1, "Training time grows fast with the number of rows."),
            ],
        },
        # ------------------------------------------------------------------ 11
        {
            "title": "Naive Bayes: Fast Probability Classifiers",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=Q8l0Vip5YUw",
            "content": r"""
**Learning objective:** Explain how Naive Bayes uses Bayes' theorem with a "naive" independence assumption, and build a small SMS spam filter with scikit-learn.

## Bayes' theorem again

In Math & Python for AI you used Bayes' theorem to update a belief with evidence. **Naive Bayes** turns that into a classifier:

> P(spam | words) is proportional to P(spam) × P(word₁ | spam) × P(word₂ | spam) × …

- **P(spam)** — how common spam is overall (the prior).
- **P(word | spam)** — how often each word appears in spam messages, learned from the training data.

The model computes this score for every class (spam and not spam) and picks the larger one.

## Why "naive"?

It assumes every word (feature) is **independent** of the others once you know the class. That is clearly false — "free" and "prize" often appear together. Surprisingly, Naive Bayes still works well, especially for **text**, because it only needs the **right ranking** of classes, not perfect probabilities.

## A tiny SMS spam filter

```python
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

messages = [
    "Win a free phone now", "Claim your prize money today",
    "Meeting moved to 3pm", "Can you send the report",
    "Free airtime click this link", "Lunch at noon tomorrow?",
    "You won cash prize claim now", "Please review the budget file",
]
labels = [1, 1, 0, 0, 1, 0, 1, 0]          # 1 = spam

vec = CountVectorizer()                     # turns text into word counts
X_text = vec.fit_transform(messages)
print(vec.get_feature_names_out()[:10])

spam_filter = MultinomialNB().fit(X_text, labels)

new = ["Free prize waiting claim now", "Send me the meeting notes"]
print(spam_filter.predict(vec.transform(new)))
print(spam_filter.predict_proba(vec.transform(new)).round(3))
```

The first new message is classified as spam (probability about **0.99**), the second as normal (spam probability about **0.07**) — after seeing only eight examples!

`CountVectorizer` builds a **bag of words**: one column per word, counting how often it appears. Word order is ignored.

## Smoothing: the zero problem

If the word "airtime" never appeared in normal training messages, P(airtime | normal) would be 0 and would wipe out the whole product. Naive Bayes adds a small count to every word (**Laplace smoothing**, the `alpha=1.0` setting) so nothing is ever exactly zero.

## Naive Bayes for numbers

`GaussianNB` assumes each numeric feature follows a normal (bell) curve within each class.

{LOANS}

{SPLIT}

```python
from sklearn.naive_bayes import GaussianNB

nb = GaussianNB().fit(X_train, y_train)
print("Test accuracy:", round(nb.score(X_test, y_test), 3))
```

About **0.81** — lower than logistic regression (0.84), because income and loan size are not normally distributed and the model cannot combine them into the loan-to-income ratio that really drives risk.

## Which Naive Bayes?

| Version | Features | Typical use |
|---|---|---|
| MultinomialNB | Word counts | Spam filters, topic classification |
| BernoulliNB | Yes/no features (word present or not) | Short texts |
| GaussianNB | Numbers | Quick baseline on numeric data |

## Strengths and weaknesses

Naive Bayes trains in a blink, needs little data, and works well for text. Its probabilities are often too extreme (close to 0 or 1), and it cannot learn interactions between features.

## Key terms

- **Naive Bayes** — a classifier using Bayes' theorem with independent features.
- **Prior** — how common a class is before seeing the evidence.
- **Bag of words** — text represented by word counts, ignoring order.
- **Laplace smoothing** — adding a small count so no probability is zero.

**Takeaway:** Naive Bayes multiplies simple word (or feature) probabilities; it is a fast, strong baseline for text even though its independence assumption is false.

## Try it yourself

1. Add five more messages of your own (some in Kinyarwanda, for example "Watsindiye amafaranga") and retrain. Does it still work?
2. Try `BernoulliNB` on the same messages.
3. Print the words with the biggest difference in `spam_filter.feature_log_prob_` between the two classes. Which words are most "spammy"?
4. Explain to a friend why the model is called "naive".
""",
            "quiz": [
                ("Which theorem is Naive Bayes built on?",
                 ["Pythagoras", "Bayes' theorem", "The central limit theorem", "Fermat's theorem"],
                 1, "It combines a prior with evidence."),
                ("What is 'naive' about Naive Bayes?",
                 ["It uses little data", "It assumes features are independent given the class", "It cannot use text", "It has no prior"],
                 1, "The independence assumption is the naive part."),
                ("What does CountVectorizer do?",
                 ["Translates text", "Turns text into word-count columns (bag of words)", "Removes spam", "Scales numbers"],
                 1, "Each word becomes a column of counts."),
                ("Why is Laplace smoothing used?",
                 ["To stop a never-seen word from making a probability exactly zero", "To speed up training", "To scale features", "To remove stop words"],
                 0, "A single zero would wipe out the whole product."),
                ("Which version suits word counts?",
                 ["GaussianNB", "MultinomialNB", "LinearRegression", "KMeans"],
                 1, "MultinomialNB models counts."),
                ("Why did GaussianNB do worse than logistic regression on the loans?",
                 ["It cannot combine features such as loan and income, and the features are not bell-shaped", "It overfits deep trees", "It needs more trees", "The data has no labels"],
                 0, "Its assumptions do not match this data."),
            ],
        },
        # ------------------------------------------------------------------ 12
        {
            "title": "Week 2 Project: Compare Models on Medical Data",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=0pP4EwWJgIU",
            "content": r"""
**Learning objective:** Compare seven classifiers fairly on a real medical dataset, choose one with good reasons, and explain the result responsibly.

## The data: breast-cancer screening

scikit-learn includes a real dataset from the University of Wisconsin: measurements of cell nuclei from **569** breast-tissue samples, each labelled **malignant** (cancer) or **benign** (not cancer). Doctors use tools like this to support — never replace — their judgement.

```python
import pandas as pd
from sklearn.datasets import load_breast_cancer

data = load_breast_cancer(as_frame=True)
X, y = data.data, data.target
print(X.shape)
print(data.target_names)          # 0 = malignant, 1 = benign
print(y.value_counts())
X.iloc[:, :6].head()
```

Watch out: here **0 means malignant** and **1 means benign**. Always check what each label means before you interpret results.

## Step 1 — Explore

- How many malignant and benign samples are there? (212 and 357.)
- Compare the average `mean radius` of malignant and benign samples (`groupby(y)`).
- Draw a histogram of `mean radius` coloured by class.

## Step 2 — Split once, for everyone

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
```

## Step 3 — Compare seven models

`make_pipeline` glues a scaler and a model together so the scaler is always fitted on training data only (you will learn pipelines fully in Week 4).

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

models = {
    "Baseline": DummyClassifier(),
    "Logistic regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "k-NN (k=5)": make_pipeline(StandardScaler(), KNeighborsClassifier()),
    "Decision tree": DecisionTreeClassifier(max_depth=4, random_state=42),
    "Random forest": RandomForestClassifier(n_estimators=300, random_state=42),
    "Gradient boosting": GradientBoostingClassifier(random_state=42),
    "SVM (RBF)": make_pipeline(StandardScaler(), SVC()),
    "Naive Bayes": GaussianNB(),
}
scores = {}
for name, m in models.items():
    m.fit(X_train, y_train)
    scores[name] = round(m.score(X_test, y_test), 3)
print(pd.Series(scores).sort_values(ascending=False))
```

You should find logistic regression on top (about **0.99**), SVM and k-NN close behind (about 0.98), the ensembles about 0.96, and the baseline at about **0.63**.

## Step 4 — Think before you choose

The test set has only 143 samples, so one more or one fewer correct answer moves accuracy by 0.7 points. Differences of one or two points may be **luck**. In Week 3 you will use cross-validation to compare models more reliably.

Also ask: **which mistake is worse?** Calling a cancer "benign" (a missed cancer) is far more dangerous than calling a benign sample "malignant" (which leads to more tests). Count the missed cancers for your top model:

```python
best = models["Logistic regression"]
pred = best.predict(X_test)
missed = ((y_test == 0) & (pred == 1)).sum()
false_alarms = ((y_test == 1) & (pred == 0)).sum()
print("Missed cancers:", missed, " False alarms:", false_alarms)
```

## Step 5 — Report (one page)

1. The task, the data (569 samples, 30 measurements) and what 0 and 1 mean.
2. A sorted table of the eight test accuracies.
3. Your chosen model and **three reasons** (accuracy, simplicity, explainability, speed).
4. The number of missed cancers and false alarms, and why that matters more than accuracy.
5. Limits: one hospital's data from the 1990s; a model must be validated locally before any clinical use; the decision always stays with a doctor.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Fairness | Same split and test set for every model |
| Preparation | Scaling only inside pipelines for scale-sensitive models |
| Judgement | Notes that small differences may be luck |
| Responsibility | Discusses missed cancers and human oversight |
| Communication | Clear table and plain-English conclusion |

**Takeaway:** No algorithm wins everywhere; compare several on the same split, consider which mistakes matter, and choose with reasons — not only with the highest number.

## Try it yourself

Complete Steps 1–5. Then change `random_state=42` in the split to 0, 1 and 2. Does the ranking of the models change? What does that teach you about trusting a single test score?
""",
            "quiz": [
                ("In load_breast_cancer, what does target 0 mean?",
                 ["Benign", "Malignant", "Missing", "Unknown"],
                 1, "Always check label meanings: 0 = malignant here."),
                ("Why use make_pipeline(StandardScaler(), model)?",
                 ["To make the model slower", "So scaling is always learned from training data only", "To remove features", "To draw charts"],
                 1, "Pipelines prevent leakage from the test set."),
                ("Logistic regression scores 0.986 and random forest 0.958 on 143 test samples. What is the careful conclusion?",
                 ["Random forests are always worse", "The difference is small and may partly be luck; check with cross-validation", "Logistic regression is perfect", "The test set is wrong"],
                 1, "Small test sets make small differences unreliable."),
                ("Which mistake is most dangerous in cancer screening?",
                 ["A false alarm", "A missed cancer", "Both are equal", "Neither matters"],
                 1, "A missed cancer can delay treatment."),
                ("What did the baseline score, and why does it matter?",
                 ["About 0.63 — any useful model must beat always guessing 'benign'", "1.0", "0.0", "It was not needed"],
                 0, "The baseline shows what no learning achieves."),
                ("Who should make the final medical decision?",
                 ["The model", "A qualified doctor, supported by the model", "The data scientist", "The patient's neighbour"],
                 1, "AI supports, humans decide in high-stakes care."),
            ],
        },
    ],
}

for _lesson in WEEK2["lessons"]:
    _lesson["content"] = _lesson["content"].replace("{SPLIT}", SPLIT)
fill_data(WEEK2)
