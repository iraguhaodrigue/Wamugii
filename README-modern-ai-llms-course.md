# Course 6 – Modern AI: LLMs & Generative AI

This update adds the full Course 6: 24 lessons over 4 weeks (about 26 hours).

- **Week 1 · How Large Language Models Work** – from chatbots to LLMs, tokens and BPE (and why
  Kinyarwanda costs more tokens), next-token prediction and sampling (temperature, top-k, top-p),
  building and training a tiny GPT in PyTorch, and how a base model becomes an assistant
  (chat templates, instruction tuning, DPO). Project: train and study your own language model.
- **Week 2 · Building with LLM APIs** – your first API call, prompt engineering, structured output
  and tool use, conversations, memory and streaming, cost, caching, retries and reliability.
  Project: a customer-support assistant with privacy redaction and hand-off to a human.
- **Week 3 · Embeddings, Search and RAG** – embeddings and cosine similarity, a vector store with
  filters, retrieval-augmented generation with citations and "I don't know", BM25 and hybrid search,
  recall@k, and evaluating LLM apps (refusal tests, citation checks, LLM-as-judge).
  Project: "Ask the Handbook".
- **Week 4 · Agents, Generative AI and Responsible Deployment** – an agent loop with tools, step
  limits and human approval, fine-tuning vs prompting vs RAG with LoRA built from scratch, a small
  diffusion model and image input, open models with transformers and Ollama plus quantization,
  prompt-injection defences, personal data and bias testing. Final project: a tested FastAPI AI
  assistant with guardrails, rate limits and a Dockerfile + certificate.

Every lesson has a short video, "Go deeper" full lectures (Andrej Karpathy, 3Blue1Brown, CS50,
EuroPython/PyData/PyCon talks, LiveOverflow), notes with ready-to-run code, a PDF handout, a
6-question quiz, and the course has a 197-question final-exam bank.

All 123 code blocks were run and checked. The numbers in the notes are the ones the code prints.
The API lessons were tested end to end with the real Python SDKs against a local test server, so
the code shape is right; the exact wording of model answers will differ for students.

What students need: Google Colab (free). For the API lessons (Weeks 2–4) they need an API key –
the notes show Anthropic (Claude) and Google Gemini's free tier, stored in Colab's Secrets panel,
never in the code. The open-model lesson downloads a small model (about 270 MB) in Colab.

## Deploy

No database change this time (no new migration).

On your computer, in the repo root:

```bash
unzip -o wamugii-modern-ai-llms-course.zip
git add -A
git commit -m "feat: full Modern AI: LLMs & Generative AI course (Course 6)"
git push
```

On the droplet:

```bash
cd /opt/wamugii && git checkout -- wamugii-frontend/package-lock.json && git pull

# backend: the course content is inside the backend image, so rebuild it
# (use the next version number, e.g. v8 if you used v7 last time)
cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v8 .
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v8 uvicorn app.main:app --host 127.0.0.1 --port 8001

# safe to run even if already up to date
docker exec wamugii-backend alembic upgrade head

# load Course 6 (lessons, PDFs, lectures, exam bank)
docker exec wamugii-backend python -m app.seed_course_content modern_ai_llms_generative

# frontend (home page card + course page)
/opt/redeploy-wamugii.sh
```

The old short 9-lesson version of the course is hidden; students keep their enrolment.
