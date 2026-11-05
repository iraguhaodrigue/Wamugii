"""Deep Learning & Neural Networks -- Week 4: Sequences, Attention and Generative Models. Original WAMUGII content."""

# Customer-support messages for a mobile network (simulated): 3 topics.
MESSAGES = r"""
```python
import re
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

TEMPLATES = {
    "payment": ["i sent money to {who} but it did not arrive", "my payment to {who} failed",
                "money was deducted twice for {who}", "how do i reverse a payment to {who}",
                "the merchant {who} did not receive my payment"],
    "network": ["my {what} is not working in {where}", "no {what} signal in {where} since morning",
                "{what} is very slow in {where}", "i cannot connect to {what} in {where}",
                "the {what} keeps dropping in {where}"],
    "account": ["i forgot my {thing}", "please reset my {thing}", "my {thing} is blocked",
                "how do i change my {thing}", "someone asked for my {thing} on the phone"],
}
FILL = {"who": ["my brother", "the shop", "a wrong number", "the school", "my landlord", "the supermarket"],
        "what": ["internet", "data bundle", "4g", "network", "airtime bundle"],
        "where": ["kigali", "huye", "musanze", "rubavu", "nyagatare", "my village"],
        "thing": ["pin", "password", "sim card", "mobile money pin", "account"]}
TOPICS = list(TEMPLATES)

def make_messages(n, seed):
    rng = np.random.default_rng(seed)
    texts, labels = [], []
    for _ in range(n):
        label = int(rng.integers(0, 3))
        text = re.sub(r"\{(\w+)\}", lambda m: str(rng.choice(FILL[m.group(1)])),
                      str(rng.choice(TEMPLATES[TOPICS[label]])))
        if rng.random() < 0.3:
            text = str(rng.choice(["hello ", "please ", "good morning ", "help "])) + text
        if rng.random() < 0.3:
            text += str(rng.choice([" thank you", " urgent", " please help", " today"]))
        texts.append(text)
        labels.append(label)
    return texts, torch.tensor(labels)

train_texts, y_train = make_messages(800, seed=0)
test_texts, y_test = make_messages(200, seed=1)
for t, l in zip(train_texts[:4], y_train[:4]):
    print(f"[{TOPICS[l]}] {t}")
```
""".strip()

VOCAB = r"""
```python
vocab = {"<pad>": 0, "<unk>": 1}
for text in train_texts:                      # build the vocabulary from training text only
    for word in text.split():
        vocab.setdefault(word, len(vocab))

def encode(text, max_len=14):
    ids = [vocab.get(w, vocab["<unk>"]) for w in text.split()][:max_len]
    return ids + [vocab["<pad>"]] * (max_len - len(ids))

X_train = torch.tensor([encode(t) for t in train_texts])
X_test = torch.tensor([encode(t) for t in test_texts])

def fit(model, epochs=30, lr=1e-2):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for epoch in range(epochs):
        model.train()
        perm = torch.randperm(len(X_train))
        for start in range(0, len(perm), 32):
            idx = perm[start:start + 32]
            opt.zero_grad()
            F.cross_entropy(model(X_train[idx]), y_train[idx]).backward()
            opt.step()
    model.eval()
    with torch.no_grad():
        return round((model(X_test).argmax(1) == y_test).float().mean().item(), 3)
print("vocabulary size:", len(vocab), "| first message as ids:", X_train[0].tolist())
```
""".strip()

WEEK4 = {
    "title": "Week 4 · Sequences, Attention and Generative Models",
    "lessons": [
        # ------------------------------------------------------------------ 19
        {
            "title": "Text as Numbers: Tokens and Embeddings",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=wjZofJX0v4M",
            "content": r"""
**Learning objective:** Turn text into tokens and ids, explain word embeddings, and train a neural text classifier whose embeddings learn word meanings from the task.

## Computers need numbers

A network cannot read "my mobile money pin is blocked". Text goes through three steps:

1. **Tokenise** — split the text into pieces called **tokens**: words, parts of words or characters.
2. **Index** — give every token in the **vocabulary** a number (an id).
3. **Embed** — turn every id into a short vector of learned numbers: an **embedding**.

Large language models use **sub-word tokens** (for example "unbelievable" → "un", "believ", "able"), so they can handle any word — including Kinyarwanda words they rarely saw — with a vocabulary of about 50,000–200,000 tokens. Here we use simple whole words.

## The data: customer messages

A mobile network receives thousands of messages a day. We will sort them automatically into three queues — **payment**, **network** and **account** — so each reaches the right team faster. The messages are simulated from templates.

{MESSAGES}

## Tokens and ids

{VOCAB}

`<pad>` fills short messages up to a fixed length so they fit in one tensor; `<unk>` stands for any word never seen in training.

## Why not one-hot vectors?

One-hot encoding a 50,000-word vocabulary gives 50,000-long vectors where every word is equally different from every other: "internet" is as far from "4g" as from "landlord". An **embedding** is a short, dense vector (here 16 numbers; in large models thousands) that is **learned**. Words used in similar ways end up with similar vectors.

```python
emb = nn.Embedding(num_embeddings=len(vocab), embedding_dim=16, padding_idx=0)
print(emb(X_train[:2]).shape)          # 2 messages x 14 tokens x 16 numbers
```

An embedding layer is just a table with one learnable row per token — looking up row 7 is the same as multiplying a one-hot vector by a weight matrix, but much faster.

## A simple text classifier

Average the embeddings of the words in a message (ignoring padding), then classify:

```python
class BagOfEmbeddings(nn.Module):
    def __init__(self, vocab_size, dim=16, n_classes=3):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, dim, padding_idx=0)
        self.out = nn.Linear(dim, n_classes)

    def forward(self, x):
        e = self.emb(x)                                  # (batch, tokens, dim)
        mask = (x != 0).unsqueeze(-1).float()            # 1 for real words, 0 for padding
        mean = (e * mask).sum(1) / mask.sum(1).clamp(min=1)
        return self.out(mean)

torch.manual_seed(0)
bag = BagOfEmbeddings(len(vocab))
print("test accuracy:", fit(bag))
```

The model sorts the test messages almost perfectly. These template messages are much cleaner than real ones — with real customers you would expect spelling mistakes, mixed Kinyarwanda, English and French, and lower accuracy.

## What did the embeddings learn?

Nobody told the model what words mean. It learned embeddings only to sort messages — yet related words moved close together:

```python
E = F.normalize(bag.emb.weight.detach(), dim=1)      # unit length -> dot product = cosine similarity
id_to_word = {i: w for w, i in vocab.items()}

def neighbours(word, k=4):
    sims = E @ E[vocab[word]]
    best = sims.argsort(descending=True)[1:k + 1]
    return [id_to_word[int(i)] for i in best]

for w in ["pin", "internet", "payment", "huye"]:
    print(f"{w:9s} ->", neighbours(w))
```

"huye" ends up near other places (kigali, nyagatare, village); "pin" near "account" and "sim". On huge text collections, the same idea (word2vec, 2013) learned famous relationships such as king − man + woman ≈ queen. Large language models learn embeddings with thousands of dimensions in exactly this spirit.

## Use it

```python
def route(message):
    with torch.no_grad():
        probs = F.softmax(bag(torch.tensor([encode(message)])), dim=1)[0]
    return TOPICS[int(probs.argmax())], round(float(probs.max()), 2)

print(route("my internet is not working in rubavu"))
print(route("please reset my password urgent"))
print(route("the bus was late today"))          # off-topic: watch the confidence
```

Look at the last answer: the bus message has nothing to do with the network, yet the model still picks a queue — with high confidence. A classifier can only choose among the classes it knows. Real systems add an "other" class trained on off-topic messages, or a separate check that sends unfamiliar messages to a person.

## The weakness of a "bag"

Averaging ignores **word order**: "money sent to me, not by me" and "money sent by me, not to me" look identical. The next two lessons fix this with networks that read in order (RNNs) and networks that relate every word to every other (attention).

## Key terms

- **Token** — a piece of text (word, sub-word or character).
- **Vocabulary** — the set of tokens the model knows, each with an id.
- **Padding** — filler ids that make sequences the same length.
- **Embedding** — a learned dense vector for each token.
- **Cosine similarity** — how closely two vectors point the same way.

**Takeaway:** Text becomes tokens, tokens become ids, and ids become learned embeddings in which words used alike sit close together.

## Try it yourself

1. Change `embedding_dim` to 2 and plot every word's 2-D embedding with its label. Do topics form groups?
2. Add five messages in Kinyarwanda to the training data (for example "internet ntikora i Huye"). What happens to unknown words at test time?
3. Find the test messages with the lowest confidence. Why are they harder?
4. Write a character-level `encode` function. What are its advantages for misspelled messages?
""",
            "quiz": [
                ("What is a token?",
                 ["A password", "A piece of text such as a word, sub-word or character", "A GPU", "A label"],
                 1, "Text is split into tokens before modelling."),
                ("What is a word embedding?",
                 ["A one-hot vector", "A short learned vector of numbers for each token", "The text itself", "The vocabulary size"],
                 1, "Embeddings are learned during training."),
                ("Why are embeddings better than one-hot vectors?",
                 ["They are longer", "They are short and place words used alike close together", "They need no training", "They store the text"],
                 1, "Dense vectors capture similarity."),
                ("What does the <pad> token do?",
                 ["Marks unknown words", "Fills short sequences up to a fixed length", "Ends the training", "Marks spam"],
                 1, "Batches need equal lengths."),
                ("What is the main weakness of averaging word embeddings?",
                 ["It is too slow", "It ignores word order", "It cannot learn", "It needs images"],
                 1, "A bag of words loses order."),
                ("Why do large language models use sub-word tokens?",
                 ["To handle any word, even rare ones, with a fixed vocabulary", "To make text longer", "Because words are illegal", "To avoid embeddings"],
                 0, "Rare words split into known pieces."),
            ],
        },
        # ------------------------------------------------------------------ 20
        {
            "title": "Recurrent Networks and LSTMs for Sequences",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=YCzL96nL7j0",
            "content": r"""
**Learning objective:** Explain how recurrent networks carry memory through a sequence, why LSTMs were invented, and forecast a time series with an LSTM compared with honest baselines.

## Data that comes in order

Sales per day, rainfall per week, words in a sentence, heartbeats in an ECG — in a **sequence**, order carries meaning. A **recurrent neural network (RNN)** reads one step at a time and keeps a **hidden state**: a running summary of everything it has seen so far.

> new hidden state = activation(W × current input + U × previous hidden state + b)

The same weights are used at every step — like weight sharing in a CNN, but along time.

## The trouble with plain RNNs

Training an RNN means backpropagating through every time step — a very deep network. Gradients vanish (or explode) over long sequences, so a plain RNN forgets what happened more than a few steps ago.

The **LSTM** (Long Short-Term Memory, 1997) adds a **cell state** — a conveyor belt of memory — controlled by three **gates**:

| Gate | Decides |
|---|---|
| Forget gate | What to erase from memory |
| Input gate | What new information to store |
| Output gate | What to reveal as the hidden state |

Gates are small sigmoid layers whose outputs (0 to 1) act like taps. The **GRU** is a simpler cousin with two gates. Before transformers (2017), LSTMs powered speech recognition and machine translation.

## The data: daily electricity demand

We simulate two years of daily electricity demand (in megawatts) for a city: a weekly pattern (lower on weekends), slow growth, a yearly wave and noise.

```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt

rng = np.random.default_rng(4)
days = np.arange(730)
weekly = np.array([1.0, 1.02, 1.03, 1.03, 1.05, 0.92, 0.85])[days % 7]
demand = (150 + 0.04 * days) * weekly + 8 * np.sin(2 * np.pi * days / 365) + rng.normal(0, 3, len(days))

plt.plot(demand)
plt.xlabel("day")
plt.ylabel("demand (MW)")
plt.title("Simulated daily electricity demand")
plt.show()
```

## Windows: turn a series into examples

Each example is the last **28 days**; the target is the **next** day. We train on the first 600 days and test on the rest — never shuffle time series across the split, or the model sees the future.

```python
WINDOW = 28
mean, std = demand[:600].mean(), demand[:600].std()      # training statistics only
z = (demand - mean) / std

X = np.stack([z[i:i + WINDOW] for i in range(len(z) - WINDOW)])
y = z[WINDOW:]
split = 600 - WINDOW
X_train, y_train, X_test, y_test = X[:split], y[:split], X[split:], y[split:]
real = y_test * std + mean
print(X_train.shape, X_test.shape)
```

## Baselines first

```python
yesterday = X_test[:, -1] * std + mean          # "tomorrow = today"
last_week = X_test[:, -7] * std + mean          # "tomorrow = same day last week"
print("MAE, same as yesterday:", round(np.abs(yesterday - real).mean(), 2), "MW")
print("MAE, same as last week:", round(np.abs(last_week - real).mean(), 2), "MW")
```

"Same as yesterday" is poor (about **11 MW** off) because of the weekend drop; "same day last week" is strong (about **3.5 MW**). Any model must beat **3.5**.

## An LSTM forecaster

```python
class Forecaster(nn.Module):
    def __init__(self, hidden=32):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden, batch_first=True)
        self.out = nn.Linear(hidden, 1)

    def forward(self, x):                    # x: (batch, 28 days)
        outputs, (h, c) = self.lstm(x.unsqueeze(-1))
        return self.out(outputs[:, -1]).squeeze(-1)   # use the state after the last day

t = lambda a: torch.tensor(a, dtype=torch.float32)
torch.manual_seed(0)
model = Forecaster()
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
for epoch in range(60):
    model.train()
    perm = torch.randperm(len(X_train))
    for start in range(0, len(perm), 32):
        idx = perm[start:start + 32]
        opt.zero_grad()
        F.mse_loss(model(t(X_train[idx])), t(y_train[idx])).backward()
        opt.step()

model.eval()
with torch.no_grad():
    forecast = model(t(X_test)).numpy() * std + mean
print("MAE, LSTM:", round(np.abs(forecast - real).mean(), 2), "MW")

plt.plot(real, label="real")
plt.plot(forecast, label="LSTM forecast")
plt.legend()
plt.title("Test period: next-day forecasts")
plt.show()
```

The LSTM is off by about **2.9 MW**, beating the strong weekly baseline (about 3.5). It learned the weekly rhythm **and** the slower changes from the data, with no calendar given to it.

## Sequences beyond time series

- `nn.LSTM` also reads **text**: feed it the word embeddings from Lesson 19 instead of one number per day.
- **Bidirectional** LSTMs read forwards and backwards (useful for whole sentences).
- For many sequence tasks today, **transformers** (next lesson) are faster to train and more accurate, but LSTMs remain useful for small data and streaming signals on small devices.

## Key terms

- **Sequence** — data where order matters.
- **RNN** — a network that reads step by step and keeps a hidden state.
- **Hidden state** — the running memory of an RNN.
- **LSTM / GRU** — RNNs with gates that keep long-term memory.
- **Window** — a fixed number of past steps used as one example.
- **Seasonal baseline** — "same as last week": the forecast to beat.

**Takeaway:** RNNs and LSTMs carry a memory along a sequence; for forecasting, build windows without peeking at the future and always beat a seasonal baseline.

## Try it yourself

1. Replace `nn.LSTM` with `nn.GRU`. Is it better, worse or the same?
2. Use a 14-day window instead of 28. What happens to the error, and why?
3. Forecast 7 days ahead instead of 1 (change the target). How much harder is it?
4. Add the day of the week as a second input feature (`input_size=2`). Does the LSTM improve?
""",
            "quiz": [
                ("What does an RNN keep while reading a sequence?",
                 ["Nothing", "A hidden state summarising what it has seen", "The whole dataset", "Only the last input"],
                 1, "The hidden state is its memory."),
                ("Why were LSTMs invented?",
                 ["To process images", "Plain RNNs forget long-range information because gradients vanish", "To replace embeddings", "To make networks smaller"],
                 1, "Gates and a cell state keep long-term memory."),
                ("What does the forget gate of an LSTM decide?",
                 ["What to erase from memory", "The learning rate", "The batch size", "Which word comes next"],
                 0, "Gates act like taps between 0 and 1."),
                ("Why must time-series data not be shuffled across the train/test split?",
                 ["Shuffling is slow", "The model would see the future, making the test dishonest", "LSTMs cannot read shuffled data", "It changes the units"],
                 1, "Train on the past, test on the future."),
                ("Which baseline was strongest for daily demand with a weekly pattern?",
                 ["Same as yesterday", "Same day last week", "The overall mean", "Zero"],
                 1, "It captures the weekly rhythm."),
                ("What does batch_first=True mean in nn.LSTM?",
                 ["The batch dimension comes first: (batch, time, features)", "Train the first batch only", "Sort batches", "Shuffle batches"],
                 0, "It sets the tensor layout."),
            ],
        },
        # ------------------------------------------------------------------ 21
        {
            "title": "Attention and Transformers",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=eMlx5fFNoYc",
            "content": r"""
**Learning objective:** Compute self-attention step by step, explain queries, keys, values, heads and positional encodings, and build a small transformer classifier in PyTorch.

## The idea that changed AI

In 2017 a Google paper called **"Attention Is All You Need"** introduced the **transformer**. Instead of reading words one at a time like an RNN, every word looks at **every other word at once** and decides which ones matter for its meaning. In "the bank of the river", the word "bank" pays attention to "river" and so means riverside, not money. Transformers power ChatGPT, Claude, Gemini, translation, and modern vision and speech models.

## Self-attention in four steps

Each token's embedding is turned into three vectors by three learned weight matrices:

- **Query (Q)** — "what am I looking for?"
- **Key (K)** — "what do I contain?"
- **Value (V)** — "what information do I pass on?"

Then:

1. **Scores:** compare every query with every key (dot product).
2. **Scale:** divide by √(dimension) to keep numbers moderate.
3. **Softmax:** turn each row of scores into attention weights that sum to 1.
4. **Mix:** each token's new vector is the weighted average of all the values.

> Attention(Q, K, V) = softmax(Q Kᵀ ÷ √d) V

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)
tokens = ["money", "sent", "to", "landlord"]
d = 8
x = torch.randn(len(tokens), d)                     # pretend embeddings
Wq, Wk, Wv = (torch.randn(d, d) * 0.5 for _ in range(3))

Q, K, V = x @ Wq, x @ Wk, x @ Wv
scores = Q @ K.T / d ** 0.5                         # every token vs every token
weights = F.softmax(scores, dim=-1)                 # each row sums to 1
output = weights @ V

print("attention weights (row = token looking, column = token looked at):")
for tok, row in zip(tokens, weights):
    print(f"{tok:9s}", [round(w, 2) for w in row.tolist()])
print(output.shape)
```

With random weights the pattern is meaningless; training makes it useful. The output has the same shape as the input — one new, **context-aware** vector per token.

PyTorch has this built in, optimised for GPUs:

```python
same = F.scaled_dot_product_attention(Q.unsqueeze(0), K.unsqueeze(0), V.unsqueeze(0))
print(torch.allclose(same[0], output, atol=1e-5))
```

## Multi-head attention

One attention pattern cannot capture everything (grammar, meaning, references…). **Multi-head attention** runs several attention operations ("heads") in parallel on smaller slices of the vectors and joins the results. `nn.MultiheadAttention(embed_dim=32, num_heads=4)` gives four heads of 8 dimensions each.

## Order: positional encodings

Attention by itself treats a sentence like a bag of words — it has no idea which word came first. Transformers **add a position vector** to each token's embedding (fixed sine waves, or learned position embeddings), so "dog bites man" and "man bites dog" differ.

## The transformer block

> x → multi-head self-attention → add & normalise → feed-forward network → add & normalise

The "add" steps are residual connections (Lesson 10), and "normalise" is **layer normalisation**. Models stack many blocks: about 12 in early BERT, around a hundred in today's largest language models.

- **Encoder** blocks (BERT style) see the whole text — good for classification and search.
- **Decoder** blocks (GPT style) only look at earlier tokens (a **causal mask**) and are trained to predict the next token — that is how chatbots generate text.

## A small transformer classifier

Let's give the customer-message router from Lesson 19 a transformer encoder.

{MESSAGES}

{VOCAB}

```python
class TinyTransformer(nn.Module):
    def __init__(self, vocab_size, d=32, heads=4, layers=2, max_len=14, n_classes=3):
        super().__init__()
        self.tok = nn.Embedding(vocab_size, d, padding_idx=0)
        self.pos = nn.Embedding(max_len, d)                     # learned positions
        block = nn.TransformerEncoderLayer(d_model=d, nhead=heads, dim_feedforward=64,
                                           dropout=0.1, batch_first=True)
        self.encoder = nn.TransformerEncoder(block, num_layers=layers, enable_nested_tensor=False)
        self.out = nn.Linear(d, n_classes)

    def forward(self, x):
        positions = torch.arange(x.shape[1], device=x.device)
        h = self.tok(x) + self.pos(positions)
        h = self.encoder(h, src_key_padding_mask=(x == 0))     # ignore padding
        mask = (x != 0).unsqueeze(-1).float()
        return self.out((h * mask).sum(1) / mask.sum(1))

torch.manual_seed(0)
tiny = TinyTransformer(len(vocab))
print("parameters:", sum(p.numel() for p in tiny.parameters()))
print("test accuracy:", fit(tiny, epochs=20, lr=1e-3))
```

The transformer also routes the messages almost perfectly. On this easy, template-made data, the simple bag of embeddings was already enough — the transformer's advantage shows on long, real text where word order and context matter, and above all when it is **pretrained** on huge amounts of text and then fine-tuned (transfer learning again, as in Lesson 16).

## Why transformers won

- **Parallel:** all tokens are processed at once, so GPUs train them much faster than RNNs.
- **Long range:** any word can attend directly to any other, however far apart.
- **Scale:** performance keeps improving with more data, parameters and computing — the path to large language models.

The price: attention compares every token with every other, so cost grows with the **square** of the text length.

## Key terms

- **Self-attention** — every token weighs every other token to build a context-aware vector.
- **Query, key, value** — the three learned projections used by attention.
- **Multi-head attention** — several attention patterns in parallel.
- **Positional encoding** — information about word order added to embeddings.
- **Transformer block** — attention + feed-forward, with residuals and layer norm.
- **Encoder / decoder** — sees all tokens / sees only earlier tokens (for generation).

**Takeaway:** Attention lets every token look at every other token at once; stacked with feed-forward layers, residuals and positions, it forms the transformer behind modern AI.

## Try it yourself

1. In the attention example, multiply `Wq` by 10. What happens to the attention weights, and why does dividing by √d matter?
2. Add a causal mask (`torch.triu`) to the scores so tokens cannot look at later tokens. Print the new weights.
3. Train `TinyTransformer` with 1 layer and 1 head. Does it still work on these messages?
4. Count how many attention scores a 2,000-token document needs per head and per layer.
""",
            "quiz": [
                ("What does self-attention let each token do?",
                 ["Ignore the other tokens", "Weigh every other token to build a context-aware representation", "Sort the sentence", "Delete padding"],
                 1, "Every token attends to all tokens."),
                ("In attention, what are the scores computed from?",
                 ["Values and labels", "Dot products of queries and keys", "The learning rate", "Pixel colours"],
                 1, "softmax(Q Kᵀ ÷ √d) V."),
                ("Why do transformers need positional encodings?",
                 ["Attention alone ignores word order", "To make the model smaller", "To replace embeddings", "To mask padding"],
                 0, "Positions tell the model where each word is."),
                ("What is multi-head attention?",
                 ["Several attention patterns computed in parallel", "A network with many outputs", "Two GPUs", "A type of pooling"],
                 0, "Each head can focus on different relations."),
                ("How do GPT-style decoders generate text?",
                 ["By looking only at earlier tokens and predicting the next one", "By sorting words", "By reading images", "By averaging embeddings"],
                 0, "A causal mask hides future tokens."),
                ("What is a main cost of attention?",
                 ["It cannot use GPUs", "Its cost grows with the square of the sequence length", "It needs no data", "It forgets everything"],
                 1, "Every token is compared with every token."),
            ],
        },
        # ------------------------------------------------------------------ 22
        {
            "title": "Autoencoders and Generative Models",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=bbOFvxbMIV0",
            "content": r"""
**Learning objective:** Build an autoencoder that compresses images into a tiny code, use it to detect unusual inputs and to create new images, and explain how VAEs, GANs and diffusion models generate data.

## Learning without labels — again

An **autoencoder** is a network trained to **copy its input to its output** through a narrow middle layer called the **bottleneck**:

> image → encoder → small code → decoder → rebuilt image

Because the code is small, the network cannot memorise every pixel. It must learn the most important patterns — a kind of non-linear PCA (Machine Learning Fundamentals, Lesson 20). No labels are needed: the image is its own target.

## An autoencoder for digits

We squeeze each 64-pixel digit into just **2 numbers**:

```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits

digits = load_digits()
X = torch.tensor(digits.data / 16.0, dtype=torch.float32)
labels = digits.target

torch.manual_seed(0)
encoder = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 2))
decoder = nn.Sequential(nn.Linear(2, 32), nn.ReLU(), nn.Linear(32, 64), nn.Sigmoid())
opt = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=1e-3)

for epoch in range(100):
    perm = torch.randperm(len(X))
    for start in range(0, len(perm), 64):
        idx = perm[start:start + 64]
        opt.zero_grad()
        loss = F.mse_loss(decoder(encoder(X[idx])), X[idx])   # target = the input itself
        loss.backward()
        opt.step()
print("reconstruction error:", round(loss.item(), 4))
```

## Look at the rebuilt digits

```python
with torch.no_grad():
    rebuilt = decoder(encoder(X[:8]))
fig, axes = plt.subplots(2, 8, figsize=(10, 3))
for k in range(8):
    axes[0, k].imshow(X[k].view(8, 8), cmap="gray_r"); axes[0, k].axis("off")
    axes[1, k].imshow(rebuilt[k].view(8, 8), cmap="gray_r"); axes[1, k].axis("off")
axes[0, 0].set_title("original", loc="left"); axes[1, 0].set_title("from 2 numbers", loc="left")
plt.show()
```

From only two numbers the decoder rebuilds blurry but recognisable digits.

## The map of the code space

```python
with torch.no_grad():
    codes = encoder(X).numpy()
plt.figure(figsize=(6, 5))
plt.scatter(codes[:, 0], codes[:, 1], c=labels, cmap="tab10", s=6)
plt.colorbar(label="digit")
plt.title("Every digit as a point in the 2-D code space")
plt.show()
```

Digits of the same kind gather in the same regions — although the autoencoder **never saw a label**.

## Use 1 — Anomaly detection

An autoencoder rebuilds well only what looks like its training data. Anything unusual comes back badly:

```python
with torch.no_grad():
    digit_error = ((decoder(encoder(X)) - X) ** 2).mean(dim=1)
    noise = torch.rand(20, 64)
    noise_error = ((decoder(encoder(noise)) - noise) ** 2).mean(dim=1)
print("average error, real digits: ", round(digit_error.mean().item(), 3))
print("average error, random noise:", round(noise_error.mean().item(), 3))
```

Random noise has an error about **five times** larger. The same trick flags unusual machine vibrations, network traffic or transactions — without any labelled examples of failures.

## Use 2 — Generating new images

Pick new points in the code space and decode them: images that were **never in the dataset**.

```python
grid = torch.tensor([[a, b] for b in np.linspace(codes[:, 1].max(), codes[:, 1].min(), 6)
                            for a in np.linspace(codes[:, 0].min(), codes[:, 0].max(), 6)],
                    dtype=torch.float32)
with torch.no_grad():
    made = decoder(grid)
fig, axes = plt.subplots(6, 6, figsize=(6, 6))
for ax, img in zip(axes.ravel(), made):
    ax.imshow(img.view(8, 8), cmap="gray_r")
    ax.axis("off")
plt.suptitle("New digits decoded from points on a grid")
plt.show()
```

Moving across the grid morphs one digit smoothly into another. A plain autoencoder's code space has gaps, though, so some points decode to nonsense.

## The generative model family

| Model | Idea | Known for |
|---|---|---|
| **VAE** (variational autoencoder) | Forces the code space to be smooth and filled, so any point decodes to something sensible | Smooth latent spaces, science data |
| **GAN** (generative adversarial network) | A generator fakes images; a discriminator tries to catch fakes; both improve | Very sharp faces (2014–2020) |
| **Diffusion model** | Learns to remove noise step by step, starting from pure noise | Stable Diffusion, DALL-E, video models |
| **Autoregressive transformer** | Predicts the next token again and again | ChatGPT, Claude, music and code generation |

## Responsibility

Generative models can create **deepfakes**, fake documents and misleading images. Label AI-generated content, never generate content that imitates real people or official documents, and respect the rights of the people whose data trained the model.

## Key terms

- **Autoencoder** — a network trained to rebuild its input through a bottleneck.
- **Encoder / decoder** — compresses to a code / rebuilds from a code.
- **Latent (code) space** — the space of compressed codes.
- **Reconstruction error** — how badly the input is rebuilt; high for anomalies.
- **VAE, GAN, diffusion** — families of generative models.

**Takeaway:** Autoencoders learn compact codes without labels; their reconstruction error spots anomalies, and decoding new codes generates new data — the doorway to modern generative AI.

## Try it yourself

1. Use a bottleneck of 8 instead of 2. How do the reconstructions and the error change?
2. Train the autoencoder only on digits 0–4, then compare the reconstruction error of digits 5–9. Could this detect "new kinds" of data?
3. Add noise to the inputs but keep clean targets (a **denoising** autoencoder). Show noisy inputs and the cleaned outputs.
4. In two sentences, explain to a friend how a diffusion model makes an image.
""",
            "quiz": [
                ("What is an autoencoder trained to do?",
                 ["Predict labels", "Rebuild its own input through a small bottleneck", "Sort images", "Translate text"],
                 1, "The input is its own target."),
                ("Why must the bottleneck be small?",
                 ["To force the network to learn the most important patterns instead of copying", "To save electricity only", "Because GPUs require it", "To add labels"],
                 0, "Compression forces useful features."),
                ("How can an autoencoder detect anomalies?",
                 ["Unusual inputs are rebuilt badly, so their reconstruction error is high", "It counts pixels", "It uses labels of failures", "It cannot"],
                 0, "High error means 'not like the training data'."),
                ("How can a trained decoder generate new images?",
                 ["By decoding new points from the code space", "By copying training images", "By sorting labels", "By adding noise to labels"],
                 0, "New codes give new images."),
                ("Which model family powers tools like Stable Diffusion?",
                 ["k-means", "Diffusion models that remove noise step by step", "Decision trees", "LSTMs only"],
                 1, "They start from noise and denoise."),
                ("In a GAN, what does the discriminator do?",
                 ["Generates images", "Tries to tell real images from generated ones", "Encodes text", "Sets the learning rate"],
                 1, "Generator and discriminator compete."),
            ],
        },
        # ------------------------------------------------------------------ 23
        {
            "title": "Deploying Deep Learning Responsibly",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=cswXUNtUfuI",
            "content": r"""
**Learning objective:** Save and reload a trained network, measure its size and speed, serve it behind a web API, and plan monitoring, privacy and fairness for a deployed deep-learning system.

## From notebook to product

A model in a notebook helps nobody. To be useful it must be saved, loaded by an application (a website, a phone app, a USSD or WhatsApp service), answer fast enough, and be **watched** while people use it.

We deploy the digit reader from Week 2.

```python
import time
import io
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

digits = load_digits()
X_train, X_test, y_train, y_test = train_test_split(digits.data / 16.0, digits.target,
                                                    test_size=0.2, random_state=0, stratify=digits.target)
Xtr, Xte = torch.tensor(X_train, dtype=torch.float32), torch.tensor(X_test, dtype=torch.float32)
ytr, yte = torch.tensor(y_train), torch.tensor(y_test)

class DigitNet(nn.Module):
    def __init__(self, hidden=64):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(64, hidden), nn.ReLU(), nn.Linear(hidden, 10))

    def forward(self, x):
        return self.net(x)

torch.manual_seed(0)
model = DigitNet()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
for epoch in range(40):
    perm = torch.randperm(len(Xtr))
    for start in range(0, len(perm), 32):
        idx = perm[start:start + 32]
        opt.zero_grad()
        F.cross_entropy(model(Xtr[idx]), ytr[idx]).backward()
        opt.step()
model.eval()
with torch.no_grad():
    test_acc = (model(Xte).argmax(1) == yte).float().mean().item()
print("test accuracy:", round(test_acc, 3))
```

## Save a checkpoint

Save the weights **plus** everything needed to use them correctly:

```python
checkpoint = {
    "state_dict": model.state_dict(),
    "hidden": 64,
    "input_scaling": "divide pixels by 16",
    "classes": list(range(10)),
    "test_accuracy": round(test_acc, 3),
    "torch_version": torch.__version__,
}
torch.save(checkpoint, "digitnet_v1.pt")

loaded = torch.load("digitnet_v1.pt", weights_only=False)
model2 = DigitNet(loaded["hidden"])
model2.load_state_dict(loaded["state_dict"])
model2.eval()
print("same predictions:", torch.equal(model2(Xte).argmax(1), model(Xte).argmax(1)))
```

Only load checkpoint files you trust: `weights_only=False` allows a file to run code when opened. For files from others, keep the default `weights_only=True` and save only tensors and plain values.

## Size and speed

```python
buffer = io.BytesIO()
torch.save(model.state_dict(), buffer)
print("model size:", round(buffer.getbuffer().nbytes / 1024, 1), "KB")

one = Xte[:1]
with torch.inference_mode():
    start = time.perf_counter()
    for _ in range(1000):
        model(one)
    per_image = (time.perf_counter() - start) / 1000
    start = time.perf_counter()
    model(Xte)
    batch_time = time.perf_counter() - start
print(f"one image: {per_image * 1e6:.0f} microseconds;  {len(Xte)} images in one batch: {batch_time * 1e3:.1f} ms")
```

This tiny model is about 21 KB and answers in microseconds. A ResNet-50 is about 100 MB; a large language model needs many gigabytes and powerful GPUs. Ways to make big models practical:

- **Batching** — answer many requests together (much faster per item).
- **Half precision** (`model.half()` on a GPU) — half the memory, often faster.
- **Quantisation** — store weights in 8 bits or fewer; small models for phones.
- **Distillation** — train a small "student" to copy a big "teacher".
- **Export** to **ONNX**, TensorFlow Lite or Core ML to run on phones and edge devices without Python.

## Serve it behind an API

A web API lets any app send an image and get an answer. Here with **FastAPI** — the same framework that powers the WAMUGII website:

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="Digit reader")

class DigitImage(BaseModel):
    pixels: list[float] = Field(min_length=64, max_length=64)   # 8 x 8 values, 0..16

@app.post("/predict")
def predict(image: DigitImage):
    x = torch.tensor([image.pixels], dtype=torch.float32) / 16.0
    with torch.inference_mode():
        probs = F.softmax(model2(x), dim=1)[0]
    best = int(probs.argmax())
    confident = float(probs[best]) >= 0.8
    return {"digit": best, "confidence": round(float(probs[best]), 3),
            "action": "accept" if confident else "send to a person"}

client = TestClient(app)                 # test the API without starting a server
response = client.post("/predict", json={"pixels": digits.data[0].tolist()})
print(response.status_code, response.json())
print(client.post("/predict", json={"pixels": [1.0, 2.0]}).status_code)   # bad input is rejected
```

In production you would run it with `uvicorn`, inside Docker, on a server — as you did for the WAMUGII platform. Notice two good habits: **input validation** (exactly 64 pixels) and a **confidence rule** that sends unsure cases to a person.

## Watch it after launch

- **Inputs:** are new images darker, blurrier, from new phones? (data drift)
- **Outputs:** has the share of "send to a person" jumped?
- **Truth:** collect a sample of real cases with correct labels every month and re-measure accuracy.
- **Groups:** check results by region, language, device or skin tone where relevant.
- **Retrain** with new, representative data when performance falls — and test the new model before replacing the old one.

## Responsible deep learning

- **Privacy:** photos, voices and messages are personal data. Rwanda's data protection law (Law No. 058/2021) requires a lawful purpose, consent or another legal basis, security, and limits on keeping data. Collect only what you need.
- **Consent and fairness to data givers:** farmers, patients and customers who provide data should know how it is used.
- **Transparency:** write a model card (Machine Learning Fundamentals, Lesson 23): purpose, training data, accuracy, limits.
- **Energy and cost:** training big models uses a lot of electricity; reuse pretrained models and choose the smallest model that does the job.
- **Human oversight:** high-stakes decisions (health, credit, justice) need a person in the loop.

## Key terms

- **Checkpoint** — a saved file with weights and the settings needed to use them.
- **Inference** — using a trained model to make predictions.
- **Latency** — time to answer one request.
- **Quantisation / distillation** — making models smaller and faster.
- **API** — a web interface that apps call to get predictions.
- **Data drift** — real inputs changing over time.

**Takeaway:** Deploying a network means saving it with its settings, serving it fast behind a validated API, routing unsure cases to people, and monitoring it — while protecting privacy and staying transparent.

## Try it yourself

1. Add `"version": "v1"` to the API response and a GET endpoint `/health` that returns `{"status": "ok"}`. Test both with `TestClient`.
2. Time the model on batches of 1, 32 and 360 images. How does the time per image change?
3. Make the API reject pixel values outside 0–16 (hint: `Field(ge=0, le=16)` on the items).
4. Write a half-page monitoring plan for a crop-disease app used by 10,000 farmers.
""",
            "quiz": [
                ("What should a checkpoint contain besides the weights?",
                 ["Nothing else", "The settings needed to rebuild and use the model correctly, such as input scaling", "The training data", "Passwords"],
                 1, "Without the settings, the weights are easy to misuse."),
                ("Why only load checkpoint files you trust?",
                 ["They are large", "Loading with weights_only=False can run code from the file", "They expire", "They contain labels"],
                 1, "Untrusted files are a security risk."),
                ("What does batching do for inference?",
                 ["Answers many requests together, much faster per item", "Makes the model bigger", "Changes the labels", "Stops monitoring"],
                 0, "GPUs and CPUs work best on batches."),
                ("Which technique stores weights in 8 bits or fewer to make models smaller?",
                 ["Dropout", "Quantisation", "Augmentation", "Attention"],
                 1, "Quantisation shrinks models for phones."),
                ("Why does the API send low-confidence answers to a person?",
                 ["To keep a human in the loop where the model is unsure", "To slow the system down", "Because FastAPI requires it", "To collect passwords"],
                 0, "Human oversight for uncertain cases."),
                ("Which Rwandan law governs personal data such as photos and voices?",
                 ["Law No. 058/2021 on the protection of personal data and privacy", "There is none", "A traffic law", "The tax code"],
                 0, "Photos and voices are personal data."),
            ],
        },
        # ------------------------------------------------------------------ 24
        {
            "title": "Final Project: A Deep-Learning System and Certificate",
            "minutes": 120,
            "video": "https://www.youtube.com/watch?v=ZAGiinWiFsE",
            "content": r"""
**Learning objective:** Design, build, evaluate and present a complete deep-learning system for a real problem, using everything in this course — and earn your certificate.

## Choose your track

| Track | Problem | Starting point |
|---|---|---|
| **A — Vision** | Recognise 3+ classes of images (crop conditions, local fruits, waste types, road signs…) | Week 3 project: ImageFolder + pretrained ResNet |
| **B — Forecasting** | Forecast a daily or hourly series (sales, electricity, rainfall, clinic visits) | Lesson 20 LSTM, with seasonal baselines |
| **C — Language** | Sort messages, reviews or questions into categories, in English, Kinyarwanda or both | Lessons 19 and 21: embeddings and a transformer |

Use **real data** where you can: your own photos (with permission), open data from the National Institute of Statistics of Rwanda or Kaggle, or anonymised data from your workplace. If you cannot get real data, extend the simulated datasets from this course and say so clearly.

## The seven parts (every track)

1. **Problem and users** — who will use it, what decision it supports, what a mistake costs.
2. **Data** — source, size, classes or variables, cleaning, train / validation / test split (by time for forecasting), consent and privacy.
3. **Baseline** — a simple method first: logistic regression, "same as last week", or a bag of embeddings.
4. **Deep model** — architecture, why you chose it, augmentation or regularisation, optimiser, learning rate, early stopping.
5. **Evaluation** — test results used once, compared with the baseline; confusion matrix or error plot; mistakes studied; results by group where relevant.
6. **Trust** — confidence rule for human review; saliency maps (vision) or examples of hard cases; limits.
7. **Deployment plan** — checkpoint, a FastAPI endpoint (tested with `TestClient`), monitoring, retraining, model card.

## Starter checklist (copy into your notebook)

```python
CHECKLIST = [
    "Problem, users and cost of mistakes written down",
    "Data source, licence and consent recorded",
    "Train / validation / test split made before any modelling",
    "Baseline trained and scored",
    "Deep model trained with early stopping on validation data",
    "Test set used exactly once",
    "Mistakes and confidence studied",
    "Checkpoint saved with its settings",
    "API endpoint tested with TestClient",
    "Model card and monitoring plan written",
]
done = {item: False for item in CHECKLIST}
done["Problem, users and cost of mistakes written down"] = True
print(f"{sum(done.values())} of {len(done)} steps done")
for item, ok in done.items():
    print("[x]" if ok else "[ ]", item)
```

## Present it (10 minutes)

- Slide 1: the problem and the users.
- Slide 2: the data and its limits.
- Slide 3: baseline vs deep model (one table).
- Slide 4: one chart (learning curves, confusion matrix or forecast plot).
- Slide 5: risks, human oversight and the deployment plan.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Problem | Real users and costs of mistakes are clear |
| Data | Honest description, good splits, privacy respected |
| Method | Baseline first; deep model trained with validation and early stopping |
| Evaluation | Test used once; mistakes and groups analysed |
| Trust and deployment | Confidence rule, tested API, monitoring plan, model card |
| Communication | A non-expert understands the result in 10 minutes |

## Getting your certificate

1. Complete **every lesson** in the course.
2. The **final exam** then unlocks on the course page: 60 questions (single answer, multiple answers, true/false and fill in the blank), 90 minutes, 60% to pass, 3 attempts. The exam opens in full screen; leaving the exam screen is counted, and the third time ends the exam automatically.
3. Pass the exam and your **WAMUGII Certificate** appears on the course page with your score. Add it — and your project notebook — to your CV and LinkedIn.

## What you can do now

You can build neural networks from scratch and with PyTorch; train them well with good optimisers, regularisation, normalisation and early stopping; build CNNs with augmentation and transfer learning; work with sequences using embeddings, LSTMs and attention; create autoencoders; and deploy models responsibly. Next in the WAMUGII AI Program: **Modern AI — Large Language Models and Generative AI**, where you will use and adapt the transformers behind today's AI assistants.

**Takeaway:** A deep-learning system is more than a network: real users, honest data, a baseline, careful evaluation, human oversight and a deployment plan make it worth using.

## Try it yourself

Complete the seven parts for your track and present your project. Ask your instructor for feedback in the lesson Q&A below — share your notebook link and one question you want help with.
""",
            "quiz": [
                ("What should you build before the deep model?",
                 ["Nothing", "A simple baseline to compare against", "The API", "The certificate"],
                 1, "A baseline proves the deep model adds value."),
                ("How must a time-series project split its data?",
                 ["Randomly", "By time: train on the past, test on the future", "By label", "It does not matter"],
                 1, "Never let the model see the future."),
                ("How many times should the test set be used?",
                 ["Every epoch", "Once, at the end", "Never", "Twice"],
                 1, "Choices are made with validation data."),
                ("Which belongs in the trust part of the project?",
                 ["A confidence rule that sends unsure cases to a person", "Hiding mistakes", "Removing the baseline", "Using the test set for tuning"],
                 0, "Human review for uncertain predictions."),
                ("What is required before the final exam unlocks?",
                 ["Paying a fee", "Completing every lesson", "Passing a quiz once", "Nothing"],
                 1, "All lessons must be complete."),
                ("What is the pass mark of the final exam?",
                 ["50%", "60%", "75%", "100%"],
                 1, "60% unlocks the certificate."),
            ],
        },
    ],
}

for _lesson in WEEK4["lessons"]:
    _lesson["content"] = (_lesson["content"].replace("{MESSAGES}", MESSAGES)
                          .replace("{VOCAB}", VOCAB))
