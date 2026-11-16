# Course upgrade: Student Handbook, "Run Python" in lessons, ratings and better course pages

This update makes the WAMUGII courses feel professional in three ways:

1. **AI Foundations Student Handbook.** A 197-page book (about 65,000 words) that teaches the whole course by reading alone.
2. **Run Python in the browser.** Every Python example in a lesson now has a **Run** button. The code runs on the student's own device, with nothing sent to our server.
3. **Better course pages.** Star ratings and reviews, a handbook section with a free sample chapter, a "Practise as you read" section, instructors, a FAQ, "What's included", and "Continue learning" for enrolled students.

---

## 1. The Student Handbook (AI Foundations)

**What students get**

- **24 full chapters**, one per lesson, each about 3 times longer than the old notes. Each chapter has:
  - goals
  - numbered sections
  - worked examples with every step shown
  - diagrams
  - "Common mistake" and "In Rwanda" boxes
  - a summary and key terms
  - a self-check (the same questions as the online quiz)
  - "Think deeper" questions
  - a practice activity
- **The project chapters (6, 12, 18 and 24)** each include a complete **model answer**, so students see what "good" looks like.
- **At the back of the book:** a glossary of every key term, an answer key with the reason for every answer, and a model answer for every Think deeper question.
- **Inside the PDF:** a cover, "How to use this handbook", a contents page with page numbers, and clickable bookmarks.

**Where it appears**

- **Lesson 1** now has a download called "AI Foundations - Complete Student Handbook.pdf".
- **Every lesson's PDF** is now its full chapter, with the answers at the end. These replace the old 2-page handouts.
- **The public course page** shows "Learn by reading, too" and a **free sample chapter** (chapter 1) that anyone can download.

**Files**

| File | What it is |
|---|---|
| `wamugii-backend/app/course_content/handbooks/ai-foundations/01.md` … `24.md`, `intro.md` | The chapter text (easy to edit) |
| `wamugii-backend/app/course_content/handbooks/ai-foundations/handbook.pdf` | The complete book |
| `wamugii-backend/app/course_content/handbooks/ai-foundations/handbook.json` | Page and word count, shown on the course page |
| `wamugii-backend/app/course_content/pdfs/ai-foundations/01.pdf` … `24.pdf` | One chapter per lesson (replaced) |
| `wamugii-backend/scripts/course_make_handbook.py` | Builds the PDFs from the chapter files |
| `wamugii-backend/scripts/handbook_figures.py` | The 17 diagrams |

**To change a chapter later:**

1. Edit the `.md` file.
2. Rebuild the PDFs. You need Python with `playwright` (and Chromium), `markdown` and `pypdf`, and the Inter and Lora fonts.
   ```
   cd wamugii-backend
   python scripts/course_make_handbook.py ai_foundations
   ```
3. Run the seed again (see "Deploy" below).

---

## 2. "Run Python" in lessons

- Each Python example has **Run**, **Edit**, **Copy** and **Reset** buttons.
  - Students can change the code and run it again. **Ctrl+Enter** also runs it.
  - Output, tables and **matplotlib charts** appear under the code.
- **All the examples in one lesson share their variables, like a notebook.** If a student runs block 3 before block 1, the error box offers **"Run the earlier blocks first"**.
- **It uses Pyodide 0.29.4** (Python 3.13 compiled to WebAssembly). numpy, pandas, scikit-learn, scipy and matplotlib load automatically.
  - The first run takes 10–30 seconds while Python downloads (about 7 seconds in my test).
  - After that it is instant, and the browser keeps the files in its cache.
- **Examples that cannot work in a browser** (PyTorch, API keys, FastAPI servers, subprocess) show a clear note with a Google Colab link instead of a Run button. This includes later blocks that depend on them.

**Tested.** I ran all 618 Python examples from the 5 coding courses inside Pyodide:

| Course | Run in the browser | Colab only |
|---|---|---|
| Math & Python for AI | 111 of 115 | 0 |
| Machine Learning Fundamentals | 129 of 129 | 0 |
| Responsible AI & Deployment | 114 | 14 |
| Deep Learning & Neural Networks | 21 | 91 (they use PyTorch) |
| Modern AI: LLMs & Generative AI | 59 | 75 (PyTorch or API keys) |

- No runnable example fails, except 4 in Math & Python:
  - lesson 1, block 4 is the deliberate "missing bracket" error example;
  - lesson 24 (the final project) uses data the student builds in lesson 23.
- In a real browser, I also tested: the first run, the error hint, a chart, the Colab note, editing and Stop.

**Files:** `wamugii-frontend/src/lib/python/runtime.ts`, `src/components/courses/PythonRunner.tsx`, and `src/components/courses/LessonContent.tsx` (changed).

---

## 3. Ratings, reviews and better course pages

**Star ratings and reviews**

- **Who can rate:** a student rates a course (1–5 stars and an optional comment) after completing **a quarter of the lessons**.
  - The "Rate this course" card appears in the course player.
  - One review per student; writing again updates it.
- **On the course page:**
  - the average, the number of ratings, a bar for each star and the reviews;
  - only the student's first name and initial ("Aline M."), never the email or surname.
- **Course cards** in the catalogue show ★ 4.8 (12).
- **Staff tab:** admins and staff get a new **Reviews** tab on each course to **hide** a bad review (spam, insults) or show it again.
  - A hidden review leaves the average but is kept, so the decision can be undone.

**Other new parts of the course page**

- "Learn by reading, too" (the handbook, with the sample download)
- "Practise as you read" (on coding courses)
- "Your instructors"
- "Questions students ask" (FAQ)
- "What's included"
- **"Continue learning · 40% done"** instead of "Enroll" when the student is already enrolled

**Backend**

| File | What it is |
|---|---|
| `app/models/course_review.py` | **New table** `course_reviews` |
| `alembic/versions/c4e8a1f2d6b9_course_reviews.py` | **New migration** (after `b7d2e4f6a8c1`) |
| `app/services/course_reviews.py`, `app/schemas/course_review.py` | The rules and data shapes |
| `app/api/v1/courses.py` | Public reviews, sample chapter download and staff moderation |
| `app/api/v1/client.py` | A student reads, writes and deletes their own rating |
| `app/seed_course_content.py` | Now attaches the handbook to lesson 1 |
| `tests/test_course_reviews.py` | **13 new tests** |

New endpoints:

- `GET /api/v1/courses/{slug}/reviews` (public)
- `GET /api/v1/courses/{slug}/sample-chapter` (public PDF)
- `GET`, `PUT`, `DELETE /api/v1/client/courses/{id}/review` (student)
- `GET /api/v1/courses/by-id/{id}/reviews` and `PATCH /api/v1/courses/by-id/{id}/reviews/{review_id}` (admin and staff)

**Test results**

- Backend: **546 passed** (533 before plus 13 new).
- Frontend: `tsc` OK, lint with no new warnings, build OK.

---

## How to apply

**Important:** first commit and push the security fixes from Claude Code. Those changes touch some of the same files (`client.py`, the course pages and `types/api.ts`). If you unzip this update on top of them, it would overwrite those changes. So use the **patch file**, which merges with your changes instead of replacing files:

```
cd wamugii                       # repo root
git status                       # should be clean (security fixes already committed)
git apply --3way wamugii-course-upgrade.patch
git status                       # check the changed files
```

- If git reports a conflict in a file, open it, keep **both** changes, then `git add` the file.
- `src/types/api.ts` is generated, so if it conflicts, just regenerate it: start the backend locally, then run `npm run gen:api` in `wamugii-frontend`.
- If your tree has no other changes, you can use the zip instead: unzip it at the repo root.

Then commit and push:

```
git add -A
git commit -m "feat: AI Foundations handbook, run Python in lessons, course ratings and better course pages"
git push
```

## Deploy (on the droplet)

1. `git pull` in `/opt/wamugii`.
2. Build the new backend image (next `vN`) and run `/opt/redeploy-wamugii.sh`, as usual.
3. **Run the migration** (new table): `docker exec wamugii-backend alembic upgrade head`
4. **Re-seed AI Foundations** (new chapter PDFs, plus the handbook on lesson 1): `docker exec wamugii-backend python -m app.seed_course_content ai_foundations`
5. Deploy the frontend.
6. **Update the security headers (CSP)** from the security fixes. Pyodide loads from jsDelivr and runs WebAssembly in a Web Worker. In `deploy/nginx-security-headers.conf` (Plesk → Additional nginx directives), add to the Content-Security-Policy:
   - `script-src`: `https://cdn.jsdelivr.net 'wasm-unsafe-eval'`
   - `connect-src`: `https://cdn.jsdelivr.net`
   - `worker-src`: `'self' blob:`

   While the CSP is still "Report-Only" nothing breaks. But add these before you switch it to enforcing, or the Run button will stop working.
   - *Optional:* to serve Python from your own server instead of jsDelivr, copy the Pyodide 0.29.4 files to a folder on your site. Set `VITE_PYODIDE_URL=https://wamugii.kento.rw/pyodide/` when building the frontend.

## How to check it works (live)

1. Open `https://wamugii.kento.rw/courses/ai-foundations`. You should see the "197-page handbook" chip in the hero and the "Learn by reading, too" section. **Download the sample chapter** (a 9-page PDF).
2. As a student, open **Machine Learning Fundamentals**, lesson 2. Press **Run** on the first example; after a short wait you see `(600, 6)` and a table.
3. Open **Deep Learning**, lesson 5. The examples show the Colab note instead of Run.
4. Open AI Foundations lesson 1: **"AI Foundations - Complete Student Handbook.pdf"** is in the downloads.
5. Complete 6 lessons of AI Foundations, then rate it in the player. The rating appears on the course page under "What students say".
6. As admin, open the course → **Reviews** tab → **Hide** or **Show again** works.

## Next ideas

- Full handbooks for the other six courses. They use the same builder; only the chapter `.md` files need writing.
- Paid courses with online payment, once the payment gateway is chosen.
- A certificate check page (`/verify/<id>`) with a QR code.
