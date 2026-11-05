"""Deep Learning & Neural Networks -- Week 2: Training Deep Networks Well. Original WAMUGII content."""

from app.course_content.ml_data import LOANS_DATA

DIGITS = r"""
```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

digits = load_digits()
X, y = digits.data / 16.0, digits.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2,
                                                  random_state=0, stratify=y_train)
to_x = lambda a: torch.tensor(a, dtype=torch.float32)
to_y = lambda a: torch.tensor(a, dtype=torch.long)
Xtr, Xva, Xte = to_x(X_train), to_x(X_val), to_x(X_test)
ytr, yva, yte = to_y(y_train), to_y(y_val), to_y(y_test)
print(len(Xtr), "train,", len(Xva), "validation,", len(Xte), "test")
```
""".strip()

WEEK2 = {
    "title": "Week 2 · Training Deep Networks Well",
    "lessons": [
        # ------------------------------------------------------------------ 7
        {
            "title": "Building Models with nn.Module and the Training Loop",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=rrekAv9Fml4",
            "content": r"""
**Learning objective:** Define networks with `nn.Sequential` and `nn.Module`, write the standard PyTorch training loop with an optimiser, and track training and validation results every epoch.

## Stop managing weights by hand

In Week 1 you created every weight tensor yourself. PyTorch's `torch.nn` package does that for you: a layer such as `nn.Linear(64, 32)` creates and initialises its own weights and bias, and an **optimiser** applies the gradient-descent update to all of them.

{DIGITS}

We now keep **three** sets: training (to learn), **validation** (to watch progress and make choices) and test (for the final, honest score) — as in Machine Learning Fundamentals.

## nn.Sequential: layers in a row

```python
torch.manual_seed(0)
model = nn.Sequential(
    nn.Linear(64, 64),
    nn.ReLU(),
    nn.Linear(64, 10),        # 10 logits, one per digit
)
print(model)
print("parameters:", sum(p.numel() for p in model.parameters()))
```

64 × 64 + 64 + 64 × 10 + 10 = **4,810** learnable numbers, created and initialised automatically.

## nn.Module: your own model class

For anything more than a simple stack, write a class. `__init__` creates the layers; `forward` says how data flows through them:

```python
class DigitNet(nn.Module):
    def __init__(self, hidden=64):
        super().__init__()
        self.hidden = nn.Linear(64, hidden)
        self.out = nn.Linear(hidden, 10)

    def forward(self, x):
        x = F.relu(self.hidden(x))
        return self.out(x)

net = DigitNet()
print(net(Xtr[:3]).shape)     # 3 examples -> 3 rows of 10 logits
```

You call the model like a function — `net(x)` — and PyTorch runs `forward`.

## The training loop

Every PyTorch project uses the same five lines per batch:

```python
torch.manual_seed(0)
model = DigitNet()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

def accuracy(m, X, y):
    m.eval()
    with torch.no_grad():
        return (m(X).argmax(dim=1) == y).float().mean().item()

history = {"train_loss": [], "val_loss": [], "val_acc": []}
for epoch in range(30):
    model.train()
    perm = torch.randperm(len(Xtr))
    for start in range(0, len(perm), 32):
        idx = perm[start:start + 32]
        optimizer.zero_grad()                    # 1. clear old gradients
        logits = model(Xtr[idx])                 # 2. forward pass
        loss = F.cross_entropy(logits, ytr[idx]) # 3. loss
        loss.backward()                          # 4. backpropagation
        optimizer.step()                         # 5. update every weight

    model.eval()
    with torch.no_grad():
        history["train_loss"].append(F.cross_entropy(model(Xtr), ytr).item())
        history["val_loss"].append(F.cross_entropy(model(Xva), yva).item())
    history["val_acc"].append(accuracy(model, Xva, yva))

print("validation accuracy after 30 epochs:", round(history["val_acc"][-1], 3))
```

Learn these five steps by heart: **zero_grad, forward, loss, backward, step**. They are the same for a 5,000-parameter digit model and a 70-billion-parameter language model.

## train() and eval() modes

`model.train()` and `model.eval()` switch some layers between behaviours — **dropout** (Lesson 9) and **batch normalisation** (Lesson 10) act differently while training. Always call `model.eval()` before measuring or predicting, and wrap predictions in `torch.no_grad()` to save memory and time.

## Plot the learning curves

```python
plt.plot(history["train_loss"], label="training loss")
plt.plot(history["val_loss"], label="validation loss")
plt.xlabel("epoch")
plt.legend()
plt.title("Learning curves")
plt.show()
```

Both curves should fall together. If the training loss keeps falling while the validation loss turns upwards, the model is **overfitting** — Lesson 9.

## Predict on new data

```python
model.eval()
with torch.no_grad():
    probs = F.softmax(model(Xte[:5]), dim=1)
print(probs.argmax(dim=1).tolist(), "true:", yte[:5].tolist())
print("confidence:", [round(c, 2) for c in probs.max(dim=1).values.tolist()])
print("test accuracy:", round(accuracy(model, Xte, yte), 3))
```

## Save and load

```python
torch.save(model.state_dict(), "digitnet.pt")      # only the learned numbers
again = DigitNet()
again.load_state_dict(torch.load("digitnet.pt"))
print("same answers:", torch.equal(again.eval()(Xte), model.eval()(Xte)))
```

A **state_dict** holds the weights; you rebuild the same class and load them in.

## Key terms

- **nn.Module** — the base class for PyTorch models; `forward` defines the computation.
- **nn.Sequential** — a quick way to stack layers.
- **Optimiser** — applies the weight updates (SGD, Adam…).
- **Training loop** — zero_grad, forward, loss, backward, step.
- **train() / eval()** — switch layer behaviour for training or prediction.
- **state_dict** — a model's learned weights, for saving and loading.

**Takeaway:** In PyTorch you describe the model once with nn.Module, and every training step is the same five lines: zero_grad, forward, loss, backward, step.

## Try it yourself

1. Change the hidden size to 16 and to 256. How do the parameter count and the validation accuracy change?
2. Add a second hidden layer to `DigitNet` and train it again.
3. Remove `optimizer.zero_grad()`. Describe what happens to the loss.
4. Print the five test digits the model is least confident about. Are they messy?
""",
            "quiz": [
                ("What does nn.Linear(64, 10) create?",
                 ["A dataset", "A layer with its own 64 × 10 weights and 10 biases", "A loss function", "An optimiser"],
                 1, "Layers create and initialise their own parameters."),
                ("In an nn.Module class, what does the forward method define?",
                 ["How data flows through the layers", "The learning rate", "The test set", "How to save the model"],
                 0, "Calling model(x) runs forward."),
                ("What is the correct order of the training step?",
                 ["step, backward, loss, forward, zero_grad", "zero_grad, forward, loss, backward, step", "forward, step, zero_grad, loss, backward", "loss, forward, step, backward, zero_grad"],
                 1, "Clear, predict, measure, backpropagate, update."),
                ("What does optimizer.step() do?",
                 ["Computes gradients", "Updates every weight using its gradient", "Loads data", "Evaluates the model"],
                 1, "backward computes, step updates."),
                ("Why call model.eval() before measuring accuracy?",
                 ["Some layers such as dropout behave differently during training", "It makes the model learn faster", "It deletes gradients", "It is only for GPUs"],
                 0, "eval() switches layers to prediction behaviour."),
                ("What does model.state_dict() contain?",
                 ["The training data", "The model's learned weights and biases", "The loss history", "The source code"],
                 1, "It is what you save and load."),
            ],
        },
        # ------------------------------------------------------------------ 8
        {
            "title": "Optimisers: SGD, Momentum and Adam",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=ErnWZxJovaM",
            "content": r"""
**Learning objective:** Explain how SGD, momentum and Adam update weights, compare them on the same model, and choose a learning rate and a learning-rate schedule.

## The optimiser decides how to step

All optimisers use the gradient. They differ in **how** they turn it into a step.

| Optimiser | Idea | Everyday picture |
|---|---|---|
| **SGD** | Step = learning rate × gradient | Walking downhill one careful step at a time |
| **SGD + momentum** | Keep some speed from previous steps | A ball rolling downhill: it speeds up on long slopes and rolls over small bumps |
| **Adam** | Momentum + a separate, automatic step size for every weight | A hiker who takes short steps on rough ground and long steps on smooth ground |

**Adam** (2014) is the most popular default: it works well with little tuning, usually with a learning rate around **0.001**.

## A fair comparison

{DIGITS}

```python
def make_model(seed=0):
    torch.manual_seed(seed)
    return nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10))

def train(optimizer_fn, epochs=20):
    model = make_model()
    opt = optimizer_fn(model.parameters())
    val_losses = []
    g = torch.Generator().manual_seed(0)          # same batches for every optimiser
    for epoch in range(epochs):
        model.train()
        perm = torch.randperm(len(Xtr), generator=g)
        for start in range(0, len(perm), 32):
            idx = perm[start:start + 32]
            opt.zero_grad()
            F.cross_entropy(model(Xtr[idx]), ytr[idx]).backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            val_losses.append(F.cross_entropy(model(Xva), yva).item())
    with torch.no_grad():
        acc = (model(Xva).argmax(1) == yva).float().mean().item()
    return val_losses, acc

runs = {
    "SGD lr=0.01": lambda p: torch.optim.SGD(p, lr=0.01),
    "SGD lr=0.1": lambda p: torch.optim.SGD(p, lr=0.1),
    "SGD + momentum": lambda p: torch.optim.SGD(p, lr=0.01, momentum=0.9),
    "Adam lr=0.001": lambda p: torch.optim.Adam(p, lr=0.001),
    "Adam lr=0.1": lambda p: torch.optim.Adam(p, lr=0.1),
}
for name, fn in runs.items():
    losses, acc = train(fn)
    plt.plot(losses, label=name)
    print(f"{name:15s} final validation loss {losses[-1]:.3f}  accuracy {acc:.3f}")
plt.xlabel("epoch")
plt.ylabel("validation loss")
plt.legend()
plt.show()
```

What you should see:

- **SGD with lr = 0.01** crawls: after 20 epochs it is still far from done (validation accuracy around 0.85).
- **Momentum** with the same small learning rate is many times faster.
- **SGD with lr = 0.1** and **Adam with lr = 0.001** both train well (about 0.94–0.96).
- **Adam with lr = 0.1** is too aggressive: its loss jumps around and ends worse.

The learning rate matters more than the choice of optimiser. Too small wastes time; too big makes training unstable or makes it explode.

## How momentum works (in one line)

> velocity = 0.9 × velocity + gradient,   weight = weight − learning rate × velocity

Gradients that keep pointing the same way add up; gradients that flip back and forth cancel out.

## How to choose a learning rate

1. Start with the default: Adam 0.001, or SGD with momentum 0.01–0.1.
2. Try values 10 times apart (0.0001, 0.001, 0.01) and compare validation loss after a few epochs.
3. If the loss goes up or becomes `nan`, the learning rate is too big.

## Learning-rate schedules

Big steps help early; small steps help to settle at the end. A **schedule** lowers the learning rate during training:

```python
model = make_model()
opt = torch.optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=20)
rates = []
for epoch in range(20):
    # ... one epoch of training would go here ...
    rates.append(opt.param_groups[0]["lr"])
    opt.step()          # (an optimiser step must come before the scheduler step)
    scheduler.step()    # once per epoch
plt.plot(rates)
plt.title("Cosine learning-rate schedule")
plt.xlabel("epoch")
plt.show()
```

The cosine schedule glides smoothly from 0.1 down to almost 0. `StepLR` (divide by 10 every few epochs) and `OneCycleLR` (warm up, then cool down) are other common choices.

## Weight decay and AdamW

Optimisers can also gently pull weights towards zero every step — **weight decay**, the deep-learning version of Ridge regularisation. With Adam, use `torch.optim.AdamW(params, lr=1e-3, weight_decay=0.01)`, which applies it correctly. More in the next lesson.

## Key terms

- **SGD** — stochastic gradient descent on mini-batches.
- **Momentum** — keeps a running "velocity" so steps build up speed.
- **Adam / AdamW** — adaptive step size for every weight; AdamW adds proper weight decay.
- **Learning-rate schedule** — lowers the learning rate during training.
- **Diverging** — the loss grows instead of shrinking, often because the learning rate is too big.

**Takeaway:** Adam with a learning rate near 0.001 is a strong default; the learning rate is the single most important setting, and a schedule helps to finish training well.

## Try it yourself

1. Add `"Adam lr=0.01"` to the comparison. Where does it land?
2. Use `torch.optim.SGD(p, lr=0.1, momentum=0.9)`. Is it better or worse than plain SGD at 0.1?
3. Put the cosine scheduler into a real training run with SGD + momentum and compare the final validation accuracy.
4. Find the largest Adam learning rate that still trains smoothly on the digits.
""",
            "quiz": [
                ("What does momentum add to SGD?",
                 ["Random noise", "A running velocity so consistent gradients build up speed", "More layers", "A new loss"],
                 1, "Like a ball rolling downhill."),
                ("What is special about Adam?",
                 ["It needs no gradients", "It adapts the step size for every weight automatically", "It only works on CPUs", "It removes the learning rate"],
                 1, "Adaptive per-weight step sizes."),
                ("What is a common default learning rate for Adam?",
                 ["10", "1", "0.001", "0.0000001"],
                 2, "Around 1e-3."),
                ("The training loss suddenly grows and becomes nan. What is the most likely cause?",
                 ["The learning rate is too large", "The batch is too small", "The data is too clean", "Too few epochs"],
                 0, "Too-big steps make training diverge."),
                ("What does a learning-rate schedule do?",
                 ["Changes the learning rate during training, usually lowering it", "Changes the model architecture", "Shuffles the data", "Deletes old weights"],
                 0, "Big steps early, small steps late."),
                ("Which optimiser applies weight decay correctly for Adam-style training?",
                 ["SGD", "AdamW", "Momentum", "Softmax"],
                 1, "AdamW decouples weight decay."),
            ],
        },
        # ------------------------------------------------------------------ 9
        {
            "title": "Overfitting: Dropout, Weight Decay and Early Stopping",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=mFZazxxCKbw",
            "content": r"""
**Learning objective:** Recognise overfitting in learning curves and fight it with dropout, weight decay and early stopping.

## Big networks memorise

Neural networks have many parameters, so with little data they can simply **memorise** the training examples — including their noise. The signs are the same as in Machine Learning Fundamentals: training results keep improving while validation results get worse.

To make overfitting easy to see, we train a large network (more than 80,000 weights) on only **200** digit images:

```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

digits = load_digits()
X, y = digits.data / 16.0, digits.target
X_rest, X_val, y_rest, y_val = train_test_split(X, y, test_size=0.5, random_state=0, stratify=y)
X_small, _, y_small, _ = train_test_split(X_rest, y_rest, train_size=200, random_state=0, stratify=y_rest)
Xs, ys = torch.tensor(X_small, dtype=torch.float32), torch.tensor(y_small)
Xv, yv = torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val)

def big_net(dropout=0.0):
    return nn.Sequential(
        nn.Linear(64, 256), nn.ReLU(), nn.Dropout(dropout),
        nn.Linear(256, 256), nn.ReLU(), nn.Dropout(dropout),
        nn.Linear(256, 10))

def train(dropout=0.0, weight_decay=0.0, epochs=300, seed=0):
    torch.manual_seed(seed)
    model = big_net(dropout)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=weight_decay)
    train_loss, val_loss = [], []
    for epoch in range(epochs):
        model.train()
        perm = torch.randperm(len(Xs))
        for start in range(0, len(perm), 32):
            idx = perm[start:start + 32]
            opt.zero_grad()
            F.cross_entropy(model(Xs[idx]), ys[idx]).backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            train_loss.append(F.cross_entropy(model(Xs), ys).item())
            val_loss.append(F.cross_entropy(model(Xv), yv).item())
    with torch.no_grad():
        val_acc = (model(Xv).argmax(1) == yv).float().mean().item()
    return train_loss, val_loss, val_acc

tr, va, acc = train()
best = int(np.argmin(va))
print(f"best validation loss {min(va):.3f} at epoch {best}; at the end {va[-1]:.3f}")
print("final training loss:", round(tr[-1], 4), " validation accuracy:", round(acc, 3))
plt.plot(tr, label="training loss")
plt.plot(va, label="validation loss")
plt.axvline(best, color="grey", ls="--")
plt.legend()
plt.show()
```

The training loss falls to almost **zero** — the network has memorised the 200 images. The validation loss is lowest after roughly **30–40 epochs** and then **rises** again as the network becomes over-confident on what it memorised.

## Tool 1 — Early stopping

The simplest cure: stop when the validation loss stops improving, and keep the **best** weights.

```python
import copy

def train_early_stopping(patience=20, max_epochs=300, seed=0):
    torch.manual_seed(seed)
    model = big_net()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.0)
    best_loss, best_state, waited = float("inf"), None, 0
    for epoch in range(max_epochs):
        model.train()
        perm = torch.randperm(len(Xs))
        for start in range(0, len(perm), 32):
            idx = perm[start:start + 32]
            opt.zero_grad()
            F.cross_entropy(model(Xs[idx]), ys[idx]).backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            v = F.cross_entropy(model(Xv), yv).item()
        if v < best_loss:
            best_loss, best_state, waited = v, copy.deepcopy(model.state_dict()), 0
        else:
            waited += 1
            if waited >= patience:
                print("stopped at epoch", epoch)
                break
    model.load_state_dict(best_state)
    return model, best_loss

model, best_loss = train_early_stopping()
print("best validation loss kept:", round(best_loss, 3))
```

**Patience** is how many epochs to wait for an improvement before giving up. Early stopping also saves a lot of training time.

## Tool 2 — Dropout

**Dropout** switches off a random share of neurons (for example 50%) at every training step. No neuron can rely on one particular partner, so the network learns more robust, spread-out features — like a football team that trains with random players missing. At prediction time (`model.eval()`) all neurons are used again.

```python
layer = nn.Dropout(0.5)
x = torch.ones(1, 8)
layer.train(); print("training:", layer(x))
layer.eval();  print("evaluating:", layer(x))
```

During training about half the values become 0 and the rest are doubled (so the average stays the same). In eval mode nothing changes.

## Tool 3 — Weight decay

**Weight decay** shrinks every weight a little at each step (the `weight_decay` setting of AdamW) — the same idea as Ridge regression. Smaller weights mean a smoother, simpler function.

## Compare them

```python
for name, kwargs in [("no regularisation", {}),
                     ("dropout 0.5", {"dropout": 0.5}),
                     ("weight decay 1e-3", {"weight_decay": 1e-3}),
                     ("dropout + weight decay", {"dropout": 0.5, "weight_decay": 1e-3})]:
    tr, va, acc = train(**kwargs)
    print(f"{name:24s} best val loss {min(va):.3f}  final val loss {va[-1]:.3f}  val acc {acc:.3f}")
```

Dropout clearly lowers the validation loss. Weight decay of 0.001 changes little on its own here (try 0.01), and dropout plus weight decay ends with the lowest validation loss and the best accuracy. The accuracy differences are small here because the digits are easy — on harder data, regularisation often decides whether a model is usable at all.

## The most powerful cure: more data

Regularisation helps, but nothing beats **more and more varied training data**. When collecting more is impossible, you can create variations of the data you have — **data augmentation**, Lesson 15.

## Key terms

- **Overfitting** — memorising training data instead of learning general patterns.
- **Early stopping** — stop when validation loss stops improving and keep the best weights.
- **Patience** — epochs to wait for improvement before stopping.
- **Dropout** — randomly switching off neurons during training.
- **Weight decay** — shrinking weights a little at each step.

**Takeaway:** Watch the validation curve: early stopping, dropout and weight decay keep big networks from memorising, and more data is the strongest cure of all.

## Try it yourself

1. Train with 800 training images instead of 200. Does the network still overfit as badly?
2. Try dropout rates 0.2, 0.5 and 0.8. Which is too much?
3. Change patience to 5 and to 50. How do the stopping epoch and the best loss change?
4. Plot the training and validation loss for "dropout + weight decay" on the same chart as "no regularisation".
""",
            "quiz": [
                ("Training loss is near 0 but validation loss is rising. What is happening?",
                 ["Underfitting", "Overfitting", "The data is unlabelled", "The learning rate is zero"],
                 1, "The network memorised the training set."),
                ("What does early stopping keep?",
                 ["The last weights", "The weights from the epoch with the best validation loss", "Random weights", "Only the biases"],
                 1, "Restore the best state at the end."),
                ("What does dropout do during training?",
                 ["Deletes training examples", "Randomly switches off a share of neurons at each step", "Lowers the learning rate", "Removes layers forever"],
                 1, "Neurons cannot rely on specific partners."),
                ("What happens to dropout in model.eval() mode?",
                 ["It drops even more neurons", "It is switched off and all neurons are used", "It crashes", "It halves every output"],
                 1, "Dropout only acts during training."),
                ("Weight decay is most similar to which classic method?",
                 ["k-means", "Ridge (L2) regularisation", "Decision trees", "PCA"],
                 1, "Both shrink weights towards zero."),
                ("What is usually the strongest cure for overfitting?",
                 ["More and more varied training data", "A bigger learning rate", "Fewer validation examples", "Training longer"],
                 0, "Data beats tricks."),
            ],
        },
        # ------------------------------------------------------------------ 10
        {
            "title": "Initialisation, Batch Norm and Vanishing Gradients",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=P6sfmUTpUmc",
            "content": r"""
**Learning objective:** Explain why gradients can vanish in deep networks, measure it, and fix it with ReLU, good initialisation, batch normalisation and residual connections.

## Why deep networks were hard to train

Until about 2010, networks with more than a few layers barely learned. The reason is in backpropagation: the gradient for an early layer is a **product** of many local slopes, one per layer. The sigmoid's slope is at most 0.25. Multiply ten numbers of 0.25 or less and you get almost nothing — the early layers receive no learning signal. This is the **vanishing gradient** problem. (If the slopes are bigger than 1, gradients can **explode** instead.)

## Measure it

We build a 10-layer network, run one backward pass, and print the average gradient size of each layer, from the first to the last:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.datasets import load_digits

digits = load_digits()
X = torch.tensor(digits.data[:200] / 16.0, dtype=torch.float32)
y = torch.tensor(digits.target[:200])

def deep_net(activation, he_init=False, batch_norm=False, depth=10):
    torch.manual_seed(0)
    layers = []
    for i in range(depth):
        linear = nn.Linear(64, 64)
        if he_init:
            nn.init.kaiming_normal_(linear.weight, nonlinearity="relu")
            nn.init.zeros_(linear.bias)
        layers.append(linear)
        if batch_norm:
            layers.append(nn.BatchNorm1d(64))
        layers.append(activation())
    layers.append(nn.Linear(64, 10))
    return nn.Sequential(*layers)

def gradient_sizes(model):
    F.cross_entropy(model(X), y).backward()
    return [f"{m.weight.grad.abs().mean().item():.0e}" for m in model if isinstance(m, nn.Linear)]

print("sigmoid:         ", gradient_sizes(deep_net(nn.Sigmoid)))
print("ReLU + He init:  ", gradient_sizes(deep_net(nn.ReLU, he_init=True)))
print("sigmoid + BN:    ", gradient_sizes(deep_net(nn.Sigmoid, batch_norm=True)))
```

What you should see:

- **Sigmoid:** the first layer's gradients are around **0.00000000001** (1e-11), while the last layer's are around 0.01 — a difference of about a billion times. The early layers cannot learn.
- **ReLU with He initialisation:** every layer's gradient is about the same size (around 1e-3). Healthy.
- **Sigmoid with batch normalisation:** also healthy, even with the sigmoid.

## Fix 1 — ReLU

ReLU's slope is exactly 1 for positive inputs, so it does not shrink the gradient as it passes through. That simple change is a big part of why "deep" learning took off.

## Fix 2 — Good initialisation

Weights should start at a size that keeps signals from shrinking or growing from layer to layer:

- **He (Kaiming) initialisation** for ReLU: random normal with variance 2 ÷ (number of inputs).
- **Xavier (Glorot) initialisation** for tanh/sigmoid: variance about 1 ÷ (number of inputs).

PyTorch's layers already use sensible defaults; for very deep ReLU networks, `nn.init.kaiming_normal_` makes it explicit. This is also why you scaled weights by √(2/64) in the Week 1 project.

## Fix 3 — Batch normalisation

**Batch norm** standardises each neuron's outputs over the current mini-batch (mean 0, standard deviation 1 — like StandardScaler, but inside the network), then lets the network learn its own scale and shift. It keeps every layer's inputs in a healthy range, allows bigger learning rates and often speeds training up a lot.

```python
bn = nn.BatchNorm1d(3)
batch = torch.tensor([[1.0, 200.0, -5.0], [3.0, 400.0, -1.0], [5.0, 600.0, 3.0]])
bn.train()
print(bn(batch).detach().round(decimals=2))
```

Each column comes out with mean 0 and similar spread, whatever its original scale. Like dropout, batch norm behaves differently in `train()` and `eval()` mode: at prediction time it uses averages remembered from training.

## Fix 4 — Residual connections

A **residual** (skip) connection adds a block's input to its output: output = x + block(x). The gradient can flow straight through the "+" — a highway past the layers. Residual networks (**ResNets**, 2015) made networks with 100+ layers trainable, and every transformer uses them too.

```python
class ResidualBlock(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(width, width), nn.ReLU(), nn.Linear(width, width))

    def forward(self, x):
        return F.relu(x + self.layers(x))      # the skip connection

block = ResidualBlock(64)
print(block(torch.randn(5, 64)).shape)
```

## Exploding gradients and clipping

When gradients explode (common in recurrent networks, Week 4), **gradient clipping** caps their size before the update:

```python
model = deep_net(nn.ReLU, he_init=True)
F.cross_entropy(model(X), y).backward()
total = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
print("gradient size before clipping:", round(total.item(), 3))
```

Put it between `loss.backward()` and `optimizer.step()`.

## Key terms

- **Vanishing gradient** — gradients shrink towards zero in early layers, so they stop learning.
- **Exploding gradient** — gradients grow huge and make training unstable.
- **He / Xavier initialisation** — starting weight sizes that keep signals healthy.
- **Batch normalisation** — standardising layer outputs over each mini-batch.
- **Residual connection** — adding a block's input to its output.
- **Gradient clipping** — capping the gradient size.

**Takeaway:** Deep networks train well when gradients can flow: use ReLU, sensible initialisation, batch normalisation and skip connections, and clip gradients if they explode.

## Try it yourself

1. Repeat the measurement with `nn.Tanh`. Is it better or worse than sigmoid?
2. Use ReLU **without** He initialisation (the PyTorch default). How do the gradient sizes compare?
3. Train the 10-layer sigmoid network with and without batch norm on the digits for 20 epochs. Compare validation accuracy.
4. Stack four `ResidualBlock`s after an input layer and train them on the digits.
""",
            "quiz": [
                ("Why do gradients vanish in deep sigmoid networks?",
                 ["The data is too big", "Many small slopes (at most 0.25) are multiplied together", "ReLU is missing from the data", "The test set is small"],
                 1, "The product of many small numbers is tiny."),
                ("Why does ReLU help with vanishing gradients?",
                 ["Its slope is 1 for positive inputs, so it does not shrink the gradient", "It removes layers", "It adds noise", "It makes the network smaller"],
                 0, "Gradients pass through unchanged where the neuron is active."),
                ("Which initialisation is designed for ReLU networks?",
                 ["Zero initialisation", "He (Kaiming) initialisation", "All ones", "Random text"],
                 1, "Variance 2 ÷ inputs."),
                ("What does batch normalisation do?",
                 ["Deletes small batches", "Standardises layer outputs over each mini-batch", "Changes the labels", "Sorts the data"],
                 1, "Like StandardScaler inside the network."),
                ("What does a residual connection compute?",
                 ["block(x) only", "x + block(x)", "x × 0", "The loss"],
                 1, "The skip path lets gradients flow."),
                ("Where does gradient clipping go in the training step?",
                 ["Before the forward pass", "Between loss.backward() and optimizer.step()", "After saving the model", "Inside the dataset"],
                 1, "Clip the computed gradients, then update."),
            ],
        },
        # ------------------------------------------------------------------ 11
        {
            "title": "Datasets, DataLoaders and Tabular Data",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=V_xro1bcAuA",
            "content": r"""
**Learning objective:** Feed data to PyTorch with `Dataset` and `DataLoader`, prepare tabular data correctly, and split data into training, validation and test sets.

## Why not just slice tensors?

Until now we shuffled indices by hand. Real projects use PyTorch's two data tools:

- **Dataset** — knows how many examples there are and how to get example number i.
- **DataLoader** — wraps a Dataset and gives you shuffled **mini-batches**, optionally loading them in parallel.

Images that do not fit in memory, text files, audio — all are handled the same way: write a Dataset, wrap it in a DataLoader, and the training loop never changes.

## The loans data again

We use the mobile-money micro-loans data from Machine Learning Fundamentals: predict `defaulted` (1 = did not repay).

{LOANS}

## Prepare tabular data for a network

Networks are as sensitive to scale as k-NN: income in hundreds of thousands next to a 0/1 column would make training slow and unstable. **Standardise**, using the training rows only:

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X = loans.drop(columns="defaulted").to_numpy()
y = loans["defaulted"].to_numpy()
X_dev, X_test, y_dev, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_dev, y_dev, test_size=0.2, random_state=42, stratify=y_dev)

scaler = StandardScaler().fit(X_train)            # learn from training rows only
X_train, X_val, X_test = (scaler.transform(a) for a in (X_train, X_val, X_test))
print(len(X_train), len(X_val), len(X_test))
```

## A custom Dataset

```python
import torch
from torch.utils.data import Dataset, DataLoader

class LoanDataset(Dataset):
    def __init__(self, features, labels):
        self.x = torch.tensor(features, dtype=torch.float32)
        self.y = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return self.x[i], self.y[i]

train_ds = LoanDataset(X_train, y_train)
print(len(train_ds), train_ds[0])
```

Only two methods are needed: `__len__` and `__getitem__`.

## A DataLoader

```python
train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
val_loader = DataLoader(LoanDataset(X_val, y_val), batch_size=256)

xb, yb = next(iter(train_loader))
print(xb.shape, yb.shape)          # one batch: 64 rows of 5 features
print("batches per epoch:", len(train_loader))
```

- `shuffle=True` for training (a new order every epoch); no shuffling for validation and test.
- `num_workers=2` loads batches in parallel — useful for images on disk.
- For data already in tensors, `TensorDataset(x, y)` saves writing a class.

## Train with the loader

```python
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)
model = nn.Sequential(nn.Linear(5, 32), nn.ReLU(), nn.Linear(32, 1))
opt = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(30):
    model.train()
    for xb, yb in train_loader:                 # the loop is now very clean
        opt.zero_grad()
        loss = F.binary_cross_entropy_with_logits(model(xb).squeeze(1), yb)
        loss.backward()
        opt.step()

model.eval()
with torch.no_grad():
    val_logits = torch.cat([model(xb).squeeze(1) for xb, _ in val_loader])
val_acc = ((val_logits > 0).float().numpy() == y_val).mean()
print("validation accuracy:", round(val_acc, 3))
```

## Categories in tabular networks

For a column such as district, either one-hot encode it (as in Machine Learning Fundamentals) or use an **embedding** layer that learns a small vector for each category — the same idea used for words in Week 4.

## Should you use a network for tables?

Honest advice from industry and research: on ordinary tables of a few thousand rows, **gradient boosting and logistic regression are usually as good or better** than neural networks, and they are faster and easier to explain. Networks shine with images, sound, text and very large or mixed datasets. The next lesson's project tests this claim.

## Key terms

- **Dataset** — gives the number of examples and example i.
- **DataLoader** — turns a Dataset into shuffled mini-batches.
- **TensorDataset** — a ready-made Dataset for tensors.
- **Batch size** — examples per update.
- **Embedding** — a learned vector for each category.

**Takeaway:** Wrap your data in a Dataset and a DataLoader, scale features with training statistics only, and the same clean training loop works for any data.

## Try it yourself

1. Replace `LoanDataset` with `TensorDataset` and check that training gives the same result.
2. Train with batch sizes 8, 64 and 512. How do speed and validation accuracy change?
3. Remove the StandardScaler and train again. What happens?
4. Add the engineered feature `loan_to_income` from Machine Learning Fundamentals before scaling. Does the network improve?
""",
            "quiz": [
                ("Which two methods must a custom Dataset have?",
                 ["fit and predict", "__len__ and __getitem__", "forward and backward", "train and eval"],
                 1, "Size and how to fetch example i."),
                ("What does a DataLoader provide?",
                 ["A trained model", "Shuffled mini-batches from a Dataset", "A loss function", "Plots"],
                 1, "It batches and shuffles."),
                ("Which loader should shuffle?",
                 ["Only the training loader", "Only the test loader", "Neither", "Both validation and test"],
                 0, "Evaluation order does not matter."),
                ("Why standardise tabular features for a network?",
                 ["Features with big numbers would make training slow and unstable", "Networks cannot read decimals", "To add labels", "It is not needed"],
                 0, "Similar scales help gradient descent."),
                ("Where must the scaler learn its mean and standard deviation?",
                 ["From all the data", "From the training rows only", "From the test rows", "From the labels"],
                 1, "Otherwise test information leaks."),
                ("For a small table of a few thousand rows, which is often as good or better than a neural network?",
                 ["Gradient boosting or logistic regression", "A CNN", "An LSTM", "A transformer"],
                 0, "Networks shine on images, sound and text."),
            ],
        },
        # ------------------------------------------------------------------ 12
        {
            "title": "Week 2 Project: A Neural Network for Loan Risk",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=V_xro1bcAuA",
            "content": r"""
**Learning objective:** Build a complete, well-trained neural network for a real business problem — with a validation set, early stopping and a fair baseline — and report honestly whether deep learning was worth it.

## The brief

The SACCO from Machine Learning Fundamentals heard that "AI with neural networks" beats everything. Your job: test the claim fairly on its micro-loan data and recommend what to use.

{LOANS}

## Part 1 — Prepare (train / validation / test)

```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import copy
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from torch.utils.data import TensorDataset, DataLoader

loans["loan_to_income"] = loans["loan_rwf"] / loans["income_rwf"]
X = loans.drop(columns="defaulted").to_numpy()
y = loans["defaulted"].to_numpy()
X_dev, X_test, y_dev, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_dev, y_dev, test_size=0.2, random_state=42, stratify=y_dev)
scaler = StandardScaler().fit(X_train)
X_train, X_val, X_test = (scaler.transform(a) for a in (X_train, X_val, X_test))
t = lambda a: torch.tensor(a, dtype=torch.float32)
train_loader = DataLoader(TensorDataset(t(X_train), t(y_train)), batch_size=64, shuffle=True)
```

## Part 2 — The network, with dropout and batch norm

```python
class LoanNet(nn.Module):
    def __init__(self, n_features, hidden=64, dropout=0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden), nn.BatchNorm1d(hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(hidden, hidden), nn.BatchNorm1d(hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(hidden, 1))

    def forward(self, x):
        return self.net(x).squeeze(1)
```

## Part 3 — Train with early stopping on validation AUC

```python
def val_auc(model):
    model.eval()
    with torch.no_grad():
        return roc_auc_score(y_val, model(t(X_val)).numpy())

torch.manual_seed(0)
model = LoanNet(X_train.shape[1])
opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
best_auc, best_state, waited, history = 0, None, 0, []
for epoch in range(200):
    model.train()
    for xb, yb in train_loader:
        opt.zero_grad()
        F.binary_cross_entropy_with_logits(model(xb), yb).backward()
        opt.step()
    auc = val_auc(model)
    history.append(auc)
    if auc > best_auc:
        best_auc, best_state, waited = auc, copy.deepcopy(model.state_dict()), 0
    else:
        waited += 1
        if waited >= 20:
            break
model.load_state_dict(best_state)
print(f"stopped after {len(history)} epochs, best validation AUC {best_auc:.3f}")
```

## Part 4 — The fair comparison

Both models see exactly the same training rows and are judged once on the same test rows:

```python
from sklearn.linear_model import LogisticRegression

logreg = LogisticRegression().fit(X_train, y_train)
model.eval()
with torch.no_grad():
    nn_scores = model(t(X_test)).numpy()
print("Neural network test AUC:     ", round(roc_auc_score(y_test, nn_scores), 3))
print("Logistic regression test AUC:", round(roc_auc_score(y_test, logreg.predict_proba(X_test)[:, 1]), 3))
```

Expect the two to be **very close** (both around 0.86–0.88). That is the honest result: the loans were created by a fairly simple rule, and logistic regression already captures it. The network adds complexity — thousands of weights, more settings, harder explanations — without a clear gain.

## Part 5 — Recommendation (one page)

1. The question and the data.
2. The network: layers, dropout, batch norm, optimiser, early stopping (with the learning curve).
3. A table of test AUC for both models.
4. Your recommendation, with reasons: accuracy, simplicity, explainability to borrowers and regulators, cost of running.
5. When the SACCO **should** consider deep learning (for example: millions of transactions, text from customer messages, or images of documents).

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Method | Train / validation / test split; scaler fitted on training rows |
| Training | Early stopping on validation with best weights restored |
| Fairness | Same data and test set for both models; test used once |
| Judgement | Honest conclusion, even if the network does not win |
| Communication | Clear recommendation a board can act on |

**Takeaway:** A good engineer uses deep learning where it adds value — and proves it with a fair baseline instead of assuming it.

## Try it yourself

Complete Parts 1–5. Then remove `loan_to_income` and retrain both models. Which one suffers more without the engineered feature, and why might that be?
""",
            "quiz": [
                ("Why does the project use a separate validation set?",
                 ["To choose when to stop training without touching the test set", "To train faster", "Because PyTorch requires three sets", "To increase AUC"],
                 0, "The test set stays untouched until the end."),
                ("What is restored when early stopping ends?",
                 ["The first weights", "The weights with the best validation AUC", "Random weights", "The logistic regression"],
                 1, "Best state, not last state."),
                ("Which layer types help this network generalise?",
                 ["Dropout and batch normalisation", "Softmax and pooling", "Convolution and LSTM", "Embedding only"],
                 0, "Both appear in LoanNet."),
                ("The network and logistic regression both score about 0.87 AUC. What is the best recommendation?",
                 ["Always use the network because it is AI", "Prefer the simpler logistic regression unless the network clearly wins", "Use neither", "Average them blindly"],
                 1, "Simpler and explainable wins a tie."),
                ("When would deep learning be worth trying for the SACCO?",
                 ["Never", "With very large data or images and text, such as customer messages", "Only with 50 rows", "Only for printing reports"],
                 1, "Deep learning shines on unstructured data."),
                ("Why are both models judged on the same test rows?",
                 ["So the comparison is fair", "To save memory", "Because the scaler needs it", "It does not matter"],
                 0, "Different test sets would make the comparison meaningless."),
            ],
        },
    ],
}

for _lesson in WEEK2["lessons"]:
    _lesson["content"] = (_lesson["content"].replace("{DIGITS}", DIGITS)
                          .replace("{LOANS}", LOANS_DATA))
