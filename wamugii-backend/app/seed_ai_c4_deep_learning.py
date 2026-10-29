"""
WAMUGII AI Program — Course 4: "Deep Learning & Neural Networks".
University-level, original WAMUGII content in simple English.
Run:  python -m app.seed_ai_c4_deep_learning
"""

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.models.course import CourseStatus
from app.schemas.course import CourseCreate, LessonCreate

COURSE_SLUG = "deep-learning-neural-networks"

COURSE = CourseCreate(
    title="Deep Learning & Neural Networks",
    slug=COURSE_SLUG,
    category="Artificial Intelligence",
    is_free=True,
    status=CourseStatus.PUBLISHED,
    display_order=5,
    description=(
        "Course 4 of the WAMUGII AI Program. Understand and build neural "
        "networks — the technology behind modern image, speech and language AI. "
        "From a single neuron to deep networks, you'll learn activation "
        "functions, how networks learn through loss and gradient descent, "
        "backpropagation, and the main architectures (CNNs for images, RNNs for "
        "sequences) — plus how to train them well. Simple English, clear "
        "intuition, and a hands-on project. By the end you can build and train a "
        "simple neural network."
    ),
)

LESSONS = [
    {
        "title": "4.1 From a Neuron to a Network",
        "content": """\
**Learning objective:** Understand the artificial neuron (perceptron) and how
stacking neurons forms a network.

## The artificial neuron

A neural network is built from tiny units called **neurons**. One neuron does
three simple things:

1. **Multiply** each input by a **weight**.
2. **Add** them all up (plus a bias) — this is the dot product from Course 2.
3. Pass the result through an **activation function** to get the output.

```
output = activation( x1*w1 + x2*w2 + x3*w3 + b )
```

A single neuron is basically the logistic regression you already know from
Course 3.

## Why stack neurons into layers

One neuron can only learn simple, straight-line patterns. Real problems are
complex. So we arrange neurons in **layers**:

- **Input layer** — your features enter here.
- **Hidden layers** — the "thinking" layers in the middle that find patterns.
- **Output layer** — the final prediction.

Each neuron connects to the neurons in the next layer. A network with several
hidden layers is a **deep** network — hence **deep learning**.

## Why depth is powerful

Early layers learn **simple patterns** (edges in an image); later layers combine
them into **complex patterns** (a shape, then a face). The network builds
understanding in stages, which is why deep networks can handle images, speech, and
language that older methods could not.

## Key terms

**Neuron / perceptron**, **Weight**, **Bias**, **Activation function**, **Layer
(input/hidden/output)**, **Deep network**.

## Practice

Draw (on paper) a small network: 3 inputs, one hidden layer of 4 neurons, and 1
output. How many weights connect the input layer to the hidden layer? (Hint:
every input connects to every hidden neuron.)
""",
    },
    {
        "title": "4.2 Activation Functions",
        "content": """\
**Learning objective:** Understand why activation functions exist and know the
main ones and when to use them.

## Why we need them

Without an activation function, a neuron is just a weighted sum — a straight line.
Stacking many straight lines still gives a straight line, so the network could
never learn curves or complex patterns. The **activation function adds
non-linearity**, letting the network bend and learn complex shapes. It is the
single reason deep networks are powerful.

## The main activation functions

- **ReLU (Rectified Linear Unit)** — `max(0, x)`. If the input is negative, output
  0; otherwise pass it through. Simple and fast; the **default for hidden
  layers**.
- **Sigmoid** — squashes to a probability between 0 and 1. Used in the **output
  layer for binary classification** (as in logistic regression).
- **Softmax** — turns several outputs into probabilities that add up to 1. Used in
  the **output layer for multi-class classification** ("is this a cat, dog, or
  bird?").
- **Tanh** — squashes to between −1 and +1; sometimes used in hidden layers.

## A simple rule of thumb

- Hidden layers → **ReLU**.
- Output, two classes → **Sigmoid**.
- Output, many classes → **Softmax**.
- Output, a number (regression) → **no activation** (plain value).

## Key terms

**Activation function**, **Non-linearity**, **ReLU**, **Sigmoid**, **Softmax**,
**Tanh**.

## Practice

For each network, name the output activation: (a) predict if an X-ray shows
pneumonia (yes/no); (b) classify a photo as one of 10 animals; (c) predict
tomorrow's temperature in °C.
""",
    },
    {
        "title": "4.3 How Networks Learn — Loss and Gradient Descent",
        "content": """\
**Learning objective:** Understand how a network measures its error and improves,
connecting directly to the calculus from Course 2.

## The learning loop

A neural network learns by repeating this loop many times:

1. **Forward pass** — feed inputs through the network to get a prediction.
2. **Compute the loss** — measure how wrong the prediction is.
3. **Backward pass** — work out how each weight contributed to the error
   (backpropagation, next lesson).
4. **Update the weights** — nudge each weight to reduce the loss (gradient
   descent).

Repeat over the whole dataset many times. Each full pass is called an **epoch**.

## The loss function

The **loss** is a single number saying how wrong the network is right now.

- **Classification** → *cross-entropy* loss.
- **Regression** → *mean squared error* loss.

Training has one goal: **make the loss as small as possible.**

## Gradient descent (from Course 2)

To shrink the loss, we use **gradient descent**: compute the gradient (the uphill
direction of the loss) and step the **opposite** way — downhill.

> new weight = old weight − (learning rate × gradient)

The **learning rate** sets the step size. Too high → the training overshoots and
becomes unstable. Too low → it learns painfully slowly. Choosing it well is part
of the craft.

## Batches

We usually don't use the whole dataset for every step. We use small **batches**
(e.g. 32 examples at a time). This is faster and helps training. One pass through
all batches = one **epoch**.

## Key terms

**Forward pass**, **Loss**, **Cross-entropy**, **Gradient descent**, **Learning
rate**, **Epoch**, **Batch**.

## Practice

A model trains for 50 epochs. The loss drops fast, then jumps up and down wildly
and never settles. What is the most likely cause, and what one setting would you
change first?
""",
    },
    {
        "title": "4.4 Backpropagation (Intuition)",
        "content": """\
**Learning objective:** Understand, in plain language, how a network figures out
which weights to change — without heavy maths.

## The problem backpropagation solves

A deep network has thousands or millions of weights. When the prediction is wrong,
how does it know **which weights** to blame, and by how much? That is what
**backpropagation** ("backprop") answers.

## The idea — assign blame backwards

1. The error is measured at the **output**.
2. Backprop passes that error **backwards** through the network, layer by layer.
3. At each layer, it works out **how much each weight contributed** to the error.
4. Weights that pushed the answer in the wrong direction get adjusted more.

Think of a team that produced a wrong result. You trace back: the final step was
off *because* an earlier step was off, *because* an earlier one was. Backprop
spreads responsibility back through the whole chain.

## The chain rule (named, not drilled)

Mathematically, backprop uses the **chain rule** of calculus to connect the final
error to each weight through all the layers in between. You don't compute this by
hand — **frameworks like TensorFlow and PyTorch do backprop automatically.** Your
job is to understand *what* it does: it provides the gradient that gradient
descent (Lesson 4.3) then uses to update every weight.

## The two work together

- **Backpropagation** → computes *which direction* each weight should move.
- **Gradient descent** → actually *takes the step*.

Together they are the engine that trains every neural network.

## Key terms

**Backpropagation**, **Blame / credit assignment**, **Chain rule**, **Automatic
differentiation**.

## Practice

Explain to a friend, in 3–4 sentences and no maths, how a neural network decides
which of its many weights to change after a wrong prediction. Use the "trace the
blame backwards" picture.
""",
    },
    {
        "title": "4.5 Building a Neural Network",
        "content": """\
**Learning objective:** Build and train a simple neural network with Keras, seeing
how the ideas become a few lines of code.

## Frameworks do the hard parts

You will not code backprop or gradient descent by hand — **Keras** (part of
TensorFlow) and **PyTorch** do that for you. You describe the network; the
framework trains it.

## A small network in Keras

```python
from tensorflow import keras
from tensorflow.keras import layers

model = keras.Sequential([
    layers.Dense(16, activation="relu", input_shape=(3,)),  # hidden layer
    layers.Dense(8,  activation="relu"),                    # hidden layer
    layers.Dense(1,  activation="sigmoid"),                 # output: yes/no
])

model.compile(optimizer="adam",
              loss="binary_crossentropy",
              metrics=["accuracy"])

model.fit(X_train, y_train, epochs=20, batch_size=32,
          validation_split=0.2)

model.evaluate(X_test, y_test)
```

## Reading the code

- `Dense` — a normal fully-connected layer; the number is how many neurons.
- `activation` — ReLU in hidden layers, sigmoid for a yes/no output (Lesson 4.2).
- `optimizer="adam"` — a smart version of gradient descent (a good default).
- `loss` — how error is measured (binary cross-entropy for yes/no).
- `epochs` — how many times to pass over the data.
- `validation_split` — hold back 20% to watch for overfitting while training.

## The shape of the network mirrors the problem

- **Input shape** = number of features.
- **Output layer** = your target: 1 sigmoid (yes/no), N softmax (N classes), or 1
  plain unit (a number).

## Key terms

**Keras / TensorFlow**, **Sequential**, **Dense layer**, **compile**, **optimizer
(Adam)**, **epochs**, **validation_split**.

## Practice

Write (in Keras style) the first and last layers for a network that takes **10
features** and classifies into **4 categories**. State the input shape, the output
layer size, and its activation.
""",
    },
    {
        "title": "4.6 Convolutional Neural Networks (Images)",
        "content": """\
**Learning objective:** Understand why images need a special kind of network and
how CNNs see.

## Why images are different

An image is a grid of pixels — a 200×200 colour photo has 120,000 numbers. Feeding
those straight into a normal network is wasteful and ignores an important fact:
**nearby pixels belong together.** A different design is needed.

## The convolution idea

A **Convolutional Neural Network (CNN)** slides a small window (a **filter**)
across the image, looking for a **local pattern** — an edge, a corner, a colour
blob. The same filter is used all over the image, so the network learns "an edge
is an edge wherever it appears."

- **Early layers** detect simple patterns: edges, lines.
- **Middle layers** combine them: shapes, textures.
- **Late layers** combine those: eyes, wheels, whole objects.

This mirrors how the network builds understanding in stages (Lesson 4.1).

## Pooling

Between convolutions, **pooling** shrinks the image (e.g. keeps the strongest
value in each small region). This keeps the important information, reduces the
numbers to process, and makes the network robust to small shifts.

## A typical CNN

```
Image → [Convolution → ReLU → Pooling] × several → Flatten → Dense → Output
```

## Where CNNs are used

Medical image diagnosis, crop-disease detection from leaf photos, face
recognition, number-plate reading, quality inspection — anywhere the input is an
image.

## Key terms

**CNN**, **Filter / kernel**, **Convolution**, **Pooling**, **Feature map**,
**Flatten**.

## Practice

Explain in your own words why a CNN is better than a normal network for
recognising a cat in a photo — mention "local patterns" and "the same filter
everywhere."
""",
    },
    {
        "title": "4.7 Recurrent Networks and Sequences",
        "content": """\
**Learning objective:** Understand why sequence data needs memory, and how RNNs
(and their successors) provide it.

## Sequence data is everywhere

Some data comes in an **order**, where earlier items affect later ones:

- **Text** — "the bank of the river" vs "money in the bank"; word order matters.
- **Speech** — sounds in sequence.
- **Time series** — sales day by day, sensor readings over time.

A normal network treats each input independently, so it can't use order. We need
**memory**.

## Recurrent Neural Networks (RNNs)

An **RNN** processes a sequence one step at a time and carries a **hidden state** —
a memory of what it has seen so far — forward to the next step. So when it reads a
word, it remembers the words before it.

```
word1 → [RNN] → memory → [RNN] → memory → [RNN] → output
word2 ───────────┘          │
word3 ──────────────────────┘
```

## The weakness, and the fix

Simple RNNs **forget** things that happened long ago in a long sequence. Improved
versions — **LSTM** and **GRU** — add gates that decide what to keep and what to
forget, so they remember important information for longer.

## The modern successor

Today, most sequence and language tasks use **Transformers** instead of RNNs,
because they handle long sequences better and train faster. That is the subject of
Course 5 — but the problem RNNs were built to solve (understanding order and
context) is exactly what Transformers solve even better.

## Key terms

**Sequence data**, **RNN**, **Hidden state / memory**, **LSTM / GRU**,
**Transformer (next course)**.

## Practice

Give two examples of sequence data from your own life or work where the **order**
of the items changes the meaning. For each, say what would be lost if the order
were ignored.
""",
    },
    {
        "title": "4.8 Training Neural Networks Well",
        "content": """\
**Learning objective:** Apply the practical techniques that make the difference
between a network that works and one that doesn't.

## Deep networks overfit easily

Neural networks have huge numbers of weights, so they **memorise** training data
very easily (Course 3's overfitting, amplified). Most practical skill in deep
learning is about controlling this.

## The key techniques

- **More data.** Deep learning is hungry; more and more varied data is the best
  cure.
- **Data augmentation.** For images, create more training examples by flipping,
  rotating, or cropping existing ones — the network learns to generalise.
- **Dropout.** During training, randomly "switch off" some neurons each step. This
  stops the network relying too much on any one path and reduces overfitting.
  ```python
  layers.Dropout(0.3)   # drop 30% of neurons during training
  ```
- **Early stopping.** Watch the validation loss; when it stops improving and
  starts rising, **stop training** — that is the overfitting point.
- **Normalise inputs.** Scale features (Course 3) so training is stable and fast.

## Watch the two curves

Plot **training loss** and **validation loss** against epochs:

- Both falling together → good, keep going.
- Training keeps falling but validation rises → **overfitting** — stop, or add
  dropout/data.
- Both stuck high → **underfitting** — bigger network, train longer, better
  features.

## Choosing the learning rate

The learning rate is the setting that most often decides success. If training is
unstable, lower it; if it's painfully slow, raise it. Optimisers like **Adam**
adjust it somewhat automatically, which is why they're a good default.

## Key terms

**Dropout**, **Data augmentation**, **Early stopping**, **Validation loss curve**,
**Learning rate**, **Normalisation**.

## Practice

While training, your training accuracy reaches 98% but validation accuracy sits at
74% and is getting worse. Name what's happening and **three** specific things you
would try to fix it.
""",
    },
    {
        "title": "4.9 Project — Train a Neural Network (Assessment)",
        "content": """\
**This is your Course 4 assessment.** You will build, train and evaluate a neural
network, and show you can control overfitting.

## The task

Pick a dataset suitable for a neural network and build one with Keras (or PyTorch).
Good options: a simple image set (e.g. handwritten digits / MNIST, or a small
image folder), or a structured dataset from an earlier course. Produce your code
and a short report.

## Required steps

1. **State the problem** and its type, and why a neural network suits it.
2. **Prepare the data**: scale/normalise inputs; for images, consider **data
   augmentation** (Lesson 4.8). Split into train / validation / test.
3. **Build the network**: choose the layers, the hidden **activations (ReLU)**, and
   the correct **output layer** for your problem (Lesson 4.2).
4. **Train it**: compile with a loss and the Adam optimiser; train for several
   epochs with a **validation split**.
5. **Plot the training and validation loss** over epochs and read the curves
   (Lesson 4.8).
6. **Control overfitting**: if you see it, apply **dropout** and/or **early
   stopping**, and show the before/after.
7. **Evaluate on the test set** with the right metric and report the honest final
   result.

## What good work looks like

- The output layer and loss **match the problem** (sigmoid+binary-crossentropy,
  softmax+categorical-crossentropy, or plain+MSE).
- You **diagnose overfitting from the loss curves**, not by guessing.
- You apply a fix and **show it helped**.
- You report a final test score and state honestly what the model can and can't do.

## Submit

Keep your code, your loss-curve plot, and your report together. Completing this
means you can build and *train* a neural network and keep it honest — real deep
learning. Next, Course 5 reaches today's frontier: large language models and
generative AI.
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
