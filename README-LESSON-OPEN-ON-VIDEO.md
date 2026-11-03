# Update: lessons open straight on the video + phone fixes

This update changes the **frontend only**. You do not need to rebuild the backend or reload any courses.

## What changed

1. **Lessons open straight on the video.**
   Before, clicking a lesson first showed the top of the page and then slowly scrolled down to the video.
   Now the page opens with the video already on screen. There is no scrolling animation.
   This works for all of these:
   - a lesson link on the course page;
   - a shared lesson link;
   - Login, when it sends the student back to their lesson;
   - a lesson picked from the lesson list;
   - the "Next lesson" and "Previous" buttons.
2. **A smaller course bar at the top of the lesson page.** It holds the back arrow, the course title and the progress bar. The lesson title and video now sit right under it.
3. **Bug fix: two lessons on screen at once.** After picking a new lesson, the old lesson could stay on screen above the new one. This bug was in the last update. It is fixed now.
4. **Phone fixes:**
   - A new **Lessons** button jumps to the lesson list, which is at the bottom of the page on phones.
   - The copy-link button is a small icon on phones.
   - Wide tables in the lesson notes show as one small card per row on phones, so no words are cut off.
   - The lesson notes use more of the screen width on phones.
   - On the public course page, each lesson title gets the full width on phones, with "45 min · video" under it.
5. **Every page now opens at the top.** Before, a new page could open half-way down if you clicked a link at the bottom of the last page. The Back button still returns you to where you were.

## Checked on

- Computer (1280 px wide), iPhone 13 (390 px) and a small Android phone (360 px).
- All 48 lessons (both courses) open with the video on screen.
- No page scrolls sideways on phones.

## Deploy steps

### 1. On your computer (at the repo root)

```bash
unzip -o wamugii-lesson-open-on-video.zip
git add -A
git commit -m "fix: open lessons directly on the video, no double lesson, phone layout"
git push
```

### 2. On the droplet

```bash
cd /opt/wamugii
git checkout -- wamugii-frontend/package-lock.json
git pull
/opt/redeploy-wamugii.sh
```

Then open any lesson link on your phone. It should open with the video on screen.
