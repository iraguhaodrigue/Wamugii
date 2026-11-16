# Deploy: handbook, Run Python, ratings and Open in Colab (all in one)

This one update has everything since your security fixes (commit `7169bd0`):

- the AI Foundations Student Handbook (197 pages), with the new chapter PDFs for every lesson;
- the "Run" button on Python examples in lessons;
- star ratings and reviews, and the better course pages;
- the "Open in Google Colab" button on every coding lesson.

It also fixes two small things in your security fixes:

1. In `deploy/nginx-security-headers.conf`, the sitemap was sent to port **8000**, but the live backend uses port **8001**. Now fixed.
2. The security headers (Content-Security-Policy) now allow the Run button, so you don't need to edit them by hand.

The course page conflict is already solved: your page titles and my new sections are both kept.

**Tested:** 584 backend tests pass (your 571 plus 13 new). The frontend type check, lint and build all pass.

---

## Part A: On your laptop (PowerShell, inside the `wamugii` folder)

**1. Remove the half-applied update from before.** Your security commit stays safe; this only removes what the first patch put in.

```powershell
cd "C:\Users\Gadget store\Desktop\app\wamugii"
git reset --hard HEAD
git status
```

`git status` should say "nothing to commit, working tree clean".

**2. Put the new files in.** Right-click `wamugii-all-in-one.zip` in your Downloads folder and choose **Extract All…**. Open the extracted folder, select **everything inside it**, and copy it into `C:\Users\Gadget store\Desktop\app\wamugii`. When Windows asks, choose **Replace the files in the destination**.

**3. Check, commit and push.**

```powershell
git status
git add -A
git commit -m "feat: AI Foundations handbook, Run Python in lessons, ratings, Open in Colab"
git push
```

`git status` should show 81 files (43 new, 38 changed).

**Other way (instead of step 2):** `git apply --3way "$HOME\Downloads\wamugii-all-in-one.patch"` gives exactly the same result.

---

## Part B: The notebooks repository (if not done yet)

```powershell
cd "C:\Users\Gadget store\Desktop\app"
git clone https://github.com/iraguhaodrigue/wamugii-notebooks.git
```

1. Extract `wamugii-notebooks.zip` (from the earlier message).
2. Copy everything **inside** its `wamugii-notebooks` folder (`README.md` and the 5 course folders) into the new `wamugii-notebooks` folder.
3. Commit and push:

```powershell
cd wamugii-notebooks
git add -A
git commit -m "Lesson notebooks for the WAMUGII AI Program"
git branch -M main
git push -u origin main
```

---

## Part C: On the droplet (`ssh root@146.190.21.86`)

```bash
cd /opt/wamugii && git checkout -- wamugii-frontend/package-lock.json && git pull

cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v11 .
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v11 uvicorn app.main:app --host 127.0.0.1 --port 8001

docker exec wamugii-backend alembic upgrade head          # new reviews table
docker exec wamugii-backend python -m app.seed_course_content ai_foundations   # new chapters + handbook
curl -s http://127.0.0.1:8001/api/v1/health                # should show "status":"ok"

/opt/redeploy-wamugii.sh                                    # frontend
```

---

## Part D: Plesk (security headers)

1. Open `deploy/nginx-security-headers.conf` in Notepad.
2. Copy everything in it.
3. In **Plesk → Websites & Domains → wamugii.kento.rw → Apache & nginx Settings → Additional nginx directives**, paste it and click **OK**.

No editing is needed; the file is ready.

---

## Part E: Tell Claude "deployed"

Claude will test the live site:

- the handbook and the sample chapter;
- the Run button;
- the Open in Colab links;
- ratings;
- the security headers, `/api/v1/health`, `robots.txt` and `sitemap.xml`.
