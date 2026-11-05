"""Deep Learning & Neural Networks -- Week 1: Neural Networks from Scratch. Original WAMUGII content."""

MOONS = r"""
```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

X, y = make_moons(n_samples=1000, noise=0.2, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
print(X_train.shape, X_test.shape)
plt.scatter(X[:, 0], X[:, 1], c=y, s=8)
plt.title("Two moons: a pattern a straight line cannot separate")
plt.show()
```
""".strip()

WEEK1 = {
    "title": "Week 1 · Neural Networks from Scratch",
    "lessons": [
        # ------------------------------------------------------------------ 1
        {
            "title": "What Deep Learning Is — and Your First Neuron",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=aircAruvnKk",
            "content": r"""
**Learning objective:** Explain what deep learning is and where it is used, describe an artificial neuron in plain words, and compute one — and a whole layer of them — with NumPy.

## From machine learning to deep learning

In **Machine Learning Fundamentals** you gave models features that people had prepared: income, loan size, size in m². That works well for tables. But what are the "features" of a photo of a cassava leaf, a voice saying "Muraho", or a chest X-ray? Nobody can write them down by hand.

**Deep learning** solves this. A **neural network** with many layers learns the features **by itself**, straight from raw pixels, sound waves or text. The first layers learn simple patterns (edges, short sounds), the next layers combine them into bigger ones (leaf spots, syllables), and the last layers make the decision.

| | Classic machine learning | Deep learning |
|---|---|---|
| Features | Designed by people | Learned from raw data |
| Best for | Tables of numbers | Images, sound, text, video |
| Data needed | Hundreds to thousands of rows | Usually thousands to millions of examples |
| Computing | A laptop | Often a GPU (Colab gives one free) |

## Where deep learning is used

- **Health:** reading X-rays and eye scans, digital stethoscopes that recognise heart sounds.
- **Farming:** phone apps that recognise crop diseases from a photo of a leaf.
- **Language:** speech recognition, translation and chatbots — including for Kinyarwanda, Swahili and other African languages.
- **Everyday tools:** face unlock, photo search, keyboard suggestions, fraud detection.

Large language models such as ChatGPT and Claude are deep neural networks too — you will meet their key idea, **attention**, in Week 4.

## The artificial neuron

A neuron is a tiny calculator:

1. It takes some **inputs** (x₁, x₂, …).
2. It multiplies each input by a **weight** (w₁, w₂, …) — how important that input is.
3. It adds everything up, plus a **bias** b.
4. It passes the total through an **activation function**, which decides how strongly the neuron "fires".

> output = activation(w₁x₁ + w₂x₂ + … + b)

The weights and bias are what the network **learns**. Everything else is fixed.

## One neuron in NumPy

Suppose a neuron decides whether you should take a moto instead of walking. Inputs: distance in km, whether it is raining (0/1), and how late you are in minutes.

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

x = np.array([3.0, 1.0, 10.0])          # 3 km, raining, 10 minutes late
w = np.array([0.8, 1.5, 0.2])           # importance of each input
b = -4.0                                # bias: a starting preference for walking

z = np.dot(w, x) + b                    # weighted sum
print("weighted sum:", round(z, 2))
print("probability of taking a moto:", round(sigmoid(z), 3))
```

The weighted sum is 0.8 × 3 + 1.5 × 1 + 0.2 × 10 − 4 = **1.9**, and the sigmoid turns it into a probability of about **0.87**. Change the inputs and see how the output moves.

## Many neurons = a layer

A **layer** is many neurons that all look at the same inputs, each with its own weights. With NumPy, a whole layer is one **matrix multiplication** — the matrix maths you learned in Math & Python for AI:

```python
rng = np.random.default_rng(0)
X = rng.random((5, 3))          # 5 examples, 3 inputs each
W = rng.normal(0, 1, (3, 4))    # 3 inputs -> 4 neurons
b = np.zeros(4)

layer_output = sigmoid(X @ W + b)
print(layer_output.shape)       # (5, 4): 5 examples, 4 neuron outputs each
print(layer_output.round(2))
```

`X @ W` computes all 20 weighted sums (5 examples × 4 neurons) at once. This is why deep learning runs so well on **GPUs**, chips built to do huge matrix multiplications in parallel.

## Stacking layers: a deep network

A network passes the output of one layer as the input to the next:

> inputs → hidden layer 1 → hidden layer 2 → … → output layer

"Deep" simply means **many hidden layers**. Modern image models have dozens; large language models have around a hundred, with billions of weights.

```python
W1, b1 = rng.normal(0, 1, (3, 4)), np.zeros(4)   # layer 1: 3 -> 4
W2, b2 = rng.normal(0, 1, (4, 1)), np.zeros(1)   # layer 2: 4 -> 1

hidden = sigmoid(X @ W1 + b1)
output = sigmoid(hidden @ W2 + b2)
print(output.round(3).ravel())
print("number of learnable numbers:", W1.size + b1.size + W2.size + b2.size)
```

These random weights give meaningless answers. **Training** — next lessons — finds weights that give good ones.

## Key terms

- **Deep learning** — machine learning with neural networks of many layers that learn features from raw data.
- **Neuron** — weighted sum of inputs plus a bias, passed through an activation function.
- **Weight / bias** — the numbers a network learns.
- **Layer** — a group of neurons that see the same inputs.
- **Hidden layer** — a layer between the input and the output.
- **Parameters** — all the weights and biases of a network.

**Takeaway:** A neural network is layers of simple neurons; each layer is a matrix multiplication followed by an activation, and learning means finding good weights.

## Try it yourself

1. In the moto neuron, find an input where the probability is below 0.5. Which input matters most?
2. Change the bias to −8. What happens, and what does the bias mean in plain words?
3. Build a layer with 3 inputs and 10 neurons for 7 examples. What shape is the output?
4. Count the parameters of a network with layers 64 → 32 → 10. (Hint: weights plus biases for each layer.)
""",
            "quiz": [
                ("What is the main difference between deep learning and classic machine learning?",
                 ["Deep learning uses no data", "Deep learning learns features from raw data with many layers", "Deep learning only works on tables", "Classic ML uses GPUs"],
                 1, "Deep networks learn their own features."),
                ("What does a neuron compute before its activation function?",
                 ["A random number", "A weighted sum of its inputs plus a bias", "The average of the outputs", "A sort of the inputs"],
                 1, "w·x + b, then the activation."),
                ("What does a network learn during training?",
                 ["The inputs", "The weights and biases", "The number of examples", "The activation formula"],
                 1, "Weights and biases are the parameters."),
                ("How is a whole layer of neurons computed efficiently?",
                 ["With a loop over each neuron", "With one matrix multiplication", "With sorting", "With a pie chart"],
                 1, "X @ W computes every weighted sum at once."),
                ("What does 'deep' mean in deep learning?",
                 ["The data is very large", "The network has many hidden layers", "It runs underground", "It uses deep colours"],
                 1, "Depth means many layers."),
                ("A layer has 3 inputs and 4 neurons. How many weights does it have (without biases)?",
                 ["7", "12", "4", "3"],
                 1, "3 × 4 = 12 weights."),
            ],
        },
        # ------------------------------------------------------------------ 2
        {
            "title": "Activation Functions and the Forward Pass",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=CqOfi41LfDw",
            "content": r"""
**Learning objective:** Compare the sigmoid, tanh, ReLU and softmax activation functions, explain why networks need them, and run a complete forward pass that turns inputs into class probabilities.

## Why activations matter

Without an activation function, a layer is just a weighted sum — a straight-line function. Stacking ten straight-line layers still gives a straight line, so the network could never learn a curved pattern like the two moons. The activation adds a **bend**. With enough bends, a network can draw almost any shape.

```python
import numpy as np

rng = np.random.default_rng(1)
W1, W2 = rng.normal(size=(2, 3)), rng.normal(size=(3, 1))
x = rng.normal(size=(4, 2))

two_linear_layers = (x @ W1) @ W2
one_linear_layer = x @ (W1 @ W2)
print(np.allclose(two_linear_layers, one_linear_layer))   # True: no extra power
```

Two linear layers are exactly the same as one. The activation is what makes depth useful.

## The four you must know

```python
import matplotlib.pyplot as plt

z = np.linspace(-5, 5, 200)
sigmoid = 1 / (1 + np.exp(-z))
tanh = np.tanh(z)
relu = np.maximum(0, z)

plt.plot(z, sigmoid, label="sigmoid")
plt.plot(z, tanh, label="tanh")
plt.plot(z, relu, label="ReLU")
plt.axhline(0, color="grey", lw=0.5)
plt.legend()
plt.title("Activation functions")
plt.show()
```

| Activation | Output range | Where it is used |
|---|---|---|
| **Sigmoid** | 0 to 1 | Output layer for yes/no (a probability) |
| **Tanh** | −1 to 1 | Older networks, inside LSTMs |
| **ReLU** = max(0, z) | 0 to infinity | **Default for hidden layers** — simple and fast |
| **Softmax** | 0 to 1, all outputs sum to 1 | Output layer for several classes |

Why is ReLU the default? It is very cheap to compute, and for positive inputs its slope is always 1, so learning signals pass through many layers without fading (Lesson 10 explains this "vanishing gradient" problem).

## Softmax: scores into probabilities

For a problem with several classes (digits 0–9, or diseases A, B, C), the last layer gives one **score** (called a **logit**) per class. Softmax turns them into probabilities that add up to 1:

> softmax(zᵢ) = e^zᵢ ÷ (e^z₁ + e^z₂ + … )

```python
def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))   # subtract max for safety
    return e / e.sum(axis=-1, keepdims=True)

logits = np.array([2.0, 1.0, 0.1])
p = softmax(logits)
print(p.round(3), "sum =", p.sum().round(3))
```

The scores 2.0, 1.0 and 0.1 become probabilities of about **0.66, 0.24 and 0.10**. Subtracting the maximum first does not change the answer but prevents overflow when scores are large.

## A complete forward pass

The **forward pass** sends inputs through every layer to the output. Here is a network for 3 classes with 4 inputs, one hidden layer of 8 ReLU neurons, and a softmax output:

```python
rng = np.random.default_rng(42)
X = rng.normal(size=(6, 4))                          # 6 examples, 4 features

W1, b1 = rng.normal(0, 0.5, (4, 8)), np.zeros(8)     # input -> hidden
W2, b2 = rng.normal(0, 0.5, (8, 3)), np.zeros(3)     # hidden -> output

hidden = np.maximum(0, X @ W1 + b1)                  # ReLU
logits = hidden @ W2 + b2
probs = softmax(logits)

print(probs.round(2))
print("predicted classes:", probs.argmax(axis=1))
print("every row sums to 1:", np.allclose(probs.sum(axis=1), 1))
```

`argmax` picks the class with the highest probability for each example.

## Choosing the output layer

| Task | Output layer | Example |
|---|---|---|
| Predict a number | 1 neuron, **no** activation | Rent, temperature |
| Yes / no | 1 neuron + **sigmoid** | Loan default, spam |
| One of several classes | 1 neuron per class + **softmax** | Digit 0–9, crop disease |

## Key terms

- **Activation function** — adds a non-linear bend after each weighted sum.
- **ReLU** — max(0, z); the standard hidden-layer activation.
- **Logit** — a raw class score before softmax.
- **Softmax** — turns logits into probabilities that sum to 1.
- **Forward pass** — computing the output from the input, layer by layer.

**Takeaway:** Activations give networks their power to bend; ReLU is used inside, and sigmoid or softmax at the output turn scores into probabilities.

## Try it yourself

1. Apply softmax to [5, 5, 5]. What do you get, and why?
2. Multiply the logits [2.0, 1.0, 0.1] by 10 and apply softmax again. What happens to the probabilities?
3. Replace ReLU with tanh in the forward pass. Do the predicted classes change?
4. Plot the slope (derivative) of the sigmoid: s × (1 − s). Where is it largest, and how small is it at z = 5?
""",
            "quiz": [
                ("Why does a network need activation functions?",
                 ["To make it faster", "Without them, stacked layers are still one straight-line function", "To store data", "To remove the bias"],
                 1, "Activations add the non-linear bends."),
                ("What is ReLU(−3)?",
                 ["−3", "0", "3", "1"],
                 1, "ReLU keeps positives and turns negatives into 0."),
                ("Which activation suits the output of a 10-class digit classifier?",
                 ["ReLU", "Softmax", "No activation", "Tanh"],
                 1, "Softmax gives one probability per class."),
                ("What do softmax outputs always add up to?",
                 ["0", "1", "10", "It depends"],
                 1, "They form a probability distribution."),
                ("Which output layer suits predicting monthly rent?",
                 ["Softmax", "Sigmoid", "One neuron with no activation", "ReLU over 10 neurons"],
                 2, "A number can be any value, so no squashing."),
                ("What is the forward pass?",
                 ["Updating the weights", "Computing outputs from inputs layer by layer", "Splitting the data", "Plotting the loss"],
                 1, "Inputs flow forward to the output."),
            ],
        },
        # ------------------------------------------------------------------ 3
        {
            "title": "Loss Functions and Gradient Descent",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=IHZwWFHWa-w",
            "content": r"""
**Learning objective:** Measure how wrong a network is with mean squared error and cross-entropy, and train a single neuron with gradient descent.

## A score for being wrong

To improve, a network needs one number that says how wrong it is: the **loss**. Training means changing the weights to make the loss smaller.

- **Mean squared error (MSE)** — for numbers: the average of (prediction − truth)². You used it in Math & Python for AI.
- **Cross-entropy** — for classes: punishes confident wrong answers very hard.

> binary cross-entropy = −[ y × log(p) + (1 − y) × log(1 − p) ]

where y is the true label (0 or 1) and p is the predicted probability of class 1.

```python
import numpy as np

def bce(y, p):
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))

for p in [0.99, 0.9, 0.6, 0.4, 0.1, 0.01]:
    print(f"true label 1, predicted {p:4.2f} -> loss {bce(1, p):.3f}")
```

A confident correct answer (0.99) costs almost nothing (about 0.01). A confident wrong answer (0.01) costs about **4.6**. Cross-entropy teaches the network not to be confidently wrong. For several classes, **categorical cross-entropy** is −log(probability given to the true class).

## Gradient descent, again

The loss depends on every weight. The **gradient** tells us, for each weight, which direction makes the loss go **up** — so we step the other way:

> new weight = old weight − learning rate × gradient

This is exactly the gradient descent you did by hand for linear regression. Deep learning uses the same idea for millions of weights at once.

## Train one neuron (logistic regression)

A single neuron with a sigmoid is logistic regression. For cross-entropy loss, the gradient has a beautifully simple form: (prediction − truth) × input.

{MOONS}

```python
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

w = np.zeros(2)
b = 0.0
lr = 0.5
history = []
for epoch in range(500):
    p = sigmoid(X_train @ w + b)
    loss = bce(y_train, np.clip(p, 1e-9, 1 - 1e-9)).mean()
    history.append(loss)
    grad_w = X_train.T @ (p - y_train) / len(y_train)
    grad_b = (p - y_train).mean()
    w -= lr * grad_w
    b -= lr * grad_b

acc = ((sigmoid(X_test @ w + b) > 0.5) == y_test).mean()
print("final loss:", round(history[-1], 3), " test accuracy:", acc)
plt.plot(history)
plt.xlabel("epoch")
plt.ylabel("cross-entropy loss")
plt.show()
```

The loss falls quickly then levels off, and the single neuron reaches about **0.86** test accuracy. It cannot do better: one neuron draws one **straight** line, and the moons are curved. Next lesson, a hidden layer fixes that.

## Check a gradient by nudging

You can always check a gradient numerically: nudge a weight a tiny bit and see how the loss changes.

```python
def mean_loss(w, b):
    p = np.clip(sigmoid(X_train @ w + b), 1e-9, 1 - 1e-9)
    return bce(y_train, p).mean()

eps = 1e-5
w_plus = w.copy(); w_plus[0] += eps
w_minus = w.copy(); w_minus[0] -= eps
numeric = (mean_loss(w_plus, b) - mean_loss(w_minus, b)) / (2 * eps)
analytic = X_train[:, 0] @ (sigmoid(X_train @ w + b) - y_train) / len(y_train)
print(round(numeric, 6), round(analytic, 6))
```

The two numbers agree — our formula is right. This **gradient check** is a classic debugging trick.

## Mini-batches and epochs

Real datasets are too big to use all at once. **Stochastic / mini-batch gradient descent** uses a small random batch (for example 32 or 64 examples) for each step. One pass through all the batches is an **epoch**. Batches make training faster and the noise even helps escape poor solutions.

## Key terms

- **Loss** — one number measuring how wrong the predictions are.
- **Cross-entropy** — the standard loss for classification.
- **Gradient** — the direction in which each weight increases the loss.
- **Learning rate** — the size of each step.
- **Mini-batch** — a small group of examples used for one update.
- **Epoch** — one full pass through the training data.

**Takeaway:** Training is a loop — predict, measure the loss, compute gradients, step downhill — and cross-entropy is the loss for classification.

## Try it yourself

1. Try learning rates 0.05, 0.5 and 5. Plot the three loss curves on one chart.
2. Change the training loop to use random mini-batches of 32 rows. Does it still learn?
3. Compute the categorical cross-entropy when the true class gets probability 0.7, then 0.05.
4. Plot the straight decision line w₁x₁ + w₂x₂ + b = 0 on top of the moons scatter plot.
""",
            "quiz": [
                ("What does the loss measure?",
                 ["The training speed", "How wrong the predictions are", "The number of layers", "The accuracy on new data only"],
                 1, "Training tries to make the loss small."),
                ("Which loss is standard for classification?",
                 ["Mean squared error", "Cross-entropy", "R²", "Median error"],
                 1, "Cross-entropy punishes confident mistakes."),
                ("The true label is 1 and the model predicts 0.01. What happens to the cross-entropy loss?",
                 ["It is almost 0", "It is large (about 4.6)", "It is negative", "It is exactly 1"],
                 1, "Confident wrong answers cost the most."),
                ("In gradient descent, which way does each weight move?",
                 ["In the direction of the gradient", "Opposite to the gradient, downhill", "At random", "It does not move"],
                 1, "new w = w − learning rate × gradient."),
                ("Why can a single neuron not reach high accuracy on the two moons?",
                 ["It has no bias", "It can only draw a straight boundary", "The data has no labels", "The learning rate is wrong"],
                 1, "Curved patterns need hidden layers."),
                ("What is one epoch?",
                 ["One weight update", "One full pass through the training data", "One layer", "One test prediction"],
                 1, "An epoch covers every training example once."),
            ],
        },
        # ------------------------------------------------------------------ 4
        {
            "title": "Backpropagation: How Networks Learn",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=Ilg3gGewQ5U",
            "content": r"""
**Learning objective:** Explain backpropagation with the chain rule, and write a two-layer neural network in NumPy that learns the curved two-moons pattern.

## The problem backpropagation solves

A network can have millions of weights. For each one we need its gradient: "if I change this weight a little, how does the loss change?" Nudging each weight one by one would take forever. **Backpropagation** computes **all** the gradients in one backward sweep through the network — about the same cost as one forward pass. It is the engine of all deep learning.

## The chain rule in one picture

If the loss depends on the output, the output depends on the hidden layer, and the hidden layer depends on a weight, then:

> how loss changes with the weight = (how loss changes with the output) × (how output changes with the hidden layer) × (how hidden layer changes with the weight)

Backpropagation starts at the loss and walks **backwards**, multiplying these local slopes layer by layer and reusing them — that is why it is fast.

## The network

- Input: 2 numbers (the moon coordinates).
- Hidden layer: 16 ReLU neurons.
- Output: 1 sigmoid neuron (probability of moon 1).
- Loss: binary cross-entropy.

{MOONS}

## Forward and backward, step by step

```python
rng = np.random.default_rng(0)
H = 16
W1 = rng.normal(0, 1, (2, H))          # input -> hidden
b1 = np.zeros(H)
W2 = rng.normal(0, 1, (H, 1)) * np.sqrt(1 / H)   # hidden -> output
b2 = np.zeros(1)

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def forward(X):
    z1 = X @ W1 + b1
    a1 = np.maximum(0, z1)              # ReLU
    z2 = a1 @ W2 + b2
    p = sigmoid(z2).ravel()
    return z1, a1, p

lr = 0.5
losses = []
for epoch in range(2000):
    z1, a1, p = forward(X_train)
    n = len(y_train)
    losses.append(-np.mean(y_train * np.log(p + 1e-9) + (1 - y_train) * np.log(1 - p + 1e-9)))

    # backward pass (chain rule, from the loss back to the first layer)
    dz2 = (p - y_train)[:, None] / n    # loss -> output score
    dW2 = a1.T @ dz2                    # -> weights of layer 2
    db2 = dz2.sum(axis=0)
    da1 = dz2 @ W2.T                    # -> hidden activations
    dz1 = da1 * (z1 > 0)                # -> through ReLU (slope 1 or 0)
    dW1 = X_train.T @ dz1               # -> weights of layer 1
    db1 = dz1.sum(axis=0)

    # gradient descent step
    W1 -= lr * dW1; b1 -= lr * db1
    W2 -= lr * dW2; b2 -= lr * db2

test_acc = ((forward(X_test)[2] > 0.5) == y_test).mean()
print("final training loss:", round(losses[-1], 3))
print("test accuracy:", test_acc)
```

Read the backward pass from top to bottom: each line is one link of the chain rule. The ReLU passes the gradient through where the neuron was active (z1 > 0) and blocks it where it was off.

The network reaches about **0.96** test accuracy, up from 0.86 with a single neuron. The hidden layer learned to bend the boundary.

## See the curved boundary

```python
xx, yy = np.meshgrid(np.linspace(-2, 3, 300), np.linspace(-1.5, 2, 300))
grid = np.c_[xx.ravel(), yy.ravel()]
zz = forward(grid)[2].reshape(xx.shape)
plt.contourf(xx, yy, zz > 0.5, alpha=0.3)
plt.scatter(X_test[:, 0], X_test[:, 1], c=y_test, s=10)
plt.title("Decision boundary learned by a 16-neuron hidden layer")
plt.show()

plt.plot(losses)
plt.xlabel("epoch")
plt.ylabel("loss")
plt.show()
```

## Why random starting weights?

If every weight started at zero, every hidden neuron would compute the same thing and receive the same gradient — they would stay identical forever. Random initial weights **break the symmetry** so each neuron can learn something different. Scaling them sensibly (here by √(1/H)) keeps the signals a healthy size (Lesson 10).

## You will rarely write this again

From the next lesson, **PyTorch** computes the backward pass for you automatically. But now you know what `loss.backward()` really does: exactly the chain-rule steps above, for any network you build.

## Key terms

- **Backpropagation** — computing every gradient in one backward sweep using the chain rule.
- **Chain rule** — multiply the slopes of each step to get the overall slope.
- **Hidden layer** — lets the network learn curved boundaries.
- **Symmetry breaking** — random initial weights so neurons learn different things.

**Takeaway:** Backpropagation walks backwards from the loss, multiplying local slopes, to give every weight its gradient — and a single hidden layer already turns a straight line into a curve.

## Try it yourself

1. Change the hidden layer to 2, 4 and 64 neurons. How does the test accuracy and the boundary change?
2. Start all weights at zero. What happens to training, and why?
3. Add a second hidden layer (16 → 16). Write its backward lines by following the same pattern.
4. Use the gradient-check trick from Lesson 3 on one entry of W1 to confirm your backward pass.
""",
            "quiz": [
                ("What does backpropagation compute?",
                 ["The predictions", "The gradient of the loss for every weight", "The test accuracy", "The number of layers"],
                 1, "It gives each weight its gradient efficiently."),
                ("Which mathematical rule is backpropagation built on?",
                 ["Pythagoras' theorem", "The chain rule", "Bayes' theorem", "The central limit theorem"],
                 1, "Local slopes are multiplied along the chain."),
                ("In which direction does backpropagation move through the network?",
                 ["From input to output", "From the loss back towards the input", "Randomly", "Only through the first layer"],
                 1, "Hence 'back' propagation."),
                ("How does ReLU pass gradients backwards?",
                 ["It doubles them", "It passes them where the neuron was active and blocks them where it was off", "It always blocks them", "It turns them into probabilities"],
                 1, "Its slope is 1 for positive inputs and 0 otherwise."),
                ("Why are initial weights random instead of all zero?",
                 ["Zero weights use more memory", "To break symmetry so neurons learn different things", "Random weights are always correct", "PyTorch requires it"],
                 1, "Identical neurons would stay identical."),
                ("Adding a 16-neuron hidden layer raised accuracy on the moons from about 0.86 to about 0.96. Why?",
                 ["The data changed", "The hidden layer lets the boundary curve", "The test set got easier", "The learning rate was removed"],
                 1, "Hidden layers give the network non-linear power."),
            ],
        },
        # ------------------------------------------------------------------ 5
        {
            "title": "PyTorch: Tensors and Autograd",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=ORMx45xqWkA",
            "content": r"""
**Learning objective:** Create and reshape PyTorch tensors, use a GPU when one is available, let autograd compute gradients, and rebuild last lesson's network in a few lines.

## Why PyTorch?

**PyTorch** is the most used deep-learning library in research and industry (with TensorFlow/Keras and JAX as the others). It gives you:

1. **Tensors** — like NumPy arrays, but able to run on a GPU.
2. **Autograd** — automatic backpropagation: you write the forward pass, PyTorch computes every gradient.
3. **Ready-made building blocks** — layers, losses, optimisers and data tools.

It is already installed in Google Colab. To get a free GPU there: **Runtime → Change runtime type → T4 GPU**.

## Tensors

```python
import torch

a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print(a.shape, a.dtype)
print(a * 10)               # element-wise, like NumPy
print(a @ a)                # matrix multiplication
print(a.mean(), a.sum(dim=0))

z = torch.zeros(3, 4)
r = torch.randn(2, 3)       # random normal numbers
print(z.shape, r.shape)
print(r.reshape(3, 2).shape, r.T.shape)
```

Moving between NumPy and PyTorch is easy:

```python
import numpy as np

arr = np.arange(6).reshape(2, 3)
t = torch.from_numpy(arr).float()   # NumPy -> tensor (float32 for networks)
back = t.numpy()                    # tensor -> NumPy
print(t, back.dtype)
```

Neural networks use **float32** numbers almost everywhere — that is why we call `.float()`.

## CPU or GPU?

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using:", device)
x = torch.randn(1000, 1000, device=device)
y = x @ x          # runs on the GPU if there is one
print(y.shape, y.device)
```

Write `device` once at the top of every notebook and move your model and data to it with `.to(device)`. The same code then runs on a laptop CPU or a Colab GPU.

## Autograd: gradients for free

Mark a tensor with `requires_grad=True` and PyTorch records every operation on it. Calling `.backward()` runs backpropagation:

```python
w = torch.tensor(3.0, requires_grad=True)
loss = (w - 5) ** 2          # smallest when w = 5
loss.backward()
print("gradient:", w.grad)   # 2 × (3 − 5) = −4
```

The gradient is **−4**: increasing w lowers the loss, exactly what the derivative rules give. Let gradient descent find w = 5:

```python
w = torch.tensor(0.0, requires_grad=True)
for step in range(50):
    loss = (w - 5) ** 2
    loss.backward()
    with torch.no_grad():      # updating weights is not part of the graph
        w -= 0.1 * w.grad
    w.grad.zero_()             # gradients add up unless you reset them!
print(round(w.item(), 3))
```

Two rules to remember: update weights inside `torch.no_grad()`, and **reset gradients** every step — PyTorch adds new gradients to old ones by default.

## Last lesson's network, with autograd

```python
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

X, y = make_moons(n_samples=1000, noise=0.2, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
Xtr, ytr = torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32)
Xte, yte = torch.tensor(X_test, dtype=torch.float32), torch.tensor(y_test, dtype=torch.float32)

torch.manual_seed(0)
W1 = (torch.randn(2, 16)).requires_grad_()
b1 = torch.zeros(16, requires_grad=True)
W2 = (torch.randn(16, 1) * 0.25).requires_grad_()
b2 = torch.zeros(1, requires_grad=True)
params = [W1, b1, W2, b2]

for epoch in range(2000):
    hidden = torch.relu(Xtr @ W1 + b1)
    logits = (hidden @ W2 + b2).squeeze(1)
    loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, ytr)
    loss.backward()                         # all four gradients, automatically
    with torch.no_grad():
        for p in params:
            p -= 0.5 * p.grad
            p.grad.zero_()

with torch.no_grad():
    pred = torch.relu(Xte @ W1 + b1) @ W2 + b2
    acc = ((pred.squeeze(1) > 0) == yte.bool()).float().mean()
print("loss:", round(loss.item(), 3), " test accuracy:", round(acc.item(), 3))
```

There is **no backward code** — `loss.backward()` replaces the six chain-rule lines from Lesson 4, and the network again reaches about **0.96**.

`binary_cross_entropy_with_logits` combines the sigmoid and the loss in one numerically safe step, so the model outputs raw scores (logits). A logit above 0 means a probability above 0.5.

## Key terms

- **PyTorch** — a deep-learning library built on tensors and autograd.
- **Tensor** — a multi-dimensional array that can live on a CPU or GPU.
- **Autograd** — PyTorch's automatic differentiation (backpropagation).
- **requires_grad** — tells PyTorch to track a tensor for gradients.
- **torch.no_grad()** — switch off tracking, for updates and predictions.
- **Device** — where computation runs: "cpu" or "cuda" (GPU).

**Takeaway:** PyTorch tensors are GPU-ready NumPy arrays, and autograd turns any forward computation into gradients with one call to `.backward()`.

## Try it yourself

1. Create a tensor of shape (2, 3, 4). What are `t.shape[1]` and `t.numel()`?
2. Remove `p.grad.zero_()` from the moons loop. What happens to training, and why?
3. Use autograd to find the slope of y = x³ at x = 2. Check it with the derivative rule (3x²).
4. In Colab, switch to a T4 GPU and time a (4000 × 4000) matrix multiplication on CPU and GPU.
""",
            "quiz": [
                ("What is the main extra power of a PyTorch tensor compared with a NumPy array?",
                 ["It can only hold text", "It can run on a GPU and track gradients", "It is always smaller", "It cannot do maths"],
                 1, "GPU support and autograd."),
                ("What does loss.backward() do?",
                 ["Deletes the loss", "Computes gradients for every tensor that requires them", "Updates the weights", "Splits the data"],
                 1, "Autograd runs backpropagation."),
                ("Why call grad.zero_() every step?",
                 ["To speed up the GPU", "PyTorch adds new gradients to old ones unless you reset them", "To delete the model", "It is not needed"],
                 1, "Gradients accumulate by default."),
                ("For loss = (w − 5)² at w = 3, what gradient does autograd give?",
                 ["4", "−4", "0", "25"],
                 1, "2 × (3 − 5) = −4."),
                ("Which number type do neural networks usually use?",
                 ["float32", "string", "int8 only", "bool"],
                 0, "That is why we call .float()."),
                ("Why update weights inside torch.no_grad()?",
                 ["The update itself should not be recorded as part of the model's computation", "It makes the update bigger", "To use the CPU", "It saves the model"],
                 0, "Only the forward pass should build the graph."),
            ],
        },
        # ------------------------------------------------------------------ 6
        {
            "title": "Week 1 Project: Read Handwritten Digits",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=tIeHLnjs5U8",
            "content": r"""
**Learning objective:** Build, train and evaluate a neural network that reads handwritten digits — first from scratch in NumPy, then with PyTorch autograd — and explain its mistakes.

## The brief

Post offices, banks and schools still read handwritten numbers on forms. Your task: build a network that reads digits 0–9 from small images, using the **digits** dataset built into scikit-learn (1,797 images of 8 × 8 pixels, from 43 writers).

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

digits = load_digits()
X = digits.data / 16.0            # pixel values 0..16 -> 0..1
y = digits.target
print(X.shape, np.bincount(y))

fig, axes = plt.subplots(1, 8, figsize=(10, 2))
for ax, img, label in zip(axes, digits.images, y):
    ax.imshow(img, cmap="gray_r")
    ax.set_title(label)
    ax.axis("off")
plt.show()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0, stratify=y)
```

Each image is flattened into **64 numbers**. Dividing by 16 puts every pixel between 0 and 1 — networks learn faster with small, similar-sized inputs.

## Part 1 — A network from scratch (NumPy)

Architecture: 64 inputs → 32 ReLU neurons → 10 outputs with softmax, trained with categorical cross-entropy.

```python
rng = np.random.default_rng(0)
W1 = rng.normal(0, np.sqrt(2 / 64), (64, 32)); b1 = np.zeros(32)
W2 = rng.normal(0, np.sqrt(1 / 32), (32, 10)); b2 = np.zeros(10)
Y = np.eye(10)[y_train]                       # one-hot labels

def softmax(z):
    e = np.exp(z - z.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

lr, batch = 0.1, 64
for epoch in range(60):
    order = rng.permutation(len(X_train))
    for start in range(0, len(order), batch):
        idx = order[start:start + batch]
        xb, yb = X_train[idx], Y[idx]
        z1 = xb @ W1 + b1; a1 = np.maximum(0, z1)
        p = softmax(a1 @ W2 + b2)
        dz2 = (p - yb) / len(idx)             # softmax + cross-entropy gradient
        dW2 = a1.T @ dz2; db2 = dz2.sum(0)
        dz1 = (dz2 @ W2.T) * (z1 > 0)
        dW1 = xb.T @ dz1; db1 = dz1.sum(0)
        W1 -= lr * dW1; b1 -= lr * db1; W2 -= lr * dW2; b2 -= lr * db2

def predict(Xs):
    return (np.maximum(0, Xs @ W1 + b1) @ W2 + b2).argmax(axis=1)

print("NumPy network test accuracy:", round((predict(X_test) == y_test).mean(), 3))
```

The softmax-plus-cross-entropy gradient is simply **prediction − one-hot truth** — the same pattern as for one sigmoid neuron. You should reach about **0.97** accuracy.

## Part 2 — The same network with autograd

```python
import torch
import torch.nn.functional as F

torch.manual_seed(0)
Xtr = torch.tensor(X_train, dtype=torch.float32); ytr = torch.tensor(y_train)
Xte = torch.tensor(X_test, dtype=torch.float32); yte = torch.tensor(y_test)

W1t = (torch.randn(64, 32) * (2 / 64) ** 0.5).requires_grad_()
b1t = torch.zeros(32, requires_grad=True)
W2t = (torch.randn(32, 10) * (1 / 32) ** 0.5).requires_grad_()
b2t = torch.zeros(10, requires_grad=True)
params = [W1t, b1t, W2t, b2t]

for epoch in range(60):
    perm = torch.randperm(len(Xtr))
    for start in range(0, len(perm), 64):
        idx = perm[start:start + 64]
        logits = torch.relu(Xtr[idx] @ W1t + b1t) @ W2t + b2t
        loss = F.cross_entropy(logits, ytr[idx])      # softmax + cross-entropy
        loss.backward()
        with torch.no_grad():
            for p in params:
                p -= 0.1 * p.grad
                p.grad.zero_()

with torch.no_grad():
    pred_t = (torch.relu(Xte @ W1t + b1t) @ W2t + b2t).argmax(dim=1)
print("PyTorch network test accuracy:", round((pred_t == yte).float().mean().item(), 3))
```

`F.cross_entropy` takes raw logits and integer labels and applies softmax inside. Both versions should land close to each other.

## Part 3 — Evaluate like a professional

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

pred = predict(X_test)
ConfusionMatrixDisplay(confusion_matrix(y_test, pred)).plot(cmap="Blues")
plt.show()

wrong = np.where(pred != y_test)[0]
print("mistakes:", len(wrong), "of", len(y_test))
fig, axes = plt.subplots(1, min(6, len(wrong)), figsize=(10, 2))
for ax, i in zip(np.atleast_1d(axes), wrong[:6]):
    ax.imshow(X_test[i].reshape(8, 8), cmap="gray_r")
    ax.set_title(f"true {y_test[i]}, said {pred[i]}")
    ax.axis("off")
plt.show()
```

Look at the mistakes. Are they digits a person would also find hard?

## Part 4 — Compare with a baseline

Train `LogisticRegression(max_iter=2000)` from scikit-learn on the same split. A network should beat it — but by how much? On tiny 8 × 8 images the gap is small; on real photos it becomes enormous.

## Part 5 — Report (one page)

1. Data: size, image size, classes, how you scaled the pixels.
2. Architecture and training settings (layers, learning rate, batch size, epochs).
3. Test accuracy of both versions and of the baseline.
4. The confusion matrix and the three most common confusions, with a short explanation.
5. One idea to improve the model, and one real use in Rwanda (for example reading marks on exam sheets).

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Data | Pixels scaled, stratified split, sample images shown |
| From scratch | NumPy network trains and reaches about 0.97 |
| Autograd | PyTorch version matches the NumPy result |
| Evaluation | Confusion matrix and mistakes analysed |
| Communication | Clear report with a baseline comparison |

**Takeaway:** You built the same digit reader twice — by hand and with autograd — and now understand exactly what deep-learning libraries automate.

## Try it yourself

Complete Parts 1–5. Then add a second hidden layer (64 → 64 → 32 → 10) to the PyTorch version. Does it help on this small dataset?
""",
            "quiz": [
                ("Why divide the digit pixels by 16?",
                 ["To delete them", "To put every input between 0 and 1, which helps training", "To make images bigger", "To change the labels"],
                 1, "Small, similar-sized inputs train better."),
                ("How many inputs does the network take for one 8 × 8 image?",
                 ["8", "16", "64", "10"],
                 2, "The image is flattened to 64 numbers."),
                ("What is the gradient of softmax + cross-entropy with respect to the logits?",
                 ["Always zero", "Predicted probabilities minus the one-hot truth", "The input pixels", "The learning rate"],
                 1, "p − y, as for a single sigmoid neuron."),
                ("What does F.cross_entropy expect?",
                 ["Probabilities and one-hot labels", "Raw logits and integer class labels", "Images", "Only one class"],
                 1, "It applies softmax inside."),
                ("Why compare the network with logistic regression?",
                 ["To show whether the extra complexity is worth it", "Because networks cannot be evaluated", "To make the network slower", "It is required by PyTorch"],
                 0, "A baseline turns a score into evidence."),
                ("What is a mini-batch in this project?",
                 ["All 1,797 images", "64 random training images used for one update", "One pixel", "The test set"],
                 1, "Each step uses a small random batch."),
            ],
        },
    ],
}

for _lesson in WEEK1["lessons"]:
    _lesson["content"] = _lesson["content"].replace("{MOONS}", MOONS)
