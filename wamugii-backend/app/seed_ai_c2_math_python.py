"""
WAMUGII AI Program — Course 2: "Math & Python for AI".
University-level, original WAMUGII content in simple English.
Run:  python -m app.seed_ai_c2_math_python
"""

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.models.course import CourseStatus
from app.schemas.course import CourseCreate, LessonCreate

COURSE_SLUG = "math-python-for-ai"

COURSE = CourseCreate(
    title="Math & Python for AI",
    slug=COURSE_SLUG,
    category="Artificial Intelligence",
    is_free=True,
    status=CourseStatus.PUBLISHED,
    display_order=3,
    description=(
        "Course 2 of the WAMUGII AI Program. The practical foundation every AI "
        "practitioner needs: Python for working with data (NumPy and Pandas), "
        "and the core mathematics that machine learning actually uses — linear "
        "algebra, probability, statistics, and the calculus idea behind "
        "learning. Taught in simple English with runnable code and exercises. "
        "By the end you can load, clean, analyse and visualise real data in "
        "Python and understand the maths under the models."
    ),
)

LESSONS = [
    {
        "title": "2.1 Python for AI — The Essentials",
        "content": """\
**Learning objective:** Use the core Python you need for AI — variables, data
types, collections, loops, and functions.

Python is the language of AI because it is readable and has powerful libraries.
You don't need to be an expert programmer — you need these essentials well.

## Variables and types

```python
name = "Rodrigue"      # string (text)
age = 25               # integer (whole number)
score = 87.5           # float (decimal)
passed = True          # boolean (True/False)
```

## Collections — storing many values

```python
marks = [80, 75, 90]                 # list: ordered, changeable
student = {"name": "Ana", "age": 22} # dict: key -> value pairs
```

- Use a **list** for a sequence of items.
- Use a **dict** when each value has a name (a key).

## Loops — doing something many times

```python
for mark in marks:
    print(mark)
```

## Functions — reusable blocks

```python
def average(numbers):
    return sum(numbers) / len(numbers)

print(average(marks))   # 81.666...
```

## Why this matters for AI

Every dataset you load becomes lists, dicts, and tables in Python; every model
you train is called through functions. These basics are the keyboard you'll type
all of AI on.

## Key terms

**Variable**, **String / Integer / Float / Boolean**, **List**, **Dict**,
**Loop**, **Function**.

## Practice

Write a function `pass_rate(marks, pass_mark)` that takes a list of marks and a
pass mark, and returns the percentage of students who passed. Test it on
`[80, 45, 90, 30, 70]` with a pass mark of 50.
""",
    },
    {
        "title": "2.2 NumPy — Fast Maths on Arrays",
        "content": """\
**Learning objective:** Use NumPy arrays to do fast mathematics on many numbers
at once — the backbone of all numerical AI.

## Why NumPy

A plain Python list is slow for maths on thousands of numbers. **NumPy** stores
numbers in a compact **array** and runs operations on the whole array at once
(this is called *vectorisation*). All of ML is built on it.

```python
import numpy as np

a = np.array([1, 2, 3, 4])
print(a * 2)        # [2 4 6 8]  -- multiplies every element
print(a + 10)       # [11 12 13 14]
print(a.mean())     # 2.5
```

## Arrays can have many dimensions

```python
matrix = np.array([[1, 2, 3],
                   [4, 5, 6]])
print(matrix.shape)   # (2, 3)  -> 2 rows, 3 columns
```

A dataset is usually a 2-D array: rows are examples, columns are features.

## Vectorised operations beat loops

```python
# Slow (loop) vs fast (vectorised)
prices = np.array([100, 200, 300])
with_vat = prices * 1.18     # one line, done on all at once
```

## Useful tools

```python
np.zeros((2,3))      # array of zeros
np.arange(0, 10, 2)  # [0 2 4 6 8]
a.sum(), a.max(), a.std()
```

## Key terms

**NumPy**, **Array**, **Vectorisation**, **Shape**, **Element-wise operation**.

## Practice

Create a NumPy array of 5 test scores. In one line each, compute the mean, the
highest score, and a new array where every score is boosted by 5 marks (capped
at 100 — hint: `np.minimum`).
""",
    },
    {
        "title": "2.3 Pandas — Working with Real Data",
        "content": """\
**Learning objective:** Load, explore, clean and select data using Pandas
DataFrames — the tool you'll use on almost every real dataset.

## The DataFrame

Pandas gives you the **DataFrame**: a table with named columns, like a smart
spreadsheet in code.

```python
import pandas as pd

df = pd.read_csv("students.csv")   # load a CSV file
df.head()        # first 5 rows
df.shape         # (rows, columns)
df.info()        # column names and types
df.describe()    # quick statistics
```

## Selecting data

```python
df["mark"]                 # one column
df[["name", "mark"]]       # several columns
df[df["mark"] >= 50]       # rows where mark >= 50 (filtering)
```

## Cleaning data (the real work)

```python
df.isnull().sum()          # count missing values per column
df["mark"].fillna(df["mark"].mean(), inplace=True)  # fill blanks
df.drop_duplicates(inplace=True)                    # remove duplicates
```

## Creating new columns

```python
df["passed"] = df["mark"] >= 50
df["grade"] = pd.cut(df["mark"], bins=[0,50,70,100],
                     labels=["Fail","Pass","Distinction"])
```

## Why this matters

In Course 1 you learned that data quality decides everything. Pandas is how you
actually inspect and fix data before any model sees it. Expect to spend most of
your time here — that is normal and correct.

## Key terms

**Pandas**, **DataFrame**, **read_csv**, **Filtering**, **Missing values**,
**describe()**.

## Practice

Imagine a CSV `sales.csv` with columns `product, price, quantity`. Write Pandas
code to: load it, add a `total = price * quantity` column, and show only the rows
where `total` is above 10,000.
""",
    },
    {
        "title": "2.4 Linear Algebra Essentials",
        "content": """\
**Learning objective:** Understand vectors, matrices, and the dot product — and
why machine learning is built on them.

## Why ML needs linear algebra

Every example in a dataset is a **vector** of numbers (its features). A whole
dataset is a **matrix**. Models combine these numbers using linear algebra. You
don't need deep proofs — you need the ideas.

## Vectors

A **vector** is just an ordered list of numbers:

```
student = [attendance, assignments, study_hours] = [90, 8, 12]
```

Geometrically, a vector is a point or a direction in space.

## Matrices

A **matrix** is a grid of numbers — rows and columns. A dataset of 100 students
with 3 features is a 100 × 3 matrix.

## The dot product — the key operation

The **dot product** multiplies two vectors element by element and adds the
results:

```
[90, 8, 12] · [0.5, 2, 1] = 90*0.5 + 8*2 + 12*1 = 45 + 16 + 12 = 73
```

This is **exactly** how a simple model makes a prediction: it multiplies each
feature by a **weight** and adds them up. Learning a model means **finding the
right weights**.

```python
import numpy as np
features = np.array([90, 8, 12])
weights  = np.array([0.5, 2, 1])
prediction = features.dot(weights)   # 73
```

## Key terms

**Vector**, **Matrix**, **Dot product**, **Weight**.

## Practice

A model predicts house price from `[size_m2, bedrooms, age_years]` using weights
`[500, 20000, -1000]`. Using a dot product (by hand or with NumPy), predict the
price of a house `[120, 3, 10]`. Explain in one line what the negative weight on
`age` means.
""",
    },
    {
        "title": "2.5 Probability Basics",
        "content": """\
**Learning objective:** Use basic probability and conditional probability — the
language AI uses to handle uncertainty.

## Why probability

AI rarely deals in certainties. A model doesn't say "this is spam" — it says
"this is spam with probability 0.93." Probability is how machines reason about
uncertainty.

## The basics

- A probability is a number from **0 (impossible)** to **1 (certain)**.
- `P(A)` means "the probability of event A."
- All outcomes together sum to 1. If `P(spam) = 0.3`, then `P(not spam) = 0.7`.

## Conditional probability

`P(A | B)` = "the probability of A, **given that** B happened."

*Example:* the chance an email is spam **given that** it contains the word
"free." Knowing B updates our belief about A.

## Bayes' idea (intuition)

Bayes' rule lets us **flip** a conditional: from "probability of the symptom
given the disease" to "probability of the disease given the symptom." This is the
engine behind many classifiers (including the "Naive Bayes" spam filter).

The practical lesson: **a result must be read together with how common the thing
is.** A test that is 99% accurate can still be wrong most of the time if the
disease is very rare — because there are far more healthy people to produce false
alarms.

## Key terms

**Probability**, **Event**, **Conditional probability** `P(A|B)`, **Bayes'
rule**, **Naive Bayes**.

## Practice

In a class, 20% of students fail. Of those who fail, 80% attended less than half
the classes. Of those who pass, 10% attended less than half. In words (no formula
needed), explain why "low attendance" raises the probability of failing — and why
it does not *guarantee* it.
""",
    },
    {
        "title": "2.6 Statistics for AI",
        "content": """\
**Learning objective:** Summarise and understand data using mean, spread,
distributions, and correlation.

## Describing data

- **Mean** — the average.
- **Median** — the middle value (better than mean when there are extreme values).
- **Variance / Standard deviation (std)** — how **spread out** the data is. Small
  std = values close to the mean; large std = widely spread.

```python
import numpy as np
marks = np.array([80, 75, 90, 30, 85])
marks.mean()   # average
np.median(marks)
marks.std()    # spread
```

## Distributions

A **distribution** shows how values are spread. The famous **normal (bell)
curve** appears everywhere — most values near the middle, few at the extremes.
Knowing the shape of your data guides how you model it.

## Correlation

**Correlation** measures how two things move together, from **-1 to +1**:

- **+1** — move together (more study hours → higher marks).
- **0** — no relationship.
- **-1** — move oppositely (more absences → lower marks).

```python
df[["study_hours", "mark"]].corr()
```

**Vital warning:** *correlation is not causation.* Two things moving together
does not mean one causes the other — a third hidden factor may drive both.

## Why this matters

Before modelling, statistics tells you what your data looks like, which features
relate to your target, and whether anything is strange. Skipping this is how
people build models on data they don't understand.

## Key terms

**Mean**, **Median**, **Variance**, **Standard deviation**, **Distribution**,
**Normal curve**, **Correlation**, **Correlation ≠ causation**.

## Practice

Two datasets both have a mean of 50: Set A = [49, 50, 51], Set B = [10, 50, 90].
Without calculating, say which has the larger standard deviation and why. Then
give one real example where two things are correlated but neither causes the
other.
""",
    },
    {
        "title": "2.7 Calculus Intuition for Machine Learning",
        "content": """\
**Learning objective:** Understand slope, derivative, and gradient — the idea
that lets models *learn*. (No heavy maths; intuition and purpose.)

## Learning = reducing error, step by step

A model starts with random weights and makes bad predictions. We measure how
wrong it is with a **loss** (error) value. **Learning means changing the weights
to make the loss smaller.** Calculus tells us *which direction* to change them.

## Slope and derivative

The **derivative** of a function is its **slope** — how fast the output changes
as you change the input.

- Slope **positive** → going right makes the value go **up**.
- Slope **negative** → going right makes the value go **down**.
- Slope **zero** → you are at a flat point (a minimum or maximum).

## Gradient = slope in many directions

A model has many weights, so the loss depends on many inputs. The **gradient** is
just the slope in every direction at once — it points **uphill** (toward higher
loss).

## Gradient descent — the core learning algorithm

To reduce the loss, we step in the **opposite** direction of the gradient — we go
**downhill**:

> new weight = old weight − (learning rate × gradient)

Repeat this many times and the loss slides down to a low point — the model has
**learned**. The **learning rate** controls the step size: too big and it
overshoots; too small and it learns slowly.

Picture a ball rolling down into a valley. The gradient is the slope under the
ball; gradient descent is the rolling. **This one idea trains almost every modern
AI model**, including neural networks (Course 4).

## Key terms

**Loss**, **Derivative / slope**, **Gradient**, **Gradient descent**, **Learning
rate**, **Minimum**.

## Practice

In your own words (3–4 sentences), explain to a friend who knows no maths how a
model "learns" using gradient descent. Use the ball-in-a-valley picture.
""",
    },
    {
        "title": "2.8 Visualising Data",
        "content": """\
**Learning objective:** Use simple charts to understand data and communicate
results, using matplotlib.

## Why visualise

Numbers hide patterns; pictures reveal them. A chart can show in one second what a
table of numbers hides — a trend, an outlier, a relationship. Good AI work always
*looks* at the data first.

## The main chart types (and when to use them)

- **Histogram** — the distribution of one number (e.g. spread of marks).
- **Line chart** — a value changing over time.
- **Bar chart** — comparing categories.
- **Scatter plot** — the relationship between two numbers.

## Basic matplotlib

```python
import matplotlib.pyplot as plt

plt.hist(df["mark"], bins=10)         # distribution of marks
plt.xlabel("Mark"); plt.ylabel("Students")
plt.title("Mark distribution")
plt.show()

plt.scatter(df["study_hours"], df["mark"])   # relationship
plt.xlabel("Study hours"); plt.ylabel("Mark")
plt.show()
```

## What to look for

- **Outliers** — points far from the rest (errors, or something important).
- **Shape** — is it a bell curve, skewed, or two groups?
- **Relationships** — does the scatter plot slope up, down, or scatter randomly?

## Key terms

**Histogram**, **Line chart**, **Bar chart**, **Scatter plot**, **Outlier**,
**matplotlib**.

## Practice

For a dataset of students with `study_hours` and `mark`, say which chart you'd use
to answer each question: (a) "Are marks mostly high or low?" (b) "Do more study
hours go with higher marks?" (c) "How did average marks change each year?"
""",
    },
    {
        "title": "2.9 Project — Explore a Real Dataset (Assessment)",
        "content": """\
**This is your Course 2 assessment.** You will apply everything — Python, Pandas,
statistics, and visualisation — to a real dataset.

## The task

Find a small real dataset (a CSV from your work, your studies, or a free source
like Kaggle or data.gov). Then write a short Python analysis and a one-page
report of what you found.

## Required steps

1. **Load** the data with Pandas and show its shape and columns.
2. **Clean** it: find missing values and handle them; remove duplicates; fix any
   obvious errors. Write down what you changed.
3. **Describe** it: for the important numeric columns, report the mean, median
   and standard deviation. Say what the spread tells you.
4. **Relate** it: pick two columns you think are connected and compute their
   **correlation**. State whether it's strong, weak, positive or negative — and
   remember correlation is not causation.
5. **Visualise** it: make at least **two charts** (e.g. a histogram and a scatter
   plot) and explain what each one shows.
6. **Conclude**: write 3–5 sentences on the most interesting things you learned
   about the data.

## What good work looks like

- Your cleaning steps are explained and justified.
- Your statistics are correct and you *interpret* them, not just print them.
- Your charts are the right type for the question and are labelled.
- Your conclusion is honest and based on what the data actually shows.

## Submit

Keep your code (a `.py` file or notebook) and your one-page report together. This
project proves you can take raw data and turn it into understanding — the daily
reality of AI work, and the entry ticket to Course 3, where we start building
models on exactly this kind of prepared data.
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
