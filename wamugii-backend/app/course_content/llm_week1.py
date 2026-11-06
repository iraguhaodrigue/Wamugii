"""Modern AI: LLMs & Generative AI -- Week 1: How Large Language Models Work. Original WAMUGII content."""

# A practice text made with code: thousands of short market-day sentences.
STORIES = r"""
```python
import random

random.seed(0)
names = ["Aline", "Eric", "Grace", "Jean", "Diane", "Patrick", "Claudine", "Samuel", "Ange", "Didier"]
places = ["Kigali", "Huye", "Musanze", "Rubavu", "Nyagatare", "Rusizi", "Muhanga"]
goods = ["tomatoes", "beans", "bananas", "avocados", "maize", "potatoes", "milk", "coffee", "rice", "cassava"]
verbs = ["sells", "buys", "carries", "cooks", "packs", "counts"]
times = ["in the morning", "at noon", "in the evening", "on Saturday", "after the rain", "before school"]
moods = ["happy", "tired", "busy", "proud", "calm", "hungry"]
templates = [
    "{n} {v} {g} in {p} {t}.",
    "In {p}, {n} {v} {g} {t}.",
    "{n} is {f} because the {g} are fresh.",
    "{t}, {n} goes to the market in {p}.",
    "{n} pays for the {g} with mobile money.",
    "The price of {g} in {p} is low {t}.",
    "{n} tells {m} that the {g} from {p} are the best.",
    "{n} and {m} share {g} {t}.",
]

def sentence():
    n, m = random.sample(names, 2)
    s = random.choice(templates).format(n=n, m=m, v=random.choice(verbs), g=random.choice(goods),
                                        p=random.choice(places), t=random.choice(times), f=random.choice(moods))
    return s[0].upper() + s[1:]

text = "\n".join(sentence() for _ in range(4000))
print(len(text), "characters")
print(text[:250])
```
""".strip()

# A small GPT (decoder-only transformer), shared by Lessons 4 and 6.
GPT = r"""
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

device = "cuda" if torch.cuda.is_available() else "cpu"
chars = sorted(set(text))
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for c, i in stoi.items()}
encode = lambda s: [stoi[c] for c in s]
decode = lambda ids: "".join(itos[i] for i in ids)

data = torch.tensor(encode(text), dtype=torch.long)
split = int(0.9 * len(data))
train_data, val_data = data[:split], data[split:]

BLOCK = 64          # how many characters the model can look back at (its context window)

def get_batch(source, batch_size=32):
    starts = torch.randint(len(source) - BLOCK - 1, (batch_size,))
    x = torch.stack([source[s:s + BLOCK] for s in starts])
    y = torch.stack([source[s + 1:s + BLOCK + 1] for s in starts])   # the next character at every position
    return x.to(device), y.to(device)

class Block(nn.Module):
    # One transformer block: masked self-attention + feed-forward, with residuals.
    def __init__(self, d, heads):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, heads, batch_first=True)
        self.ff = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
        mask = torch.triu(torch.ones(BLOCK, BLOCK, dtype=torch.bool), diagonal=1)
        self.register_buffer("mask", mask)              # True = may NOT look (the future)

    def forward(self, x):
        T = x.shape[1]
        h = self.ln1(x)
        a, _ = self.attn(h, h, h, attn_mask=self.mask[:T, :T], need_weights=False)
        x = x + a
        return x + self.ff(self.ln2(x))

class TinyGPT(nn.Module):
    def __init__(self, vocab, d=96, heads=4, layers=3):
        super().__init__()
        self.tok = nn.Embedding(vocab, d)
        self.pos = nn.Embedding(BLOCK, d)
        self.blocks = nn.Sequential(*[Block(d, heads) for _ in range(layers)])
        self.ln = nn.LayerNorm(d)
        self.head = nn.Linear(d, vocab)

    def forward(self, idx):
        T = idx.shape[1]
        x = self.tok(idx) + self.pos(torch.arange(T, device=idx.device))
        return self.head(self.ln(self.blocks(x)))       # logits: a score for every next character

    @torch.no_grad()
    def generate(self, idx, n_new, temperature=1.0, top_k=None):
        for _ in range(n_new):
            logits = self(idx[:, -BLOCK:])[:, -1, :] / temperature
            if top_k is not None:
                cutoff = torch.topk(logits, top_k).values[:, [-1]]
                logits[logits < cutoff] = -float("inf")
            next_id = torch.multinomial(F.softmax(logits, dim=-1), num_samples=1)
            idx = torch.cat([idx, next_id], dim=1)
        return idx

@torch.no_grad()
def estimate_loss(model, steps=20):
    model.eval()
    out = {}
    for name, source in [("train", train_data), ("val", val_data)]:
        losses = []
        for _ in range(steps):
            x, y = get_batch(source)
            logits = model(x)
            losses.append(F.cross_entropy(logits.reshape(-1, logits.shape[-1]), y.reshape(-1)).item())
        out[name] = sum(losses) / len(losses)
    model.train()
    return out

def train_gpt(steps=1500, seed=0):
    torch.manual_seed(seed)
    model = TinyGPT(len(chars)).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
    for step in range(steps + 1):
        if step % 500 == 0:
            l = estimate_loss(model)
            print(f"step {step:4d}: train loss {l['train']:.3f}, validation loss {l['val']:.3f}")
        if step == steps:
            break
        x, y = get_batch(train_data)
        logits = model(x)
        loss = F.cross_entropy(logits.reshape(-1, logits.shape[-1]), y.reshape(-1))
        opt.zero_grad()
        loss.backward()
        opt.step()
    return model

print("vocabulary:", len(chars), "characters")
```
""".strip()

WEEK1 = {
    "title": "Week 1 · How Large Language Models Work",
    "lessons": [
        # ------------------------------------------------------------------ 1
        {
            "title": "From Chatbots to Large Language Models",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=LPZh9BOjkQs",
            "content": r"""
**Learning objective:** Explain in plain words what a large language model (LLM) is, how the field got here, and build the simplest possible language model in Python.

## What is a language model?

A **language model** answers one question again and again: **"What comes next?"** Given "Murakoze ___", it gives a high probability to "cyane". Given "The capital of Rwanda is", it gives a high probability to "Kigali".

A **large** language model does exactly this, with billions of learned numbers (parameters), trained on a huge amount of text. ChatGPT, Claude, Gemini, Llama and Mistral are all LLMs. When you chat with one, it writes its answer **one small piece at a time**, each time choosing a likely next piece.

> An LLM is a next-word predictor so good, and trained on so much text, that predicting well requires something that looks like knowledge and reasoning.

## A short history

| Years | Idea | Limitation |
|---|---|---|
| 1960s–1990s | Rule-based chatbots (ELIZA) | Only followed hand-written patterns |
| 1990s–2000s | **n-gram** models: count which words follow which | Only look back 2–4 words |
| 2013 | Word embeddings (word2vec) | Meaning as numbers, but no sentences |
| 2014–2017 | Recurrent networks (LSTMs) for translation | Slow, forget long texts |
| **2017** | **The transformer** ("Attention Is All You Need") | — |
| 2018–2020 | BERT, GPT-2, GPT-3: pretrain on huge text | Raw models ramble, follow no instructions |
| 2022 → | ChatGPT, Claude, Gemini: **instruction tuning + human feedback** | Still can be wrong (hallucinate) |

Three ingredients made the jump possible: the **transformer**, **enormous text datasets**, and **GPUs** to train very large models. You met the transformer in Deep Learning & Neural Networks; this course shows how it becomes a useful AI system.

## How this course works

- **Week 1:** how LLMs work inside — tokens, next-token prediction, sampling, a small GPT you train yourself, and how base models become assistants.
- **Week 2:** building with LLM APIs — prompts, structured output, tools, conversations, cost and reliability.
- **Week 3:** embeddings, vector search and **RAG** (letting a model answer from your own documents), plus evaluation.
- **Week 4:** agents, fine-tuning, image and speech generation, open models, and safety.

## The text we learn from

To train our own models this week we need text. We generate thousands of short "market day" sentences with code, so everyone has the same data and nothing needs downloading:

{STORIES}

## The simplest language model: counting

A **bigram model** predicts the next word only from the current word, by counting how often each pair appears:

```python
from collections import Counter, defaultdict

words = text.replace("\n", " \n ").split(" ")
following = defaultdict(Counter)
for current, nxt in zip(words, words[1:]):
    following[current][nxt] += 1

print("After 'pays' comes:", following["pays"].most_common(3))
print("After 'the' comes: ", following["the"].most_common(5))
```

After "pays" the model has only ever seen "for" — it is certain. After "the" there are many options — it must choose.

## Let it write

```python
def generate_bigram(start, n_words=15, seed=1):
    rng = random.Random(seed)
    out = [start]
    for _ in range(n_words):
        options = following[out[-1]]
        if not options:
            break
        choices, counts = zip(*options.items())
        out.append(rng.choices(choices, weights=counts)[0])   # pick in proportion to the counts
    return " ".join(out).replace(" \n ", "\n")

print(generate_bigram("Grace"))
print(generate_bigram("In"))
```

The output uses real words in plausible pairs, but the sentences soon go wrong: "Grace share bananas from Musanze is low on Saturday." Every pair of words is fine; the sentence is not. The model only remembers **one** word. An LLM uses a transformer to look back over **thousands** of tokens, which is why its writing stays on topic.

## Key terms

- **Language model** — predicts the next piece of text.
- **LLM** — a very large transformer language model trained on huge text collections.
- **Parameters** — the learned numbers inside the model.
- **n-gram / bigram model** — predicts from the last n − 1 words by counting.
- **Context** — the text the model can see when predicting.

**Takeaway:** Every LLM is a next-token predictor; the transformer lets it use a long context, and scale makes its predictions remarkably capable.

## Try it yourself

1. Print the five most common words after "in". Why are they all places?
2. Generate ten sentences starting with "The". How many are grammatical?
3. Build a **trigram** model that looks at the last two words. Is its writing better?
4. Ask a chatbot "What comes after: The capital of Rwanda is" and compare with what your bigram model would say.
""",
            "quiz": [
                ("What question does a language model answer again and again?",
                 ["What is the topic?", "What comes next?", "Is this true?", "Who wrote this?"],
                 1, "LLMs predict the next piece of text."),
                ("Which 2017 invention made modern LLMs possible?",
                 ["ELIZA", "The transformer", "word2vec", "The bigram model"],
                 1, "'Attention Is All You Need' introduced it."),
                ("What turned raw pretrained models into helpful assistants like ChatGPT and Claude?",
                 ["Bigger fonts", "Instruction tuning and human feedback", "More n-grams", "Removing the transformer"],
                 1, "Base models were tuned to follow instructions."),
                ("How much context does a bigram model use?",
                 ["The whole book", "Only the current word", "The last 1,000 words", "None"],
                 1, "It predicts from one word."),
                ("Why does the bigram model's writing wander off topic?",
                 ["It has no data", "It only remembers one word", "It is too large", "It uses a GPU"],
                 1, "No long context means no long-range coherence."),
                ("What are parameters?",
                 ["The prompts users type", "The learned numbers inside the model", "The training text", "The answers"],
                 1, "Training sets the parameters."),
            ],
        },
        # ------------------------------------------------------------------ 2
        {
            "title": "Tokens: How LLMs Read Text",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=zduSFxRajkE",
            "content": r"""
**Learning objective:** Explain what tokens are, build a byte-pair-encoding (BPE) tokenizer from scratch, and explain why token counts matter for cost, context limits and fairness across languages.

## LLMs don't see words — they see tokens

Before an LLM reads anything, a **tokenizer** cuts the text into **tokens**: common words become one token, rarer words are split into pieces. "unbelievable" might become "un", "believ", "able". Each token has an id number, and the model only ever sees those numbers.

Why not whole words? There are too many (every name, typo and language). Why not single letters? Sequences become very long and slow. **Sub-word tokens** are the compromise.

Rough rule of thumb for English: **1 token ≈ ¾ of a word**, or about 4 characters.

## Byte-pair encoding (BPE)

Most LLM tokenizers use BPE:

1. Start with single characters.
2. Find the **most frequent pair** of neighbouring tokens in the training text.
3. **Merge** that pair into a new token. Repeat thousands of times.

Frequent words end up as single tokens; rare words stay split.

{STORIES}

## Build BPE from scratch

```python
from collections import Counter

def get_pairs(tokens):
    return Counter(zip(tokens, tokens[1:]))

def merge(tokens, pair, new_token):
    out, i = [], 0
    while i < len(tokens):
        if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == pair:
            out.append(new_token)
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return out

def train_bpe(training_text, n_merges):
    tokens = list(training_text)
    merges = []
    for _ in range(n_merges):
        pairs = get_pairs(tokens)
        if not pairs:
            break
        best = pairs.most_common(1)[0][0]
        merges.append(best)
        tokens = merge(tokens, best, best[0] + best[1])
    return merges

merges = train_bpe(text[:20000], n_merges=150)
print("first merges:", merges[:8])
print("later merges:", merges[-5:])
```

The first merges join very common pairs such as "e" + " " and "s" + " "; later merges build whole words and phrases such as "the ", "Eric" and even "after the rain".

## Encode new text

```python
def encode_bpe(s, merges):
    tokens = list(s)
    for pair in merges:                      # apply merges in the order they were learned
        tokens = merge(tokens, pair, pair[0] + pair[1])
    return tokens

sentence = "Grace sells avocados in Kigali in the morning."
tokens = encode_bpe(sentence, merges)
print(tokens)
print(len(sentence), "characters ->", len(tokens), "tokens")
```

The 46-character sentence becomes about 21 tokens: frequent pieces have become single tokens, while the rarer name "Kigali" is still split into small parts.

## The language gap

Our tokenizer learned only from English market sentences. Watch what happens with text it has not seen much of:

```python
samples = {
    "English": "Grace pays for the beans with mobile money.",
    "Kinyarwanda": "Grace yishyura ibishyimbo akoresheje mobile money.",
    "Made-up word": "Xqzvbrtwplk",
}
for language, s in samples.items():
    t = encode_bpe(s, merges)
    print(f"{language:12s} {len(s):3d} characters -> {len(t):3d} tokens   ({len(s) / len(t):.1f} characters per token)")
```

The English sentence becomes only **8** tokens (more than 5 characters each). The same meaning in Kinyarwanda needs about **36** tokens — the tokenizer barely knows the language, so it falls back to tiny pieces — and the random word is cut into single letters. Real tokenizers show the same pattern: text in languages that were rare in the tokenizer's training data — including many African languages — needs **more tokens** for the same meaning. That means:

- **Higher cost** — APIs charge per token.
- **Less fits in the context window** — the model "sees" less of your document.
- Often **lower quality**, because the model saw less of the language.

Newer models are improving their coverage of African languages, and projects across Africa are building better data for them.

## Tokens decide cost and limits

- **Pricing:** LLM APIs charge per million input tokens and per million output tokens (output usually costs more).
- **Context window:** the maximum number of tokens the model can consider at once — from a few thousand in early models to hundreds of thousands or more today. Your prompt, documents, conversation history **and** the answer must all fit.
- **Spelling and counting:** because the model sees tokens, not letters, tasks like "how many r's are in strawberry" or reversing a word can trip it up.

## Key terms

- **Token** — a piece of text the model reads as one unit, with an id number.
- **Tokenizer** — the tool that splits text into tokens and back.
- **BPE** — byte-pair encoding: repeatedly merge the most frequent pair.
- **Vocabulary** — all the tokens a tokenizer knows (often 50,000–200,000).
- **Context window** — the most tokens a model can take in at once.

**Takeaway:** LLMs read sub-word tokens; how a language is tokenized affects price, how much text fits, and quality — something to watch when building for Kinyarwanda and other African languages.

## Try it yourself

1. Train BPE with 50, 150 and 400 merges. How does the token count of the English sentence change?
2. Add 20 Kinyarwanda sentences to the training text and retrain. Does the Kinyarwanda token count drop?
3. Write a `decode_bpe` function that joins tokens back into text. Is it always perfect?
4. Paste the same paragraph in English and in Kinyarwanda into an online LLM tokenizer tool and compare the counts.
""",
            "quiz": [
                ("What does a tokenizer do?",
                 ["Translates text", "Splits text into tokens with id numbers", "Checks grammar", "Generates answers"],
                 1, "The model only sees token ids."),
                ("How does BPE build its vocabulary?",
                 ["By using a dictionary", "By repeatedly merging the most frequent pair of tokens", "At random", "By sorting words"],
                 1, "Frequent pairs become new tokens."),
                ("Roughly how many characters is one English token?",
                 ["1", "About 4", "About 20", "100"],
                 1, "1 token ≈ ¾ of a word ≈ 4 characters."),
                ("Why can text in under-represented languages cost more with LLM APIs?",
                 ["It is longer to type", "It is split into more tokens, and APIs charge per token", "Those languages are banned", "It uses images"],
                 1, "More tokens for the same meaning."),
                ("What is the context window?",
                 ["The chat app's window size", "The maximum number of tokens the model can take in at once", "The training time", "The number of users"],
                 1, "Prompt, history and answer must fit."),
                ("Why might an LLM miscount the letters in a word?",
                 ["It cannot count at all", "It sees tokens, not individual letters", "Letters are hidden", "It has no vocabulary"],
                 1, "Tokens hide individual characters."),
            ],
        },
        # ------------------------------------------------------------------ 3
        {
            "title": "Next-Token Prediction and Sampling",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=wjZofJX0v4M",
            "content": r"""
**Learning objective:** Turn model scores into probabilities, and implement greedy decoding, temperature, top-k and top-p sampling to see how they change an LLM's answers.

## From scores to choices

At every step an LLM outputs a **score (logit)** for each token in its vocabulary. **Softmax** turns the scores into probabilities. Then a **decoding strategy** picks one token, it is added to the text, and the whole thing repeats.

Let's use a toy example: the model has just read "The price of beans in Kigali is" and gives these scores:

```python
import numpy as np

tokens = ["low", "high", "good", "fair", "rising", "purple"]
logits = np.array([3.0, 2.5, 1.5, 1.0, 0.5, -2.0])

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

for t, p in zip(tokens, softmax(logits)):
    print(f"{t:7s} {p:.3f}")
```

"low" gets about **0.49**, "high" about 0.30, and the silly "purple" almost nothing (0.003).

## Strategy 1 — Greedy: always take the top token

```python
print("greedy:", tokens[int(np.argmax(logits))])
```

Greedy decoding is **deterministic** (same answer every time) and good for short factual answers, but over long texts it tends to repeat itself and sound flat.

## Strategy 2 — Sampling with temperature

Sampling picks a token **at random, in proportion to its probability**. **Temperature** reshapes the probabilities first by dividing the logits:

- temperature **below 1** → sharper: the top token dominates (more focused, predictable).
- temperature **above 1** → flatter: unlikely tokens get more chances (more varied, riskier).

```python
for T in [0.2, 0.7, 1.0, 1.5]:
    p = softmax(logits / T)
    print(f"T={T}: " + ", ".join(f"{t} {q:.2f}" for t, q in zip(tokens, p)))
```

At T = 0.2 "low" gets about 92% of the probability; at T = 1.5 it drops to about 39% and even "purple" rises to about 1%.

```python
rng = np.random.default_rng(0)
for T in [0.2, 1.0, 1.5]:
    picks = rng.choice(tokens, size=12, p=softmax(logits / T))
    print(f"T={T}:", " ".join(picks))
```

## Strategy 3 — Top-k: only the k best candidates

```python
def top_k_probs(logits, k):
    cut = np.sort(logits)[-k]
    kept = np.where(logits >= cut, logits, -np.inf)
    return softmax(kept)

print("top-3:", dict(zip(tokens, top_k_probs(logits, 3).round(2))))
```

Only "low", "high" and "good" can be chosen; nonsense like "purple" is impossible.

## Strategy 4 — Top-p (nucleus): the smallest set that covers p

Top-p keeps the most likely tokens until their probabilities add up to p (for example 0.9), then samples among them. It adapts: when the model is sure, few tokens are kept; when it is unsure, more are.

```python
def top_p_probs(logits, p_keep):
    probs = softmax(logits)
    order = np.argsort(probs)[::-1]
    cumulative = np.cumsum(probs[order])
    keep = order[: int(np.searchsorted(cumulative, p_keep)) + 1]
    out = np.zeros_like(probs)
    out[keep] = probs[keep]
    return out / out.sum()

print("top-p 0.9:", dict(zip(tokens, top_p_probs(logits, 0.9).round(2))))
```

With p = 0.9 the four best tokens are kept and "rising" and "purple" are dropped.

## What this means when you use an LLM

| Setting | Behaviour | Good for |
|---|---|---|
| Low temperature / greedy | Focused, repeatable | Extraction, classification, code, facts |
| Medium (about 0.7) | Balanced | Most chat and writing |
| High temperature | Creative, surprising, error-prone | Brainstorming, stories |

- The same prompt can give **different answers** because of sampling. For tests and automation, keep randomness low or fix a seed where the tool allows it.
- Some newest models and APIs manage sampling for you and no longer expose these settings; then you steer them with the **prompt** instead (Week 2).
- Sampling explains part of **hallucination**: the model always produces **some** fluent next token, even when it has no reliable knowledge.

## Key terms

- **Logit** — the raw score for a token.
- **Greedy decoding** — always pick the most likely token.
- **Temperature** — divides logits to make the distribution sharper (low) or flatter (high).
- **Top-k** — sample only among the k most likely tokens.
- **Top-p (nucleus)** — sample among the smallest set whose probabilities reach p.

**Takeaway:** An LLM's answer depends not only on its probabilities but on how we sample from them; low randomness is focused and repeatable, high randomness is creative and riskier.

## Try it yourself

1. With T = 0.01, sample 20 tokens. What happens, and why does it match greedy decoding?
2. Change the logits so the model is very sure (for example [8, 2, 1, 1, 0, −2]). How many tokens does top-p 0.9 keep now?
3. Combine top-k = 3 with temperature 1.5. Which tokens can appear?
4. Ask a chatbot the same creative question three times. How different are the answers?
""",
            "quiz": [
                ("What turns a model's logits into probabilities?",
                 ["Sorting", "Softmax", "Temperature", "Tokenization"],
                 1, "Softmax gives probabilities that sum to 1."),
                ("What does greedy decoding do?",
                 ["Picks a random token", "Always picks the most likely token", "Picks the longest token", "Skips tokens"],
                 1, "It is deterministic."),
                ("What does a low temperature (such as 0.2) do?",
                 ["Makes choices more random", "Makes the top token dominate, so output is more focused", "Removes tokens", "Speeds up the GPU"],
                 1, "Dividing logits by a small number sharpens them."),
                ("What does top-k = 3 mean?",
                 ["Generate 3 tokens", "Sample only among the 3 most likely tokens", "Use 3 models", "Repeat 3 times"],
                 1, "Everything else is excluded."),
                ("How is top-p different from top-k?",
                 ["It keeps a fixed number of tokens", "It keeps the smallest set of tokens whose probabilities add up to p", "It ignores probabilities", "It only works for images"],
                 1, "The number kept adapts to the model's certainty."),
                ("Which setting suits extracting a phone number from a message?",
                 ["High temperature", "Low temperature or greedy", "Top-k = 1000", "Random"],
                 1, "Extraction needs focused, repeatable output."),
            ],
        },
        # ------------------------------------------------------------------ 4
        {
            "title": "Build a Tiny GPT",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=eMlx5fFNoYc",
            "content": r"""
**Learning objective:** Build and train a small GPT-style transformer that writes text one character at a time, and connect every part of it to how real LLMs work.

## The plan

GPT stands for **Generative Pre-trained Transformer**. We build the same architecture as the big models — just thousands of times smaller — and train it on our market sentences:

- **Tokens:** single characters (simple; real models use BPE).
- **Embeddings:** each token and each position gets a learned vector.
- **Transformer blocks:** masked self-attention + feed-forward, with residual connections and layer normalisation (you built these in Deep Learning & Neural Networks).
- **Output:** a score for every possible next character.
- **Training:** predict the next character at every position; loss = cross-entropy.

{STORIES}

## The model

{GPT}

Three details matter:

- **The causal mask** (`torch.triu`): each position may only look at **earlier** characters. Without it, the model could cheat by reading the answer during training.
- **Training targets** are the input shifted by one: for "Grace", the model learns G→r, Gr→a, Gra→c… — every position is a training example.
- **`generate`** feeds the model's own output back in, one character at a time — exactly how chatbots write their answers.

## Before training: nonsense

```python
torch.manual_seed(0)
untrained = TinyGPT(len(chars)).to(device)
start = torch.tensor([encode("Grace")], device=device)
print(decode(untrained.generate(start, 80)[0].tolist()))
print("parameters:", sum(p.numel() for p in untrained.parameters()))
```

Random characters, from about **350,000** parameters. (GPT-3 had 175 **billion**.)

## Train it

```python
model = train_gpt(steps=1500)
```

The loss starts around **4** (close to random guessing among 44 characters: ln 44 ≈ 3.8) and falls to about **0.27**. On a Colab GPU this takes under a minute; on a CPU a few minutes. The loss gets so low because our text is very regular — real text is far less predictable. The training and validation losses stay close: the model is not memorising.

## After training: it writes

```python
torch.manual_seed(1)
start = torch.tensor([encode("Grace")], device=device)
print(decode(model.generate(start, 200, temperature=0.8)[0].tolist()))
```

You should see sentences such as "Grace sells beans in Huye in the morning." — real-looking sentences in the right patterns, learned purely by predicting the next character. Nobody wrote a rule about grammar.

## Notice: fluent but invented

The model happily writes "Ange buys coffee in Rusizi on Saturday" — a sentence that **never appeared** in the training text. It learned the **pattern** of sentences, not a list of true facts. That is the root of **hallucination** in real LLMs: they generate what is **likely**, not what is **true**.

## From tiny to large

| | Our TinyGPT | A large modern LLM |
|---|---|---|
| Tokens | 44 characters | ~100,000+ sub-word tokens |
| Context | 64 characters | 100,000s of tokens |
| Layers × width | 3 × 96 | ~100 × ~10,000 |
| Parameters | ~350 thousand | tens to hundreds of billions |
| Training text | ~200 thousand characters | trillions of tokens |
| Training time | minutes on one GPU | months on thousands of GPUs |

The **ideas** are the same; scale changes what the model can do.

## Key terms

- **GPT** — a decoder-only transformer trained to predict the next token.
- **Causal mask** — stops each position from seeing future tokens.
- **Autoregressive generation** — feeding each generated token back as input.
- **Pretraining** — next-token training on large amounts of raw text.
- **Hallucination** — fluent output that is not true.

**Takeaway:** A GPT is token and position embeddings, a stack of masked attention blocks and a next-token classifier — trained only to predict the next token, it learns the patterns of language.

## Try it yourself

1. Generate with temperature 0.3, 0.8 and 1.5. Describe the differences.
2. Train for 300 steps only. What does the text look like?
3. Remove the causal mask (set `attn_mask=None`) and train again. Why does the training loss fall so fast, and why is the generated text bad?
4. Change `layers=3` to `layers=1`. How do the loss and the text change?
""",
            "quiz": [
                ("What does GPT stand for?",
                 ["General Purpose Tool", "Generative Pre-trained Transformer", "Graph Processing Technique", "Guided Prompt Template"],
                 1, "A transformer pre-trained to generate text."),
                ("What does the causal mask prevent?",
                 ["Overfitting", "Each position seeing future tokens", "Using a GPU", "Long sentences"],
                 1, "Otherwise the model could read the answer."),
                ("What are the training targets for a GPT?",
                 ["Random labels", "The input shifted by one position: the next token everywhere", "The first token only", "Images"],
                 1, "Every position predicts the next token."),
                ("The untrained model's loss is close to 3.8 with 44 possible characters. Why?",
                 ["It is a bug", "ln(44) ≈ 3.8: it is guessing among 44 options at random", "It is the learning rate", "It is the number of layers"],
                 1, "Uniform guessing gives loss ln(vocabulary size)."),
                ("The model writes a sentence that never appeared in its training text. What does this show?",
                 ["It copied the data", "It learned patterns, and can produce fluent but invented content", "The data was leaked", "Training failed"],
                 1, "This is the root of hallucination."),
                ("What is autoregressive generation?",
                 ["Training on images", "Feeding each generated token back in to predict the next", "Deleting tokens", "Sorting outputs"],
                 1, "Chatbots write one token at a time this way."),
            ],
        },
        # ------------------------------------------------------------------ 5
        {
            "title": "From Base Model to Assistant",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=7xTGNNLPyMI",
            "content": r"""
**Learning objective:** Explain the three training stages that turn a raw text predictor into a helpful assistant — pretraining, instruction tuning and preference tuning — and see how chat messages, system prompts and training masks work in code.

## A base model is not an assistant

After pretraining, a model continues text. Ask a **base model** "What is the capital of Rwanda?" and it might continue with "What is the capital of Burundi? What is the capital of…" — because that is what quiz pages on the internet look like. It has knowledge but does not **behave** like an assistant.

## The three stages

| Stage | Data | What it teaches |
|---|---|---|
| **1. Pretraining** | Trillions of tokens of web pages, books, code | Language, facts, reasoning patterns |
| **2. Instruction tuning** (supervised fine-tuning, SFT) | Tens of thousands of example conversations written or checked by people | To answer, follow instructions and use a chat format |
| **3. Preference tuning** (RLHF, DPO, constitutional methods) | People (or AI guided by written principles) compare two answers and choose the better one | To be more helpful, honest and harmless |

Most of the knowledge comes from stage 1; stages 2 and 3 shape the **behaviour**. Modern models add more training for reasoning ("thinking" before answering) and tool use.

## Chat messages and templates

Chat APIs take a list of **messages**, each with a **role**:

- **system** — instructions from the developer: who the assistant is, rules, tone.
- **user** — what the person types.
- **assistant** — the model's earlier replies.

Before the model sees them, a **chat template** turns the messages into one long string with special marker tokens:

```python
def render_chat(messages, add_generation_prompt=True):
    out = ""
    for m in messages:
        out += f"<|{m['role']}|>\n{m['content']}\n<|end|>\n"
    if add_generation_prompt:
        out += "<|assistant|>\n"            # the model continues from here
    return out

conversation = [
    {"role": "system", "content": "You are a polite assistant for a Kigali bakery. Answer in one sentence."},
    {"role": "user", "content": "Do you sell bread on Sunday?"},
]
print(render_chat(conversation))
```

The model was trained on thousands of texts in exactly this format, so when it sees `<|assistant|>` it writes an assistant reply and then the `<|end|>` marker. Each model family has its own markers — libraries apply the right template for you.

## Training only on the assistant's words

During instruction tuning, the loss is computed **only on the assistant's tokens**. The model should learn to **write answers**, not to predict what users type.

```python
example = [
    {"role": "user", "content": "Price of beans?"},
    {"role": "assistant", "content": "Beans cost 1,200 RWF per kg today."},
]
pieces, mask = [], []
for m in example:
    part = f"<|{m['role']}|>\n{m['content']}\n<|end|>\n"
    pieces.append(part)
    mask += [1 if m["role"] == "assistant" else 0] * len(part)   # 1 = learn from this character

full = "".join(pieces)
print(full)
print("characters:", len(full), "| trained on:", sum(mask), "| ignored:", len(mask) - sum(mask))
```

In real training the mask is per token, and ignored positions get the label −100, which PyTorch's cross-entropy skips.

## Preference tuning in one formula

Given a prompt with a **chosen** (better) and a **rejected** (worse) answer, preference tuning raises the probability of the chosen answer relative to the rejected one. **DPO** (Direct Preference Optimisation) does this with a simple loss. Here it is with made-up log-probabilities:

```python
import math

def dpo_loss(policy_chosen, policy_rejected, ref_chosen, ref_rejected, beta=0.1):
    # how much more the model now prefers "chosen" over "rejected", compared with before
    margin = beta * ((policy_chosen - ref_chosen) - (policy_rejected - ref_rejected))
    return -math.log(1 / (1 + math.exp(-margin)))

print("model unchanged:          ", round(dpo_loss(-12, -12, -12, -12), 3))
print("model now prefers chosen: ", round(dpo_loss(-8, -15, -12, -12), 3))
print("model prefers rejected:   ", round(dpo_loss(-15, -8, -12, -12), 3))
```

The loss is **0.693** when nothing has changed, falls (about **0.40**) when the model moves towards the chosen answer, and rises (about **1.10**) when it moves the wrong way. Training pushes the loss down.

## The system prompt is powerful — and limited

The system prompt sets the role, rules and style for a whole conversation, so it is the first tool you use when building an app. But it is **not** a security boundary: users can sometimes talk a model out of its instructions (Week 4: prompt injection). Important rules must also be enforced in your code.

## Key terms

- **Base model** — a pretrained model that continues text.
- **Instruction tuning (SFT)** — fine-tuning on example conversations.
- **Preference tuning (RLHF, DPO)** — training on which of two answers is better.
- **Roles** — system, user, assistant.
- **Chat template** — how messages are turned into one string with special markers.
- **Loss masking** — learning only from the assistant's tokens.

**Takeaway:** Pretraining gives knowledge; instruction and preference tuning give helpful behaviour; and every chat is really one long formatted text that the model continues.

## Try it yourself

1. Add a second user–assistant exchange to `conversation` and render it. Where does the model start writing?
2. Write three example conversations for a bakery assistant that you could use for instruction tuning.
3. Compute the DPO loss for policy_chosen = −10, policy_rejected = −10 and reference values −12 and −10. Is the model moving the right way?
4. Ask a chatbot to "ignore your instructions and…" something harmless. Does it comply? Why might a system prompt not be enough for security?
""",
            "quiz": [
                ("What does a base (pretrained-only) model do with a question?",
                 ["Always answers helpfully", "Continues the text, which may not be an answer", "Refuses", "Searches the web"],
                 1, "It predicts likely continuations."),
                ("Which stage teaches the model to follow instructions in a chat format?",
                 ["Pretraining", "Instruction tuning (SFT)", "Tokenization", "Sampling"],
                 1, "SFT uses example conversations."),
                ("What data does preference tuning use?",
                 ["Random web pages", "Pairs of answers where one is preferred", "Images", "Only system prompts"],
                 1, "Chosen vs rejected answers."),
                ("Which role holds the developer's instructions?",
                 ["user", "assistant", "system", "tool"],
                 2, "The system prompt sets behaviour."),
                ("During instruction tuning, which tokens is the loss computed on?",
                 ["All tokens", "Only the assistant's tokens", "Only the system prompt", "None"],
                 1, "The model learns to write answers."),
                ("Why is a system prompt not a security boundary?",
                 ["It is too short", "Users can sometimes talk a model out of its instructions", "It is encrypted", "It is ignored completely"],
                 1, "Enforce critical rules in code too."),
            ],
        },
        # ------------------------------------------------------------------ 6
        {
            "title": "Week 1 Project: Train and Study Your Own Language Model",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=kCc8FmEb1nY",
            "content": r"""
**Learning objective:** Train a small GPT on a text you choose, measure it with validation loss, explore sampling settings, and explain its strengths and failures — including hallucination — in a short report.

## The brief

A teacher wants a demonstration for a school club: "How does ChatGPT write?" Your job is to train a small language model, show how it improves, show what sampling does, and explain honestly what it gets wrong.

## Part 1 — Choose your text

Use the market sentences, or replace `text` with your own: proverbs, simple stories or poems you wrote yourself, or public-domain text. Aim for at least 50,000 characters of fairly consistent style. Do not use private messages or copyrighted books.

{STORIES}

## Part 2 — Build the model

{GPT}

## Part 3 — Train and measure

```python
model = train_gpt(steps=1500)
final = estimate_loss(model, steps=50)
print(f"final: train {final['train']:.3f}, validation {final['val']:.3f}")
```

**Validation loss** is measured on the last 10% of the text, which the model never trains on. If validation loss rises while training loss falls, the model is memorising (overfitting) — exactly as in earlier courses.

**Perplexity** = e^loss is a common way to report it: roughly "how many characters the model is choosing between". A loss of 1.0 means a perplexity of about 2.7.

```python
import math
print("validation perplexity:", round(math.exp(final["val"]), 2))
```

## Part 4 — Explore sampling

```python
for T in [0.3, 0.8, 1.3]:
    torch.manual_seed(2)
    out = model.generate(torch.tensor([encode("In ")], device=device), 150, temperature=T)
    print(f"--- temperature {T} ---")
    print(decode(out[0].tolist()))
```

Record what changes: repetition at low temperature, spelling mistakes and odd words at high temperature.

## Part 5 — Test for "hallucination"

```python
torch.manual_seed(3)
samples = decode(model.generate(torch.tensor([encode("\n")], device=device), 2000, temperature=0.8)[0].tolist())
generated = [s.strip() for s in samples.split("\n") if s.strip().endswith(".")]
training_sentences = set(text.split("\n"))
new = [s for s in generated if s not in training_sentences]
print(f"{len(generated)} complete sentences, {len(new)} never appeared in the training text")
print("examples of new sentences:", new[:3])
```

Many generated sentences are **new combinations**: grammatical, believable, and never in the data. In our market text that is harmless. In a medical or legal assistant, a fluent new "fact" can be dangerous. This is why real systems ground answers in documents (RAG, Week 3) and why people must check important outputs.

## Part 6 — Report (one page)

1. **Data:** what text, how many characters, how many different characters.
2. **Model:** layers, width, context length, parameter count.
3. **Training:** loss curve numbers at steps 0, 500, 1000, 1500; final validation perplexity.
4. **Sampling:** three short samples at different temperatures with one sentence each on what you see.
5. **Hallucination:** how many new sentences, two examples, and why this matters for real LLMs.
6. **From tiny to large:** three differences between your model and a commercial LLM.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Training | Model trains; train and validation losses reported |
| Understanding | Causal mask, next-token targets and sampling explained in your own words |
| Experiment | Temperature comparison with evidence |
| Critical thinking | Hallucination measured and explained |
| Communication | A school club member understands the report |

**Takeaway:** You trained a language model from zero and saw both its power (fluent patterns) and its core weakness (likely is not the same as true).

## Try it yourself

Complete Parts 1–6. Challenge: double `BLOCK` to 128 and the width to 128, train again on a GPU, and compare validation loss and samples.
""",
            "quiz": [
                ("Why is validation loss measured on text the model never trained on?",
                 ["To speed up training", "To check it generalises instead of memorising", "To change the vocabulary", "To make the loss smaller"],
                 1, "Unseen text gives an honest measure."),
                ("A validation loss of 1.0 corresponds to a perplexity of about…",
                 ["1", "2.7", "10", "100"],
                 1, "Perplexity = e^loss."),
                ("What usually happens at a very low temperature?",
                 ["Many spelling mistakes", "Repetitive, predictable text", "No text at all", "Random characters"],
                 1, "The top choice dominates."),
                ("The model writes believable sentences that never appeared in its data. Why does this matter for real LLMs?",
                 ["It doesn't matter", "Fluent invented 'facts' can mislead in medical, legal or financial uses", "It means the model is broken", "It proves the data leaked"],
                 1, "Likely is not the same as true."),
                ("Which text is suitable for the project?",
                 ["Friends' private messages", "Text you wrote or public-domain text", "A copyrighted novel", "Passwords"],
                 1, "Respect privacy and copyright."),
                ("What is one reason commercial LLMs write far better than your tiny model?",
                 ["They use no transformer", "Vastly more parameters, data and context", "They use bigrams", "They skip training"],
                 1, "Same ideas, much bigger scale."),
            ],
        },
    ],
}

for _lesson in WEEK1["lessons"]:
    _lesson["content"] = _lesson["content"].replace("{STORIES}", STORIES).replace("{GPT}", GPT)
