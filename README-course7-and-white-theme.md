# Course 7 – Responsible AI & Deployment (Capstone) + white-theme fixes

This one update contains two things. Apply it once, then deploy once.

## 1. Course 7 – Responsible AI & Deployment (Capstone)

24 lessons over 4 weeks (about 27 hours). It replaces the short 8-lesson version; students keep
their enrolment. One realistic story runs through the whole course: a loan-repayment model for a
SACCO (made-up data, no real people).

- **Week 1 · From Notebook to Product** – model files with metadata, reproducible training,
  a FastAPI service with input checks, testing ML systems with pytest, Docker packaging.
  Project: a tested loan-scoring service.
- **Week 2 · MLOps** – CI/CD and quality gates, experiment tracking and a model registry,
  monitoring with alerts, data drift and concept drift, shadow mode / canary / A/B tests.
  Project: six months in production – detect drift, retrain, decide.
- **Week 3 · Fairness, Explainability, Privacy and Security** – fairness metrics, where bias
  comes from and how to reduce it, explaining decisions, privacy under Rwanda's Law
  No. 058/2021, attacks on AI systems and a protected API. Project: a full responsible-AI audit.
- **Week 4 · Governance, Documentation and the Capstone** – AI law and policy (Rwanda's National
  AI Policy, the EU AI Act), risk register, model cards and datasheets, human oversight,
  then plan, build and present your own end-to-end capstone + certificate.

Every lesson has a video, "Go deeper" full lectures (EuroPython, PyCon, PyData and SciPy talks),
notes with ready-to-run code, a PDF handout and a 6-question quiz. Final-exam bank: 195 questions.
All 128 code blocks were run and checked; the numbers in the notes are the ones the code prints.
Students need only Google Colab – no API key.

## 2. White (light) theme – readable everywhere

Your live site still shows the old colours because the earlier light-theme fix was never pushed.
It is included here, plus a second, deeper check of everything a student sees:

- Pale grey text, bright cyan / orange / pink / green labels on white, white numbers on the
  coloured program steps, and the faint badge in the dark top section – fixed (from the first fix).
- New in this check: quiz results (letters in the answer circles, faded wrong options), the
  certificate (ID number, "Date issued", "Authorised signature", motto), the green
  "Get my certificate" button, the locked final-exam card, lecture lengths, the "24/7" label in
  the home-page artwork, and the moving stage chips (checked at several animation moments).
- Measured on every public, client and admin page, on computer and phone sizes, plus the lesson
  player, quiz results, exam screens and certificate. The dark theme looks the same as before.

## Deploy

No database change (no new migration).

On your computer, in the repo root:

```bash
unzip -o wamugii-course7-and-white-theme.zip
git add -A
git commit -m "feat: full Responsible AI & Deployment course (Course 7) + readable light theme"
git push
```

On the droplet:

```bash
cd /opt/wamugii && git checkout -- wamugii-frontend/package-lock.json && git pull

# backend: rebuild (use the next version number, e.g. v9 if you used v8 last time)
cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v9 .
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v9 uvicorn app.main:app --host 127.0.0.1 --port 8001

docker exec wamugii-backend alembic upgrade head        # safe even if nothing to do

# load Course 7 (lessons, PDFs, lectures, exam bank)
docker exec wamugii-backend python -m app.seed_course_content responsible_ai_deployment

# frontend (white-theme fixes + course card)
/opt/redeploy-wamugii.sh
```

Then open the site, switch to the white theme with the moon/sun button, and press Ctrl+F5 once.
