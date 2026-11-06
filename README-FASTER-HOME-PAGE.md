# Faster home page + protection against the blank page

## What was slow (measured on the live site from Kigali)

- The whole website (every admin, client, exam and course page) was one 1.08 MB JavaScript file.
  A visitor had to download and run all of it before seeing anything: a white screen for 2–3 seconds.
- Asset files have no cache header, so on every visit the browser asks the server again
  ("304 Not Modified"); each question costs about 0.3 s from Rwanda.
- The course list API loaded the full notes of every lesson just to count them.
- The Google font blocked the first paint.

## What this update changes

| Change | Effect |
|---|---|
| Each page loads only when it is opened (code splitting) | First download: 277 KB → 125 KB (compressed) |
| Home sections below the first screen load in a second step | The top of the home page shows sooner |
| An instant loading screen (logo + bar) is part of the HTML | No more white screen while the code loads |
| Home data requests start immediately | Services and courses appear sooner |
| The font no longer blocks the first paint | Text shows at once in a system font, then switches to Inter |
| Course list counts lessons with one small database query | The courses API stays fast as courses grow |
| If a page's code file is missing after a deploy, the page reloads once | No blank page for visitors who had the old version open |
| `VITE_API_BASE_URL` missing → the site uses its own address | The "/undefined/api" blank page cannot happen again |
| `.gitignore` ignores every `.env.*` file | Server settings files can never be committed again |

Measured on a slow phone (4× slower CPU, 1.6 Mbps, 150 ms delay):
- something visible: **2.8–3.4 s → 0.7 s** (the new loading screen)
- real content (top bar): **~2.8 s → ~1.7 s**
- main hero image visible: **~3.7 s → ~2.5 s**

## Deploy

On your computer, in the repo root:

```bash
unzip -o wamugii-faster-home-page.zip
git add -A
git commit -m "perf: faster home page (code splitting, loading screen, early data), safer API URL"
git push
```

On the server (backend changed a little, so rebuild it; no database change):

```bash
cd /opt/wamugii && git pull
cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v7 .
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v7 uvicorn app.main:app --host 127.0.0.1 --port 8001
/opt/redeploy-wamugii.sh
```

## Recommended: let browsers keep the code files (Plesk, 2 minutes)

Asset file names change on every deploy (for example `index-DovR_v0x.js`), so browsers can keep
them for a year safely. In Plesk:

1. **Websites & Domains → wamugii.kento.rw → Apache & nginx Settings** (or "Hosting & DNS → Apache & nginx").
2. In **Additional nginx directives**, add:

   ```nginx
   location ^~ /assets/ {
       add_header Cache-Control "public, max-age=31536000, immutable";
       try_files $uri =404;
   }
   ```

3. Click **OK**. Check it from the server:

   ```bash
   curl -sI https://wamugii.kento.rw/ | grep -i "assets\|cache" ; \
   curl -sI "https://wamugii.kento.rw/$(curl -s https://wamugii.kento.rw/ | grep -o 'assets/index-[^"]*\.js' | head -1)" | grep -i cache-control
   ```

   You should see `cache-control: public, max-age=31536000, immutable`.

## Optional: Cloudflare proxy

The site's DNS is on Cloudflare but the proxy (orange cloud) is off. Turning it on for
`wamugii.kento.rw` lets Cloudflare serve the static files from a data centre close to Rwanda.
Before switching, set **SSL/TLS → Full (strict)** in Cloudflare so HTTPS keeps working with the
server's Let's Encrypt certificate. Test the site right after switching; switch back if anything breaks.
