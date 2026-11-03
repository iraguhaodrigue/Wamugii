"""Math & Python for AI -- Week 4: Calculus and Your First Model. Original WAMUGII content."""

# The Kigali moto-trip data from the Week 2 project, cleaned. Simulated for practice.
TRIPS_DATA = r"""
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
n = 300
distance = rng.uniform(1, 15, n).round(1)
rain = rng.random(n) < 0.25
hour = rng.integers(6, 23, n)
fare = (400 + 230 * distance + np.where(rain, 300, 0) + rng.normal(0, 150, n)).round(-1)
minutes = (distance * 2.8 + rng.normal(0, 3, n) + np.where(rain, 4, 0)).clip(3).round()
trips = pd.DataFrame({"distance_km": distance, "minutes": minutes, "fare_rwf": fare,
                      "hour": hour, "raining": rain})
```
""".strip()

WEEK4 = {
    "title": "Week 4 · Calculus and Your First Model",
    "lessons": [
        # ------------------------------------------------------------------ 19
        {
            "title": "Bayes' Theorem: Updating Beliefs with Evidence",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=HZGCoVF3YvM",
            "content": r"""
**Learning objective:** Use Bayes' theorem to update a probability when new evidence arrives, avoid the base-rate mistake, and see how a spam filter uses the same idea.

## A surprising test result

A disease affects **1%** of people. A test catches **95%** of sick people, but also wrongly says "positive" for **10%** of healthy people. Your test is positive. How likely is it that you are sick?

Many people answer "95%". The real answer is **under 9%**. Bayes' theorem explains why.

## Count it with 10,000 people

| | Test positive | Test negative | Total |
|---|---|---|---|
| Sick (1%) | 95 | 5 | 100 |
| Healthy (99%) | 990 | 8,910 | 9,900 |
| Total | 1,085 | 8,915 | 10,000 |

Of the 1,085 people who test positive, only 95 are sick: 95 ÷ 1,085 ≈ **8.8%**. The disease is so rare that false alarms from the large healthy group outnumber the true cases.

## Bayes' theorem

> P(A | B) = P(B | A) × P(A) ÷ P(B)

In words: **new belief = how well the evidence fits × old belief ÷ how common the evidence is.**

- **Prior** P(sick) = 0.01 — what we believed before the test.
- **Likelihood** P(positive | sick) = 0.95 — how well the evidence fits.
- **Evidence** P(positive) = 0.01 × 0.95 + 0.99 × 0.10 = 0.1085.
- **Posterior** P(sick | positive) = 0.95 × 0.01 ÷ 0.1085 ≈ 0.088.

```python
def bayes(prior, p_evidence_if_true, p_evidence_if_false):
    evidence = prior * p_evidence_if_true + (1 - prior) * p_evidence_if_false
    return prior * p_evidence_if_true / evidence

print(round(bayes(0.01, 0.95, 0.10), 3))   # 0.088
```

## Check by simulation

```python
import numpy as np
rng = np.random.default_rng(3)
people = 1_000_000
sick = rng.random(people) < 0.01
positive = np.where(sick, rng.random(people) < 0.95, rng.random(people) < 0.10)
print(round(sick[positive].mean(), 3))   # close to 0.088
```

## Updating again

A second, independent positive test? Use the first posterior as the new prior:

```python
p1 = bayes(0.01, 0.95, 0.10)
p2 = bayes(p1, 0.95, 0.10)
print(round(p1, 3), round(p2, 3))   # 0.088 -> about 0.48
```

Each piece of evidence moves the belief. This is how a careful doctor — and a careful AI — reasons.

## The base-rate mistake

Ignoring how common something is (the **base rate**, or prior) leads to wrong conclusions: *"the fraud system flagged this customer, so they must be a fraudster"*. If fraud is rare, most flags may be false alarms. Always ask: **how common was this before the evidence?**

## A spam filter uses Bayes

A **Naive Bayes** spam filter learns, from labelled emails, how often words appear in spam and in normal mail:

- P(spam) = 0.4 (40% of emails are spam)
- P("winner" | spam) = 0.20, P("winner" | normal) = 0.01

```python
print(round(bayes(0.4, 0.20, 0.01), 3))   # 0.93: an email with "winner" is probably spam
```

It combines the evidence from many words to give each email a probability. Simple, fast and still used today.

## Key terms

- **Prior** — the probability before seeing new evidence.
- **Likelihood** — how probable the evidence is if the belief is true.
- **Posterior** — the updated probability after the evidence.
- **Base rate** — how common something is in the population.
- **Naive Bayes** — a classifier that applies Bayes' theorem to many features.

**Takeaway:** Bayes' theorem updates a belief with evidence: posterior ∝ likelihood × prior. When the prior is small, even a good test produces many false alarms — always consider the base rate.

## Try it yourself

1. Recalculate the disease example if the disease affects 10% of people. What changes, and why?
2. Improve the test: false positives drop from 10% to 1%. What is P(sick | positive) now?
3. The word "free" appears in 25% of spam and 5% of normal mail; P(spam) = 0.4. What is P(spam | "free")?
""",
            "quiz": [
                ("A disease affects 1% of people; the test catches 95% of sick people and has 10% false positives. P(sick | positive) is about…",
                 ["95%", "9%", "50%", "1%"],
                 1, "Only about 95 of 1,085 positives are truly sick: about 8.8%."),
                ("In Bayes' theorem, what is the prior?",
                 ["The probability after the evidence", "The probability before seeing the new evidence", "The test's accuracy", "The number of people"],
                 1, "The prior is the starting belief, such as how common a disease is."),
                ("What is the posterior?",
                 ["The updated probability after the evidence", "The base rate", "A chart", "The false positive rate"],
                 0, "Posterior = belief after taking the evidence into account."),
                ("Why do rare conditions produce many false alarms even with good tests?",
                 ["Tests are always bad", "The healthy group is so large that its small error rate creates many false positives", "Computers are slow", "It never happens"],
                 1, "This is the base-rate effect."),
                ("After one positive test, P(sick) became 0.088. For a second independent positive test, what do you use as the new prior?",
                 ["0.01", "0.088", "0.95", "0.10"],
                 1, "Yesterday's posterior becomes today's prior."),
                ("Which AI tool is built directly on Bayes' theorem?",
                 ["Naive Bayes spam filter", "Matplotlib", "A CSV file", "k-means"],
                 0, "Naive Bayes combines word probabilities with Bayes' theorem."),
            ],
        },
        # ------------------------------------------------------------------ 20
        {
            "title": "Correlation: Do Two Things Move Together?",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=GtV-VYdNt_g",
            "content": r"""
**Learning objective:** Measure how strongly two variables are related with covariance and the correlation coefficient, read a correlation matrix, and explain why correlation does not prove causation.

## From a scatter plot to one number

A scatter plot shows whether two numbers move together. The **correlation coefficient r** puts it into one number from −1 to 1:

| r | Meaning |
|---|---|
| close to **+1** | strong positive: when one goes up, the other goes up |
| close to **0** | no straight-line relationship |
| close to **−1** | strong negative: when one goes up, the other goes down |

Rough guide: |r| above 0.7 is strong, 0.3–0.7 moderate, below 0.3 weak.

Run the setup cell (Kigali moto trips, simulated):

{TRIPS}

## Covariance and correlation

**Covariance** measures whether two variables move together, but its size depends on the units. **Correlation** divides covariance by both standard deviations, so it is always between −1 and 1 and has no units.

```python
x = trips["distance_km"]
y = trips["fare_rwf"]
cov = ((x - x.mean()) * (y - y.mean())).sum() / (len(x) - 1)
r = cov / (x.std() * y.std())
print(round(cov, 1), round(r, 3))
print(round(np.corrcoef(x, y)[0, 1], 3))   # the same r, built in
```

Distance and fare have r close to 1: longer trips cost more, very consistently.

## A correlation matrix

```python
print(trips[["distance_km", "minutes", "fare_rwf", "hour"]].corr().round(2))
```

Each cell is the correlation between two columns. Analysts scan this table early in a project: features strongly correlated with the target are good candidates for a model. `hour` shows almost no correlation with fare — in this data, the time of day does not change the price.

## r squared

**r²** is the share of the variation in one variable that a straight line on the other explains. If r = 0.98, then r² ≈ 0.96: distance alone explains about 96% of the variation in fare. You will meet r² again when you evaluate regression models.

## Correlation only sees straight lines

```python
u = np.linspace(-3, 3, 100)
v = u ** 2
print(round(np.corrcoef(u, v)[0, 1], 3))   # about 0, yet v depends completely on u!
```

r near 0 does **not** mean "no relationship" — only "no straight-line relationship". Always look at the scatter plot too.

## Correlation is not causation

Ice-cream sales and drowning accidents are positively correlated. Ice cream does not cause drowning — **hot weather** causes both. A hidden third variable like this is called a **confounder**.

Other traps:
- **Reverse causation:** people who visit hospitals more are sicker — hospitals do not make them sick.
- **Coincidence:** with enough variables, some will correlate by chance.

To show cause, you need careful experiments (like randomised trials) or strong reasoning about the mechanism. AI models learn correlations — so they can be fooled by confounders too.

## Key terms

- **Covariance** — whether two variables move together (depends on units).
- **Correlation coefficient (r)** — strength and direction of a straight-line relationship, −1 to 1.
- **Correlation matrix** — a table of r for every pair of columns.
- **r²** — share of variation explained by a straight-line relationship.
- **Confounder** — a hidden variable that affects both variables.
- **Causation** — one thing actually producing the other.

**Takeaway:** Correlation measures how strongly two numbers move together in a straight line. Use it to find useful features — but always plot the data, and never treat correlation as proof of cause.

## Try it yourself

1. What is the correlation between `distance_km` and `minutes`? Is it stronger or weaker than distance and fare?
2. Calculate the correlation between `raining` (as 0/1: `trips["raining"].astype(int)`) and `fare_rwf`. What does it tell you?
3. Think of a correlation from daily life in Rwanda that is probably caused by a confounder. Name the confounder.
""",
            "quiz": [
                ("What does r = -0.9 mean?",
                 ["No relationship", "A strong negative straight-line relationship", "A weak positive relationship", "An error"],
                 1, "Close to −1 means when one goes up the other reliably goes down."),
                ("Why is correlation easier to compare than covariance?",
                 ["It is always positive", "It has no units and is always between −1 and 1", "It uses more data", "It is faster to type"],
                 1, "Dividing by both SDs removes the units."),
                ("y = x² for x from −3 to 3 gives r ≈ 0. What does that show?",
                 ["x and y are unrelated", "Correlation only measures straight-line relationships", "The code is wrong", "r is always 0 for squares"],
                 1, "y depends completely on x, but not in a straight line."),
                ("Ice-cream sales and drowning are correlated. What is the likely explanation?",
                 ["Ice cream causes drowning", "A confounder — hot weather increases both", "Drowning causes ice-cream sales", "It is impossible"],
                 1, "Hot weather is the hidden third variable."),
                ("If r = 0.98 between distance and fare, about how much of the variation in fare does distance explain?",
                 ["98%", "about 96%", "49%", "2%"],
                 1, "r² = 0.98² ≈ 0.96."),
                ("Why do analysts look at a correlation matrix early in a project?",
                 ["To prove causation", "To find features strongly related to the target", "To delete data", "To draw maps"],
                 1, "Strongly correlated features are good candidates for a model."),
            ],
        },
        # ------------------------------------------------------------------ 21
        {
            "title": "Derivatives: The Maths of Change",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=9vKqVkMQHKk",
            "content": r"""
**Learning objective:** Explain a derivative as a slope or rate of change, calculate simple derivatives by rule and by computer, and use derivatives to find where a function is lowest.

## Why AI needs calculus

Training a model means **making its error as small as possible**. To do that, the model must know: *if I change this weight a little, does the error go up or down — and how fast?* That question is answered by a **derivative**.

## Slope: change in output per change in input

For a straight line, the **slope** is constant:

> slope = change in y ÷ change in x

A moto fare of 400 + 230 × km has slope **230**: each extra kilometre adds 230 RWF.

For a curve, the slope is different at every point. The **derivative** f′(x) is the slope at one exact point — the slope of the **tangent line** that just touches the curve there.

## Rate of change in daily life

- Speed is the derivative of distance with respect to time.
- If a bus has travelled d(t) km after t hours, d′(2) is its speed at exactly 2 hours.
- Marginal cost in business is the derivative of total cost with respect to quantity.

## Calculating a derivative with a computer

Take a tiny step h and measure the slope:

> f′(x) ≈ (f(x + h) − f(x)) ÷ h

```python
def f(x):
    return x ** 2

def derivative(func, x, h=1e-6):
    return (func(x + h) - func(x)) / h

for x in [-2, 0, 1, 3]:
    print(x, round(derivative(f, x), 3))
```

The results are close to −4, 0, 2 and 6 — always **2x**.

## A few rules

| Function | Derivative | Example |
|---|---|---|
| c (a constant) | 0 | f(x) = 5 → 0 |
| c × x | c | f(x) = 230x → 230 |
| x² | 2x | at x = 3, slope 6 |
| xⁿ | n × xⁿ⁻¹ | x³ → 3x² |
| (x − a)² | 2(x − a) | used for squared error |
| sum of functions | sum of derivatives | x² + 3x → 2x + 3 |

You do not need to memorise many rules for AI — libraries such as PyTorch calculate derivatives automatically (**autodiff**). But you must understand what they mean.

## The lowest point has slope zero

At the bottom of a valley the ground is flat: **slope = 0**. To the left the slope is negative (going down), to the right positive (going up).

```python
import numpy as np
import matplotlib.pyplot as plt

def error(w):
    return (w - 3) ** 2 + 2

ws = np.linspace(-1, 7, 200)
plt.plot(ws, error(ws))
plt.axvline(3, linestyle="--")
plt.title("Error is lowest where the slope is 0 (w = 3)")
plt.xlabel("weight w")
plt.ylabel("error")
plt.show()

for w in [1, 3, 5]:
    print(w, round(derivative(error, w), 2))   # negative, ~0, positive
```

The derivative tells you **which way is downhill**: if the slope is positive, decrease w; if negative, increase w. That is the whole idea of gradient descent — next lesson.

## More than one input: partial derivatives and the gradient

A model has many weights. A **partial derivative** measures the slope when you change **one** weight and keep the others fixed. All the partial derivatives together form the **gradient** — an arrow pointing in the direction where the error rises fastest.

```python
def error2(w, b):
    return (w - 3) ** 2 + (b + 1) ** 2

w, b, h = 0.0, 0.0, 1e-6
dw = (error2(w + h, b) - error2(w, b)) / h
db = (error2(w, b + h) - error2(w, b)) / h
print(round(dw, 2), round(db, 2))   # about -6 and 2
```

## Key terms

- **Slope** — change in output per unit change in input.
- **Derivative** — the slope at one point; the instant rate of change.
- **Tangent line** — the line that touches a curve at one point with the same slope.
- **Partial derivative** — the slope with respect to one input, others fixed.
- **Gradient** — all partial derivatives together; points uphill.
- **Autodiff** — software that computes derivatives automatically.

**Takeaway:** A derivative is a slope: how fast the output changes when the input changes. The minimum of a function is where the slope is zero, and the sign of the slope tells you which way is downhill.

## Try it yourself

1. Use `derivative()` on f(x) = x³ at x = 2. Check with the rule 3x².
2. A shop's profit is p(q) = −2q² + 400q (q = units). Find the slope at q = 50, 100 and 150. Where is profit highest?
3. Plot `error2` for b = −1 as w changes. Where is the lowest point?
""",
            "quiz": [
                ("What does a derivative measure?",
                 ["The area under a curve", "The slope or instant rate of change at a point", "The average of the data", "The number of inputs"],
                 1, "The derivative is the slope of the tangent at that point."),
                ("What is the derivative of f(x) = x² at x = 3?",
                 ["3", "6", "9", "2"],
                 1, "The rule gives 2x, so 2 × 3 = 6."),
                ("A fare is 400 + 230 × km. What is the derivative with respect to km?",
                 ["400", "230", "630", "0"],
                 1, "The constant 400 has derivative 0; 230 × km has derivative 230."),
                ("At the lowest point of a smooth error curve, the derivative is…",
                 ["Very large", "Zero", "Negative", "Undefined always"],
                 1, "The curve is flat at the minimum."),
                ("At the current weight the derivative of the error is positive. To reduce the error you should…",
                 ["Increase the weight", "Decrease the weight", "Not change anything", "Double the error"],
                 1, "Positive slope means the error rises to the right, so move left."),
                ("What is the gradient?",
                 ["A colour fade", "All the partial derivatives together, pointing uphill", "The data matrix", "A chart title"],
                 1, "The gradient collects the slopes for every weight."),
            ],
        },
        # ------------------------------------------------------------------ 22
        {
            "title": "Gradient Descent: How Models Learn",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=IHZwWFHWa-w",
            "content": r"""
**Learning objective:** Write gradient descent from scratch, see the effect of the learning rate, and explain how the same loop trains real models.

## The idea in one sentence

**Start somewhere, find which way is downhill (the derivative), take a small step that way, and repeat.**

> new weight = old weight − learning rate × derivative

The minus sign moves us **against** the slope — downhill.

## Gradient descent on one weight

We want the w that makes error(w) = (w − 3)² + 2 smallest. We know the answer is 3; let the computer find it. The derivative is 2(w − 3).

```python
def error(w):
    return (w - 3) ** 2 + 2

def slope(w):
    return 2 * (w - 3)

w = 0.0
learning_rate = 0.1
for step in range(30):
    w = w - learning_rate * slope(w)
    if step % 5 == 0:
        print(step, round(w, 4), round(error(w), 4))
print("final w:", round(w, 4))
```

w moves from 0 towards 3, quickly at first (the slope is steep), then slowly (the slope gets flatter near the bottom).

## The learning rate matters

```python
def run(lr, steps=30):
    w = 0.0
    for _ in range(steps):
        w = w - lr * slope(w)
    return w

for lr in [0.01, 0.1, 0.5, 0.9, 1.1]:
    print(lr, round(run(lr), 4))
```

| Learning rate | What happens |
|---|---|
| Too small (0.01) | Very slow — still far from 3 after 30 steps |
| Good (0.1–0.5) | Reaches 3 |
| Large (0.9) | Jumps from side to side, but still settles |
| Too large (1.1) | **Diverges** — each step overshoots more and w flies away |

Choosing the learning rate is one of the most important decisions when training models.

## Watching it learn

```python
import matplotlib.pyplot as plt

w, lr, history = 0.0, 0.1, []
for _ in range(30):
    history.append(error(w))
    w -= lr * slope(w)

plt.plot(history, marker=".")
plt.title("Error falls as gradient descent runs")
plt.xlabel("step")
plt.ylabel("error")
plt.show()
```

This curve is called the **learning curve**. When you train any model, you watch a curve like this.

## Two weights at once

With several weights, compute the partial derivative for each and update all of them together:

```python
def error2(w, b):
    return (w - 3) ** 2 + (b + 1) ** 2

w, b, lr = 0.0, 0.0, 0.1
for _ in range(100):
    dw = 2 * (w - 3)
    db = 2 * (b + 1)
    w, b = w - lr * dw, b - lr * db
print(round(w, 3), round(b, 3))   # close to 3 and -1
```

A neural network does exactly this — for millions of weights at once, using backpropagation to compute every partial derivative.

## Variations you will hear about

- **Batch gradient descent** — use all the data for each step (what we will do next lesson).
- **Stochastic gradient descent (SGD)** — use one random example per step: noisy but fast.
- **Mini-batch** — use a small group (e.g. 32 examples) per step: the usual choice.
- **Adam** — a popular method that adapts the step size for each weight automatically.

## Local minima

Some error curves have several valleys. Gradient descent finds *a* valley — not always the deepest one. In practice, for large neural networks this is usually not a big problem, but it is worth knowing.

## Key terms

- **Gradient descent** — repeatedly step against the gradient to reduce error.
- **Learning rate** — the step size.
- **Step / iteration** — one update of the weights.
- **Divergence** — the error grows instead of shrinking (learning rate too large).
- **Learning curve** — error plotted against training steps.
- **Local minimum** — a valley that is not the lowest overall.

**Takeaway:** Gradient descent is a simple loop — compute the slope, step downhill, repeat. The learning rate controls the step size: too small is slow, too large diverges.

## Try it yourself

1. Change the starting point to w = 10. Does gradient descent still reach 3?
2. Find the largest learning rate that still converges for this error function. (Hint: try values between 0.9 and 1.1.)
3. Use gradient descent to find the minimum of f(x) = x² − 6x + 13. (Slope: 2x − 6.) Check your answer by hand.
""",
            "quiz": [
                ("What is the gradient descent update rule?",
                 ["w = w + learning rate × derivative", "w = w − learning rate × derivative", "w = derivative", "w = w × 2"],
                 1, "Subtracting moves against the slope, which is downhill."),
                ("What happens when the learning rate is far too large?",
                 ["Training is slow but safe", "The steps overshoot and the error can grow (divergence)", "Nothing changes", "The model becomes smaller"],
                 1, "Big steps jump past the minimum and can fly away."),
                ("What happens when the learning rate is very small?",
                 ["Divergence", "Very slow progress", "Instant convergence", "The data is deleted"],
                 1, "Tiny steps need many iterations."),
                ("With error(w) = (w − 3)², where does gradient descent end up?",
                 ["w = 0", "w = 3", "w = -3", "w = 9"],
                 1, "The minimum is at w = 3, where the slope is zero."),
                ("What is a learning curve?",
                 ["A chart of error against training steps", "A school timetable", "The shape of the data", "A derivative"],
                 0, "It shows the error falling as training proceeds."),
                ("What is mini-batch gradient descent?",
                 ["Using one tiny model", "Updating weights using a small group of examples each step", "Using no data", "Training only once"],
                 1, "Mini-batches balance speed and stability; it is the usual choice."),
            ],
        },
        # ------------------------------------------------------------------ 23
        {
            "title": "Linear Regression from Scratch",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=7ArmBVF2dCs",
            "content": r"""
**Learning objective:** Build a linear regression model with your own gradient descent, measure its error, compare it with NumPy's answer, and evaluate it on test data.

## The model

We predict a moto fare from the trip distance with a straight line:

> predicted fare = w × distance + b

- **w** (weight, the slope): extra RWF per kilometre.
- **b** (bias, the intercept): the starting fare.

Training means finding the w and b that make predictions as close as possible to the real fares.

Run the setup cell:

{TRIPS}

## Split into training and test data

```python
idx = rng.permutation(n)
train, test = trips.iloc[idx[:240]], trips.iloc[idx[240:]]
x_train, y_train = train["distance_km"].to_numpy(), train["fare_rwf"].to_numpy()
x_test, y_test = test["distance_km"].to_numpy(), test["fare_rwf"].to_numpy()
print(len(train), len(test))
```

We learn from 240 trips and keep 60 aside to test honestly (AI Foundations, Lesson 13).

## The loss: mean squared error

> MSE = average of (prediction − real value)²

```python
def predict(x, w, b):
    return w * x + b

def mse(y_true, y_pred):
    return np.mean((y_pred - y_true) ** 2)

print(round(mse(y_train, predict(x_train, 0, 0))))   # a terrible starting guess
```

## The gradients

Using the derivative rules from Lesson 21:

> ∂MSE/∂w = 2 × average((prediction − y) × x)
> ∂MSE/∂b = 2 × average(prediction − y)

## Gradient descent

```python
w, b = 0.0, 0.0
lr = 0.01
history = []
for epoch in range(5000):
    error = predict(x_train, w, b) - y_train
    dw = 2 * np.mean(error * x_train)
    db = 2 * np.mean(error)
    w -= lr * dw
    b -= lr * db
    history.append(mse(y_train, predict(x_train, w, b)))

print(f"w = {w:.1f} RWF per km, b = {b:.1f} RWF")
```

w should come out at about **225 RWF per km** and b at about **520 RWF** — close to the rule used to simulate the data (230 RWF per km and a 400 RWF start). b is a little higher because about a quarter of the trips include a 300 RWF rain charge that this model cannot see. The model discovered the pricing rule from the examples alone.

```python
plt.plot(history)
plt.yscale("log")
plt.title("Training loss (MSE)")
plt.xlabel("epoch")
plt.show()
```

## Check against NumPy

NumPy can solve a straight-line fit directly:

```python
w_np, b_np = np.polyfit(x_train, y_train, 1)
print(round(w_np, 1), round(b_np, 1))
```

Your gradient descent should agree to within about 1 RWF. For a straight line there is an exact formula; gradient descent matters because it also works for models with no exact formula — like neural networks.

## Evaluate on the test set

```python
pred_test = predict(x_test, w, b)
mae = np.mean(np.abs(pred_test - y_test))
r2 = 1 - np.sum((y_test - pred_test) ** 2) / np.sum((y_test - y_test.mean()) ** 2)
print(f"Test MAE: {mae:.0f} RWF   Test R²: {r2:.3f}")

plt.scatter(x_test, y_test, alpha=0.6, label="real fares (test)")
xs = np.linspace(1, 15, 50)
plt.plot(xs, predict(xs, w, b), color="red", label="model")
plt.xlabel("Distance (km)")
plt.ylabel("Fare (RWF)")
plt.legend()
plt.show()
```

- **MAE** — on average, the prediction is off by this many RWF.
- **R²** — the share of variation in fares the model explains (1 = perfect).

## What the model cannot see

Part of the remaining error comes from **rain**: rainy trips cost about 300 RWF more, and our model only knows distance. Adding more features (multiple linear regression) is your final project.

## Key terms

- **Linear regression** — predicting a number with a straight-line model w × x + b.
- **Weight / bias** — slope / intercept of the line.
- **MSE** — mean squared error, the loss we minimise.
- **Epoch** — one pass of gradient descent over the training data.
- **MAE** — mean absolute error, easy to explain in real units.
- **R²** — share of variation explained by the model.

**Takeaway:** You built a real machine-learning model from scratch: a prediction function, a loss, gradients and gradient descent. It learned the fare rule from data and was checked honestly on test data.

## Try it yourself

1. Change the learning rate to 0.03, then 0.001. What happens to training?
2. Predict the fare for a 7.5 km trip with your model.
3. Train a second model that predicts `minutes` from `distance_km`. How many minutes per kilometre does it learn?
4. Compute the test MAE separately for rainy and dry trips. Which is worse, and why?
""",
            "quiz": [
                ("In the model fare = w × distance + b, what does w mean?",
                 ["The starting fare", "Extra RWF per kilometre (the slope)", "The number of trips", "The error"],
                 1, "w is the slope: how much the fare grows per km."),
                ("What loss did we minimise?",
                 ["Mean squared error (MSE)", "The number of rows", "The median", "The correlation"],
                 0, "MSE averages the squared differences between predictions and real values."),
                ("Why keep a test set aside?",
                 ["To train faster", "To check the model honestly on data it has never seen", "To make MSE bigger", "Because NumPy needs it"],
                 1, "Test data shows how the model will work on new trips."),
                ("The test MAE is 160 RWF. What does that mean?",
                 ["Predictions are off by about 160 RWF on average", "The model is 160% accurate", "160 trips were wrong", "The fare is 160 RWF"],
                 0, "MAE is the average size of the error in real units."),
                ("Why use gradient descent if np.polyfit gives the answer directly?",
                 ["polyfit is wrong", "Gradient descent also works for models with no exact formula, like neural networks", "It is always faster", "It needs no data"],
                 1, "The same loop trains far more complex models."),
                ("Part of the remaining error comes from rain. How could the model improve?",
                 ["Delete rainy trips", "Add raining as a second feature (multiple regression)", "Use a bigger learning rate", "Use fewer trips"],
                 1, "Giving the model the missing information reduces its error."),
            ],
        },
        # ------------------------------------------------------------------ 24
        {
            "title": "Final Project: Predict Trip Fares and Certificate",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=nKW8Ndu7Mjw",
            "content": r"""
**Learning objective:** Combine Python, data handling, statistics, linear algebra and calculus to build, train and evaluate a multiple linear regression model — and earn your certificate.

## The goal

Improve last lesson's fare model by using **more than one feature**: distance **and** rain (and, if you like, the hour). You will write the whole workflow yourself in one Colab notebook, in the order a professional would. Re-watch the workflow video if you need a reminder of the stages.

## Part 1 — Data (Weeks 1–2)

Generate the moto-trip data with the Week 2 project cell (including the data problems), then clean it exactly as you did in that project and write a short cleaning log.

## Part 2 — Explore (Weeks 2–3)

- Describe `fare_rwf`: mean, median, SD.
- Correlation matrix of the number columns (convert `raining` with `.astype(int)`).
- A scatter plot of distance vs fare, coloured by rain.

## Part 3 — Prepare the matrix (Week 3)

Build a feature matrix X with one row per trip and these columns: `distance_km`, `raining` (0/1). Standardise each column (Lesson 17), and keep the means and SDs so you can apply the same scaling to new trips.

```python
features = ["distance_km", "raining"]
X = clean[features].astype(float).to_numpy()
y = clean["fare_rwf"].to_numpy()

rng = np.random.default_rng(1)
idx = rng.permutation(len(X))
cut = int(0.8 * len(X))
train_idx, test_idx = idx[:cut], idx[cut:]

mean, std = X[train_idx].mean(axis=0), X[train_idx].std(axis=0)
X_scaled = (X - mean) / std
X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
y_train, y_test = y[train_idx], y[test_idx]
```

Use only the **training** rows to compute the mean and SD — otherwise information from the test set leaks into training.

## Part 4 — Train with gradient descent (Week 4)

The model is now a matrix multiplication: **prediction = X @ w + b**.

```python
w = np.zeros(X_train.shape[1])
b = 0.0
lr = 0.1
for epoch in range(2000):
    error = X_train @ w + b - y_train
    grad_w = 2 * X_train.T @ error / len(y_train)
    grad_b = 2 * error.mean()
    w -= lr * grad_w
    b -= lr * grad_b
print(w.round(1), round(b, 1))
```

Notice `X_train.T @ error`: the transpose (Lesson 14) computes the gradient for every weight in one line.

Check your answer with NumPy's least-squares solver:

```python
A = np.column_stack([X_train, np.ones(len(X_train))])
print(np.linalg.lstsq(A, y_train, rcond=None)[0].round(1))
```

## Part 5 — Evaluate

1. Test MAE and R² for the new model.
2. Compare with the distance-only model from Lesson 23. Did adding rain help? By how much?
3. Convert the weights back to real units: divide each weight by its feature's SD. How many RWF per km? How many extra RWF when it rains?
4. Predict the fare for a 6 km trip in the rain. (Scale the new trip with the **training** mean and SD.)

## Part 6 — Report (one page)

- What the model predicts and how well (MAE in RWF, R²).
- What each feature adds to the fare, in plain words.
- One chart (predicted vs real fares on the test set, with a diagonal line).
- Two limitations — for example, the data is simulated, and real fares also depend on traffic and negotiation.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Data | Problems found and fixed, with a cleaning log |
| Exploration | Correct statistics, clear labelled charts |
| Model | Gradient descent matches NumPy's answer |
| Evaluation | Honest test-set results compared with a baseline |
| Communication | A manager understands the report in five minutes |

## Getting your certificate

When you have completed **every lesson** in the course, your **WAMUGII Certificate of Completion** unlocks on the course page, and you receive a congratulations email. Add it — and a link to your project notebook — to your CV and LinkedIn.

## What you can do now

You can write Python, clean and explore data, use the maths behind AI — vectors, matrices, statistics, probability and derivatives — and you have trained a machine-learning model from scratch. Next: **Machine Learning Fundamentals**, where you will use scikit-learn to build many kinds of models quickly and evaluate them like a professional.

**Takeaway:** A real model is the sum of everything in this course: clean data, good statistics, a matrix of features, a loss, gradients and honest evaluation.

## Try it yourself

Complete Parts 1–6 in one notebook. Then add the `hour` feature to the model. Does it help? Explain your result using the correlation matrix from Part 2.
""",
            "quiz": [
                ("In multiple linear regression with a feature matrix X, how are predictions computed?",
                 ["X + w", "X @ w + b", "X / w", "w only"],
                 1, "Each row's features are combined with the weights by matrix multiplication, plus the bias."),
                ("Why compute the scaling mean and SD from the training rows only?",
                 ["It is faster", "To stop information from the test set leaking into training", "The test set has no numbers", "It does not matter"],
                 1, "The test set must stay unseen to give an honest result."),
                ("What does `X_train.T @ error` compute in the training loop?",
                 ["The predictions", "The gradient part for every weight at once", "The test score", "The mean of X"],
                 1, "The transpose spreads each error back to the features, giving one gradient value per weight."),
                ("How do you check that your gradient descent is correct?",
                 ["Compare its weights with NumPy's least-squares solution", "Run it once", "Look at the colours", "You cannot check"],
                 0, "np.linalg.lstsq gives the exact answer for linear regression."),
                ("Adding the rain feature lowers the test MAE (for example, from 160 to 120 RWF). What does that show?",
                 ["Rain information helps the model predict fares better", "The model is broken", "MAE should go up", "Rain is not related to fares"],
                 0, "A lower error on unseen data means the new feature adds useful information."),
                ("Which is an honest limitation to include in the report?",
                 ["The model is perfect", "The data is simulated; real fares also depend on traffic and negotiation", "There are no limitations", "Regression always works"],
                 1, "Honest limits make a report trustworthy."),
            ],
        },
    ],
}

for _lesson in WEEK4["lessons"]:
    _lesson["content"] = _lesson["content"].replace("{TRIPS}", TRIPS_DATA)
