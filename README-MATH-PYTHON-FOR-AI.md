# Update: Math & Python for AI — the full course (Course 3)

## What is new

1. **Math & Python for AI is now a full course.** It has 4 weeks, 24 lessons and about 20 hours of study.
   - Every lesson has a video, notes with ready-to-run Python code, a 6-question quiz and a PDF handout and worksheet.
   - There is a project at the end of every week.
   - Week 1 covers Python basics.
   - Week 2 covers working with data: NumPy, Pandas, cleaning data, grouping and charts.
   - Week 3 covers vectors, matrices, statistics and probability.
   - Week 4 covers Bayes' theorem, correlation, derivatives and gradient descent. Students then build a linear regression model from scratch.
   - Students run all the code free in **Google Colab**. There is nothing to install.
   - The old 9-lesson version is hidden automatically. Students who already enrolled stay enrolled.
2. **I ran and checked every code example** (over 110 code boxes). The numbers written in the notes match what the code really prints.
3. **Code boxes have a Copy button.** Students tap Copy and paste the code into Colab. Before this update, code boxes were almost unreadable in dark mode. That is fixed.
4. **Quizzes show code properly.** A snippet such as `2 ** 3` inside a quiz question now looks like code.
5. **Small fix in AI Foundations.** Each project lesson had an "About this project" section, and it wrongly showed an "I did this activity" tick. That heading is now "What you will do". Its 24 PDFs were rebuilt, and the loader updates them for students.
6. Handouts (PDFs) now show code in a neat grey box.

## Deploy steps

### 1. On your computer (at the repo root)

```bash
unzip -o wamugii-math-python-for-ai.zip
git add -A
git commit -m "feat: full Math & Python for AI course, copyable code blocks, code in quizzes"
git push
```

### 2. On the droplet

The backend changed (new course files and PDFs live inside the backend image), so rebuild it. The new tag is **v5**.

```bash
cd /opt/wamugii
git checkout -- wamugii-frontend/package-lock.json
git pull

cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v5 .
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v5 uvicorn app.main:app --host 127.0.0.1 --port 8001

docker exec wamugii-backend alembic upgrade head      # no new migration, safe to run

# load the new course, and refresh AI Foundations (new heading + PDFs)
docker exec wamugii-backend python -m app.seed_course_content math_python_for_ai
docker exec wamugii-backend python -m app.seed_course_content ai_foundations

/opt/redeploy-wamugii.sh
```

### 3. Check

- Open `https://wamugii.kento.rw/courses/math-python-for-ai`. You should see 4 weeks and 24 lessons, each with a ▶ icon.
- Open lesson 8, "Pandas: Tables of Data". Tap **Copy** on a code box and paste it into a new Colab notebook. It should run.
- Take one quiz and check that code like `2 ** 3` shows as code.

## Videos

All videos are free YouTube videos from well-known teaching channels. These include 3Blue1Brown, StatQuest, Crash Course Statistics, Corey Schafer, Keith Galli, Programming with Mosh, Khan Academy and freeCodeCamp.

To swap a video, change the lesson's `"video"` line in `app/course_content/mp_week*.py`. Then run the loader command again.
