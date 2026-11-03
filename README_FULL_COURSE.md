# WAMUGII: Full "AI Career Essentials" course + course platform upgrade

This zip ALSO contains everything from the previous zip (WAMUGII-Pages-Theme.zip:
light/dark switch + animated inner pages), because that one is not on GitHub yet.
Unzip this one and you have both.

Unzip at the root of your repo (the folder that has wamugii-backend and
wamugii-frontend inside). Choose "Yes to all".

## What's new

### The course (Course 1 of the AI Program)
AI Career Essentials is now a full 4-week course: 24 lessons, about 19 hours.
- Week 1 · Understanding AI (6 lessons)
- Week 2 · Using AI Tools Well (6 lessons)
- Week 3 · AI at Work (6 lessons)
- Week 4 · Responsible AI and Your Career (6 lessons)
Every lesson has full notes, a 6-question quiz (20 lessons), a downloadable PDF
(handout + worksheet + self-check), and 11 lessons have a matched YouTube video.
Every week ends with a project; the course ends with a final project + certificate.
Students keep their progress on lessons that kept the same title.

### The platform
- Lessons are grouped into weeks (course page + student player), with study time.
- Quizzes: marked on the server (answers never reach the browser early), instant
  green/red feedback with explanations, unlimited retries, pass mark 70%.
  Passing a quiz completes the lesson automatically.
- Real progress ticks per lesson; the player reopens at the student's next lesson.
- Course page shows the real number of enrolled students and total study time.
- Emails: "certificate ready" when a student finishes (once), and a weekly
  "continue your course" reminder for students inactive 3+ days.
- Admin: lesson form has "Week / module" and "Study time"; lesson list shows quiz size.
  Quizzes can be replaced via the API (PUT /api/v1/courses/{id}/lessons/{id}/quiz).

## Deploy

### 1. Laptop (PowerShell, repo folder)
    git add -A
    git commit -m "feat: full AI Career Essentials course, quizzes, weeks, course emails; theme switch + animated pages"
    git push

### 2. Droplet — pull the code
    cd /opt/wamugii && git checkout -- wamugii-frontend/package-lock.json && git pull

### 3. Droplet — rebuild the backend (it has new code this time)
First check how the current container runs (keep the output, it is your rollback):
    docker inspect wamugii-backend --format '{{.Config.Image}} {{.Config.Cmd}}'

Then build and restart (same settings as before, new image tag v3):
    cd /opt/wamugii/wamugii-backend
    docker build -t wamugii-backend:v3 .
    docker stop wamugii-backend && docker rm wamugii-backend
    docker run -d --name wamugii-backend --network host --restart unless-stopped \
      --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
      wamugii-backend:v3 uvicorn app.main:app --host 127.0.0.1 --port 8001

(If the inspect output showed a different image/command, tell me and I'll adjust.
Rollback = run the same docker run with wamugii-backend:v2.)

### 4. Droplet — update the database, then load the course
    docker exec wamugii-backend alembic upgrade head
    docker exec wamugii-backend python -m app.seed_course_content ai_career_essentials

The second command prints every lesson and "+ PDF" as it attaches the handouts.
It is safe to run again any time (that is also how you publish edits).

### 5. Droplet — frontend
    /opt/redeploy-wamugii.sh

### 6. Droplet — daily reminder emails (once)
    (crontab -l 2>/dev/null; echo "0 7 * * * docker exec wamugii-backend python -m app.send_course_reminders >> /var/log/wamugii-reminders.log 2>&1") | crontab -
Runs every day at 09:00 Kigali time. Test without sending:
    docker exec wamugii-backend python -m app.send_course_reminders --dry-run

Emails use your existing Brevo settings (BREVO_API_KEY, BREVO_FROM_EMAIL and
FRONTEND_URL in /opt/wamugii.env).

## Videos
11 lessons have a video. For the other 13, use
"AI-Career-Essentials-Video-Scripts.pdf": record, upload to YouTube, then paste
the link in Admin -> Courses -> AI Career Essentials -> lesson -> Edit -> Video URL.

## For the next courses (developers)
Course content lives in wamugii-backend/app/course_content/ (one Python file per
course). PDFs are generated with:
    python3 scripts/course_make_pdfs.py ai_career_essentials app/course_content/pdfs/ai-career-essentials
(needs: pip install markdown playwright; playwright install chromium)
