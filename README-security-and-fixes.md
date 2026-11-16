# Security and fixes — what changed and what you must do

Written in simple English. Nothing here is committed or pushed; you review and push yourself.

This covers the 10 problems from the system test. For each one: what I changed, what you must do on the server, and how to check it on the live site.

**Read this first:** three things need action from you before they work.

| What | Why |
|---|---|
| Paste the nginx file into Plesk | HSTS, CSP and the `/sitemap.xml` rule live there, not in the app |
| Rebuild and restart the backend container | There are backend code changes; the frontend redeploy script is not enough |
| Set the `.co.rw` price and switch it on | I did not touch your prices |

There is **no database migration** in this work. No new table, no new column, nothing to run with `alembic`.

---

## 1. Rate limits on login, sign-up and forms

### What was wrong
Only domain search had a limit. Anyone could try thousands of passwords on `/auth/login`, create endless accounts, or send endless password-reset emails.

### What I changed

`_visitor_key` moved out of `domains.py` into `app/core/rate_limit.py` so every router shares one copy. It is now called `visitor_key` (no underscore) because it is shared code, not private to one file. It still reads the **last** entry of `X-Forwarded-For` first — that is the one nginx adds. Earlier entries can be typed by the visitor, so trusting the first would let anyone pick their own bucket and skip the limit entirely.

The limiter also gained:

- a registry, so `reset_all()` can empty every limiter at once (the tests use this);
- `exceeded()` and `record()`, so the login limit can count **only failed attempts**;
- a check on `RATE_LIMIT_ENABLED`, so limits can be switched off.

Limits now in place, all returning **HTTP 429** with the message *"Too many attempts, try again in a few minutes."*

| Endpoint | Limit | Counted per |
|---|---|---|
| `POST /api/v1/auth/login` | 5 per minute | IP |
| `POST /api/v1/auth/login` | 10 failed attempts per 15 min | email |
| `POST /api/v1/auth/register` | 5 per hour | IP |
| `POST /api/v1/auth/register-team-member` | 5 per hour | IP |
| `POST /api/v1/auth/forgot-password` | 3 per 15 min | IP **and** email |
| `POST /api/v1/auth/reset-password` | 10 per 15 min | IP |
| `POST /api/v1/auth/refresh` | 30 per minute | IP |
| `POST /api/v1/quote-requests` | 5 per hour | IP |
| `POST /api/v1/client/domains/order` | 10 per hour | user |
| `GET /api/v1/domains/search` | 20 per minute | IP (unchanged) |

Three decisions worth knowing about:

1. **The per-email login limit counts failures only.** If you keep signing in correctly you are never locked out of your own account. Only wrong passwords count.
2. **The two sign-up forms have separate counters.** Filling the team-member form does not use up a visitor's client sign-ups.
3. **`forgot-password` gives the same answer either way.** A real address and an unknown one return the same 200 body, and the same 429 when limited. So the limit cannot be used to find out which emails have accounts. There is a test for exactly this.

Every limit is an environment variable, so you can relax one on the server without a redeploy:

```
RATE_LIMIT_ENABLED=true
RATE_LIMIT_LOGIN_PER_MINUTE=5
RATE_LIMIT_LOGIN_FAILURES_PER_EMAIL=10
RATE_LIMIT_LOGIN_FAILURE_WINDOW_MINUTES=15
RATE_LIMIT_REGISTER_PER_HOUR=5
RATE_LIMIT_REFRESH_PER_MINUTE=30
RATE_LIMIT_FORGOT_PASSWORD_PER_WINDOW=3
RATE_LIMIT_FORGOT_PASSWORD_WINDOW_MINUTES=15
RATE_LIMIT_RESET_PASSWORD_PER_WINDOW=10
RATE_LIMIT_RESET_PASSWORD_WINDOW_MINUTES=15
RATE_LIMIT_QUOTE_PER_HOUR=5
RATE_LIMIT_DOMAIN_SEARCH_PER_MINUTE=20
RATE_LIMIT_DOMAIN_ORDER_PER_HOUR=10
```

**You do not have to set any of these.** The defaults above are already the defaults in the code. Add them to `.env` only if you want different numbers.

### Two honest limitations

- **The count is per process.** If you ever run several uvicorn workers, each keeps its own count, so the real limit is roughly `limit × workers`. For stopping password guessing and form spam that is fine. A shared count would need Redis, which this server does not run.
- **The count is lost on restart.** Restarting the container empties the counters.

### The frontend

No frontend change was needed, and I want to be clear about why rather than invent one. `normalizeError` in `src/lib/apiClient.ts` already copies the server's `detail` text into `error.message`, and all five screens already display `error.message`:

- Login — `src/pages/auth/Login.tsx`
- Register — `src/pages/auth/Register.tsx`
- Forgot password — `src/pages/auth/ForgotPassword.tsx`
- Request a Quote — `src/pages/public/RequestQuote.tsx`
- Domain order — `src/components/domains/DomainSearch.tsx` (which already has its own friendly wording for a 429 on search)

So the 429 message appears in the normal red box on all of them.

### How to check it live
Try to log in with a wrong password six times quickly. The sixth attempt should show *"Too many attempts, try again in a few minutes."* instead of *"Incorrect email or password"*. Wait a minute and it works again.

---

## 2. Security headers

### Backend (done, no action needed)
`app/main.py` now has a small middleware that sets these on **every** API response, including errors:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

HSTS and CSP are deliberately **not** here. Both belong on the edge that serves the HTML, and a CSP on a JSON response protects nothing.

### Static site — this needs you

I wrote **`deploy/nginx-security-headers.conf`**. Open it and paste the whole thing here:

> **Plesk → Domains → wamugii.kento.rw → Apache & nginx Settings → "Additional nginx directives"** → paste → **OK**

It sets HSTS, the four headers above, the `/robots.txt` and `/sitemap.xml` rules, and a Content-Security-Policy.

**Note:** the file assumes the backend is reachable at `http://127.0.0.1:8000`. If your port is different, change the `proxy_pass` line in the `/sitemap.xml` block.

#### About the CSP

I built the policy by reading the code, not by guessing. It allows exactly:

| What | Allowed from | Because |
|---|---|---|
| Scripts | `'self'` | Vite builds one external script file. The built `index.html` has **no inline script**, so no `'unsafe-inline'` is needed — which is the part that actually stops injected script. |
| Styles | `'self'`, `'unsafe-inline'`, `fonts.googleapis.com` | See the warning below |
| Fonts | `'self'`, `fonts.gstatic.com` | Google Fonts serves the Inter files |
| Images | `'self'`, `data:`, `blob:`, `https:` | Course covers and logos are URLs typed into admin, so they can point anywhere; YouTube thumbnails come from `i.ytimg.com` |
| Frames | `youtube-nocookie.com`, `player.vimeo.com` | Lesson videos. `src/utils/videoEmbed.ts` only ever builds these two and rejects anything else |
| API calls | `'self'` | The browser calls the API on the same domain |

**One weak spot, stated plainly:** `style-src` has to include `'unsafe-inline'`. Many components set inline `style=""` attributes (React `style={{...}}`), and a CSP cannot allow those selectively. Removing it would mean rewriting every inline style as a CSS class — a big job across many files. Script injection is still blocked, which is the main thing a CSP is for.

**Also:** if you ever move the API to a different hostname, you must add it to `connect-src` or every request will be blocked.

#### Switching the CSP on (do this a week later)

The file ships the policy as **`Content-Security-Policy-Report-Only`**. That means the browser *reports* violations but blocks nothing, so the site cannot break.

1. Paste the file, Apply, confirm the site still works.
2. Leave it for about a week. Browse the site: home, services, a course with a video, the admin screens.
3. Open the browser console (F12). Look for lines mentioning `Content-Security-Policy`.
4. If there are none, open the file, **comment out the `Report-Only` line** and **uncomment the enforcing line** below it. The policy text is identical; only the header name changes.
5. If there are reports, send them to me and I will widen the policy.

#### Hiding `X-Powered-By: PleskLin`

The nginx file already has `proxy_hide_header X-Powered-By;`. If the header still shows up afterwards, PHP is adding it, not the proxy:

> **Plesk → Domains → wamugii.kento.rw → PHP Settings** → set `expose_php` to **off** → Apply

### How to check it live
```
curl -sI https://wamugii.kento.rw | grep -iE "strict-transport|x-frame|x-content-type|referrer|permissions|content-security|x-powered-by"
```
You should see the headers listed, and **no** `x-powered-by` line.

For the API:
```
curl -sI https://wamugii.kento.rw/api/v1/health | grep -iE "x-frame|x-content-type"
```

---

## 3. Frontend package warnings

`npm audit` reported 7 high-severity problems. I ran `npm audit fix` (**not** `--force`).

**It needed `--legacy-peer-deps`.** There is a pre-existing conflict in the project, unrelated to any of this: `typescript ~6.0.2` is installed but `openapi-typescript@7.13.0` asks for `typescript ^5.x`. Any `npm install` or `npm audit fix` fails without that flag. `--legacy-peer-deps` is not `--force` — it only tells npm to ignore that peer disagreement, which is how this project was already installed.

```
cd wamugii-frontend
npm audit fix --legacy-peer-deps
```

Result: **0 vulnerabilities**, and **no major upgrades were needed**.

| Package | Before | After |
|---|---|---|
| zod | 4.5.4 | 4.6.7 |
| vite | 8.2.2 | 8.3.7 |
| follow-redirects | 1.16.0 | 1.16.3 |
| js-yaml | 4.3.1 | 4.3.2 |
| brace-expansion | 2.1.4 | 2.1.7 |
| source-map-js | 1.2.1 | 1.2.2 |

Only `package-lock.json` changed — `package.json` did not, because every fix fitted inside the version ranges you already had.

I checked the zod forms still work. The project has no `src/schemas` folder; the schemas are written inline in the page components, and they use only `z.string()`, `z.object()`, `z.enum()`, `.min()`, `.max()`, `.email()` and `.optional()`. I ran the real login schema and an enum/optional schema against zod 4.6.7: valid input passes, invalid input fails with the same custom messages. `.email()` still works.

**One thing you should fix separately:** that `typescript` / `openapi-typescript` conflict will keep biting you on every install. The clean fix is to remove `openapi-typescript` from `devDependencies` and change the `gen:api` script to `npx openapi-typescript@7 ...`, since it is only used occasionally to regenerate types. I did not do it because it is outside this task. Say the word.

### How to check it live
This is a build-time change only. Nothing to check on the server beyond the site working after the next frontend deploy.

---

## 4. Health check endpoint

### What I changed
New file `app/api/v1/health.py`, registered first in the router so nothing can shadow it.

`GET /api/v1/health` — public, no login:

```json
{"status": "ok", "database": "ok", "version": "1.0.0"}
```

It runs `SELECT 1` against the database. If that fails it returns **HTTP 503** with `"database": "error"`. The body deliberately contains nothing else — no driver name, no host, no error text. The real reason goes to the log. There is a test asserting a database URL with a password in it never appears in the response.

`APP_VERSION` is a new setting, default `"1.0.0"`. Set `APP_VERSION` in `.env` if you want it to show a release tag.

The old `GET /health` (no `/api/v1`) still exists and is unchanged.

### Docker HEALTHCHECK
Add this to `wamugii-backend/Dockerfile`, near the end:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=4).status==200 else 1)"
```

`--start-period=40s` gives the container time to run migrations and seeding before failures count.

I did **not** add this to the Dockerfile myself, because it changes how your container is judged healthy and that can affect `docker compose` behaviour on the live server. Add it when you are ready.

### Free uptime monitor (UptimeRobot)
1. Sign up at uptimerobot.com (the free plan allows 50 monitors at 5-minute checks).
2. **+ Add New Monitor**
3. Monitor Type: **HTTP(s)**
4. Friendly Name: `WAMUGII API`
5. URL: `https://wamugii.kento.rw/api/v1/health`
6. Monitoring Interval: **5 minutes**
7. Under **Advanced**, set *Keyword* monitoring instead if you want it stricter: Monitor Type **Keyword**, Keyword Type **exists**, Keyword `"database":"ok"`. That catches the case where the API answers but the database is down — a plain HTTP check would still pass on a 200.
8. Add your email under **Alert Contacts To Notify**.

Add a second monitor for `https://wamugii.kento.rw/` so you also learn if the website itself is down.

### How to check it live
```
curl -s https://wamugii.kento.rw/api/v1/health
```
Expect `{"status":"ok","database":"ok","version":"1.0.0"}`.

---

## 5. Domain search: `.io` and `.co` always said "unknown"

### What was wrong
Availability came only from RDAP, and `.io` and `.co` are not in the IANA bootstrap file, so they always fell through to "unknown — no public lookup service".

### What I changed
`app/services/domain_lookup.py` now falls back to **WHOIS** (plain text over TCP port 43) when, and only when, there is no RDAP server for an extension. RDAP is still used wherever it exists, because it is structured and reliable.

Servers live in one dictionary so you can add more:

```python
WHOIS_SERVERS = {
    "io": "whois.nic.io",
    "co": "whois.registry.co",
}
```

It uses asyncio streams with a 5-second timeout, and shares the existing cache (5 minutes, 30 seconds for "unknown") and the same 8-at-a-time parallel limit as RDAP.

**How it decides**, deliberately cautious:

- **taken** — the reply contains a `Domain Name:` record. It also reads the expiry date and registrar when present.
- **available** — there is **no** record *and* the reply clearly says not found (`NOT FOUND`, `No Data Found`, `No match for`, `Domain not found`, `No entries found`, and similar).
- **unknown** — anything else, including a timeout or a blocked port.

The order matters and is the thing most likely to go wrong elsewhere: several registries attach *"no match for any other query is implied"* to **every** reply, including replies about registered names. Reading that as "available" would advertise a taken domain as free. So a record present always wins. There is a test for exactly this case.

A failed or blocked lookup is always **unknown**, never **available**.

### Check port 43 works from the droplet
Outbound port 43 is often blocked on hardened hosts. Run:

```
docker exec wamugii-backend python -m app.domain_check kigalishop.io google.io kigalishop.co google.co
```

- `google.io` and `google.co` should come back **taken**.
- `kigalishop.io` / `kigalishop.co` should be **available** (or taken, if someone has them).
- If **all four** say *unknown*, outbound port 43 is blocked. Open it:
  ```
  ufw allow out 43/tcp
  ```
  and check your DigitalOcean cloud firewall allows outbound TCP 43 too.

### How to check it live
Go to https://wamugii.kento.rw/domains, search `kigalishop`, and look at the `.io` and `.co` rows — they should now say available or taken, not "unknown". (They only appear if `.io`/`.co` are in your price list and active.)

---

## 6. `.co.rw` was advertised but switched off

### What was wrong
The Domains page said *"Search .rw, .co.rw, .com and more"* with `.co.rw` hard-coded, while `.co.rw` was an inactive placeholder row (added by migration `b7d2e4f6a8c1`). So the page advertised something nobody could buy.

### What I changed
`src/pages/public/Domains.tsx` now **builds that sentence from the live price list**. The page already fetched `GET /api/v1/domains/extensions`, which returns only **active** rows, so I used that. It names the first three active extensions and adds "and more" if there are more. While the list is loading it shows a sentence with no extension names at all.

The page can no longer advertise an extension that is switched off. **I did not turn `.co.rw` on** — your prices are yours.

### What you must do
> **Admin → Domains → Price list** → find `.co.rw` → set your cost price and margin → switch it **active**.

For comparison, Irembo's prices: **.co.rw 9,000 RWF**, **.rw 15,000 RWF**.

### How to check it live
Set `.co.rw` active, reload https://wamugii.kento.rw/domains, and the hero sentence should now mention `.co.rw`. Switch it off again and the mention disappears by itself.

---

## 7. SEO: same title everywhere, no robots.txt, no sitemap.xml

### Page titles
New hook **`src/hooks/useDocumentTitle.ts`**. It sets `document.title` and the meta description, and it is **completely standalone** — it does not touch `PageTitleProvider`. That matters: the existing `usePageTitle` throws an error outside that provider, which is why `FindDomain` had to stop using it. The new hook talks to the document directly and works anywhere.

Titles come out as **"Page name | WAMUGII TECH SOLUTIONS"**. Applied to:

| Page | Title |
|---|---|
| Home | *WAMUGII TECH SOLUTIONS* (site name alone) |
| Services | Services |
| Hosting | Hosting |
| Domains | Domains |
| Courses | Courses |
| Each course | the course's own title, with its description as the meta description |
| Request a Quote | Request a Quote |
| Login | Log in |
| Register | Create your account |
| 404 | Page not found |

Each page also sets its own meta description. Descriptions are trimmed to 160 characters, because search engines cut them there anyway.

### robots.txt
New file **`wamugii-frontend/public/robots.txt`**. Allows the public pages; disallows `/admin`, `/staff`, `/client`, `/team`, `/instructor`, `/login`, `/register`, `/reset-password`, `/forgot-password`, `/pending-approval` and `/join`; and points at the sitemap.

Because it is a real file in `public/`, Vite copies it into the built site and nginx serves it directly — it no longer falls through to the SPA's `index.html`. The nginx file also sets its content type to `text/plain` explicitly.

### sitemap.xml
New endpoint **`GET /api/v1/sitemap.xml`** (`app/api/v1/sitemap.py`), built from the database so it is never stale. It lists the home page, services, hosting, domains, courses and request-quote, plus `/courses/<slug>` for **every published course**. Drafts and deleted courses are left out, because they have no public page and would send crawlers to a 404.

It is served as `application/xml`, which crawlers require.

The nginx file maps `https://wamugii.kento.rw/sitemap.xml` onto that endpoint, so the public URL is the normal one.

The site URL comes from your `FRONTEND_URL` setting and falls back to `https://wamugii.kento.rw`.

### How to check it live
```
curl -s https://wamugii.kento.rw/robots.txt
curl -sI https://wamugii.kento.rw/sitemap.xml | grep -i content-type   # application/xml
curl -s https://wamugii.kento.rw/sitemap.xml | head -20
```
Then open a few pages in a browser and watch the tab title change. Finally, submit `https://wamugii.kento.rw/sitemap.xml` in Google Search Console.

---

## 8. Database backups

### What I added
Two scripts, both new.

**`scripts/backup-db.sh`** — runs `pg_dump`, gzips it with the date in the name into `/opt/wamugii/backups`, keeps 14 days, and **exits non-zero on any failure** so cron emails you.

It is careful in three ways that matter:

1. It writes to a `.part` file and renames it only on success, so a half-written dump can never be mistaken for a good backup.
2. It refuses a dump smaller than 1000 bytes — that catches the case where `pg_dump` prints an error and still exits 0.
3. It runs `gzip -t` to prove the archive is complete before keeping it.

It finds the database two ways: `docker exec` into the Postgres container (the default, matching `docker-compose.yml`), or straight `pg_dump` against `DATABASE_URL` if you set that.

**`scripts/restore-db.sh`** — restores a backup. It prints what it is about to do, then makes you **type the word `restore`**. There is no `--yes` flag on purpose.

### Install on the droplet
```
# as root
mkdir -p /opt/wamugii/backups
install -m 755 scripts/backup-db.sh    /opt/wamugii/backup-db.sh
install -m 755 scripts/restore-db.sh   /opt/wamugii/restore-db.sh
```

Check the container name first — the script defaults to `wamugii-db`:
```
docker ps --format '{{.Names}}'
```
If your Postgres container is called something else, either pass it in or edit the default:
```
DB_CONTAINER=my-db-name /opt/wamugii/backup-db.sh
```

Run it once by hand before trusting it:
```
/opt/wamugii/backup-db.sh
ls -lh /opt/wamugii/backups
```

### Daily cron
```
crontab -e
```
Add this (02:30 every night, with a log):
```
30 2 * * * /opt/wamugii/backup-db.sh >> /var/log/wamugii-backup.log 2>&1
```
Make sure cron can email you, or add a failure alert — a backup you never check is not a backup.

### Copy backups off the droplet — important
**A backup on the same server is not a backup.** If the droplet dies, so do the backups. Pick one:

**DigitalOcean Spaces, with rclone** (recommended)
```
apt install rclone
rclone config          # choose "s3", provider "DigitalOcean", paste your Spaces key and secret
```
Then add a second cron line, 30 minutes after the backup:
```
0 3 * * * rclone sync /opt/wamugii/backups spaces:wamugii-backups >> /var/log/wamugii-offsite.log 2>&1
```

**Or scp to another machine**
```
0 3 * * * scp -q /opt/wamugii/backups/$(date +%Y-%m-%d)*.sql.gz user@other-host:/backups/wamugii/
```
(Needs an SSH key with no passphrase for the cron user.)

### Test a restore — do this once, now, not during an emergency
Never test a restore on production. Restore into a throwaway database:
```
docker exec -it wamugii-db psql -U wamugii -c "CREATE DATABASE restore_test;"
gunzip -c /opt/wamugii/backups/wamugii-2026-11-10_023000.sql.gz \
  | docker exec -i wamugii-db psql -U wamugii -d restore_test
docker exec -it wamugii-db psql -U wamugii -d restore_test -c "SELECT count(*) FROM users;"
docker exec -it wamugii-db psql -U wamugii -c "DROP DATABASE restore_test;"
```
If the user count looks right, your backups work.

---

## 9. Small lint warnings

All three fixed.

**`src/pages/admin/Users.tsx`** — removed the `useEffect` that called `setPage(0)`. The page number is now reset in the two places the change actually happens: the search box's `onChange` and the role dropdown's `onChange`. No effect, and no render that shows new filters with a stale page number.

**`src/components/hosting/CreateHostingAccountModal.tsx`** and **`src/components/support/StaffCreateTicketModal.tsx`** — swapped `watch('field')` for `useWatch({ control, name: 'field' })`, taking `control` from `useForm` instead of `watch`. Behaviour is the same; `useWatch` is the subscription-based API that does not upset the React Compiler.

### How to check
```
cd wamugii-frontend && npm run lint
```
Those three warnings are gone. Other warnings remain in other files — they were there before and are outside this task.

---

## 10. Hosting plan text — for you to decide

I only looked; **I changed nothing**.

The features come from **seed data**, in migration `0f8a5b695eeb_create_hosting_plans_and_hosting_.py`, in a list called `SEED_PLANS`. It is seeded **on first run only** — so on your live site these are now ordinary rows in the database. **Editing the migration would not change the live site.** Change them in **Admin → Hosting → Plans**.

Here is what the four plans currently say:

| Plan | Price / month | Features |
|---|---|---|
| Starter | 10,000 | 1 website, SSL, **25GB SSD**, 1TB bandwidth |
| Business | 20,000 | 3 websites, SSL, **50GB SSD**, 2TB bandwidth, email support |
| Professional | 30,000 | 5 websites, SSL, **60GB SSD**, **3TB** bandwidth, priority support |
| Enterprise | 50,000 | Unlimited websites, **NVMe 70GB**, **2TB** bandwidth, dedicated support |

Three things look wrong to me:

1. **Bandwidth goes down as the price goes up.** Professional gives **3TB**; Enterprise, at 67% more money, gives **2TB**. This is the one I would fix first — a customer comparing the two will notice.
2. **Storage wording is inconsistent**, which is what you spotted. Three plans say "`NN`GB SSD"; Enterprise says "NVMe `NN`GB" — different word order and a different storage type. Also, 70GB is only 10GB more than Professional's 60GB, which looks small for the top plan.
3. **Enterprise does not mention SSL**, while all three others do. Probably implied, but it reads as if it is missing.

Decide the real numbers and I will update them, or edit them yourself in Admin → Hosting → Plans.

---

## Test results

Both suites were run in full, at the end, after every change.

**Backend — 571 passed, 0 failed** (5m 18s)
```
cd wamugii-backend && python -m pytest -q
```
That is the 533 tests you already had, plus **38 new ones**:

| File | Tests | Covers |
|---|---:|---|
| `tests/test_rate_limit.py` | 14 | every limit; a different IP is not blocked; `X-Forwarded-For` spoofing does not escape the limit; a correct password never counts against the per-email limit; the two sign-up forms have separate counters; forgot-password reveals nothing at 200 **or** 429 |
| `tests/test_domain_whois.py` | 13 | every wording of "not found"; a record wins over not-found boilerplate; an unreadable reply stays unknown; a blocked port is unknown, not available; a timeout does not hang; end-to-end through the search endpoint with a fake local WHOIS server |
| `tests/test_sitemap.py` | 6 | valid XML, public pages present, published courses listed, drafts and deleted courses excluded, `application/xml` content type |
| `tests/test_health_and_headers.py` | 5 | health 200, 503 when the database is down, no leaked detail in the body, headers on success **and** on 4xx |

Three existing tests needed small edits, all of them expected:

- `tests/test_domain_search.py` — its two rate-limit tests now ask for the `limits_on` fixture, because limits are off by default in tests.
- `tests/test_team_members.py` — `/api/v1/health` and `/api/v1/sitemap.xml` added to the allow-list in the route privacy sweep. That sweep walks every GET in the schema and fails if a team member is served anything outside their own surface, so each new public endpoint has to be allowed on purpose. Both return only public data.

One thing worth knowing about the test setup: **rate limiting is off by default in the test suite** (`tests/conftest.py`), and every limiter is emptied between tests. Without that the suite would trip its own limits — `TestClient` always presents the same address, so the many tests that register users or sign in would start getting 429s from each other. The tests that are *about* the limits ask for the `limits_on` fixture to switch them back on.

**Frontend — all three clean**
```
cd wamugii-frontend && npx tsc -b && npm run lint && npm run build
```
- `tsc -b` — no errors
- `npm run lint` — **0 errors**. Warnings remain in other files; they were there before and are outside this task. The three from Problem 9 are gone.
- `npm run build` — succeeds
- `npm audit` — **0 vulnerabilities** (was 7 high)

---

## Every file I changed

### Backend — changed
| File | Why |
|---|---|
| `app/core/rate_limit.py` | shared `visitor_key`, limiter registry, `reset_all()`, `exceeded()`/`record()`, `enforce()` |
| `app/core/config.py` | 13 rate-limit settings, `APP_VERSION` |
| `app/main.py` | security-headers middleware |
| `app/api/v1/router.py` | registered the health and sitemap routers |
| `app/api/v1/auth.py` | limits on login, register, register-team-member, refresh, forgot-password, reset-password |
| `app/api/v1/domains.py` | uses the shared `visitor_key`; search limit reads from settings |
| `app/api/v1/quote_requests.py` | limit on the public quote form |
| `app/api/v1/client.py` | limit on the domain order endpoint |
| `app/services/domain_lookup.py` | WHOIS fallback for `.io` and `.co` |

### Backend — new
| File | Why |
|---|---|
| `app/api/v1/health.py` | `GET /api/v1/health` |
| `app/api/v1/sitemap.py` | `GET /api/v1/sitemap.xml` |

### Backend — tests
| File | Why |
|---|---|
| `tests/conftest.py` | rate limits off by default, limiters reset per test, shared `limits_on` fixture |
| `tests/test_rate_limit.py` | **new** — every limit, plus the spoofing and enumeration cases |
| `tests/test_health_and_headers.py` | **new** — health 200/503, no leaked detail, headers on success and on errors |
| `tests/test_domain_whois.py` | **new** — WHOIS parsing and a fake local WHOIS server |
| `tests/test_sitemap.py` | **new** — sitemap contents, drafts excluded, content type |
| `tests/test_domain_search.py` | the two existing rate-limit tests now ask for `limits_on` |
| `tests/test_team_members.py` | allow-listed `/api/v1/health` in the route privacy sweep |

### Frontend — changed
| File | Why |
|---|---|
| `package-lock.json` | `npm audit fix` |
| `src/pages/public/Domains.tsx` | hero text built from active extensions; page title |
| `src/pages/public/Home.tsx`, `Services.tsx`, `Hosting.tsx`, `Courses.tsx`, `CourseDetail.tsx`, `RequestQuote.tsx` | page titles and meta descriptions |
| `src/pages/auth/Login.tsx`, `Register.tsx` | page titles |
| `src/pages/NotFound.tsx` | page title |
| `src/pages/admin/Users.tsx` | removed the setState-in-effect |
| `src/components/hosting/CreateHostingAccountModal.tsx` | `useWatch` instead of `watch()` |
| `src/components/support/StaffCreateTicketModal.tsx` | `useWatch` instead of `watch()` |

### Frontend — new
| File | Why |
|---|---|
| `src/hooks/useDocumentTitle.ts` | page titles and meta descriptions, independent of `PageTitleProvider` |
| `public/robots.txt` | crawler rules and the sitemap pointer |

### Repo root — new
| File | Why |
|---|---|
| `deploy/nginx-security-headers.conf` | paste into Plesk |
| `scripts/backup-db.sh` | nightly backup |
| `scripts/restore-db.sh` | restore, with confirmation |
| `README-security-and-fixes.md` | this file |

---

## Server steps, in order

1. **Push and pull.** You push; then on the droplet pull the new code.

2. **Rebuild and restart the backend.** There are backend code changes, so the frontend-only redeploy script is not enough:
   ```
   cd /path/to/wamugii-backend
   docker compose build api
   docker compose up -d api
   docker compose logs --tail=50 api
   ```
   No migration is needed. Confirm with:
   ```
   curl -s http://127.0.0.1:8000/api/v1/health
   ```

3. **Deploy the frontend** with your usual script, so `robots.txt` and the new page titles go live.

4. **Paste `deploy/nginx-security-headers.conf` into Plesk** (Domains → wamugii.kento.rw → Apache & nginx Settings → Additional nginx directives) → OK. Then check the site still loads, and:
   ```
   curl -sI https://wamugii.kento.rw | grep -i "strict-transport\|x-frame\|content-security"
   curl -sI https://wamugii.kento.rw/sitemap.xml | grep -i content-type
   ```

5. **Turn off `expose_php`** if `X-Powered-By` is still showing (Plesk → PHP Settings).

6. **Check outbound port 43:**
   ```
   docker exec wamugii-backend python -m app.domain_check kigalishop.io google.io kigalishop.co google.co
   ```
   Open it with `ufw allow out 43/tcp` if all four come back unknown.

7. **Install the backup scripts and the cron line**, then run a backup by hand and test a restore into a throwaway database (section 8).

8. **Set up off-site copies** of the backups (section 8). Do not skip this.

9. **Add the UptimeRobot monitors** (section 4).

10. **Set the `.co.rw` price and switch it on** in Admin → Domains → Price list.

11. **Decide the hosting plan wording** (section 10), especially the bandwidth going down from Professional to Enterprise.

12. **In about a week**, switch the CSP from Report-Only to enforcing (section 2).

---

## Things I deliberately did not do

- **No database migration, no new table, no new column.** Not needed for any of this.
- **I did not change any price or plan feature.** Section 10 lists what I found for you to decide.
- **I did not turn `.co.rw` on.** The page just stops advertising it until you do.
- **I did not add the Docker `HEALTHCHECK`** to the Dockerfile, because it changes how your container is judged healthy on the live server. The line to add is in section 4.
- **I did not fix the `typescript` / `openapi-typescript` peer conflict**, which is outside this task. It will keep requiring `--legacy-peer-deps` on every install until it is dealt with (section 3).
- **No secrets anywhere.** Every new setting reads from the environment through `app/core/config.py`, and the health endpoint is tested to prove it never echoes a database URL.
