"""Deep Learning & Neural Networks -- Week 3: Computer Vision with CNNs. Original WAMUGII content."""

# A small image dataset made with code: noisy shapes on a 32 x 32 canvas.
SHAPES = r"""
```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt

def make_shapes(n, kinds=("circle", "square", "triangle"), size=32, seed=0):
    # n noisy grey images of random shapes at random places and sizes
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    images = np.zeros((n, size, size), dtype=np.float32)
    labels = rng.integers(0, len(kinds), n)
    for i, lab in enumerate(labels):
        r = rng.uniform(5, 10)
        cx, cy = rng.uniform(r + 1, size - r - 1, 2)
        dx, dy = xx - cx, yy - cy
        kind = kinds[lab]
        if kind == "circle":
            mask = dx ** 2 + dy ** 2 <= r ** 2
        elif kind == "square":
            mask = (abs(dx) <= r * 0.85) & (abs(dy) <= r * 0.85)
        elif kind == "triangle":
            mask = (dy >= -r) & (dy <= r) & (abs(dx) <= (dy + r) / 2)
        elif kind == "ring":
            mask = (dx ** 2 + dy ** 2 <= r ** 2) & (dx ** 2 + dy ** 2 >= (0.55 * r) ** 2)
        elif kind == "diamond":
            mask = abs(dx) + abs(dy) <= r
        else:  # cross
            mask = ((abs(dx) <= 0.3 * r) & (abs(dy) <= r)) | ((abs(dy) <= 0.3 * r) & (abs(dx) <= r))
        images[i][mask] = rng.uniform(0.6, 1.0)
        images[i] += rng.normal(0, 0.15, (size, size))
    images = torch.tensor(np.clip(images, 0, 1)).unsqueeze(1)   # (n, 1 channel, 32, 32)
    return images, torch.tensor(labels)

X_all, y_all = make_shapes(3000)
X_train, y_train = X_all[:2400], y_all[:2400]
X_test, y_test = X_all[2400:], y_all[2400:]
names = ["circle", "square", "triangle"]

fig, axes = plt.subplots(1, 8, figsize=(12, 2))
for ax, img, lab in zip(axes, X_train, y_train):
    ax.imshow(img[0], cmap="gray")
    ax.set_title(names[lab])
    ax.axis("off")
plt.show()
print(X_train.shape, torch.bincount(y_train))
```
""".strip()

CNN_TOOLS = r"""
```python
class ShapeCNN(nn.Module):
    def __init__(self, n_classes=3):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),   # 32 -> 16
            nn.Conv2d(16, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 16 -> 8
            nn.Flatten())
        self.head = nn.Sequential(nn.Linear(32 * 8 * 8, 64), nn.ReLU(), nn.Linear(64, n_classes))

    def forward(self, x):
        return self.head(self.features(x))

def train_model(model, X, y, epochs=5, batch=64, lr=1e-3, params=None, augment=None):
    opt = torch.optim.Adam(params if params is not None else model.parameters(), lr=lr)
    for epoch in range(epochs):
        model.train()
        perm = torch.randperm(len(X))
        for start in range(0, len(perm), batch):
            idx = perm[start:start + batch]
            xb = X[idx]
            if augment is not None:
                xb = torch.stack([augment(img) for img in xb])
            opt.zero_grad()
            F.cross_entropy(model(xb), y[idx]).backward()
            opt.step()
    return model

def accuracy(model, X, y):
    model.eval()
    with torch.no_grad():
        return round((model(X).argmax(dim=1) == y).float().mean().item(), 3)
```
""".strip()

WEEK3 = {
    "title": "Week 3 · Computer Vision with CNNs",
    "lessons": [
        # ------------------------------------------------------------------ 13
        {
            "title": "Images as Numbers and Convolutions",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=py5byOOHZM8",
            "content": r"""
**Learning objective:** Describe how images are stored as tensors, apply a convolution filter by hand and with PyTorch, and explain feature maps, padding, stride and pooling.

## An image is a grid of numbers

A grey image is a 2-D grid of **pixels**; each pixel is a brightness number (0 = black, 1 or 255 = white). A colour photo has **three channels** — red, green and blue — so it is a 3-D block. PyTorch stores a batch of images as a 4-D tensor:

> (batch size, channels, height, width)

A phone photo of a cassava leaf at 224 × 224 pixels is 3 × 224 × 224 = **150,528 numbers**.

```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits

digits = load_digits()
img = torch.tensor(digits.images[0] / 16.0, dtype=torch.float32)
print(img.shape)
print(img.round(decimals=1))
plt.imshow(img, cmap="gray_r")
plt.title(f"label {digits.target[0]}")
plt.show()
```

## Why not use a plain network?

In Week 1 we **flattened** the digit into 64 numbers. That throws away the layout — the network no longer knows which pixels are neighbours — and for big photos it needs a weight for every pixel in every neuron: a 150,528-pixel photo into just 1,000 neurons is 150 million weights. Worse, a leaf spot in the top corner and the same spot in the middle would look like completely different inputs.

A **convolutional neural network (CNN)** fixes all three problems with one idea.

## The convolution

A **filter** (or **kernel**) is a small grid of weights — for example 3 × 3. It **slides** across the image; at every position it multiplies the 9 pixels under it by its 9 weights and adds them up. The result is a new image called a **feature map**, which lights up wherever the pattern in the filter appears.

Let's design a vertical-edge filter by hand:

```python
edge = torch.tensor([[-1.0, 0.0, 1.0],
                     [-1.0, 0.0, 1.0],
                     [-1.0, 0.0, 1.0]])

# a 6 x 6 image: dark on the left, bright on the right
image = torch.zeros(6, 6)
image[:, 3:] = 1.0

out = F.conv2d(image.view(1, 1, 6, 6), edge.view(1, 1, 3, 3))
print(out.squeeze())
```

The output is **3** in the two columns where dark meets bright and **0** everywhere else: the filter found the edge. Notice the output is 4 × 4, smaller than the input — a 3 × 3 filter cannot be centred on the border pixels.

## Filters on a real digit

```python
digit = img.view(1, 1, 8, 8)
vertical = F.conv2d(digit, edge.view(1, 1, 3, 3), padding=1)
horizontal = F.conv2d(digit, edge.T.reshape(1, 1, 3, 3), padding=1)

fig, axes = plt.subplots(1, 3, figsize=(8, 3))
for ax, im, title in zip(axes, [digit, vertical, horizontal], ["digit", "vertical edges", "horizontal edges"]):
    ax.imshow(im[0, 0].detach(), cmap="gray")
    ax.set_title(title)
    ax.axis("off")
plt.show()
```

In a CNN **nobody designs the filters** — they are weights, learned by backpropagation like any other. The first layers usually learn edge and colour detectors, the next layers corners and textures, deeper layers parts of objects (a leaf vein, an eye, a wheel).

## Three big advantages

1. **Few weights:** one 3 × 3 filter has 9 weights, whatever the image size.
2. **Weight sharing:** the same filter is used at every position, so a pattern is detected **wherever** it appears.
3. **Local patterns:** each output only looks at a small neighbourhood, which matches how images work.

## Padding, stride and channels

- **Padding** adds a border of zeros so the output keeps the input size (`padding=1` for a 3 × 3 filter).
- **Stride** is the step size of the slide; stride 2 halves the width and height.
- A conv layer has **many filters**: `nn.Conv2d(1, 16, 3)` learns 16 filters and outputs 16 feature maps (channels).

```python
conv = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, padding=1)
print(conv(digit).shape)                      # 16 feature maps of 8 x 8
print("weights:", conv.weight.shape, "-> parameters:", sum(p.numel() for p in conv.parameters()))
strided = nn.Conv2d(1, 16, 3, padding=1, stride=2)
print(strided(digit).shape)                   # stride 2 halves the size
```

16 filters × 9 weights + 16 biases = **160 parameters** for the whole layer.

## Pooling: shrink and keep the strongest signal

**Max pooling** takes each 2 × 2 block and keeps only its largest value. It halves the width and height, makes the network faster, and makes it less sensitive to small shifts.

```python
x = torch.tensor([[1.0, 3.0, 2.0, 0.0],
                  [4.0, 2.0, 1.0, 1.0],
                  [0.0, 1.0, 5.0, 6.0],
                  [2.0, 2.0, 7.0, 1.0]]).view(1, 1, 4, 4)
print(nn.MaxPool2d(2)(x).squeeze())
```

The four 2 × 2 blocks become **4, 2, 2 and 7**.

## Key terms

- **Pixel / channel** — one brightness value / one colour layer (RGB = 3 channels).
- **Filter (kernel)** — a small grid of learned weights that slides over the image.
- **Convolution** — sliding the filter and computing weighted sums.
- **Feature map** — the output image showing where a pattern appears.
- **Padding / stride** — border of zeros / step size of the slide.
- **Max pooling** — keeping the largest value in each block.

**Takeaway:** A convolution slides small learned filters over an image to detect patterns anywhere; stacking convolutions and pooling builds from edges up to whole objects.

## Try it yourself

1. Make a horizontal-edge test image (dark top, bright bottom) and apply both filters.
2. Design a 3 × 3 "blur" filter (all weights 1/9) and apply it to the digit.
3. What is the output size of a 3 × 3 convolution with no padding on a 32 × 32 image? With padding 1 and stride 2?
4. Count the parameters of `nn.Conv2d(3, 64, kernel_size=3)` (a colour image in, 64 filters out).
""",
            "quiz": [
                ("How does PyTorch store a batch of images?",
                 ["(height, width) only", "(batch, channels, height, width)", "As a list of strings", "(width, batch)"],
                 1, "Four dimensions: batch, channels, height, width."),
                ("What does a convolution filter do?",
                 ["Deletes pixels", "Slides over the image computing weighted sums to detect a pattern", "Changes the labels", "Sorts the pixels"],
                 1, "The output is a feature map."),
                ("Who designs the filters in a CNN?",
                 ["The programmer, by hand", "They are learned by backpropagation", "The camera", "They are random forever"],
                 1, "Filters are weights like any other."),
                ("Why does weight sharing help?",
                 ["The same filter detects a pattern wherever it appears, with few weights", "It makes images bigger", "It removes the need for data", "It sorts the classes"],
                 0, "One filter, used at every position."),
                ("What does 2 × 2 max pooling do to a 16 × 16 feature map?",
                 ["Makes it 32 × 32", "Makes it 8 × 8, keeping the largest value of each block", "Removes all channels", "Leaves it unchanged"],
                 1, "Pooling halves width and height."),
                ("How many parameters does nn.Conv2d(1, 16, 3) have?",
                 ["16", "144", "160", "9"],
                 2, "16 × 9 weights + 16 biases."),
            ],
        },
        # ------------------------------------------------------------------ 14
        {
            "title": "Building a CNN in PyTorch",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=2xqkSUhmmXU",
            "content": r"""
**Learning objective:** Build and train a convolutional network in PyTorch, follow the shape of the data through every layer, and show why it beats a plain network on images.

## The data: shapes

Real photo datasets are large downloads. To learn the ideas quickly, we make our own image dataset with code: 3,000 noisy 32 × 32 images of **circles, squares and triangles** at random sizes and positions. The same code works unchanged for real photos (Lesson 18).

{SHAPES}

## The CNN

{CNN_TOOLS}

The classic CNN pattern is **conv → ReLU → pool**, repeated, then **flatten** and a small classifier ("head").

## Follow the shapes

```python
model = ShapeCNN()
x = X_train[:4]
print("input:          ", tuple(x.shape))
for layer in model.features:
    x = layer(x)
    print(f"{layer.__class__.__name__:15s}", tuple(x.shape))
print("output logits:  ", tuple(model.head(x).shape))
print("parameters:", sum(p.numel() for p in model.parameters()))
```

- After the first conv: 16 feature maps of 32 × 32.
- After pooling: 16 × 16 × 16. After the second conv and pool: 32 × 8 × 8.
- Flatten gives 32 × 8 × 8 = **2,048** numbers, and the head turns them into 3 logits.

Getting the number in `nn.Linear(32 * 8 * 8, 64)` right is the most common CNN bug — printing the shapes like this finds it in seconds.

## Train it

```python
torch.manual_seed(0)
cnn = train_model(ShapeCNN(), X_train, y_train, epochs=5)
print("CNN test accuracy:", accuracy(cnn, X_test, y_test))
```

After only 5 epochs the CNN recognises about **95%** of the test shapes.

## Compare with a plain network

```python
torch.manual_seed(0)
mlp = nn.Sequential(nn.Flatten(), nn.Linear(32 * 32, 64), nn.ReLU(), nn.Linear(64, 3))
mlp = train_model(mlp, X_train, y_train, epochs=5)
print("Plain network test accuracy:", accuracy(mlp, X_test, y_test))
print("plain network parameters:", sum(p.numel() for p in mlp.parameters()))
```

The plain network gets only about **0.67**. It sees 1,024 unconnected numbers and must learn each shape separately at every position. The CNN's filters detect edges and corners **wherever** the shape is — that is the power of convolution.

## Look inside: the learned filters

```python
filters = cnn.features[0].weight.detach()      # 16 filters of 1 x 3 x 3
fig, axes = plt.subplots(2, 8, figsize=(10, 3))
for ax, f in zip(axes.ravel(), filters):
    ax.imshow(f[0], cmap="bwr")
    ax.axis("off")
plt.suptitle("First-layer filters learned from the data")
plt.show()

maps = F.relu(cnn.features[0](X_test[:1])).detach()[0]
fig, axes = plt.subplots(2, 8, figsize=(10, 3))
for ax, m in zip(axes.ravel(), maps):
    ax.imshow(m, cmap="gray")
    ax.axis("off")
plt.suptitle("Feature maps for one test image")
plt.show()
```

Many filters look like edge detectors in different directions — the network discovered them on its own.

## Famous CNN architectures

| Network | Year | Idea |
|---|---|---|
| LeNet | 1998 | Read handwritten cheques and postcodes |
| AlexNet | 2012 | Won ImageNet by a huge margin on GPUs — started the deep-learning boom |
| VGG | 2014 | Many small 3 × 3 convolutions |
| ResNet | 2015 | Residual connections; 50–150 layers |
| EfficientNet, ConvNeXt | 2019–2022 | Better accuracy per computation |

Today, **vision transformers** compete with CNNs on large datasets, but CNNs remain fast, reliable and excellent for phones and small datasets.

## Key terms

- **CNN** — a network built from convolution layers for images.
- **conv → ReLU → pool** — the standard CNN building block.
- **Flatten** — turn feature maps into one long vector for the classifier head.
- **Head** — the final layers that turn features into class scores.
- **Architecture** — the arrangement of layers in a network.

**Takeaway:** A CNN stacks conv–ReLU–pool blocks that learn reusable visual patterns, so it beats a plain network on images with fewer, smarter weights.

## Try it yourself

1. Add a third conv block (32 → 64 filters). What must change in the head?
2. Train for 10 epochs. How much better does the CNN get?
3. Replace max pooling with `stride=2` in the convolutions. Does accuracy change?
4. Find three test images the CNN gets wrong and show them. What makes them hard?
""",
            "quiz": [
                ("What is the classic building block of a CNN?",
                 ["Sort → split → join", "Conv → ReLU → pool", "Softmax → dropout → softmax", "Embedding → LSTM"],
                 1, "Repeated, then flatten and a head."),
                ("After two 2 × 2 poolings, what size is a 32 × 32 image?",
                 ["16 × 16", "8 × 8", "4 × 4", "32 × 32"],
                 1, "32 → 16 → 8."),
                ("With 32 channels of 8 × 8, how many numbers come out of Flatten?",
                 ["256", "2,048", "64", "32"],
                 1, "32 × 8 × 8 = 2,048."),
                ("Why did the CNN beat the plain network on the shapes?",
                 ["It had more data", "Its filters detect patterns wherever the shape appears", "It used a different test set", "Plain networks cannot use ReLU"],
                 1, "Convolution reuses detectors across positions."),
                ("What is a quick way to find a size mismatch bug in a CNN?",
                 ["Delete the head", "Pass a small batch through the layers and print each output shape", "Use a bigger learning rate", "Retrain from scratch"],
                 1, "Print the shapes layer by layer."),
                ("Which 2015 architecture introduced residual connections?",
                 ["LeNet", "AlexNet", "ResNet", "VGG"],
                 2, "ResNet made very deep CNNs trainable."),
            ],
        },
        # ------------------------------------------------------------------ 15
        {
            "title": "Data Augmentation: More Data for Free",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=eDRck258bnw",
            "content": r"""
**Learning objective:** Use torchvision transforms to create realistic variations of training images, measure the gain when data is scarce, and choose augmentations that keep the label true.

## The idea

A photo of a maize leaf is still a maize leaf if it is turned a little, moved to the left, flipped or taken in dimmer light. **Data augmentation** creates these variations **randomly every time an image is used for training**, so the network never sees exactly the same picture twice. It learns what matters (the disease spots) and ignores what does not (position, angle, lighting).

It is one of the most effective ways to fight overfitting when you have few images — the usual situation in real projects.

{SHAPES}

{CNN_TOOLS}

## torchvision transforms

```python
from torchvision.transforms import v2

augment = v2.Compose([
    v2.RandomHorizontalFlip(),
    v2.RandomAffine(degrees=20, translate=(0.15, 0.15)),   # rotate up to 20°, shift up to 15%
])

img = X_train[0]
fig, axes = plt.subplots(1, 6, figsize=(10, 2))
axes[0].imshow(img[0], cmap="gray"); axes[0].set_title("original")
for ax in axes[1:]:
    ax.imshow(augment(img)[0], cmap="gray")
    ax.set_title("augmented")
for ax in axes:
    ax.axis("off")
plt.show()
```

Each call gives a different random version of the same shape.

## Does it help? Only 300 training images

```python
X_small, y_small = X_train[:300], y_train[:300]

torch.manual_seed(0)
plain = train_model(ShapeCNN(), X_small, y_small, epochs=40, batch=32)
print("without augmentation:", accuracy(plain, X_test, y_test))

torch.manual_seed(0)
augmented = train_model(ShapeCNN(), X_small, y_small, epochs=40, batch=32, augment=augment)
print("with augmentation:   ", accuracy(augmented, X_test, y_test))
```

With only 300 images, augmentation lifts test accuracy from about **0.93** to about **0.95** — about a third of the mistakes disappear, with no new data collected. Training takes longer per epoch, because every batch is transformed on the fly.

## Common augmentations

| Transform | What it simulates |
|---|---|
| `RandomHorizontalFlip` | Mirror image |
| `RandomRotation`, `RandomAffine` | Tilted camera, object in a different place |
| `RandomResizedCrop` | Zooming in on part of the object |
| `ColorJitter` | Different light, camera or time of day |
| `GaussianBlur` | A slightly out-of-focus photo |
| `RandomErasing` | Something partly covering the object |

## The golden rule: keep the label true

Augment only in ways that **do not change the answer**:

- Flipping a leaf photo: fine. Flipping a **digit** "6" upside down turns it into a "9": wrong!
- Strong colour changes are dangerous for crop diseases where colour **is** the symptom (yellow vs green).
- Medical X-rays: flipping left and right can matter (the heart is on the left).

Think about the real camera, the real users and the real world, then choose.

## Augment training data only

Validation and test images must stay **untouched** — they represent the real images the model will meet. For real photos, all sets still get the same basic preparation (resize, convert to a tensor, normalise):

```python
train_tf = v2.Compose([v2.RandomResizedCrop(32, scale=(0.8, 1.0)),
                       v2.RandomHorizontalFlip(),
                       v2.ColorJitter(brightness=0.3)])
test_tf = v2.Identity()      # nothing random for evaluation
print(train_tf(X_test[0]).shape, test_tf(X_test[0]).shape)
```

## Key terms

- **Data augmentation** — random, label-preserving changes to training images.
- **Transform** — one image operation in torchvision (flip, rotate, crop, jitter).
- **Compose** — a chain of transforms applied in order.
- **On-the-fly augmentation** — a new random version every time an image is used.

**Takeaway:** Augmentation gives a small dataset many realistic variations for free — as long as every change keeps the label true and test images stay untouched.

## Try it yourself

1. Add `v2.RandomVerticalFlip()`. Is it safe for these shapes? Would it be safe for digits?
2. Try `degrees=90`. Does stronger augmentation help or hurt?
3. Repeat the experiment with 1,000 training images instead of 300. Is the gain smaller or larger?
4. List three augmentations you would use for photos of cassava leaves taken by farmers on phones, and one you would avoid.
""",
            "quiz": [
                ("What is data augmentation?",
                 ["Collecting more photos", "Creating random, label-preserving variations of training images", "Deleting bad images", "Adding labels"],
                 1, "New variations every time an image is used."),
                ("When is augmentation most useful?",
                 ["When there are few training images", "When there are no labels", "Only for tables", "Only on the test set"],
                 0, "It fights overfitting on small datasets."),
                ("Why is flipping a handwritten '6' upside down a bad augmentation?",
                 ["It makes the image smaller", "It can turn it into a '9', changing the true label", "Flips are slow", "Digits have colour"],
                 1, "Augmentation must keep the label true."),
                ("Which images should be augmented?",
                 ["Training images only", "Test images only", "All images", "Validation images only"],
                 0, "Evaluation images must look like real data."),
                ("Which transform simulates different lighting?",
                 ["RandomHorizontalFlip", "ColorJitter", "Flatten", "MaxPool2d"],
                 1, "ColorJitter changes brightness, contrast, colour."),
                ("Why is ColorJitter risky for some crop-disease images?",
                 ["Colour can be the symptom itself", "It makes images bigger", "It removes the leaf", "It is too slow"],
                 0, "Changing yellow to green could change the diagnosis."),
            ],
        },
        # ------------------------------------------------------------------ 16
        {
            "title": "Transfer Learning: Standing on Big Models",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=nB15sW-mkHA",
            "content": r"""
**Learning objective:** Explain transfer learning, show its benefit when data is scarce, and adapt a pretrained ResNet from torchvision to a new task by freezing or fine-tuning.

## Don't start from zero

Training a strong image model from scratch needs hundreds of thousands of labelled photos and many GPU hours. But the early layers of any good image model learn **general** patterns — edges, corners, textures, shapes — that are useful for almost every visual task.

**Transfer learning** takes a model already trained on a huge dataset (usually **ImageNet**: 1.2 million photos in 1,000 classes) and re-uses it for your task. You keep its "eyes" (the feature layers) and replace only its "brain" (the final classifier). This is how most real projects are built — including crop-disease apps trained on a few thousand leaf photos.

## Two ways to transfer

| Method | What trains | When |
|---|---|---|
| **Feature extraction (freeze)** | Only the new head | Very little data; fast; works on a CPU |
| **Fine-tuning** | The head, then some or all layers with a small learning rate | More data, or a task very different from ImageNet |

## See the benefit with our own "pretrained" model

We first train a CNN on circles, squares and triangles. Then we face a **new** task — rings, diamonds and crosses — with only **30** labelled images.

{SHAPES}

{CNN_TOOLS}

```python
import copy

# 1. "Pretrain" on the big, old task
torch.manual_seed(0)
pretrained = train_model(ShapeCNN(), X_train, y_train, epochs=5)
print("old task accuracy:", accuracy(pretrained, X_test, y_test))

# 2. The new task: only 30 training images
new_kinds = ("ring", "diamond", "cross")
X_new, y_new = make_shapes(30, kinds=new_kinds, seed=1)
X_new_test, y_new_test = make_shapes(600, kinds=new_kinds, seed=2)

def new_head():
    return nn.Sequential(nn.Linear(32 * 8 * 8, 64), nn.ReLU(), nn.Linear(64, 3))

# (a) from scratch
torch.manual_seed(0)
scratch = train_model(ShapeCNN(), X_new, y_new, epochs=60, batch=32)

# (b) transfer: keep the learned features frozen, train a new head
frozen = copy.deepcopy(pretrained)
frozen.head = new_head()
for p in frozen.features.parameters():
    p.requires_grad = False
torch.manual_seed(0)
frozen = train_model(frozen, X_new, y_new, epochs=60, batch=32, params=frozen.head.parameters())

print("from scratch:      ", accuracy(scratch, X_new_test, y_new_test))
print("transfer (frozen): ", accuracy(frozen, X_new_test, y_new_test))
```

With only 30 images, the network trained from scratch gets about **0.43** (only a little better than guessing one of three). The transferred network gets about **0.56** — the edge and corner detectors learned on the old shapes carry over to the new ones. With 90 images the gap stays large (about 0.66 vs 0.79 in our tests).

## A real pretrained network: ResNet-18

torchvision includes dozens of networks pretrained on ImageNet. In Colab, the first line below downloads the weights (about 45 MB) automatically:

```python
from torchvision import models

weights = models.ResNet18_Weights.DEFAULT
resnet = models.resnet18(weights=weights)
preprocess = weights.transforms()          # the resize/normalise these weights expect
print(resnet.fc)                           # the final layer: 512 features -> 1000 ImageNet classes
print("parameters:", sum(p.numel() for p in resnet.parameters()))
```

ResNet-18 has about **11.7 million** parameters. To adapt it to, say, 4 cassava conditions:

```python
for p in resnet.parameters():              # freeze everything ...
    p.requires_grad = False
resnet.fc = nn.Linear(resnet.fc.in_features, 4)   # ... then add a new, trainable head

trainable = sum(p.numel() for p in resnet.parameters() if p.requires_grad)
print("trainable parameters:", trainable)

fake_photos = torch.rand(2, 3, 224, 224)  # two colour images
print(resnet(preprocess(fake_photos)).shape)
```

Only **2,052** of the 11.7 million parameters now train (512 × 4 weights + 4 biases), so even a CPU can learn the new head in minutes. `preprocess` resizes and normalises images exactly the way the network saw them during pretraining — always use it.

## Fine-tuning, step by step

1. Train the new head with everything else frozen (a few epochs).
2. Unfreeze the last block (`resnet.layer4`) — or everything.
3. Continue with a **small** learning rate (for example 1e-4), so the pretrained knowledge is adjusted, not destroyed.

```python
for p in resnet.layer4.parameters():
    p.requires_grad = True
opt = torch.optim.Adam([
    {"params": resnet.layer4.parameters(), "lr": 1e-4},
    {"params": resnet.fc.parameters(), "lr": 1e-3},
])
print("trainable now:", sum(p.numel() for p in resnet.parameters() if p.requires_grad))
```

## Where pretrained models come from

- **torchvision.models** — ResNet, EfficientNet, MobileNet (small, for phones), ConvNeXt, vision transformers.
- **Hugging Face Hub** and **timm** — thousands more, for images, text and audio.
- Always check the **licence** and what data the model was trained on — a model trained only on European faces or North American crops may not work well on Rwandan data.

## Key terms

- **Transfer learning** — reusing a model trained on one task for another.
- **Pretrained model** — a network already trained on a large dataset such as ImageNet.
- **Freezing** — stopping some layers from updating (`requires_grad = False`).
- **Fine-tuning** — continuing to train pretrained layers with a small learning rate.
- **Feature extractor** — the frozen pretrained layers that turn images into features.

**Takeaway:** With little data, borrow a pretrained network's eyes and train only a new head; fine-tune gently when you have more data.

## Try it yourself

1. Fine-tune all layers of the transferred shape model (no freezing). Is it better or worse than the frozen version with 30 images?
2. Repeat the experiment with 90 and 300 new images. When does training from scratch catch up?
3. Load `models.mobilenet_v3_small` and count its parameters. Why might it suit a phone app?
4. Write down a plan to adapt ResNet-18 to 5 types of local fruit using 100 photos of each.
""",
            "quiz": [
                ("What is transfer learning?",
                 ["Copying data between computers", "Reusing a model trained on one task for a new task", "Training without data", "Moving a model to a GPU"],
                 1, "Borrow learned features."),
                ("Why do pretrained features transfer to new image tasks?",
                 ["Early layers learn general patterns such as edges and textures", "All images are the same", "The labels are copied", "They don't"],
                 0, "Low-level visual patterns are universal."),
                ("With very little data, what is usually the best approach?",
                 ["Train a huge network from scratch", "Freeze the pretrained layers and train only a new head", "Unfreeze everything with a big learning rate", "Use no validation"],
                 1, "Feature extraction needs the least data."),
                ("How do you freeze a layer in PyTorch?",
                 ["Delete it", "Set requires_grad = False on its parameters", "Call model.eval()", "Lower the batch size"],
                 1, "Frozen parameters receive no updates."),
                ("Why use a small learning rate when fine-tuning?",
                 ["To adjust the pretrained knowledge without destroying it", "To train faster", "Because GPUs require it", "To freeze the head"],
                 0, "Big steps would wipe out useful features."),
                ("What does weights.transforms() give you?",
                 ["The labels", "The exact resizing and normalisation the pretrained network expects", "A new dataset", "The model's licence"],
                 1, "Always preprocess as during pretraining."),
            ],
        },
        # ------------------------------------------------------------------ 17
        {
            "title": "Understanding and Trusting Image Models",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=NmLK_WQBxB4",
            "content": r"""
**Learning objective:** Evaluate an image model beyond accuracy, see which pixels drive its decisions with a saliency map, and recognise shortcut learning and dataset bias.

## Accuracy is not understanding

An image model can score 99% and still be useless — or dangerous — in the field. Famous examples:

- A model that "detected" pneumonia partly by reading **hospital markers** printed on X-rays: one hospital had more sick patients.
- Skin-cancer models that learned that photos with a **ruler** in them were more often cancer (doctors measure suspicious spots).
- Animal classifiers that recognised "wolf" from **snow** in the background.

This is **shortcut learning**: the model finds the easiest pattern in the training data, not the one we meant. Your job is to check.

{SHAPES}

{CNN_TOOLS}

```python
torch.manual_seed(0)
cnn = train_model(ShapeCNN(), X_train, y_train, epochs=5)
print("test accuracy:", accuracy(cnn, X_test, y_test))
```

## Step 1 — Where are the mistakes?

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cnn.eval()
with torch.no_grad():
    probs = F.softmax(cnn(X_test), dim=1)
pred = probs.argmax(dim=1)
ConfusionMatrixDisplay(confusion_matrix(y_test, pred), display_labels=names).plot(cmap="Blues")
plt.show()

wrong = torch.where(pred != y_test)[0]
fig, axes = plt.subplots(1, min(6, len(wrong)), figsize=(10, 2))
for ax, i in zip(axes, wrong[:6]):
    ax.imshow(X_test[i, 0], cmap="gray")
    ax.set_title(f"{names[y_test[i]]}→{names[pred[i]]}", fontsize=9)
    ax.axis("off")
plt.show()
```

Most mistakes are small shapes, where a triangle, square and circle look almost alike in 32 × 32 noisy pixels. That is a sensible weakness — a shortcut would look different.

## Step 2 — Is the model confident when it is wrong?

```python
confidence = probs.max(dim=1).values
print("average confidence when right:", round(confidence[pred == y_test].mean().item(), 3))
print("average confidence when wrong:", round(confidence[pred != y_test].mean().item(), 3))
```

A healthy model is **less confident** on its mistakes. That lets you build a safety rule: if confidence is below, say, 0.8, ask a human expert instead of answering.

## Step 3 — A saliency map: which pixels mattered?

The gradient of the class score with respect to the **input pixels** shows which pixels would change the decision most. Bright pixels = important pixels.

```python
def saliency(model, image, target):
    model.eval()
    x = image.unsqueeze(0).clone().requires_grad_(True)
    score = model(x)[0, target]
    score.backward()
    return x.grad.abs()[0, 0]

fig, axes = plt.subplots(2, 5, figsize=(10, 4))
for k in range(5):
    img, lab = X_test[k], y_test[k].item()
    axes[0, k].imshow(img[0], cmap="gray"); axes[0, k].set_title(names[lab]); axes[0, k].axis("off")
    axes[1, k].imshow(saliency(cnn, img, lab), cmap="hot"); axes[1, k].axis("off")
plt.suptitle("Top: image. Bottom: pixels that drive the decision")
plt.show()
```

The bright pixels should sit on the **edges and corners of the shape**, not on the noisy background. If a leaf-disease model's saliency lit up the farmer's hand or the soil, you would have found a shortcut. More advanced tools (Grad-CAM, SHAP) follow the same idea.

## Step 4 — Test on data from the real world

A model is only trustworthy on data like its training data. Ask:

- **Who and where?** Were photos taken on the same phones, in the same regions, light and seasons as the real users?
- **Is anyone missing?** Skin-condition models trained mostly on light skin perform worse on dark skin. Crop models trained on one country's varieties can fail in another.
- **Is the test set independent?** Photos of the same plant in both training and test sets inflate the score.

Collect a small **field test set** from the real setting — even 100 photos — before trusting a model.

## Robustness check: a simple shift

```python
noisy = (X_test + 0.25 * torch.randn_like(X_test)).clamp(0, 1)
print("clean test:", accuracy(cnn, X_test, y_test), " extra noise:", accuracy(cnn, noisy, y_test))
```

Accuracy drops when the images are noisier than in training. Real cameras and conditions vary — test for it, and augment for it.

## Key terms

- **Shortcut learning** — the model uses an easy but wrong clue in the data.
- **Saliency map** — input-gradient picture of which pixels drive a decision.
- **Confidence** — the highest predicted probability.
- **Distribution shift** — real data differs from training data.
- **Field test set** — examples collected from the real place of use.

**Takeaway:** Trust an image model only after checking its mistakes, its confidence, the pixels it uses, and its performance on real, representative data.

## Try it yourself

1. Find the confidence threshold below which half of the mistakes would be sent to a human. How many correct answers would also be sent?
2. Show saliency maps for three of the model's mistakes. What did it look at?
3. Make a test set where every shape is small (radius 5–6). How does accuracy change?
4. Write five questions you would ask before deploying a crop-disease app in Rwanda.
""",
            "quiz": [
                ("What is shortcut learning?",
                 ["Training faster with a GPU", "The model relies on an easy but wrong clue, like a ruler in the photo", "Using fewer layers", "Skipping validation"],
                 1, "It finds unintended patterns."),
                ("What does a saliency map show?",
                 ["The training loss", "Which input pixels most affect the class score", "The labels", "The model size"],
                 1, "It uses gradients with respect to the input."),
                ("A healthy model's confidence on its mistakes should be…",
                 ["Higher than on correct answers", "Lower than on correct answers", "Always 100%", "Exactly 50%"],
                 1, "Low confidence can trigger human review."),
                ("A skin model trained mostly on light skin works worse on dark skin. What is this?",
                 ["Overfitting to noise", "Dataset bias: a group is under-represented", "A bug in PyTorch", "Data augmentation"],
                 1, "Representative data matters."),
                ("What is a field test set?",
                 ["Training data", "Examples collected from the real place of use", "Augmented images", "Random noise"],
                 1, "It shows real-world performance."),
                ("Why might the same plant appearing in both training and test sets be a problem?",
                 ["It inflates the test score", "It lowers accuracy", "It breaks PyTorch", "It is not a problem"],
                 0, "The test set must be independent."),
            ],
        },
        # ------------------------------------------------------------------ 18
        {
            "title": "Week 3 Project: An Image Classifier from Folders",
            "minutes": 120,
            "video": "https://www.youtube.com/watch?v=WIhI1W6NoZ0",
            "content": r"""
**Learning objective:** Build a complete image-classification project the way it is done in industry: images in folders, train/validation/test splits, augmentation, a pretrained network, early stopping and an honest evaluation.

## The brief

A farmers' cooperative wants a phone app that recognises plant conditions from photos. Before collecting thousands of photos, it asks you to build the full **pipeline** on a small sample, so that real photos can simply be dropped in later.

Real image projects store pictures in **one folder per class**:

```
photos/
    healthy/      img001.jpg, img002.jpg, ...
    disease_a/    ...
    disease_b/    ...
```

To keep this project runnable for everyone, we first **write our shapes to folders as PNG files**. Later, point the same code at your own photos (for example from your phone, Google Drive, or a public dataset such as PlantVillage on Kaggle).

{SHAPES}

## Part 1 — Images into folders

```python
from pathlib import Path
from PIL import Image

root = Path("shape_photos")
X_demo, y_demo = make_shapes(600, seed=5)
for i, (img, lab) in enumerate(zip(X_demo, y_demo)):
    folder = root / names[lab]
    folder.mkdir(parents=True, exist_ok=True)
    Image.fromarray((img[0].numpy() * 255).astype("uint8")).convert("RGB").save(folder / f"{i:04d}.png")
print(sorted(p.name for p in root.iterdir()), sum(1 for _ in root.rglob("*.png")), "images")
```

## Part 2 — Load with ImageFolder and split

```python
from torchvision import datasets, models
from torchvision.transforms import v2
from torch.utils.data import DataLoader, Subset

weights = models.ResNet18_Weights.DEFAULT
base_tf = weights.transforms()                   # resize + normalise for ResNet

train_tf = v2.Compose([v2.RandomHorizontalFlip(), v2.RandomRotation(15), base_tf])

full_train = datasets.ImageFolder(root, transform=train_tf)
full_eval = datasets.ImageFolder(root, transform=base_tf)
print(full_train.classes, len(full_train))

g = torch.Generator().manual_seed(0)
order = torch.randperm(len(full_train), generator=g).tolist()
n_val = n_test = len(order) // 5
val_idx, test_idx, train_idx = order[:n_val], order[n_val:n_val + n_test], order[n_val + n_test:]

train_loader = DataLoader(Subset(full_train, train_idx), batch_size=32, shuffle=True)
val_loader = DataLoader(Subset(full_eval, val_idx), batch_size=64)
test_loader = DataLoader(Subset(full_eval, test_idx), batch_size=64)
print(len(train_idx), "train /", len(val_idx), "val /", len(test_idx), "test")
```

`ImageFolder` reads the class names from the folder names. Two copies of the dataset let the training split be augmented while validation and test stay untouched.

## Part 3 — A pretrained ResNet with a new head

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
model = models.resnet18(weights=weights)
for p in model.parameters():
    p.requires_grad = False
model.fc = nn.Linear(model.fc.in_features, len(full_train.classes))
model = model.to(device)
opt = torch.optim.Adam(model.fc.parameters(), lr=1e-3)
print("device:", device)
```

## Part 4 — Train with early stopping

```python
import copy

def evaluate(loader):
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for xb, yb in loader:
            pred = model(xb.to(device)).argmax(dim=1).cpu()
            correct += (pred == yb).sum().item()
            total += len(yb)
    return correct / total

best_acc, best_state, waited = 0.0, None, 0
for epoch in range(3):                       # use 10–20 epochs on a GPU with real photos
    model.train()
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad()
        F.cross_entropy(model(xb), yb).backward()
        opt.step()
    val_acc = evaluate(val_loader)
    print(f"epoch {epoch}: validation accuracy {val_acc:.3f}")
    if val_acc > best_acc:
        best_acc, best_state, waited = val_acc, copy.deepcopy(model.state_dict()), 0
    else:
        waited += 1
        if waited >= 3:
            break
model.load_state_dict(best_state)
print("test accuracy (used once):", round(evaluate(test_loader), 3))
```

On a Colab GPU each epoch takes seconds. A pretrained ResNet usually reaches high accuracy on such clear classes within a few epochs.

## Part 5 — Predict a single new photo

```python
def predict_photo(path):
    img = Image.open(path).convert("RGB")
    x = base_tf(img).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        p = F.softmax(model(x), dim=1)[0].cpu()
    best = int(p.argmax())
    return full_train.classes[best], round(float(p[best]), 3)

example = next(root.rglob("*.png"))
print(example.parent.name, "->", predict_photo(example))
```

## Part 6 — Evaluate and report (two pages)

1. **Data:** classes, number of images per class, how the split was made.
2. **Model:** pretrained network, what was frozen, augmentation used.
3. **Results:** validation curve, test accuracy, confusion matrix, five mistakes with comments.
4. **Trust:** saliency maps for three images (Lesson 17); confidence on right vs wrong answers.
5. **Field plan:** how you would collect real photos in Rwanda (phones, places, seasons, farmers' consent), a field test set, and a rule for sending low-confidence photos to an agronomist.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Pipeline | Folders → ImageFolder → separate train / val / test |
| Model | Pretrained network adapted with a new head |
| Training | Augmentation on training only; early stopping with best weights |
| Evaluation | Test used once; confusion matrix and mistakes studied |
| Responsibility | Field data plan, consent and human review for low confidence |

**Takeaway:** A real image project is a pipeline — folders, transforms, a pretrained model, careful splits and honest evaluation — that works the same for shapes and for real photos.

## Try it yourself

Complete Parts 1–6. Then replace the `shape_photos` folder with at least three classes of your own photos (30+ per class, taken with your phone) and run the same notebook. What changes, and what accuracy do you get?
""",
            "quiz": [
                ("How does ImageFolder know the class names?",
                 ["From a CSV file", "From the names of the sub-folders", "From the image colours", "You must type them"],
                 1, "One folder per class."),
                ("Why create two copies of the dataset with different transforms?",
                 ["So training images are augmented while validation and test stay untouched", "To double the data", "To save memory", "ImageFolder requires two"],
                 0, "Augment training only."),
                ("What must new photos go through before prediction?",
                 ["The same preprocessing (resize, normalise) used for training", "Augmentation", "Nothing", "Flipping"],
                 0, "The model expects the same input format."),
                ("Why is the test accuracy computed only once at the end?",
                 ["To keep it an honest estimate", "It is slow", "PyTorch forbids more", "It changes the weights"],
                 0, "Choices are made on validation data."),
                ("What should happen to low-confidence predictions in a farm app?",
                 ["Hide them", "Send them to a human expert such as an agronomist", "Always say 'healthy'", "Delete the photo"],
                 1, "Human review keeps the app safe."),
                ("Which part of the pretrained ResNet trains in this project?",
                 ["Every layer", "Only the new final layer (fc)", "Only the first convolution", "Nothing"],
                 1, "The backbone is frozen."),
            ],
        },
    ],
}

for _lesson in WEEK3["lessons"]:
    _lesson["content"] = (_lesson["content"].replace("{SHAPES}", SHAPES)
                          .replace("{CNN_TOOLS}", CNN_TOOLS))
