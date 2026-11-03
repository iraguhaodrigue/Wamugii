# Update: AI Foundations full course + a video in every lesson + direct lesson links

## What is new

1. **AI Foundations (Course 2) is now a full course.** It has 4 weeks, 24 lessons and about 20 hours of study.
   Every lesson has a video, notes, a 6-question quiz and a PDF handout and worksheet.
   There is a project at the end of every week.
   The old 9-lesson version is hidden automatically. Students who already enrolled stay enrolled.
2. **Every lesson in both courses now has a video.** That is 48 of 48 lessons.
   AI Career Essentials had 13 lessons without a video. They all have one now.
3. **Lesson links open the lesson directly, video first.**
   - On the public course page, every lesson is a link (a ▶ icon means it has a video).
   - The link opens that lesson straight away, with the **video at the top** and the notes below it.
   - A student who is not signed in goes to Login, then lands back on the same lesson.
   - On a free course the student is not enrolled in yet, they see one button: "Enroll free & start learning".
   - Inside a lesson, **Copy lesson link** copies a link you can share on WhatsApp or social media.
     The link looks like this: `/client/learning/ai-foundations?lesson=24`
4. The lesson page no longer scrolls sideways on phones.
5. When you run the course loader again, it now updates the PDFs that students download.

## Deploy steps

### 1. On your computer (at the repo root)

```bash
unzip -o wamugii-courses-videos-ai-foundations.zip
git add -A
git commit -m "feat: full AI Foundations course, videos for every lesson, direct video-first lesson links"
git push
```

### 2. On the droplet

The backend changed (the API now tells the course page which lessons have a video), so you must rebuild the backend image.

```bash
cd /opt/wamugii
git checkout -- wamugii-frontend/package-lock.json
git pull

# rebuild the backend (new tag v4)
cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v4 .
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v4 uvicorn app.main:app --host 127.0.0.1 --port 8001

# no new migration this time, but running it is safe
docker exec wamugii-backend alembic upgrade head

# load the content: the new AI Foundations course, plus the new videos and PDFs for AI Career Essentials
docker exec wamugii-backend python -m app.seed_course_content ai_foundations
docker exec wamugii-backend python -m app.seed_course_content ai_career_essentials

# rebuild the frontend
/opt/redeploy-wamugii.sh
```

### 3. Check

- Open `https://wamugii.kento.rw/courses/ai-foundations`. You should see 4 weeks and 24 lessons, each with a ▶ icon.
- Click any lesson. It should open that lesson with the video at the top (log in first if asked).
- Open AI Career Essentials and check that lessons 5, 7 and 19 now have videos.

## Videos

All videos are free YouTube videos from well-known educational channels, such as 3Blue1Brown, IBM Technology, CGP Grey, TED-Ed and Kurzgesagt.
To swap a video, change the lesson's `"video"` line in `app/course_content/af_week*.py` or `ace_week*.py`.
Then run the loader command above again. You can also change it in Admin → Courses → lesson → Video URL.
If you change it only in Admin, the next time you run the loader it will put the file's video back.
