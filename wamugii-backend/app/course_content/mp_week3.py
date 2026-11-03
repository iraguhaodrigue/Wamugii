"""Math & Python for AI -- Week 3: Linear Algebra, Statistics and Probability. Original WAMUGII content."""

WEEK3 = {
    "title": "Week 3 · Linear Algebra, Statistics and Probability",
    "lessons": [
        # ------------------------------------------------------------------ 13
        {
            "title": "Vectors: How AI Sees Data",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=fNk_zzaMoSs",
            "content": r"""
**Learning objective:** Explain what a vector is, add and scale vectors, compute length and the dot product, and use cosine similarity to measure how alike two things are.

## Everything becomes a list of numbers

AI cannot read a house, a student or a word directly. It turns each one into a **vector** — an ordered list of numbers:

- A house: `[size_m2, bedrooms, age_years]` → `[120, 3, 10]`
- A student: `[maths, english, science]` → `[78, 64, 85]`
- A word in a language model: hundreds of numbers called an **embedding**.

Each number is one **feature** (one dimension). A vector with 3 numbers lives in 3-dimensional space; an embedding may live in 1,000 dimensions. The maths is the same.

## Vectors in NumPy

```python
import numpy as np

aline = np.array([78, 64, 85])
eric = np.array([70, 80, 60])

print(aline + eric)        # add element by element
print(aline - eric)        # differences per subject
print(aline * 1.1)         # scale: everyone gets 10% more
print((aline + eric) / 2)  # the average student
```

Geometrically, a 2-D vector is an **arrow** from the origin. Adding vectors puts arrows end to end; scaling makes an arrow longer or shorter.

## Length (norm)

The **length** of a vector uses Pythagoras' theorem — square each number, add, take the square root:

```python
v = np.array([3, 4])
print(np.sqrt((v ** 2).sum()))   # 5.0
print(np.linalg.norm(v))         # the same, built in
```

The **distance** between two vectors is the length of their difference:

```python
print(np.linalg.norm(aline - eric))   # how different the two students are
```

k-nearest neighbours (AI Foundations, Lesson 9) uses exactly this distance to find "similar" examples.

## The dot product

Multiply matching elements and add them up:

```python
weights = np.array([0.5, 0.2, 0.3])   # importance of each subject
print(np.dot(aline, weights))          # 78×0.5 + 64×0.2 + 85×0.3 = 77.3
print(aline @ weights)                 # @ is the same thing
```

The dot product is the most important operation in AI. **A neuron is a dot product** of inputs and weights, plus a bias. A whole neural network is millions of dot products.

## Cosine similarity: same direction?

Two vectors can point in the **same direction** even if one is longer. Cosine similarity measures the angle between them:

> cosine similarity = (a · b) ÷ (|a| × |b|)

It is **1** for the same direction, **0** for unrelated (90°), and **−1** for opposite.

```python
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# features: [likes_football, likes_music, likes_maths]
u1 = np.array([5, 1, 4])
u2 = np.array([4, 0, 5])
u3 = np.array([0, 5, 1])
print(round(cosine(u1, u2), 2))   # high -> similar people
print(round(cosine(u1, u3), 2))   # low -> different interests
```

Recommendation systems and search engines use this to find similar users, products and documents. Language models compare word and sentence embeddings the same way.

## Key terms

- **Vector** — an ordered list of numbers; one number per feature.
- **Dimension** — the number of values in a vector.
- **Norm (length)** — the size of a vector: square root of the sum of squares.
- **Dot product** — multiply matching elements and add: `a @ b`.
- **Cosine similarity** — how closely two vectors point the same way (−1 to 1).
- **Embedding** — a learned vector that represents something like a word.

**Takeaway:** AI turns everything into vectors. Distance says how different two things are, the dot product powers every neuron, and cosine similarity says how alike two things are.

## Try it yourself

1. Make vectors for three students' marks in 4 subjects. Which two students are closest (smallest distance)?
2. Choose weights for the subjects that add to 1 and compute each student's weighted score with `@`.
3. Describe yourself and two friends with 4 interest scores (0–5). Use cosine similarity to find who is most like you.
""",
            "quiz": [
                ("What is a vector in AI?",
                 ["An arrow drawn on paper only", "An ordered list of numbers that describes something, one number per feature", "A type of virus", "A chart"],
                 1, "AI represents houses, students and words as lists of numbers."),
                ("What is the length of the vector [3, 4]?",
                 ["7", "5", "12", "1"],
                 1, "√(3² + 4²) = √25 = 5."),
                ("What is the dot product of [1, 2] and [3, 4]?",
                 ["[3, 8]", "11", "10", "7"],
                 1, "1×3 + 2×4 = 3 + 8 = 11."),
                ("Which AI building block is a dot product of inputs and weights (plus a bias)?",
                 ["A neuron", "A CSV file", "A histogram", "A for loop"],
                 0, "Each neuron computes a weighted sum — a dot product — then adds a bias."),
                ("Cosine similarity of two vectors pointing in exactly the same direction is…",
                 ["0", "1", "-1", "100"],
                 1, "Same direction gives cosine similarity 1."),
                ("What does the distance between two student vectors tell you?",
                 ["Their ages", "How different their scores are overall", "Their names", "Nothing useful"],
                 1, "A small distance means similar profiles; k-NN uses this idea."),
            ],
        },
        # ------------------------------------------------------------------ 14
        {
            "title": "Matrices: Many Calculations at Once",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=kYB8IZa5AuE",
            "content": r"""
**Learning objective:** Describe a matrix by its shape, multiply a matrix by a vector and by another matrix, use the transpose, and see how one matrix multiplication makes predictions for a whole dataset.

## A matrix is a table of numbers

A **matrix** is a grid of numbers with rows and columns. A dataset is a matrix: one **row per example**, one **column per feature**.

```python
import numpy as np

# columns: size_m2, bedrooms, age_years
X = np.array([
    [120, 3, 10],
    [80, 2, 25],
    [200, 4, 3],
    [95, 2, 15],
])
print(X.shape)   # (4, 3): 4 houses, 3 features
```

We usually write the shape as **rows × columns**: X is a 4 × 3 matrix.

## Matrix × vector = predictions for every row

Suppose a simple model prices a house (in thousands of RWF) as:

> price = 250 × size + 4,000 × bedrooms − 300 × age

Put the weights in a vector and multiply:

```python
w = np.array([250, 4000, -300])
prices = X @ w
print(prices)     # one prediction per house
```

Each row of X is dot-multiplied with w. **One line predicts the whole dataset.** This is exactly what a linear model — and each layer of a neural network — does.

## The shape rule

You can multiply A @ B only when **the number of columns of A equals the number of rows of B**:

> (4 × 3) @ (3,) → (4,)  ✓
> (4 × 3) @ (3 × 2) → (4 × 2)  ✓
> (4 × 3) @ (4 × 3) → error ✗

When you get a shape error in AI code, write the shapes down — the fix is almost always here.

## Matrix × matrix

Two different models (two sets of weights) at once:

```python
W = np.array([
    [250, 200],
    [4000, 6000],
    [-300, -100],
])           # 3 × 2: one column per model
print(X @ W)  # 4 × 2: every house priced by both models
```

A neural-network layer with 3 inputs and 2 neurons is exactly this: `outputs = X @ W + b`.

## The transpose

The **transpose** swaps rows and columns: a 4 × 3 matrix becomes 3 × 4.

```python
print(X.T.shape)    # (3, 4)
print(X.T @ X)      # a 3 × 3 matrix used in linear regression formulas
```

## Matrices transform space

3Blue1Brown's video shows the deeper idea: a 2 × 2 matrix **moves every point** of the plane — rotating, stretching or flipping it.

```python
rotate_90 = np.array([[0, -1],
                      [1,  0]])
stretch = np.array([[2, 0],
                    [0, 1]])
point = np.array([1, 2])
print(rotate_90 @ point)   # [-2  1]
print(stretch @ point)     # [2 2]
```

Neural networks learn matrices that transform data step by step until the answer becomes easy to read off.

## The identity matrix

The identity matrix `I` has 1s on the diagonal and 0s elsewhere. Multiplying by it changes nothing — like multiplying a number by 1.

```python
I = np.eye(3)
print(np.allclose(X @ I, X))   # True
```

## Key terms

- **Matrix** — a 2-D grid of numbers (rows × columns).
- **Shape** — rows × columns, e.g. 4 × 3.
- **Matrix multiplication** (`@`) — dot products of rows with columns.
- **Shape rule** — columns of A must equal rows of B.
- **Transpose** (`.T`) — swap rows and columns.
- **Identity matrix** — the matrix that leaves vectors unchanged.

**Takeaway:** A dataset is a matrix, a model's weights are a vector or matrix, and `X @ w` makes predictions for every example at once. Check shapes whenever multiplication fails.

## Try it yourself

1. Add a fifth house to X and predict its price with `X @ w`.
2. Change the weights so that age does not matter (weight 0). Which house changes most?
3. Predict the shape of `X @ W` when X is 100 × 5 and W is 5 × 8. Check it with `np.ones` arrays.
4. Use the stretch and rotation matrices one after the other on the point [1, 2]. Does the order matter?
""",
            "quiz": [
                ("A dataset has 500 examples and 6 features. What is its shape?",
                 ["6 × 500", "500 × 6", "3000 × 1", "500 × 500"],
                 1, "Rows are examples and columns are features: 500 × 6."),
                ("What does `X @ w` compute for a data matrix X and weight vector w?",
                 ["The sum of all numbers", "A prediction (weighted sum) for every row at once", "The transpose", "The average row"],
                 1, "Each row is dot-multiplied with the weights — one prediction per example."),
                ("Can you multiply a (4 × 3) matrix by a (3 × 2) matrix?",
                 ["Yes, the result is 4 × 2", "No", "Yes, the result is 3 × 3", "Yes, the result is 4 × 3"],
                 0, "Inner sizes match (3 and 3); the result takes the outer sizes: 4 × 2."),
                ("What does the transpose do?",
                 ["Deletes rows", "Swaps rows and columns", "Doubles every number", "Sorts the matrix"],
                 1, "A 4 × 3 matrix becomes 3 × 4."),
                ("What is special about the identity matrix?",
                 ["It is all zeros", "Multiplying by it leaves a vector unchanged", "It rotates by 90°", "It cannot be multiplied"],
                 1, "The identity matrix acts like the number 1."),
                ("What does one layer of a neural network compute?",
                 ["outputs = X @ W + b (then an activation)", "Only an average", "A pie chart", "A sorted list"],
                 0, "A layer is a matrix multiplication plus a bias, followed by an activation function."),
            ],
        },
        # ------------------------------------------------------------------ 15
        {
            "title": "Describing Data: Averages and Spread",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=kn83BA7cRNM",
            "content": r"""
**Learning objective:** Calculate and interpret the mean, median, mode, range, variance, standard deviation and percentiles, and choose the right summary when data has outliers.

## Two questions about any column of numbers

1. **Where is the middle?** (centre)
2. **How spread out are the values?** (spread)

## The centre: mean, median, mode

```python
import numpy as np
import pandas as pd

# monthly income (RWF) of 9 workers in a small company
income = np.array([180000, 200000, 210000, 220000, 230000,
                   240000, 250000, 260000, 2500000])
print(np.mean(income))     # about 476,667
print(np.median(income))   # 230,000
```

- **Mean** — add all values and divide by how many. Sensitive to extreme values.
- **Median** — the middle value after sorting. Not affected by one extreme value.
- **Mode** — the most common value. Useful for categories (most common product, most common shoe size).

The manager's 2,500,000 RWF pulls the mean far above what a typical worker earns. **When there are outliers, the median describes the "typical" value better.** That is why reports on household income usually quote the median.

## The spread: range, variance, standard deviation

Two classes can have the same average mark but very different spreads:

```python
class_a = np.array([60, 62, 65, 65, 68, 70])
class_b = np.array([30, 45, 65, 70, 85, 95])
for name, marks in [("A", class_a), ("B", class_b)]:
    print(name, marks.mean().round(1), marks.max() - marks.min(), marks.std(ddof=1).round(1))
```

- **Range** — max − min. Simple, but depends on just two values.
- **Variance** — the average of squared distances from the mean.
- **Standard deviation (SD)** — the square root of the variance, back in the original units. Roughly: *"how far a typical value is from the mean."*

`ddof=1` gives the **sample** standard deviation (divide by n − 1), which is what Pandas uses by default. Use it when your data is a sample from a bigger population.

## Percentiles and the five-number summary

The **p-th percentile** is the value below which p% of the data falls. The 25th, 50th and 75th percentiles are the **quartiles**.

```python
marks = pd.Series([45, 52, 58, 61, 64, 66, 70, 73, 78, 85, 92])
print(marks.describe())
q1, q3 = marks.quantile([0.25, 0.75])
print("IQR:", q3 - q1)
```

The **interquartile range (IQR)** = Q3 − Q1 is the spread of the middle half. A common rule flags values below Q1 − 1.5 × IQR or above Q3 + 1.5 × IQR as possible **outliers**.

## Why AI needs these

- **Data cleaning:** spotting outliers and impossible values.
- **Feature scaling:** many models work better when features are rescaled using mean and SD (**standardisation**, next lesson's z-scores).
- **Evaluation:** a model's average error is a mean; its consistency is a spread.
- **Honest reporting:** "average" without spread can mislead.

## Key terms

- **Mean** — the arithmetic average.
- **Median** — the middle value of sorted data.
- **Mode** — the most frequent value.
- **Standard deviation** — the typical distance of values from the mean.
- **Percentile / quartile** — value below which a given % of data lies.
- **IQR** — Q3 − Q1, the spread of the middle 50%.
- **Outlier** — a value far from the rest.

**Takeaway:** Always report a centre *and* a spread. Use the median when outliers are present, and use SD or IQR to show how varied the data is.

## Try it yourself

1. Use the `income` array. Remove the manager's salary — how much do the mean and median change? Explain why.
2. For `class_a` and `class_b`, write one sentence each describing the class using mean and SD.
3. Use the IQR rule to check whether 2,500,000 RWF is an outlier in `income`.
""",
            "quiz": [
                ("Which measure of centre is least affected by one very large value?",
                 ["Mean", "Median", "Range", "Variance"],
                 1, "The median depends on the middle value only, so extreme values barely move it."),
                ("What is the median of 3, 9, 4, 1, 7?",
                 ["4", "7", "4.8", "9"],
                 0, "Sorted: 1, 3, 4, 7, 9. The middle value is 4."),
                ("What does the standard deviation describe?",
                 ["The most common value", "How far values typically are from the mean", "The largest value", "The number of values"],
                 1, "SD measures spread in the same units as the data."),
                ("Two classes have the same mean mark but class B has a much larger SD. What does that mean?",
                 ["Class B's marks are more spread out", "Class B did better", "Class B has more students", "Nothing"],
                 0, "A larger SD means marks vary more around the same average."),
                ("What is the IQR?",
                 ["Max − min", "Q3 − Q1, the spread of the middle half", "The mean of quartiles", "The median"],
                 1, "The interquartile range covers the middle 50% of values."),
                ("Why should a report give a spread as well as an average?",
                 ["To fill space", "Because an average alone can hide how varied the data is", "Spreads are always zero", "Averages are always wrong"],
                 1, "Two very different groups can share the same average."),
            ],
        },
        # ------------------------------------------------------------------ 16
        {
            "title": "Probability: Measuring Uncertainty",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=OyddY7DlV58",
            "content": r"""
**Learning objective:** Calculate basic probabilities, use the complement, "and" and "or" rules, understand independence and conditional probability, and check answers by simulation.

## AI lives with uncertainty

A spam filter does not *know* an email is spam; it says *"97% likely"*. A weather model says *"70% chance of rain in Musanze tomorrow"*. **Probability** is the language AI uses to express how sure it is.

## The basics

Probability is a number from **0** (impossible) to **1** (certain). For equally likely outcomes:

> P(event) = number of favourable outcomes ÷ total number of outcomes

- Rolling a 6 with one die: P = 1/6 ≈ 0.167.
- Picking a girl from a class of 18 girls and 22 boys: P = 18/40 = 0.45.

## Three rules

**1. Complement — "not":** P(not A) = 1 − P(A).
If P(rain) = 0.3, then P(no rain) = 0.7.

**2. "And" for independent events:** P(A and B) = P(A) × P(B).
Two dice both show 6: 1/6 × 1/6 = 1/36. Events are **independent** when one does not change the chance of the other.

**3. "Or":** P(A or B) = P(A) + P(B) − P(A and B).
We subtract the overlap so it is not counted twice. If A and B cannot happen together, the overlap is 0.

## Conditional probability: "given that"

P(A | B) means *"the probability of A, given that B happened"*:

> P(A | B) = P(A and B) ÷ P(B)

Example — 1,000 mobile-money transactions:

| | Flagged by system | Not flagged | Total |
|---|---|---|---|
| Fraud | 18 | 2 | 20 |
| Normal | 40 | 940 | 980 |
| Total | 58 | 942 | 1,000 |

- P(fraud) = 20/1000 = 0.02
- P(fraud | flagged) = 18/58 ≈ 0.31
- P(flagged | fraud) = 18/20 = 0.90

Notice: **P(fraud | flagged) is not the same as P(flagged | fraud).** Mixing them up is one of the most common mistakes in data work — and in news reports. You met these numbers before as **precision** (0.31) and **recall** (0.90).

## Check by simulation

When maths feels tricky, simulate thousands of random trials:

```python
import numpy as np
rng = np.random.default_rng(0)

die1 = rng.integers(1, 7, 100000)
die2 = rng.integers(1, 7, 100000)
print(((die1 == 6) & (die2 == 6)).mean())   # close to 1/36 = 0.0278
print(((die1 + die2) == 7).mean())          # close to 6/36 = 0.1667
```

The share of trials where the event happens gets closer to the true probability as the number of trials grows — the **law of large numbers**.

## Expected value

The **expected value** is the long-run average outcome:

> E = Σ (value × probability)

A raffle ticket costs 1,000 RWF. There is a 1 in 500 chance to win 200,000 RWF. Expected winnings = 200,000 × 1/500 = 400 RWF — less than the 1,000 RWF price, so on average you lose 600 RWF per ticket.

## Key terms

- **Probability** — a number from 0 to 1 measuring how likely an event is.
- **Complement** — the event "not A": 1 − P(A).
- **Independent events** — one does not affect the other.
- **Conditional probability** — P(A | B), the chance of A given B.
- **Law of large numbers** — with many trials, the observed share approaches the true probability.
- **Expected value** — the long-run average result.

**Takeaway:** Probability measures uncertainty from 0 to 1. Learn the complement, "and" and "or" rules, never confuse P(A | B) with P(B | A), and check your answers with simulation.

## Try it yourself

1. A bag has 5 red, 3 blue and 2 green beads. What is P(red)? P(not green)?
2. Simulate drawing one bead 100,000 times with `rng.choice(["red"]*5 + ["blue"]*3 + ["green"]*2, 100000)` and compare with your answers.
3. From the fraud table, calculate P(flagged | normal). What does it mean for customers?
4. Compute the expected value of a game: pay 500 RWF, roll a die, win 2,000 RWF on a 6. Should you play?
""",
            "quiz": [
                ("If P(rain) = 0.3, what is P(no rain)?",
                 ["0.3", "0.7", "1.3", "0"],
                 1, "Complement rule: 1 − 0.3 = 0.7."),
                ("What is the probability that two fair dice both show 6?",
                 ["1/6", "2/6", "1/36", "1/12"],
                 2, "The dice are independent: 1/6 × 1/6 = 1/36."),
                ("In the fraud table, P(fraud | flagged) = 18/58. What does it mean?",
                 ["Of all flagged transactions, about 31% are really fraud", "Of all fraud, 31% is flagged", "31% of all transactions are fraud", "The system is 31% fast"],
                 0, "Given that a transaction was flagged, 18 of 58 were fraud."),
                ("Are P(A | B) and P(B | A) always equal?",
                 ["Yes", "No — mixing them up is a common mistake", "Only for dice", "Only when A is rare"],
                 1, "P(fraud | flagged) = 0.31 but P(flagged | fraud) = 0.90."),
                ("What does the law of large numbers say?",
                 ["Large numbers are always correct", "With many trials, the observed share gets close to the true probability", "Probabilities grow over time", "Random numbers stop being random"],
                 1, "Simulation works because of this law."),
                ("A ticket costs 1,000 RWF with a 1/500 chance to win 200,000 RWF. What is the expected winning?",
                 ["200,000 RWF", "1,000 RWF", "400 RWF", "0 RWF"],
                 2, "200,000 × 1/500 = 400 RWF, less than the ticket price."),
            ],
        },
        # ------------------------------------------------------------------ 17
        {
            "title": "Distributions and the Normal Curve",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=bPFNxD3Yg6U",
            "content": r"""
**Learning objective:** Recognise common shapes of data (normal, skewed, uniform, bimodal), use the 68–95–99.7 rule, compute z-scores, and standardise features for AI.

## The shape of data

A **distribution** describes how often each value occurs. Draw a histogram and you see its shape:

| Shape | What it looks like | Example |
|---|---|---|
| **Normal** (bell curve) | Symmetric, most values near the middle | Adult heights, measurement errors |
| **Right-skewed** | A long tail to the right | Incomes, house prices, sale sizes |
| **Left-skewed** | A long tail to the left | Marks on a very easy test |
| **Uniform** | All values equally common | A fair die |
| **Bimodal** | Two peaks | Arrival times at a bus stop with two rush hours |

In a right-skewed distribution, the **mean is larger than the median** — the long tail pulls the mean up.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(1)
normal = rng.normal(165, 8, 5000)            # heights in cm
skewed = rng.lognormal(12, 0.6, 5000)        # incomes, long right tail
uniform = rng.integers(1, 7, 5000)           # dice

fig, axes = plt.subplots(1, 3, figsize=(12, 3))
axes[0].hist(normal, bins=40); axes[0].set_title("Normal")
axes[1].hist(skewed, bins=40); axes[1].set_title("Right-skewed")
axes[2].hist(uniform, bins=np.arange(0.5, 7.5, 1)); axes[2].set_title("Uniform")
plt.tight_layout()
plt.show()
print(np.mean(skewed) > np.median(skewed))   # True
```

## The normal distribution

The normal (Gaussian) distribution is described by just two numbers: the **mean (μ)** and the **standard deviation (σ)**. It appears everywhere because many small random effects added together produce a bell curve.

**The 68–95–99.7 rule:** in a normal distribution,
- about **68%** of values are within 1 SD of the mean,
- about **95%** within 2 SD,
- about **99.7%** within 3 SD.

If adult heights have mean 165 cm and SD 8 cm, about 95% of adults are between 149 and 181 cm.

```python
heights = rng.normal(165, 8, 100000)
within_2sd = ((heights > 165 - 16) & (heights < 165 + 16)).mean()
print(round(within_2sd, 3))   # about 0.954
```

## z-scores: how unusual is a value?

A **z-score** says how many standard deviations a value is from the mean:

> z = (value − mean) ÷ SD

A student scores 82 in a test with mean 70 and SD 6: z = (82 − 70) ÷ 6 = **2.0** — better than about 97.7% of the class (if marks are roughly normal). A z-score above 3 or below −3 is very unusual and worth checking.

z-scores let you compare different scales: a 75 in a hard exam may be more impressive than an 85 in an easy one.

## Standardisation for AI

Features often have very different scales: size in m² (50–300), bedrooms (1–6), price in RWF (millions). Many models (k-NN, neural networks, gradient descent) work much better when every feature is on a similar scale. **Standardising** turns each feature into z-scores — mean 0, SD 1:

```python
X = np.array([[120, 3], [80, 2], [200, 4], [95, 2]], dtype=float)
X_std = (X - X.mean(axis=0)) / X.std(axis=0)
print(X_std.round(2))
print(X_std.mean(axis=0).round(2), X_std.std(axis=0).round(2))   # ~[0 0] [1 1]
```

You will use this in Week 4 to make gradient descent work well.

## Key terms

- **Distribution** — how often each value occurs.
- **Normal distribution** — the symmetric bell curve, described by μ and σ.
- **Skewed** — having a long tail on one side.
- **68–95–99.7 rule** — shares of a normal distribution within 1, 2 and 3 SDs.
- **z-score** — (value − mean) ÷ SD.
- **Standardisation** — rescaling features to mean 0 and SD 1.

**Takeaway:** Always look at the shape of your data. Use the 68–95–99.7 rule for bell-shaped data, z-scores to measure how unusual a value is, and standardisation to put features on the same scale.

## Try it yourself

1. Simulate 10,000 test marks with mean 60 and SD 12. What share are above 84? Compare with the 68–95–99.7 rule.
2. A sale of 45,000 RWF happens in a shop where sales have mean 12,000 and SD 8,000. Compute the z-score. Is it unusual?
3. Make a histogram of the right-skewed incomes and mark the mean and median with `plt.axvline`. Which is bigger?
""",
            "quiz": [
                ("Incomes usually have a long tail to the right. In such data, how do mean and median compare?",
                 ["Mean < median", "Mean > median", "They are always equal", "Median is always zero"],
                 1, "The few very high values pull the mean above the median."),
                ("In a normal distribution, about what share of values lies within 2 SD of the mean?",
                 ["68%", "95%", "50%", "99.7%"],
                 1, "The 68–95–99.7 rule: about 95% within 2 SD."),
                ("Mean 70, SD 6. What is the z-score of 82?",
                 ["12", "2", "1.17", "-2"],
                 1, "(82 − 70) ÷ 6 = 2."),
                ("What does standardising a feature do?",
                 ["Deletes outliers", "Rescales it to mean 0 and SD 1", "Sorts it", "Turns it into text"],
                 0, "Subtract the mean and divide by the SD."),
                ("Which two numbers fully describe a normal distribution?",
                 ["Min and max", "Mean and standard deviation", "Median and mode", "Count and sum"],
                 1, "μ and σ define the bell curve."),
                ("Why standardise features before training many models?",
                 ["To make the data secret", "So features with large numbers do not dominate and training works better", "Models cannot read decimals", "It is never useful"],
                 1, "Similar scales help distance-based models and gradient descent."),
            ],
        },
        # ------------------------------------------------------------------ 18
        {
            "title": "Week 3 Project: Statistics of a Class",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=R4yfNi_8Kqw",
            "content": r"""
**Learning objective:** Apply vectors, descriptive statistics, distributions and probability to a realistic dataset, and explain the results in plain language.

## The dataset

A school wants to understand the results of 120 Senior 6 students in three subjects. The data is **simulated** for practice. Run this cell:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rng = np.random.default_rng(2026)
n = 120
ability = rng.normal(0, 1, n)
results = pd.DataFrame({
    "maths": (62 + 12 * ability + rng.normal(0, 8, n)).clip(0, 100).round(),
    "physics": (58 + 11 * ability + rng.normal(0, 9, n)).clip(0, 100).round(),
    "english": (66 + 4 * ability + rng.normal(0, 10, n)).clip(0, 100).round(),
    "school": rng.choice(["Day", "Boarding"], size=n, p=[0.6, 0.4]),
})
results["average"] = results[["maths", "physics", "english"]].mean(axis=1).round(1)
print(results.head())
```

## Part 1 — Describe (Lesson 15)

For each subject, report the mean, median, SD and IQR. Which subject is hardest? Which has the most varied results? Write two sentences.

## Part 2 — Shape (Lesson 17)

Draw a histogram for each subject on one figure. Do they look roughly normal? Mark the mean on each with `axvline`.

## Part 3 — z-scores (Lesson 17)

Add a column with each student's maths z-score. List the students with |z| > 2. Are any marks suspicious enough to double-check?

## Part 4 — Probability (Lesson 16)

Using the data as your "population":
1. What is P(average ≥ 70)?
2. What is P(maths ≥ 70 | boarding) and P(maths ≥ 70 | day)? Is there a difference?
3. What is P(maths ≥ 70 and english ≥ 70)? Compare it with P(maths ≥ 70) × P(english ≥ 70). Are the two subjects independent?

## Part 5 — Vectors (Lesson 13)

Treat each student as a vector `[maths, physics, english]`.
1. Find the two students who are most similar (smallest distance). Hint: loop over pairs, or use the code below.
2. Which student is furthest from the class average vector?

```python
from itertools import combinations
X = results[["maths", "physics", "english"]].to_numpy()
best = min(combinations(range(n), 2), key=lambda p: np.linalg.norm(X[p[0]] - X[p[1]]))
print(best, X[best[0]], X[best[1]])
```

## Part 6 — Report

Write a one-page note for the head teacher:
- three findings with numbers,
- one chart,
- one honest limitation (for example: the data shows a link between boarding and maths marks, but not *why*).

**Takeaway:** Statistics turn 360 marks into a few clear, honest sentences. Centre, spread, shape, probability and similarity are the tools you will use in every AI project.

## Try it yourself

Complete Parts 1–6 in a Colab notebook. Swap reports with a classmate and check one calculation from their work.
""",
            "quiz": [
                ("Which statistic tells you which subject had the most varied results?",
                 ["The mean", "The standard deviation (or IQR)", "The number of students", "The mode of school"],
                 1, "Spread measures like SD and IQR show variation."),
                ("A student's maths z-score is 2.4. What does it mean?",
                 ["The mark is 2.4", "The mark is 2.4 standard deviations above the mean — unusually high", "The mark is below average", "The data is wrong"],
                 1, "z measures distance from the mean in SDs."),
                ("If P(maths ≥ 70 and english ≥ 70) is much larger than P(maths ≥ 70) × P(english ≥ 70), what does that suggest?",
                 ["The subjects are independent", "Good results in one subject go with good results in the other (not independent)", "The data is empty", "Probability does not apply"],
                 1, "For independent events the product rule holds; a big difference shows they are related."),
                ("How do you measure how similar two students are across 3 subjects?",
                 ["Compare their names", "Compute the distance between their score vectors", "Add their marks", "Count their subjects"],
                 1, "A small distance between vectors means similar profiles."),
                ("Which is an honest limitation to mention?",
                 ["The results prove boarding causes better marks", "The data shows a link, but not the reason for it", "Statistics are always perfect", "There are no limitations"],
                 1, "Correlation in data does not prove cause."),
                ("Which chart best shows whether a subject's marks look roughly normal?",
                 ["Histogram", "Pie chart", "Line chart over time", "Table"],
                 0, "A histogram shows the shape of the distribution."),
            ],
        },
    ],
}
