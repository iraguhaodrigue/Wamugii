"""Machine Learning Fundamentals -- Week 1: Your First Models with scikit-learn. Original WAMUGII content."""

from app.course_content.ml_data import fill_data

WEEK1 = {
    "title": "Week 1 · Your First Models with scikit-learn",
    "lessons": [
        # ------------------------------------------------------------------ 1
        {
            "title": "What Machine Learning Really Is — and scikit-learn",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=Gv9_4yMHFhI",
            "content": r"""
**Learning objective:** Explain what a machine-learning model is, name the steps every scikit-learn project follows, and train and test your first model in Google Colab.

## From rules to learning

In ordinary programming, **you** write the rules: "if the house has 3 bedrooms, the rent is 300,000 RWF". Real life is too messy for that. Rent depends on size, district, distance to town, furniture — and on things nobody wrote down.

In **machine learning** you give the computer many **examples** (homes and their real rents), and it **learns the rule by itself**. The learned rule is called a **model**. Then you use the model on new homes it has never seen.

> Data + an algorithm → a trained model → predictions on new data.

This course is the hands-on part of the WAMUGII AI Program: you will build the most important kinds of models used in industry, and learn how to check them honestly. You need the Python and Pandas from **Math & Python for AI**.

## The two big kinds of supervised learning

| Problem | What you predict | Example from this course |
|---|---|---|
| **Regression** | A number | The monthly rent of a home in Kigali |
| **Classification** | A category (yes/no, A/B/C) | Will a mobile-money borrower repay the loan? |

Both are **supervised** learning: every training example has the correct answer (the **label** or **target**). In Week 4 you will also meet **unsupervised** learning, where there is no answer column.

## Meet scikit-learn

**scikit-learn** (imported as `sklearn`) is the most used Python library for classic machine learning. It is free, already installed in Google Colab, and every model in it works the **same way**:

1. **Choose** a model: `model = LinearRegression()`
2. **Fit** (train) it on training data: `model.fit(X_train, y_train)`
3. **Predict** on new data: `model.predict(X_test)`
4. **Score** it: compare predictions with the real answers.

Learn these four steps once and you can use dozens of algorithms. This is why professionals love scikit-learn.

## X and y

scikit-learn expects two things:

- **X** — the **features**: a table with one row per example and one column per input (size, distance…). Written with a capital X because it is a table (a matrix).
- **y** — the **target**: one value per row, the answer to learn (the rent).

## Our data: Kigali home rents

Open a new notebook at colab.research.google.com and run this cell. It creates 600 homes. The data is **simulated** (made with code), so everyone gets the same numbers.

{HOMES}

`homes.head()` shows the first five homes. The rent depends on size, district, distance to the city centre and whether the home is furnished — plus some random noise, like in real life.

## Your first model

Start simple: predict rent from **size only**.

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

X = homes[["size_m2"]]          # double brackets: X must be a table
y = homes["rent_rwf"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

model = LinearRegression()      # 1. choose
model.fit(X_train, y_train)     # 2. fit
pred = model.predict(X_test)    # 3. predict
print("MAE:", round(mean_absolute_error(y_test, pred)), "RWF")   # 4. score
```

You should see an MAE of about **42,000 RWF**: on homes the model never saw, its guesses are off by about 42,000 RWF on average.

## Why split the data?

`train_test_split` keeps **20%** of the homes aside as a **test set**. The model learns only from the other 80%. Testing on homes it has never seen tells you how it will do in real life. Testing on the training homes would be like giving students the exam questions the night before — the score would look great and mean nothing.

`random_state=42` makes the random split repeatable, so your numbers match these notes.

## Use the model

```python
new_home = pd.DataFrame({"size_m2": [100]})
print(model.predict(new_home).round(-3))
print("RWF per extra m²:", model.coef_.round(0))
```

The model predicts about **337,000 RWF** for a 100 m² home and learned that each extra square metre adds about **2,650 RWF** of rent.

## What a model is not

- A model is **not** magic: it only finds patterns that are in the data.
- It can be **confidently wrong** for unusual cases (a 400 m² villa — there are none in the data).
- It copies the **past**. If the past was unfair, the model can be unfair too (Week 4).

## Key terms

- **Model** — the rule learned from examples.
- **Features (X)** — the inputs; **target (y)** — the answer to predict.
- **Fit** — train the model on data; **predict** — use it on new data.
- **Training set / test set** — data to learn from / data kept aside to check honestly.
- **MAE** — mean absolute error: the average size of the mistakes, in real units.

**Takeaway:** Every scikit-learn project follows the same four steps — choose, fit, predict, score — and is always tested on data the model has never seen.

## Try it yourself

1. Change `test_size` to 0.3. Does the MAE change much?
2. Train a model that uses `km_to_centre` only. Is it better or worse than size? Why might that be?
3. Predict the rent of a 60 m² home and a 150 m² home.
4. In your own words, write two sentences explaining to a friend the difference between regression and classification.
""",
            "quiz": [
                ("What is a machine-learning model?",
                 ["A rule written by hand", "A rule the computer learned from examples", "A database of homes", "A chart"],
                 1, "The model is the pattern learned from data."),
                ("Predicting the monthly rent of a home is which kind of problem?",
                 ["Classification", "Regression", "Clustering", "Search"],
                 1, "Rent is a number, so it is regression."),
                ("What are the four steps every scikit-learn model follows?",
                 ["Choose, fit, predict, score", "Open, read, close, print", "Draw, colour, save, share", "Sort, filter, group, plot"],
                 0, "The same four steps work for every algorithm."),
                ("Why do we keep a test set aside?",
                 ["To make training faster", "To check the model honestly on data it has never seen", "Because scikit-learn needs exactly 20%", "To make the MAE larger"],
                 1, "Unseen data shows how the model will work in real life."),
                ("In scikit-learn, what is y?",
                 ["The table of features", "The target: the answer to learn", "The test score", "The random seed"],
                 1, "X holds the inputs and y holds the answers."),
                ("The test MAE is 42,000 RWF. What does that mean?",
                 ["Guesses are off by about 42,000 RWF on average", "The model is 42% accurate", "42,000 homes were wrong", "The rent is 42,000 RWF"],
                 0, "MAE is the average size of the error in real units."),
            ],
        },
        # ------------------------------------------------------------------ 2
        {
            "title": "Preparing Data: Encoding and Scaling",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=irHhDMbw3xo",
            "content": r"""
**Learning objective:** Turn text categories into numbers with one-hot encoding, put numbers on the same scale with standardisation, and avoid the most common data-preparation mistake: leakage.

## Models only understand numbers

A model does maths. It cannot multiply "Gasabo" by anything. Before training, every feature must be a **number**, and many models also need the numbers to be on a **similar scale**. This preparation is often most of the work in a real project.

Run the homes cell again:

{HOMES}

```python
print(homes.dtypes)
print(homes["district"].value_counts())
```

`district` is text and `furnished` is True/False. Both need converting.

## True / False → 1 / 0

```python
homes["furnished"] = homes["furnished"].astype(int)
print(homes["furnished"].head())
```

## Categories → one-hot encoding

Could we write Gasabo = 1, Kicukiro = 2, Nyarugenge = 3? **No.** The model would think Nyarugenge is "three times" Gasabo and that Kicukiro sits "between" them. Districts have **no order**.

Instead we use **one-hot encoding**: one new 0/1 column per category.

| district | district_Gasabo | district_Kicukiro | district_Nyarugenge |
|---|---|---|---|
| Gasabo | 1 | 0 | 0 |
| Kicukiro | 0 | 1 | 0 |
| Nyarugenge | 0 | 0 | 1 |

```python
X = pd.get_dummies(homes.drop(columns="rent_rwf"), columns=["district"], dtype=int)
print(X.columns.tolist())
X.head()
```

You now have 7 feature columns, all numbers.

**When order is real**, keep the order: education level (primary < secondary < university) or clothing size (S < M < L) can be coded 1, 2, 3. This is called **ordinal encoding**.

## The scikit-learn way: OneHotEncoder

`pd.get_dummies` is quick for exploring. In real projects we use scikit-learn's `OneHotEncoder`, because it **remembers** the categories it saw in training and handles new ones safely:

```python
from sklearn.preprocessing import OneHotEncoder

enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
enc.fit(homes[["district"]])
print(enc.categories_)
print(enc.transform(pd.DataFrame({"district": ["Kicukiro", "Musanze"]})))
```

"Musanze" never appeared in the training data, so it becomes all zeros instead of crashing your app.

## Scaling: putting numbers on the same ruler

Look at the ranges:

```python
print(homes[["bedrooms", "size_m2", "km_to_centre"]].describe().loc[["min", "max"]])
```

Bedrooms go from 1 to 4, size from 25 to about 166. Models that measure **distances** between examples (k-nearest neighbours, Lesson 5) or use gradient descent would treat size as far more important just because its numbers are bigger.

**Standardisation** rescales each column to mean 0 and standard deviation 1 — the z-score you met in Math & Python for AI:

> z = (value − mean) ÷ standard deviation

```python
from sklearn.preprocessing import StandardScaler

nums = homes[["bedrooms", "size_m2", "km_to_centre"]]
scaler = StandardScaler()
scaled = scaler.fit_transform(nums)
print(scaled.mean(axis=0).round(2), scaled.std(axis=0).round(2))
```

Every column now has mean 0 and SD 1. `MinMaxScaler` is another option: it squeezes each column into 0–1.

| Model | Needs scaling? |
|---|---|
| Linear and logistic regression | Helps, and matters with regularisation |
| k-nearest neighbours, SVM | **Yes** — they use distances |
| Decision trees, random forests | No — they only compare values |

## The golden rule: fit on training data only

The scaler learns a mean and SD; the encoder learns the categories. They must learn them from the **training set only**, then apply the same numbers to the test set:

```python
from sklearn.model_selection import train_test_split

X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
cols = ["bedrooms", "size_m2", "km_to_centre"]
scaler = StandardScaler().fit(X_train[cols])      # learn from training rows
X_train_s = scaler.transform(X_train[cols])
X_test_s = scaler.transform(X_test[cols])         # reuse the training numbers
print(X_test_s.mean(axis=0).round(2))             # close to 0, not exactly 0
```

If you fit the scaler on all the data, information about the test set **leaks** into training and your test score becomes too optimistic. This mistake is called **data leakage**. In Week 4 you will use a **Pipeline**, which makes this rule automatic.

## Missing values

Real data has gaps. Two simple choices: drop the rows (if very few) or **impute** — fill them with the column's median (numbers) or most common value (categories). scikit-learn's `SimpleImputer(strategy="median")` does this, and like the scaler it must be fitted on training data only.

## Key terms

- **One-hot encoding** — one 0/1 column per category, for categories with no order.
- **Ordinal encoding** — numbers 1, 2, 3 for categories that have a real order.
- **Standardisation** — rescale to mean 0, SD 1 (StandardScaler).
- **Imputation** — filling missing values.
- **Data leakage** — test-set information sneaking into training.

**Takeaway:** Convert every feature to numbers, scale them when the model uses distances, and always learn preparation steps from the training data only.

## Try it yourself

1. One-hot encode `district` with `drop_first=True`. How many district columns do you get, and why is that still enough information?
2. Scale `size_m2` with `MinMaxScaler`. What are the new minimum and maximum?
3. Make a small DataFrame with a column `education` (primary, secondary, university) and code it in order 1, 2, 3 with `.map()`.
4. Put three missing values into `size_m2` and fill them with `SimpleImputer(strategy="median")`.
""",
            "quiz": [
                ("Why can't we code Gasabo = 1, Kicukiro = 2, Nyarugenge = 3?",
                 ["Python cannot store numbers", "The model would think the districts have an order and size", "It uses too much memory", "scikit-learn forbids it"],
                 1, "Districts have no order, so one-hot encoding is used."),
                ("How many 0/1 columns does one-hot encoding make for a feature with 3 categories (without drop_first)?",
                 ["1", "2", "3", "6"],
                 2, "One column per category."),
                ("What does StandardScaler do to each column?",
                 ["Sorts it", "Rescales it to mean 0 and standard deviation 1", "Deletes outliers", "Rounds it"],
                 1, "Standardisation produces z-scores."),
                ("Which model does NOT need scaled features?",
                 ["k-nearest neighbours", "Support vector machine", "Decision tree", "Logistic regression with regularisation"],
                 2, "Trees only compare values against thresholds."),
                ("Why must the scaler be fitted on the training set only?",
                 ["It is faster", "To avoid leaking test-set information into training", "The test set has no numbers", "Because fit only works once"],
                 1, "Fitting on all data is data leakage."),
                ("What does OneHotEncoder(handle_unknown='ignore') do with a district it never saw?",
                 ["Crashes", "Turns it into all zeros", "Guesses the closest district", "Deletes the row"],
                 1, "Unknown categories become zeros instead of an error."),
            ],
        },
        # ------------------------------------------------------------------ 3
        {
            "title": "Linear Regression with scikit-learn",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=7ArmBVF2dCs",
            "content": r"""
**Learning objective:** Train a multiple linear regression model in scikit-learn, read its coefficients in plain words, and judge it with MAE, R² and a baseline.

## From one feature to many

In Math & Python for AI you built linear regression from scratch with gradient descent. scikit-learn does the same job in one line — and with many features at once:

> rent = w₁ × size + w₂ × distance + w₃ × furnished + … + b

Each **weight** (coefficient) says how much the rent changes when that feature goes up by one, with the others held the same.

{HOMES}

## Prepare and split

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

X = pd.get_dummies(homes.drop(columns="rent_rwf"), columns=["district"], dtype=int)
X["furnished"] = X["furnished"].astype(int)
y = homes["rent_rwf"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

## Train and read the model

```python
model = LinearRegression().fit(X_train, y_train)

coefs = pd.Series(model.coef_, index=X.columns).round(0)
print(coefs)
print("intercept:", round(model.intercept_))
```

Read it like a sentence:

- **size_m2 ≈ +2,580**: each extra square metre adds about 2,580 RWF a month.
- **km_to_centre ≈ −6,400**: each kilometre further from town lowers rent by about 6,400 RWF.
- **furnished ≈ +59,000**: furniture adds about 59,000 RWF.
- **district_Gasabo** is about 30,000 RWF above **district_Kicukiro** — compare districts with each other, not with zero.
- **bedrooms ≈ +700** only: once size is known, the number of bedrooms adds almost nothing. Bedrooms and size carry the same information.

The model rediscovered the rule used to simulate the data (2,600 per m², −6,000 per km, +60,000 furnished). With real data you never know the true rule — that is why we test.

## Evaluate honestly

```python
pred = model.predict(X_test)
print("MAE:", round(mean_absolute_error(y_test, pred)), "RWF")
print("R²: ", round(r2_score(y_test, pred), 3))
```

You should get an MAE of about **20,000 RWF** and R² of about **0.94**. Using all features halved the error of the size-only model from Lesson 1 (about 42,000).

## Always compare with a baseline

A model is only useful if it beats a lazy guess. The laziest regression guess is "every home costs the average rent":

```python
from sklearn.dummy import DummyRegressor

base = DummyRegressor(strategy="mean").fit(X_train, y_train)
print("Baseline MAE:", round(mean_absolute_error(y_test, base.predict(X_test))))
```

The baseline is off by about **90,000 RWF**. Our model is more than four times better. Always report a baseline — it turns a number into a story.

## Look at the mistakes

```python
import matplotlib.pyplot as plt

plt.scatter(y_test, pred, alpha=0.6)
plt.plot([50_000, 600_000], [50_000, 600_000], color="red")   # perfect predictions
plt.xlabel("Real rent (RWF)")
plt.ylabel("Predicted rent (RWF)")
plt.title("Predicted vs real rent (test homes)")
plt.show()

errors = y_test - pred
print("Largest under-prediction:", round(errors.max()))
```

Points close to the red line are good predictions. Look for patterns: if all the big errors were furnished homes in Gasabo, the model would be missing something.

## When linear regression struggles

- **Curved relationships** — it can only draw straight lines (unless you add features like size²).
- **Outliers** — one mistyped rent of 50,000,000 RWF pulls the whole line.
- **Features that move together** (size and bedrooms) — the coefficients become unstable and hard to read, even when predictions stay good. Regularisation (Lesson 16) helps.

## Key terms

- **Multiple linear regression** — a straight-line model with several features.
- **Coefficient (weight)** — change in the prediction when one feature rises by 1.
- **Intercept** — the prediction when all features are 0.
- **R²** — share of the variation explained (1 = perfect, 0 = no better than the mean).
- **Baseline** — a simple guess every model must beat.

**Takeaway:** scikit-learn trains linear regression in one line; your job is to read the coefficients in plain words and prove the model beats a baseline on unseen data.

## Try it yourself

1. Remove `bedrooms` from X and retrain. Does the test MAE change? What does that tell you?
2. Predict the rent of a furnished 90 m² home in Kicukiro, 4 km from town. (Build a one-row DataFrame with the same columns as X.)
3. Add a column `size_sq = size_m2 ** 2`. Does it help? Why or why not?
4. Write three sentences for a landlord explaining what the model learned.
""",
            "quiz": [
                ("The coefficient of km_to_centre is about −6,400. What does it mean?",
                 ["Rent rises 6,400 RWF per km", "Each extra km from town lowers rent by about 6,400 RWF, other things equal", "6,400 homes are far from town", "The model is wrong"],
                 1, "A negative weight lowers the prediction as the feature grows."),
                ("Why is the bedrooms coefficient so small?",
                 ["Bedrooms do not matter to anyone", "Size already carries the same information", "It is a bug", "Bedrooms were removed"],
                 1, "Bedrooms and size move together; once size is known, bedrooms add little."),
                ("What does R² = 0.94 mean?",
                 ["94% of predictions are exactly right", "The model explains about 94% of the variation in rent", "The error is 94 RWF", "94 homes were used"],
                 1, "R² is the share of variation explained."),
                ("What does DummyRegressor(strategy='mean') predict?",
                 ["The average training rent for every home", "The best possible rent", "Random rents", "Zero"],
                 0, "It is a lazy baseline to compare against."),
                ("On a predicted-vs-real plot, where are perfect predictions?",
                 ["On the diagonal line", "At the bottom", "On the left edge", "Anywhere"],
                 0, "Predicted equals real on the diagonal."),
                ("Which situation is hard for plain linear regression?",
                 ["A straight-line relationship", "A strongly curved relationship", "Numbers on similar scales", "A clean dataset"],
                 1, "It can only draw straight lines unless you add new features."),
            ],
        },
        # ------------------------------------------------------------------ 4
        {
            "title": "Logistic Regression: Predicting Yes or No",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=yIYKR4sgzI8",
            "content": r"""
**Learning objective:** Train a logistic regression classifier, turn its output into probabilities and decisions, and explain why accuracy alone can mislead.

## The problem: will the loan be repaid?

Mobile-money lenders in Rwanda and across Africa give small loans in seconds, using data instead of paperwork. The model must answer a **yes/no** question: will this borrower **default** (fail to repay)? That is **classification**.

Run the loans cell. It creates 2,000 past borrowers. `defaulted = 1` means the loan was not repaid.

{LOANS}

About **21%** of borrowers defaulted.

## From a line to a probability

Linear regression can give any number, like −3 or 250. For yes/no we want a **probability** between 0 and 1. Logistic regression computes a straight-line score, then squeezes it through the **sigmoid** (S-shaped) curve:

> probability = 1 ÷ (1 + e^(−score))

A very negative score gives a probability near 0, a score of 0 gives 0.5, a large score gives nearly 1. Despite its name, logistic regression is a **classification** model.

## Train it

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

X = loans.drop(columns="defaulted")
y = loans["defaulted"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

scaler = StandardScaler().fit(X_train)
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

clf = LogisticRegression().fit(X_train_s, y_train)
print("Accuracy:", accuracy_score(y_test, clf.predict(X_test_s)))
```

`stratify=y` keeps the same share of defaulters (21%) in both the training and test sets — important whenever one class is smaller.

You should get about **0.84** accuracy.

## Is 84% good? Check the baseline

```python
from sklearn.dummy import DummyClassifier

lazy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
print("Baseline accuracy:", accuracy_score(y_test, lazy.predict(X_test)))
```

A "model" that says **nobody ever defaults** scores about **0.79** — and is useless, because it never catches a single bad loan. Our model is better, but only by 5 points. In Week 3 you will learn measures (precision, recall) that show what really matters.

## Probabilities, not just labels

```python
new = pd.DataFrame({
    "income_rwf":      [150_000, 400_000],
    "loan_rwf":        [250_000,  50_000],
    "months_customer": [3, 40],
    "late_payments":   [2, 0],
    "salaried":        [0, 1],
})
print(clf.predict_proba(scaler.transform(new))[:, 1].round(3))
```

The first applicant (low income, big loan, new customer, two late payments) gets a default probability of about **0.92**; the second about **0.001**. `predict()` simply says "1" when the probability is above **0.5** — but a lender can choose another **threshold**, for example refuse above 0.3 (Lesson 15).

## Reading the coefficients

```python
print(pd.Series(clf.coef_[0], index=X.columns).round(2))
```

Because the features are standardised, the sizes can be compared:

- **income_rwf** is negative: higher income → lower risk.
- **loan_rwf** and **late_payments** are positive: bigger loans and past lateness → higher risk.
- **months_customer** and **salaried** are negative: loyal and salaried customers are safer.

These directions make business sense — a good check that the model learned something real.

## More than two classes

Logistic regression also handles several classes (for example: low, medium, high risk). scikit-learn does this automatically when y has more than two values.

## Key terms

- **Classification** — predicting a category.
- **Logistic regression** — a linear score passed through the sigmoid to give a probability.
- **Sigmoid** — S-shaped curve that turns any number into 0–1.
- **predict_proba** — the predicted probability of each class.
- **Threshold** — the probability above which we say "yes" (0.5 by default).
- **Stratify** — keep class shares the same in train and test.

**Takeaway:** Logistic regression gives a probability for each case; accuracy must always be compared with the "most frequent class" baseline.

## Try it yourself

1. Train without scaling (use `LogisticRegression(max_iter=1000)`). Is the accuracy very different? Are the coefficients easier or harder to compare?
2. Find the five test borrowers with the highest predicted default probability. Look at their features — do they make sense?
3. Count how many test borrowers have a probability above 0.3, and how many above 0.5.
4. Explain to a loan officer, in three sentences, why 79% accuracy can be useless.
""",
            "quiz": [
                ("What does logistic regression predict?",
                 ["Any number such as a rent", "The probability of a class, used to classify", "Clusters", "A straight line only"],
                 1, "It is a classification model despite its name."),
                ("What does the sigmoid function do?",
                 ["Sorts data", "Squeezes any score into a probability between 0 and 1", "Removes outliers", "Draws a straight line"],
                 1, "The S-curve maps scores to 0–1."),
                ("A model that predicts 'no default' for everyone gets 79% accuracy. Why is that useless?",
                 ["79% is too low", "It never catches a single defaulter", "It is too slow", "It uses too many features"],
                 1, "High accuracy can hide a model that misses everything important."),
                ("What does stratify=y do in train_test_split?",
                 ["Sorts the rows", "Keeps the same share of each class in train and test", "Removes the target", "Scales the data"],
                 1, "Stratifying keeps class proportions equal."),
                ("By default, when does predict() return 1?",
                 ["When the probability is above 0.5", "Always", "When the probability is above 0.9", "When income is high"],
                 0, "The default threshold is 0.5."),
                ("The coefficient for late_payments is positive. What does it mean?",
                 ["More late payments → higher predicted default risk", "Late payments lower risk", "The feature is useless", "The data is wrong"],
                 0, "A positive weight raises the probability of class 1."),
            ],
        },
        # ------------------------------------------------------------------ 5
        {
            "title": "k-Nearest Neighbours: Learning from Similar Cases",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=HVXime0nQeI",
            "content": r"""
**Learning objective:** Explain how k-nearest neighbours classifies a new case, show why scaling matters for it, and choose a good value of k.

## The idea: ask the neighbours

k-nearest neighbours (**k-NN**) is the simplest model to understand. To classify a new borrower:

1. Measure the **distance** from the new borrower to every borrower in the training data.
2. Take the **k** closest ones (for example k = 5).
3. **Vote**: if 4 of the 5 neighbours defaulted, predict "default".

There is no real training step — k-NN just **remembers** the training data. That makes it a **lazy learner**: fast to train, slow to predict on big data.

## Distance

For two borrowers with features (a₁, a₂) and (b₁, b₂), the straight-line (Euclidean) distance is:

> distance = √((a₁ − b₁)² + (a₂ − b₂)²)

— the same Pythagoras you used for vector length in Math & Python for AI, with as many features as you have.

{LOANS}

## Why scaling is essential here

Income is measured in hundreds of thousands of RWF; late payments are 0, 1 or 2. Without scaling, a difference of 1,000 RWF in income counts more than a difference of 2 late payments — nonsense. Let's measure it:

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

X = loans.drop(columns="defaulted")
y = loans["defaulted"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

scaler = StandardScaler().fit(X_train)
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

raw = KNeighborsClassifier(n_neighbors=15).fit(X_train, y_train)
scaled = KNeighborsClassifier(n_neighbors=15).fit(X_train_s, y_train)
print("Unscaled:", accuracy_score(y_test, raw.predict(X_test)))
print("Scaled:  ", accuracy_score(y_test, scaled.predict(X_test_s)))
```

Scaling lifts accuracy from about **0.82** to about **0.84**. On data where the units differ even more, the gap can be huge.

## Choosing k

```python
for k in [1, 5, 15, 25, 51]:
    knn = KNeighborsClassifier(n_neighbors=k).fit(X_train_s, y_train)
    print(k, accuracy_score(y_test, knn.predict(X_test_s)))
```

- **k = 1** copies the single closest borrower — it follows noise and scores worst (about **0.77**). This is **overfitting**.
- **Large k** smooths too much: with k = 1,500 every prediction becomes the majority class. This is **underfitting**.
- A middle value (here around 15–25) works best.

Choosing k by looking at the **test set** is actually cheating a little — you are tuning to the exam. In Week 3 you will choose k properly with **cross-validation**.

Tip: for two classes, use an **odd k** so votes cannot tie.

## k-NN for numbers

`KNeighborsRegressor` predicts a number by **averaging** the neighbours' values — for example the average rent of the 10 most similar homes. Estate agents do this in their heads: "similar flats nearby rent for about…".

## Strengths and weaknesses

| Strengths | Weaknesses |
|---|---|
| Very easy to explain | Slow to predict on large data |
| No training time | Needs scaling |
| Works for any shape of boundary | Struggles with many features (distances lose meaning) |

## Key terms

- **k-nearest neighbours** — predict from the k most similar training examples.
- **Euclidean distance** — straight-line distance between two examples.
- **Lazy learner** — stores the data instead of learning a formula.
- **Overfitting** — following noise in the training data (k too small).
- **Underfitting** — too simple to capture the pattern (k too large).

**Takeaway:** k-NN predicts from similar past cases; it only works well when features are scaled and k is neither too small nor too large.

## Try it yourself

1. Plot test accuracy for k from 1 to 60 (`plt.plot`). Where is the best region?
2. Use `KNeighborsRegressor(n_neighbors=10)` on the homes data (one-hot district, scaled numbers). Compare its MAE with linear regression from Lesson 3.
3. Try `weights="distance"` so closer neighbours get a bigger vote. Does it help?
4. Explain why k-NN would be slow for a lender with 10 million past loans.
""",
            "quiz": [
                ("How does k-NN classify a new example?",
                 ["By a straight-line formula", "By a vote of the k most similar training examples", "By random choice", "By the first row of the data"],
                 1, "The nearest neighbours vote."),
                ("Why must features be scaled for k-NN?",
                 ["To save memory", "So features with big numbers do not dominate the distance", "Because k must be odd", "It is not needed"],
                 1, "Distances are unfair when units differ."),
                ("What usually happens with k = 1?",
                 ["Underfitting", "Overfitting: the model follows noise", "Perfect test accuracy", "An error"],
                 1, "One neighbour copies noise in the training data."),
                ("Why is k-NN called a lazy learner?",
                 ["It is slow to train", "It stores the training data instead of learning a formula", "It never predicts", "It uses few features"],
                 1, "Work happens at prediction time."),
                ("For a yes/no problem, why choose an odd k?",
                 ["It is faster", "So votes cannot tie", "Even numbers are not allowed", "It improves scaling"],
                 1, "With two classes an odd k avoids ties."),
                ("Which model predicts a number from the average of similar cases?",
                 ["KNeighborsRegressor", "LogisticRegression", "KMeans", "DummyClassifier"],
                 0, "The regressor averages neighbours' values."),
            ],
        },
        # ------------------------------------------------------------------ 6
        {
            "title": "Week 1 Project: Predict Rents in Kigali",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=RlQuVL6-qe8",
            "content": r"""
**Learning objective:** Run a complete regression project from raw data to a short report: prepare the features, compare three models against a baseline, and explain the winner.

## The brief

A property website in Kigali wants to show visitors a **fair rent estimate** for any home. You are the data scientist. Build the model, test it honestly and write a one-page report for the manager.

{HOMES}

## Step 1 — Explore (15 minutes)

- `homes.describe()` and `homes["district"].value_counts()`.
- Average rent per district (`groupby`).
- A scatter plot of `size_m2` against `rent_rwf`, and one of `km_to_centre` against rent.

Write two sentences on what you see.

## Step 2 — Prepare

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X = pd.get_dummies(homes.drop(columns="rent_rwf"), columns=["district"], dtype=int)
X["furnished"] = X["furnished"].astype(int)
y = homes["rent_rwf"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler().fit(X_train)
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)
```

## Step 3 — Compare models

```python
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, r2_score

models = {
    "Baseline (mean)": DummyRegressor(),
    "Linear regression": LinearRegression(),
    "k-NN (k=10)": KNeighborsRegressor(n_neighbors=10),
}
results = []
for name, m in models.items():
    m.fit(X_train_s, y_train)
    pred = m.predict(X_test_s)
    results.append({"model": name,
                    "MAE": round(mean_absolute_error(y_test, pred)),
                    "R2": round(r2_score(y_test, pred), 3)})
print(pd.DataFrame(results))
```

Linear regression should win clearly (MAE about 20,000 RWF), k-NN comes second and the baseline is far behind. That makes sense: the rents were built from a straight-line rule, which is exactly what linear regression can learn.

## Step 4 — Explain the winner

- Print the coefficients of a linear model trained on the **unscaled** features (they are easier to read in RWF).
- Which three features matter most? Explain them in plain words.
- Plot predicted vs real rent for the test homes.

## Step 5 — Use it

Estimate the rent for three example homes of your choice (one per district). Present the answers rounded to the nearest 5,000 RWF — false precision looks unprofessional.

## Step 6 — Report (one page)

1. **Goal** — one sentence.
2. **Data** — 600 simulated homes; the features used.
3. **Results** — a small table of the three models with MAE and R².
4. **What drives rent** — the top three features, in RWF.
5. **Limits** — at least two (for example: simulated data; no information on building quality, water or security; rents change every year).

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Preparation | All features numeric, split before scaling |
| Comparison | Baseline included, same test set for every model |
| Explanation | Coefficients explained in plain RWF terms |
| Honesty | Limits stated clearly |
| Communication | A manager understands it in five minutes |

**Takeaway:** A real project is a story: explore, prepare, compare against a baseline, explain the winner and state its limits.

## Try it yourself

Finish Steps 1–6 in one notebook. Then challenge yourself: remove the `district` columns and retrain. How much worse does the model get? What does that tell the property website?
""",
            "quiz": [
                ("Why compare every model with a baseline?",
                 ["To make the table longer", "To prove the model is better than a lazy guess", "Because scikit-learn requires it", "To slow down training"],
                 1, "A baseline turns a number into evidence."),
                ("Why must all models be tested on the same test set?",
                 ["To save memory", "So the comparison is fair", "It is the only way to train", "It is not important"],
                 1, "Different test sets would make the scores incomparable."),
                ("Why did linear regression win on this data?",
                 ["It is always the best model", "The rents were built from a straight-line rule", "It ignores the data", "It uses distances"],
                 1, "The model shape matches how the data was created."),
                ("Why train a separate linear model on unscaled features for the report?",
                 ["Its coefficients are in real units (RWF), easier to explain", "It is more accurate", "Scaled models cannot predict", "To leak data"],
                 0, "Unscaled coefficients read as 'RWF per m²'."),
                ("Which is an honest limitation of this project?",
                 ["The model is perfect", "The data is simulated and lacks building quality and security", "There are no limits", "R² is always 1"],
                 1, "Stating limits builds trust."),
                ("Why round rent estimates to the nearest 5,000 RWF?",
                 ["Avoid false precision", "The model cannot add", "To hide mistakes", "Python requires it"],
                 0, "The model's error is about 20,000 RWF, so exact figures mislead."),
            ],
        },
    ],
}

fill_data(WEEK1)
