# Final exams, instructor accounts, full lectures and Course 4 (Machine Learning Fundamentals)

This update adds:

1. **A proctored final exam for every course** (like Huawei ICT Academy exams)
   - 60 questions, 90 minutes, pass mark 60%, 3 attempts, 24 hours between attempts.
   - 4 question types: true/false, single answer, multiple answers, fill in the blank.
   - Questions are drawn at random from a bigger bank, grouped by type, options shuffled.
   - The exam opens in full screen. Leaving the exam screen (another tab, another app,
     a pop-up taking focus, leaving full screen, reloading the page) shows a warning.
     The **3rd time the exam is submitted automatically**.
   - Copy, paste, right-click and print-screen are blocked and logged.
   - Marking happens on the server only. Answers are saved every 2 seconds.
   - Results show a score per week (topic). Passing unlocks the certificate, which now
     shows "final exam passed with X%".
   - Admin/instructor can change the rules per course and give a student 1 more attempt.
2. **Instructor accounts**
   - New role `INSTRUCTOR`. An admin assigns an instructor to a course by email
     (course page → **Instructors** tab). A normal registered user is promoted automatically.
   - Instructors see only their courses: edit lessons, videos, PDFs, the exam question bank,
     see students, progress and exam results, and answer student questions.
   - Students can ask questions under every lesson; instructors get an email and
     students get an email when someone answers.
3. **"Go deeper" full lectures** under the short video of each lesson
   (Harvard CS50, MIT, Stanford, freeCodeCamp, StatQuest, Data School, PyCon/SciPy talks).
4. **Course 4 – Machine Learning Fundamentals**: 24 lessons, 4 weeks, about 22 hours,
   every code block tested with scikit-learn, quizzes, a project every week, handout PDFs,
   and a 196-question exam bank.
5. Exam banks for Courses 1–3 too (166, 189 and 189 questions).

## Deploy (same steps as before + 1 new migration step)

On your computer, in the repo root:

```bash
unzip -o wamugii-exams-instructors-ml-course.zip
git add -A
git commit -m "feat: proctored final exams, instructor accounts, full lectures, Course 4 Machine Learning Fundamentals"
git push
```

On the droplet:

```bash
cd /opt/wamugii && git checkout -- wamugii-frontend/package-lock.json && git pull

# backend: use the next version number (v5, or v6 if you already used v5)
cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v5 .
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v5 uvicorn app.main:app --host 127.0.0.1 --port 8001

# NEW and REQUIRED: database changes (new tables + new role)
docker exec wamugii-backend alembic upgrade head

# load / refresh all 4 courses (lessons, PDFs, lectures, exam banks)
docker exec wamugii-backend python -m app.seed_course_content ai_career_essentials
docker exec wamugii-backend python -m app.seed_course_content ai_foundations
docker exec wamugii-backend python -m app.seed_course_content math_python_for_ai
docker exec wamugii-backend python -m app.seed_course_content machine_learning_fundamentals

# frontend
/opt/redeploy-wamugii.sh
```

Students keep their enrolments and progress. Old short lessons of Course 4 are hidden.

## Create an instructor

1. The instructor registers normally on the website.
2. Admin opens **Courses → Machine Learning Fundamentals → Instructors**, types the
   instructor's email and clicks **Assign**.
3. The instructor logs in and lands on **My Courses** (`/instructor`).

## Optional: AI help to write exam questions

The **Draft with AI** button in the exam tab asks Claude to draft questions from the
lesson notes. Drafts are shown for review and are saved only when you click save.
To turn it on, add your key to `/opt/wamugii.env` and restart the backend container:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Without a key, everything else works; the button just says AI drafting is not set up.

## Good to know

- A website cannot stop someone from switching tabs or using a second phone. It can
  only detect it, warn, log it, and auto-submit. On iPhone Safari there is no full-screen
  mode, so only tab and app switching are detected there.
- Reloading the exam page counts as leaving the exam screen.
- Students must finish every lesson before the exam unlocks.
