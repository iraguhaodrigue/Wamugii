"""Modern AI: LLMs & Generative AI -- Week 3: Embeddings, Search and RAG. Original WAMUGII content."""

from app.course_content.llm_week2 import SETUP

# A made-up member handbook used as the document collection all week.
HANDBOOK = r"""
```python
HANDBOOK = {
    "Opening hours": "The Kigali Tech Hub is open Monday to Friday from 8:00 to 20:00 and on Saturday "
                     "from 9:00 to 14:00. The hub is closed on Sundays and on public holidays.",
    "Membership plans": "There are three plans. The Student plan costs 10,000 RWF per month and needs a "
                        "valid student card. The Standard plan costs 25,000 RWF per month. The Team plan "
                        "costs 90,000 RWF per month for up to five people.",
    "Joining": "To become a member, fill in the online form, bring your national ID or passport to the "
               "front desk, and pay the first month. Your access card is ready the same day.",
    "Payment": "Fees are paid by mobile money or bank transfer before the 5th of each month. Members who "
               "pay late for two months lose access until the balance is cleared.",
    "Cancelling": "You may cancel your membership at any time with 14 days' written notice by email. "
                  "Fees already paid for the current month are not refunded.",
    "Wi-Fi": "The Wi-Fi network is called KTH-Members. The password is printed on your access card and "
             "changes every three months. Guests use the separate KTH-Guest network.",
    "Meeting rooms": "Members can book the two meeting rooms through the hub app. Standard and Team members "
                     "get 4 free hours per month; Student members get 1 free hour. Extra hours cost 5,000 RWF.",
    "Guests": "Each member may bring up to two guests per day. Guests must sign in at the front desk "
              "and leave by 18:00.",
    "Printing": "Black-and-white printing costs 50 RWF per page and colour printing 200 RWF per page. "
                "Students get 100 free black-and-white pages per month.",
    "Events": "The hub runs a free coding workshop every Wednesday at 17:00 and a startup pitch night "
              "on the last Friday of each month. Members can register in the hub app.",
    "Lockers": "Lockers can be rented for 3,000 RWF per month. Lost locker keys cost 5,000 RWF to replace.",
    "Code of conduct": "Members must respect others, keep noise low in the quiet zone, and never share their "
                       "access card. Harassment leads to immediate cancellation of membership.",
    "Lost and found": "Items left behind are kept at the front desk for 30 days, then donated.",
    "Accessibility": "The ground floor, meeting rooms and toilets are wheelchair accessible. A lift serves "
                     "all floors. Contact the front desk to arrange other support.",
}
chunks = [{"id": i, "title": t, "text": f"{t}. {body}"} for i, (t, body) in enumerate(HANDBOOK.items())]
print(len(chunks), "sections")
```
""".strip()

# Questions with the section that answers each one (for evaluation).
QUESTIONS = r"""
```python
test_questions = [
    ("How much is the student membership?", "Membership plans"),
    ("Can I come to the hub on Sunday?", "Opening hours"),
    ("What is the Wi-Fi password?", "Wi-Fi"),
    ("How do I book a meeting room?", "Meeting rooms"),
    ("If I quit, do I get my money back for this month?", "Cancelling"),
    ("How many friends can I bring with me?", "Guests"),
    ("What does colour printing cost?", "Printing"),
    ("When is the coding workshop?", "Events"),
    ("What documents do I need to sign up?", "Joining"),
    ("What happens if I don't pay my fees on time?", "Payment"),
    ("I left my bag at the hub last week. Is it still there?", "Lost and found"),
    ("Is there a lift for wheelchair users?", "Accessibility"),
]
print(len(test_questions), "labelled questions")
```
""".strip()

# Embeddings built locally (no download): TF-IDF + truncated SVD ("latent semantic analysis").
EMBED = r"""
```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer

texts = [c["text"] for c in chunks]
embedder = make_pipeline(TfidfVectorizer(stop_words="english", sublinear_tf=True),
                         TruncatedSVD(n_components=12, random_state=0),
                         Normalizer())                      # unit length: dot product = cosine similarity
doc_vectors = embedder.fit_transform(texts)

def embed(text_list):
    return embedder.transform(text_list)

print("each section is now a vector of", doc_vectors.shape[1], "numbers")
```
""".strip()

WEEK3 = {
    "title": "Week 3 · Embeddings, Search and RAG",
    "lessons": [
        # ------------------------------------------------------------------ 13
        {
            "title": "Embeddings: Meaning as Numbers",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=Q_slEpNuhMc",
            "content": r"""
**Learning objective:** Explain what text embeddings are, compare texts with cosine similarity, build simple embeddings yourself, and know when to use a modern embedding model.

## Turning meaning into a list of numbers

An **embedding** is a vector — a list of numbers — that represents the meaning of a piece of text. Texts with similar meaning get vectors that point in similar directions, even if they use different words:

- "How much does membership cost?" and "What is the monthly fee?" → close vectors.
- "How much does membership cost?" and "Where are the toilets?" → far apart.

Embeddings power **semantic search**, recommendations, clustering of feedback, duplicate detection and — most importantly for this week — **RAG**.

## Cosine similarity

To compare two vectors, measure the angle between them:

> cosine similarity = (a · b) ÷ (|a| × |b|) — 1 means the same direction, 0 means unrelated

```python
import numpy as np

def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# toy 3-number "embeddings": [money, technology, food]
fee = np.array([0.9, 0.1, 0.0])
price = np.array([0.8, 0.2, 0.1])
wifi = np.array([0.1, 0.9, 0.0])
print("fee vs price:", round(cosine(fee, price), 2))
print("fee vs wifi: ", round(cosine(fee, wifi), 2))
```

"fee" and "price" are about **0.98** similar; "fee" and "wifi" only about **0.22**. Real embeddings have hundreds or thousands of numbers, learned by neural networks — no human chooses what each number means.

## Our document collection

All week we work with a made-up handbook of a technology hub in Kigali:

{HANDBOOK}

## Keyword search fails on different words

The classic approach, **TF-IDF**, scores texts by shared words, weighting rare words more:

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(stop_words="english")
doc_tfidf = tfidf.fit_transform([c["text"] for c in chunks])

def keyword_search(query, k=3):
    scores = (doc_tfidf @ tfidf.transform([query]).T).toarray().ravel()
    best = np.argsort(scores)[::-1][:k]
    return [(chunks[i]["title"], round(float(scores[i]), 2)) for i in best]

print(keyword_search("membership plans price"))
print(keyword_search("If I quit, do I get my money back?"))
```

The first query shares words with the "Membership plans" section and works. The second shares almost **no words** with the "Cancelling" section ("quit" vs "cancel", "money back" vs "refunded"), so keyword search struggles — the right section is missing or ranked low.

## Embeddings capture related words

**Latent semantic analysis** compresses TF-IDF into a few dimensions with SVD (the PCA idea from Machine Learning Fundamentals), so words that appear in similar contexts move together. It runs locally, with no download:

{EMBED}

```python
def semantic_search(query, k=3):
    scores = doc_vectors @ embed([query])[0]
    best = np.argsort(scores)[::-1][:k]
    return [(chunks[i]["title"], round(float(scores[i]), 2)) for i in best]

print(semantic_search("membership plans price"))
print(semantic_search("When can I visit on the weekend?"))
```

The first query works well (Membership plans scores about **0.84**). The second returns scores of **0.0** for every section: "visit" and "weekend" never appear in the handbook, so our embedder has never seen them and turns the question into an empty vector. Our home-made embeddings only know the words in 14 short sections. **Modern embedding models** are neural networks trained on billions of sentences, and they handle synonyms, paraphrases and even several languages far better.

## Modern embedding models

| Option | Notes |
|---|---|
| Open models with `sentence-transformers` (for example multilingual MiniLM, E5, BGE) | Free, run in Colab or on your own server; some support Kinyarwanda and Swahili reasonably well |
| Embedding APIs (Voyage AI, OpenAI, Google, Cohere) | Paid per token, very good quality, no GPU needed |

The code shape is always the same: `vectors = model.encode(list_of_texts)` (or an API call), then cosine similarity. In the rest of the week, swap our `embed()` function for a real model in your own projects — nothing else changes.

## Key terms

- **Embedding** — a vector that represents meaning.
- **Cosine similarity** — how closely two vectors point the same way (−1 to 1).
- **Semantic search** — search by meaning instead of exact words.
- **TF-IDF** — word-count scores that weight rare words more.
- **Embedding model** — a neural network that turns text into embeddings.

**Takeaway:** Embeddings turn meaning into vectors so we can search by meaning; keyword search misses paraphrases, and modern embedding models handle them far better than simple methods.

## Try it yourself

1. Compute the cosine similarity of `fee` with itself and with `-fee`. What do 1 and −1 mean?
2. Try five questions of your own with `keyword_search` and `semantic_search`. When does each win?
3. Change `n_components` to 4 and to 13. How do the results change?
4. Group the support messages from Week 2 into clusters with k-means on their embeddings (Machine Learning Fundamentals, Lesson 19).
""",
            "quiz": [
                ("What is a text embedding?",
                 ["A compressed file", "A vector of numbers representing the meaning of text", "A tokenizer", "A database"],
                 1, "Similar meanings → similar vectors."),
                ("Cosine similarity of 1 means…",
                 ["Unrelated", "Pointing in exactly the same direction", "Opposite", "Missing data"],
                 1, "The angle between the vectors is 0."),
                ("Why does keyword search fail for 'If I quit, do I get my money back?'",
                 ["It is too long", "It shares almost no words with the 'Cancelling' section", "TF-IDF cannot read questions", "The section is missing"],
                 1, "Different words, same meaning."),
                ("What does semantic search compare?",
                 ["Exact words", "Meaning, through embeddings", "File sizes", "Dates"],
                 1, "It finds paraphrases."),
                ("Why are modern embedding models much better than our home-made ones?",
                 ["They use more colours", "They are neural networks trained on billions of sentences", "They need no input", "They only use keywords"],
                 1, "Scale and training data."),
                ("Which is an open-source way to create embeddings?",
                 ["sentence-transformers models", "A spreadsheet", "A chat app", "Printing the text"],
                 0, "Free models you can run yourself."),
            ],
        },
        # ------------------------------------------------------------------ 14
        {
            "title": "Vector Search and Vector Databases",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=Lha_QCkXxm0",
            "content": r"""
**Learning objective:** Build a small vector store in NumPy with search and metadata filters, understand how vector databases scale to millions of items, and choose a practical option.

## What a vector store does

A **vector store** keeps three things for every item: the **vector**, the original **text**, and **metadata** (title, date, language, owner…). It answers: "give me the k items whose vectors are closest to this query vector, optionally only those matching a filter".

{HANDBOOK}

{EMBED}

## A vector store in 30 lines

```python
class VectorStore:
    def __init__(self):
        self.vectors = None
        self.items = []

    def add(self, texts, metadatas):
        new = embed(texts)
        self.vectors = new if self.vectors is None else np.vstack([self.vectors, new])
        for text, meta in zip(texts, metadatas):
            self.items.append({"text": text, **meta})

    def search(self, query, k=3, where=None):
        scores = self.vectors @ embed([query])[0]          # cosine (vectors are unit length)
        order = np.argsort(scores)[::-1]
        results = []
        for i in order:
            item = self.items[i]
            if where and any(item.get(key) != value for key, value in where.items()):
                continue                                    # metadata filter
            results.append({**item, "score": round(float(scores[i]), 3)})
            if len(results) == k:
                break
        return results

store = VectorStore()
money_topics = {"Membership plans", "Payment", "Cancelling", "Printing", "Lockers"}
store.add([c["text"] for c in chunks],
          [{"title": c["title"], "topic": "money" if c["title"] in money_topics else "general"} for c in chunks])

for r in store.search("How much does it cost each month?", k=3):
    print(r["score"], r["title"])
print("--- only money topics ---")
for r in store.search("How much does it cost each month?", k=3, where={"topic": "money"}):
    print(r["score"], r["title"])
```

**Metadata filters** are essential in real apps: search only this customer's documents, only the latest policy, only Kinyarwanda texts.

## How fast is brute force?

Comparing the query with every vector is called **exact (brute-force) search**. With NumPy it is surprisingly fast:

```python
import time

rng = np.random.default_rng(0)
many = rng.normal(size=(100_000, 384)).astype("float32")      # 100,000 vectors of 384 numbers
many /= np.linalg.norm(many, axis=1, keepdims=True)
query = many[123] + 0.05 * rng.normal(size=384).astype("float32")

start = time.perf_counter()
top5 = np.argsort(many @ query)[::-1][:5]
print(f"searched 100,000 vectors in {(time.perf_counter() - start) * 1000:.0f} ms; best match: {top5[0]}")
print(f"memory: {many.nbytes / 1e6:.0f} MB")
```

100,000 vectors take well under a second and about 150 MB of memory — enough for many small and medium apps. The best match is item **123**, the one we disguised with noise.

## Scaling up: approximate nearest neighbours

For millions of vectors, comparing with everything becomes too slow. **Approximate nearest-neighbour (ANN)** indexes (such as HNSW graphs or clustered indexes) check only a small, promising part of the data, returning almost the same results in milliseconds — trading a tiny bit of accuracy for big speed-ups.

## Choosing a vector store

| Option | Good for |
|---|---|
| NumPy (like ours) | Learning, up to ~100,000 items |
| FAISS (library) | Fast search inside one Python program |
| Chroma, LanceDB | Simple embedded vector databases for prototypes |
| **pgvector** (PostgreSQL extension) | Apps that already use PostgreSQL — vectors next to your normal tables |
| Qdrant, Weaviate, Milvus, Pinecone | Large dedicated vector databases and managed services |

If your app already uses PostgreSQL (like the WAMUGII platform), **pgvector** is often the simplest choice: one database, normal backups, and SQL filters with vector search.

## Keep vectors in sync

When a document changes, re-embed it and replace its vector; when it is deleted, delete its vector. Store which embedding model produced each vector — vectors from different models cannot be compared.

## Key terms

- **Vector store / vector database** — stores vectors with text and metadata and finds the nearest ones.
- **Metadata filter** — restricts search to items with certain properties.
- **Exact (brute-force) search** — compare with every vector.
- **Approximate nearest neighbours (ANN)** — fast indexes that check only part of the data.
- **pgvector** — vector search inside PostgreSQL.

**Takeaway:** A vector store is vectors plus text plus metadata with a nearest-neighbour search; brute force is fine for small collections, ANN indexes and vector databases handle millions.

## Try it yourself

1. Add a `delete(title)` method to `VectorStore`.
2. Add a "language" field to the metadata and store two sections translated into Kinyarwanda. Filter by language.
3. Time the brute-force search with 10,000, 100,000 and 300,000 vectors. Is the growth linear?
4. Read the pgvector documentation and write the SQL to create a table with a 384-number vector column.
""",
            "quiz": [
                ("What does a vector store keep for each item?",
                 ["Only the text", "The vector, the original text and metadata", "Only the vector", "The API key"],
                 1, "All three are needed for useful results."),
                ("What is a metadata filter used for?",
                 ["Making vectors longer", "Searching only items with certain properties, such as one customer's documents", "Changing the embedding model", "Deleting the store"],
                 1, "Essential for privacy and relevance."),
                ("What is brute-force (exact) search?",
                 ["Guessing", "Comparing the query with every vector", "Searching by keywords", "Searching only the first item"],
                 1, "Simple and fine for small collections."),
                ("Why use an approximate nearest-neighbour index?",
                 ["To get perfect results", "To search millions of vectors quickly by checking only part of the data", "To encrypt data", "To make embeddings"],
                 1, "Speed for a tiny loss of accuracy."),
                ("Your app already uses PostgreSQL. Which option is often simplest?",
                 ["A spreadsheet", "pgvector", "Printing vectors", "A second app"],
                 1, "Vectors next to your normal tables."),
                ("Why record which embedding model made each vector?",
                 ["For billing", "Vectors from different models cannot be compared", "To speed up search", "It is not needed"],
                 1, "Mixing models breaks similarity."),
            ],
        },
        # ------------------------------------------------------------------ 15
        {
            "title": "Retrieval-Augmented Generation (RAG)",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=vSwK5sBpD2c",
            "content": r"""
**Learning objective:** Build a complete RAG pipeline that retrieves the right sections, asks the model to answer only from them with citations, and says "I don't know" when the answer is not there.

## Why RAG?

An LLM only knows what was in its training data — not your organisation's handbook, today's prices or last week's decisions — and it may **invent** an answer rather than admit it does not know. **Retrieval-Augmented Generation** fixes this:

1. **Retrieve** the most relevant passages from your documents.
2. **Augment** the prompt with them.
3. **Generate** an answer grounded in those passages, with citations.

Updating knowledge becomes easy: change the documents, not the model.

{SETUP}

{HANDBOOK}

{EMBED}

## Step 1 — Retrieve

```python
def retrieve(question, k=3):
    scores = doc_vectors @ embed([question])[0]
    best = np.argsort(scores)[::-1][:k]
    return [chunks[i] for i in best]

for c in retrieve("How much is the student plan?"):
    print("-", c["title"])
```

## Step 2 — Build a grounded prompt

```python
RAG_SYSTEM = (
    "You answer questions about the Kigali Tech Hub using ONLY the numbered sources provided. "
    "Cite sources like [1] after each fact. If the sources do not contain the answer, reply exactly: "
    "\"I don't know based on the handbook.\" Never use outside knowledge."
)

def build_prompt(question, sources):
    numbered = "\n".join(f"[{n}] {s['text']}" for n, s in enumerate(sources, start=1))
    return f"<sources>\n{numbered}\n</sources>\n\n<question>{question}</question>"

sources = retrieve("How much is the student plan?")
print(build_prompt("How much is the student plan?", sources))
```

The prompt contains the question **and** the evidence. The system prompt sets strict rules: only the sources, cite them, admit when the answer is missing.

## Step 3 — Generate, with citations you can check

```python
import re

def answer(question, k=3):
    sources = retrieve(question, k)
    text = ask(build_prompt(question, sources), system=RAG_SYSTEM, max_tokens=300)
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text) if 1 <= int(n) <= len(sources)})
    return {"answer": text, "sources": [sources[n - 1]["title"] for n in cited],
            "retrieved": [s["title"] for s in sources]}

result = answer("How much is the student plan?")
print(result["answer"])
print("cited:", result["sources"], "| retrieved:", result["retrieved"])
```

Because citations are numbers, your app can **show the cited sections** next to the answer, so people can check it. Answers with no valid citation can be flagged.

## Step 4 — Questions the handbook cannot answer

```python
print(answer("Who won the football match yesterday?")["answer"])
```

A good RAG system answers "I don't know based on the handbook." A system that answers anyway is hallucinating — test for this on purpose.

## Where RAG goes wrong

| Problem | Symptom | Fix (next lessons) |
|---|---|---|
| Wrong passages retrieved | Answer misses the point or says "I don't know" wrongly | Better chunking, hybrid search, reranking |
| Right passages, wrong answer | Misreads numbers, mixes plans | Clearer prompt, smaller context, better model |
| Answer goes beyond sources | Invented details | Strict instructions, citation checks, evaluation |
| Outdated documents | Correct citation, old fact | Keep the document store up to date |

The first one is the most common: **if retrieval fails, generation cannot succeed.** That is why the next lesson focuses on retrieval.

## Key terms

- **RAG** — retrieve relevant passages, add them to the prompt, generate a grounded answer.
- **Grounding** — basing the answer on supplied evidence.
- **Citation** — a pointer from a claim to its source.
- **Context stuffing** — putting retrieved passages in the prompt.
- **Refusal ("I don't know")** — the correct behaviour when the sources lack the answer.

**Takeaway:** RAG gives an LLM your organisation's knowledge at question time; ground every answer in retrieved sources, cite them, and make "I don't know" the expected reply when the answer is missing.

## Try it yourself

1. Ask five questions from the handbook and check every citation against the source text.
2. Change `k` to 1 and to 6. When does a small k miss information? When does a large k confuse the model?
3. Remove "Never use outside knowledge" from the system prompt and ask about the football match again.
4. Add a new section "Parking" to the handbook, rebuild the embeddings, and ask about parking.
""",
            "quiz": [
                ("What problem does RAG solve?",
                 ["Slow GPUs", "The model not knowing your own, current documents and inventing answers", "Tokenization", "Image generation"],
                 1, "It brings in your knowledge at question time."),
                ("What are the three steps of RAG?",
                 ["Train, test, deploy", "Retrieve, augment, generate", "Tokenize, embed, sort", "Ask, wait, print"],
                 1, "Retrieve passages, add them to the prompt, generate."),
                ("Why number the sources and ask for citations like [1]?",
                 ["To make the prompt longer", "So people and code can check each claim against its source", "Numbers are cheaper", "The API requires it"],
                 1, "Citations make answers verifiable."),
                ("What should a good RAG system answer when the sources lack the answer?",
                 ["Its best guess", "\"I don't know based on the handbook.\"", "Nothing", "A random source"],
                 1, "Admitting ignorance prevents hallucination."),
                ("What is the most common cause of bad RAG answers?",
                 ["The font", "Retrieval returning the wrong passages", "Too many citations", "Short questions"],
                 1, "If retrieval fails, generation fails."),
                ("How do you update a RAG system's knowledge?",
                 ["Retrain the model", "Update the documents and their vectors", "Change the API key", "You cannot"],
                 1, "Knowledge lives in the documents."),
            ],
        },
        # ------------------------------------------------------------------ 16
        {
            "title": "Better Retrieval: Chunking, Hybrid Search and Reranking",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=9wk7mGB_Gp4",
            "content": r"""
**Learning objective:** Measure retrieval quality with recall@k on labelled questions, and improve it with keyword search (BM25), hybrid search, query rewriting and reranking.

## Measure retrieval on its own

Before judging answers, check whether the **right section** is among the retrieved ones. For each test question we know which section answers it:

{HANDBOOK}

{QUESTIONS}

{EMBED}

```python
def recall_at_k(search_fn, k=3):
    hits = 0
    for question, expected in test_questions:
        titles = [chunks[i]["title"] for i in search_fn(question)[:k]]
        hits += expected in titles
    return hits / len(test_questions)

def embedding_ranking(question):
    return list(np.argsort(doc_vectors @ embed([question])[0])[::-1])

for k in [1, 3, 5]:
    print(f"embeddings recall@{k}: {recall_at_k(embedding_ranking, k):.2f}")
```

**Recall@k** = the share of questions whose correct section appears in the top k. It is the single most useful number for a RAG system: if it is low, no prompt can save the answers.

## BM25: keyword search done well

**BM25** is the classic search-engine formula: it rewards rare words that appear in a document, with diminishing returns for repeated words and a correction for long documents.

```python
import math
import re
from collections import Counter

STOP = {"the", "a", "an", "is", "are", "i", "my", "do", "to", "of", "and", "for", "in", "on", "at",
        "what", "how", "can", "me", "it", "if", "with", "does", "there", "this", "be", "by", "or"}

def tokenize(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP]

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [tokenize(d) for d in docs]
        self.avg = sum(len(d) for d in self.docs) / len(self.docs)
        self.df = Counter(w for d in self.docs for w in set(d))
        self.N, self.k1, self.b = len(self.docs), k1, b

    def scores(self, query):
        out = []
        for d in self.docs:
            tf, s = Counter(d), 0.0
            for w in tokenize(query):
                if w in tf:
                    idf = math.log(1 + (self.N - self.df[w] + 0.5) / (self.df[w] + 0.5))
                    s += idf * tf[w] * (self.k1 + 1) / (tf[w] + self.k1 * (1 - self.b + self.b * len(d) / self.avg))
            out.append(s)
        return np.array(out)

bm25 = BM25([c["text"] for c in chunks])
def bm25_ranking(question):
    return list(np.argsort(bm25.scores(question))[::-1])

for k in [1, 3]:
    print(f"BM25 recall@{k}: {recall_at_k(bm25_ranking, k):.2f}")
```

On our handbook BM25 finds the right section first for about **58%** of questions (embeddings: about **67%**). Questions like "If I quit…" share no words with their section, so BM25 cannot find them. Keyword search is still strong for exact terms — names, codes, numbers — where embeddings can be vague.

## Hybrid search: combine both

**Reciprocal rank fusion (RRF)** merges rankings without worrying about score scales: each document gets 1 ÷ (60 + its rank) from each method, and the sums are compared.

```python
def hybrid_ranking(question, c=60):
    fused = Counter()
    for ranking in (embedding_ranking(question), bm25_ranking(question)):
        for rank, doc in enumerate(ranking):
            fused[doc] += 1 / (c + rank + 1)
    return [doc for doc, _ in fused.most_common()]

for name, fn in [("embeddings", embedding_ranking), ("BM25", bm25_ranking), ("hybrid", hybrid_ranking)]:
    print(f"{name:10s} recall@1 {recall_at_k(fn, 1):.2f}   recall@3 {recall_at_k(fn, 3):.2f}")
```

Look closely at the result: on this tiny collection, hybrid search is **not** better than embeddings alone (recall@3 about 0.83 against 0.92) — BM25's mistakes pull some right answers down. On large real collections with a strong embedding model, hybrid search is usually a strong default, because keywords catch exact terms and embeddings catch paraphrases. The lesson: **never assume an improvement — measure it on your own questions.**

## Chunking: what is one "document"?

Real documents are long. You split them into **chunks** before embedding:

- **Too large** — one vector must represent many topics; retrieval gets vague, prompts get long and costly.
- **Too small** — chunks lose context ("It costs 5,000 RWF" — what does?).
- Good defaults: a few hundred tokens per chunk, split at headings or paragraphs, with a little **overlap** between neighbours, and the section title copied into each chunk (as ours do).

```python
def chunk_text(text, size=40, overlap=10):
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, max(len(words) - overlap, 1), step)]

long_doc = " ".join(c["text"] for c in chunks[:4])
pieces = chunk_text(long_doc)
print(len(long_doc.split()), "words ->", len(pieces), "chunks")
print(pieces[1][:120], "...")
```

## Query rewriting and reranking

- **Query rewriting:** ask an LLM to turn a vague or chatty question into a clean search query ("I left my bag… is it still there?" → "lost and found items kept how long"). Also useful to translate Kinyarwanda questions before searching English documents.
- **Reranking:** retrieve generously (say 20 chunks), then let a stronger model — a cross-encoder or an LLM — score each chunk against the question and keep the best 3. More accurate, a little slower.

{SETUP}

```python
def rewrite_query(question):
    return ask("Rewrite this question as a short search query of key words. Reply with the query only.\n\n"
               f"<question>{question}</question>", max_tokens=40).strip()

print(rewrite_query("I left my bag at the hub last week. Is it still there?"))
```

## Key terms

- **Recall@k** — share of questions whose correct chunk is in the top k results.
- **BM25** — a strong keyword ranking formula.
- **Hybrid search** — combining keyword and embedding rankings.
- **Reciprocal rank fusion** — merging rankings by 1 ÷ (c + rank).
- **Chunking / overlap** — splitting documents into searchable pieces that share a little text.
- **Reranking** — re-scoring retrieved chunks with a stronger model.

**Takeaway:** Measure retrieval with recall@k first; then improve it with sensible chunking, hybrid keyword + embedding search, query rewriting and reranking.

## Try it yourself

1. Find the questions each method gets wrong at k = 1. Why do they fail?
2. Write five new test questions that use different words from the handbook. Which method wins now?
3. Try `chunk_text` with sizes 20, 40 and 80 words. How many chunks does each make?
4. Use `rewrite_query` before `bm25_ranking` and measure recall@1 again.
""",
            "quiz": [
                ("What does recall@3 measure?",
                 ["Answer quality", "The share of questions whose correct chunk is in the top 3 results", "Speed", "Cost"],
                 1, "It isolates retrieval quality."),
                ("When is keyword search (BM25) especially strong?",
                 ["For paraphrases", "For exact terms such as names, codes and numbers", "For images", "Never"],
                 1, "Exact matches matter."),
                ("What does hybrid search combine?",
                 ["Two LLMs", "Keyword and embedding rankings", "Text and images", "Training and testing"],
                 1, "Each catches what the other misses."),
                ("What is a problem with very large chunks?",
                 ["They cannot be embedded", "One vector must represent many topics, so retrieval gets vague", "They are always too cheap", "They have no words"],
                 1, "Smaller focused chunks retrieve better."),
                ("What is reranking?",
                 ["Sorting alphabetically", "Re-scoring many retrieved chunks with a stronger model and keeping the best", "Deleting chunks", "Changing the question"],
                 1, "Retrieve generously, then rerank."),
                ("Why rewrite a user's question before searching?",
                 ["To make it longer", "To turn chatty or translated questions into clean search queries", "To hide it", "It is required"],
                 1, "Better queries → better retrieval."),
            ],
        },
        # ------------------------------------------------------------------ 17
        {
            "title": "Evaluating LLM Applications",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=6u996P09EZE",
            "content": r"""
**Learning objective:** Build an evaluation set for an LLM app, score answers with automatic checks and an LLM judge, test refusal and citation behaviour, and use the results to decide what to change.

## "It looked good in the demo" is not evaluation

LLM apps fail in subtle ways: a wrong number, a confident invention, a refusal when the answer was available. Changing the prompt, the model or the retrieval can fix one case and break three others. You need a **repeatable test** you can run after every change — like the test sets in Machine Learning Fundamentals.

{SETUP}

{HANDBOOK}

{EMBED}

## The app under test

```python
import re

RAG_SYSTEM = ("Answer using ONLY the numbered sources. Cite like [1]. If the sources do not contain "
              "the answer, reply exactly: \"I don't know based on the handbook.\"")

def retrieve(question, k=3):
    return [chunks[i] for i in np.argsort(doc_vectors @ embed([question])[0])[::-1][:k]]

def rag_answer(question):
    sources = retrieve(question)
    numbered = "\n".join(f"[{n}] {s['text']}" for n, s in enumerate(sources, 1))
    text = ask(f"<sources>\n{numbered}\n</sources>\n\n<question>{question}</question>",
               system=RAG_SYSTEM, max_tokens=300)
    return text, sources
```

## An evaluation set

Each case has a question, **facts the answer must contain**, and whether the app should refuse:

```python
eval_set = [
    {"q": "How much is the Student plan per month?", "must_include": ["10,000"], "refuse": False},
    {"q": "Until what time is the hub open on Saturday?", "must_include": ["14:00"], "refuse": False},
    {"q": "How many free meeting-room hours do Student members get?", "must_include": ["1"], "refuse": False},
    {"q": "How long is lost property kept?", "must_include": ["30"], "refuse": False},
    {"q": "What is the price of a coffee at the hub cafe?", "must_include": [], "refuse": True},
    {"q": "Who is the President of the hub's board?", "must_include": [], "refuse": True},
]
print(len(eval_set), "test cases")
```

Include **unanswerable** questions on purpose: they test whether the app admits it does not know.

## Automatic checks

```python
REFUSAL = "i don't know based on the handbook"

def check(case, answer, sources):
    text = answer.lower()
    refused = REFUSAL in text
    result = {"refusal_ok": refused == case["refuse"]}
    if not case["refuse"]:
        result["facts_ok"] = all(fact.lower() in text for fact in case["must_include"])
        cited = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]
        result["cites_ok"] = bool(cited) and all(1 <= n <= len(sources) for n in cited)
    return result

rows = []
for case in eval_set:
    answer, sources = rag_answer(case["q"])
    rows.append({"q": case["q"][:45], **check(case, answer, sources)})

import pandas as pd
report = pd.DataFrame(rows)
print(report)
print({c: f"{report[c].dropna().mean():.0%}" for c in report.columns if c != "q"})
```

Three simple, objective checks: Did it refuse when it should (and only then)? Does the answer contain the required facts? Does every citation point to a real source?

## LLM-as-judge for the rest

Some qualities — is the answer complete, polite, faithful to the sources? — are hard to check with code. You can ask a **second model call** to grade with a clear rubric:

```python
JUDGE = ("You grade answers. Given SOURCES, QUESTION and ANSWER, score from 1 to 5: "
         "5 = fully correct and supported by the sources, 3 = partly correct or missing details, "
         "1 = wrong or not supported. Reply in the form:\nSCORE: <number>\nREASON: <one sentence>")

def judge(question, answer, sources):
    numbered = "\n".join(f"[{n}] {s['text']}" for n, s in enumerate(sources, 1))
    verdict = ask(f"SOURCES:\n{numbered}\n\nQUESTION: {question}\n\nANSWER: {answer}", system=JUDGE, max_tokens=100)
    match = re.search(r"SCORE:\s*([1-5])", verdict)
    return (int(match.group(1)) if match else None), verdict

answer, sources = rag_answer(eval_set[0]["q"])
score, verdict = judge(eval_set[0]["q"], answer, sources)
print("judge score:", score)
```

Judges are useful but imperfect: they can be too kind, prefer longer answers, or share the same blind spots as the model being judged. **Check a sample of judge scores by hand**, and prefer objective checks where possible.

## Use the results

- Look at **every failure**, not just the average. Group failures: retrieval missed? Wrong number? Refused wrongly?
- Change **one thing at a time** (prompt, k, chunking, model), re-run the whole set, and compare.
- Keep the evaluation set growing: every bug reported by a real user becomes a new test case.
- For languages such as Kinyarwanda, build test cases in that language — quality can be very different from English.

## Key terms

- **Evaluation set** — questions with expected facts or behaviour, run after every change.
- **Refusal test** — an unanswerable question that should produce "I don't know".
- **Citation check** — verifying citations point to real retrieved sources.
- **LLM-as-judge** — using a model with a rubric to grade answers.
- **Regression** — something that used to work and broke after a change.

**Takeaway:** Evaluate LLM apps like software: a growing test set with objective checks, refusal tests and a carefully checked LLM judge, re-run after every change.

## Try it yourself

1. Add five more cases, including two in Kinyarwanda. Which checks fail?
2. Change `k` in `retrieve` from 3 to 1. Which scores drop?
3. Ask the judge to grade a deliberately wrong answer ("The Student plan costs 50,000 RWF [1]"). Does it notice?
4. Write the evaluation as a function you can run with one line after each change, and save its results with the date.
""",
            "quiz": [
                ("Why is a demo not enough to evaluate an LLM app?",
                 ["Demos are illegal", "Changes can fix one case and break others; you need a repeatable test set", "Demos cost too much", "LLMs cannot be tested"],
                 1, "Evaluate like software."),
                ("Why include unanswerable questions in the evaluation set?",
                 ["To confuse the model", "To test that the app admits when it does not know", "To increase cost", "They are not useful"],
                 1, "Refusal behaviour matters."),
                ("What does a citation check verify?",
                 ["Spelling", "That citations point to real retrieved sources", "Token counts", "Response time"],
                 1, "Invalid citations reveal invention."),
                ("What is an LLM-as-judge?",
                 ["A human expert", "A model call that grades answers with a rubric", "A legal system", "An embedding"],
                 1, "Useful for hard-to-code qualities."),
                ("What is a weakness of LLM judges?",
                 ["They are always perfect", "They can be too kind or share blind spots, so sample their scores by hand", "They cannot read", "They need GPUs"],
                 1, "Trust, but verify."),
                ("What should you do with a bug reported by a real user?",
                 ["Ignore it", "Add it to the evaluation set as a new test case", "Delete the app", "Change the model at random"],
                 1, "The test set should grow."),
            ],
        },
        # ------------------------------------------------------------------ 18
        {
            "title": "Week 3 Project: Ask the Handbook",
            "minutes": 120,
            "video": "https://www.youtube.com/watch?v=-eRjgj1zww4",
            "content": r"""
**Learning objective:** Build, evaluate and improve a complete question-answering assistant over a document collection, and report its quality honestly.

## The brief

Your school, church, SACCO, company or community group has rules and information in documents that people keep asking about. Build an **"Ask the Handbook"** assistant that answers from those documents with citations, and prove how good it is.

Start with the practice handbook; then replace it with real documents you are allowed to use (no personal data).

{SETUP}

{HANDBOOK}

{QUESTIONS}

## Part 1 — Index the documents

{EMBED}

## Part 2 — Retrieval with hybrid search

```python
import math, re
from collections import Counter

STOP = {"the", "a", "an", "is", "are", "i", "my", "do", "to", "of", "and", "for", "in", "on", "at",
        "what", "how", "can", "me", "it", "if", "with", "does", "there", "this", "be", "by", "or"}
tok = lambda s: [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP]
docs_tok = [tok(c["text"]) for c in chunks]
avg_len = sum(map(len, docs_tok)) / len(docs_tok)
df = Counter(w for d in docs_tok for w in set(d))

def bm25(query, k1=1.5, b=0.75):
    out = []
    for d in docs_tok:
        tf = Counter(d)
        out.append(sum(math.log(1 + (len(docs_tok) - df[w] + 0.5) / (df[w] + 0.5))
                       * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(d) / avg_len))
                       for w in tok(query) if w in tf))
    return np.array(out)

def retrieve(question, k=3):
    fused = Counter()
    for ranking in (np.argsort(doc_vectors @ embed([question])[0])[::-1], np.argsort(bm25(question))[::-1]):
        for rank, i in enumerate(ranking):
            fused[int(i)] += 1 / (60 + rank + 1)
    return [chunks[i] for i, _ in fused.most_common(k)]

hits = sum(expected in [c["title"] for c in retrieve(q)] for q, expected in test_questions)
print(f"hybrid recall@3: {hits}/{len(test_questions)}")
```

## Part 3 — The assistant

```python
RAG_SYSTEM = (
    "You are the Kigali Tech Hub assistant. Answer using ONLY the numbered sources and cite them like [1]. "
    "Keep answers to at most three sentences. If the sources do not contain the answer, reply exactly: "
    "\"I don't know based on the handbook.\""
)

def ask_handbook(question):
    sources = retrieve(question)
    numbered = "\n".join(f"[{n}] {s['text']}" for n, s in enumerate(sources, 1))
    text = ask(f"<sources>\n{numbered}\n</sources>\n\n<question>{question}</question>",
               system=RAG_SYSTEM, max_tokens=300)
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text) if 1 <= int(n) <= len(sources)})
    return {"answer": text, "cited": [sources[n - 1]["title"] for n in cited]}

print(ask_handbook("How much does a locker cost?"))
```

## Part 4 — Evaluate

```python
eval_set = [
    {"q": "How much is the Team plan?", "facts": ["90,000"], "refuse": False},
    {"q": "When is the startup pitch night?", "facts": ["last Friday"], "refuse": False},
    {"q": "How much does it cost to replace a lost locker key?", "facts": ["5,000"], "refuse": False},
    {"q": "Until what time can guests stay?", "facts": ["18:00"], "refuse": False},
    {"q": "Does the hub offer free lunch?", "facts": [], "refuse": True},
]

results = []
for case in eval_set:
    out = ask_handbook(case["q"])
    text = out["answer"].lower()
    refused = "i don't know based on the handbook" in text
    results.append({
        "question": case["q"][:40],
        "refusal ok": refused == case["refuse"],
        "facts ok": case["refuse"] or all(f.lower() in text for f in case["facts"]),
        "cited": bool(out["cited"]) or case["refuse"],
    })

import pandas as pd
table = pd.DataFrame(results)
print(table)
print("pass rate:", f"{table[['refusal ok', 'facts ok', 'cited']].all(axis=1).mean():.0%}")
```

## Part 5 — Improve one thing at a time

Try at least two changes and re-run Parts 2 and 4 after each: different `k`, smaller chunks, query rewriting, a stricter prompt, a larger model. Record the numbers before and after in a table.

## Part 6 — Report (two pages)

1. **Documents:** what, how many, how you chunked them, permission to use them.
2. **Retrieval:** recall@1 and recall@3 for embeddings, BM25 and hybrid.
3. **Answers:** the evaluation table and pass rate; three example answers with their citations.
4. **Improvements:** what you changed and the measured effect.
5. **Risks:** outdated documents, questions in other languages, private information in documents, over-trust by users.
6. **Next steps:** how documents will be kept up to date, and who reviews the assistant's answers.

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Retrieval | Hybrid search with recall@k measured |
| Grounding | Answers cite sources; refusals work |
| Evaluation | Objective checks with a pass rate |
| Iteration | At least two measured improvements |
| Responsibility | Permission, privacy and freshness of documents addressed |

**Takeaway:** A trustworthy "ask the documents" assistant is built on measured retrieval, grounded answers with citations, honest refusals and an evaluation you can repeat.

## Try it yourself

Complete Parts 1–6 with the practice handbook, then with a real document collection of at least 20 sections. Share your evaluation table with your instructor in the lesson Q&A.
""",
            "quiz": [
                ("What should you measure first in a RAG project?",
                 ["The font size", "Retrieval quality, for example recall@k", "The cost of GPUs", "Answer length"],
                 1, "Good answers need good retrieval."),
                ("Which documents may you use for the project?",
                 ["Any private files you find", "Documents you are allowed to use, without personal data", "Other people's emails", "Copyrighted books"],
                 1, "Permission and privacy first."),
                ("What does the 'refusal ok' check test?",
                 ["Speed", "That the assistant refuses exactly when the answer is not in the documents", "Politeness", "Token count"],
                 1, "No invented answers."),
                ("How should you improve the assistant?",
                 ["Change everything at once", "Change one thing at a time and re-run the evaluation", "Never change it", "Remove the tests"],
                 1, "Measured iteration."),
                ("Which is a real risk of a document assistant?",
                 ["Documents never change", "Outdated documents give confident but old answers", "Citations are always wrong", "It cannot read text"],
                 1, "Keep documents up to date."),
                ("Why combine embeddings and BM25 in retrieval?",
                 ["To double the cost", "Keywords catch exact terms, embeddings catch paraphrases", "BM25 needs embeddings", "It is required by RAG"],
                 1, "Hybrid search is a strong default."),
            ],
        },
    ],
}

for _lesson in WEEK3["lessons"]:
    _lesson["content"] = (_lesson["content"].replace("{SETUP}", SETUP).replace("{HANDBOOK}", HANDBOOK)
                          .replace("{QUESTIONS}", QUESTIONS).replace("{EMBED}", EMBED))
