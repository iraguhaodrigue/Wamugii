# Domain search + domain dashboard

## What you get

**1. Public "Find a domain" page** – `https://wamugii.kento.rw/domains` (new "Domains" link in the menu)
- A visitor types a name (`kigalishop`, `kigalishop.rw`, even `www.kigalishop.co.rw`).
- The site checks every extension in your price list **live, with the official registry**, and shows:
  **Available** (with your price per year), **Taken** (with "registered until …"), or **Not confirmed**
  (registry did not answer – they can still request it).
- If the name is taken, it suggests similar free names (`getkigalishop.rw`, `kigalishop-rw.rw` …).
- "Get it" → the visitor signs in (or registers) and comes straight back to the order form:
  choose 1–5 years, see the total, click "Request". **Nothing is charged** – you register it and invoice.

**2. Client portal** – "My Domains" now has a **Find a domain** button and a yellow warning when a
domain expires within 30 days.

**3. Domain dashboard for admin and staff** – "Domains" in the sidebar now opens a dashboard:
- Cards: active domains, new requests, renewals due, yearly value.
- **New requests** from the search page, each with a **Mark registered** button (registrar, date,
  years, nameservers). The client automatically gets "your domain is now active".
- **Renewals due** in the next 90 days, overdue ones first, with auto-renew and renewal price.
- **Domains by extension** and **What people search for** (top searched names = sales leads).
- **Price list** (admin only): edit cost and margin, switch extensions on/off for search, add new ones.
- The old list is still there under **All domains**.

## How availability is checked (and why this way)

Every registry runs an official, free lookup service called **RDAP** (the modern replacement for
WHOIS). The registry answers "registered" or "not registered". It is free, needs no account or API
key, and **covers .rw** – RICTA runs it at `rdap.ricta.org.rw`. IANA publishes which server answers
for which extension; the site reads that list once a day.

- Answers are cached for 5 minutes, and each visitor can search 20 times per minute.
- "Available" means "not registered". Rare reserved or premium names can still be refused at
  registration, so the page says you confirm when you register.
- Only the searched name is saved for the dashboard (never IP addresses).

**Later (optional):** to register `.com/.org/...` automatically, connect a registrar API such as
Namecheap (it needs $50 on your account or 20 domains, plus your server IP on their allow list;
it does not sell .rw). `.rw` stays manual through your .rw registrar.

## Also fixed
- The public price-list API showed your **cost price and margin** to everyone – it now shows only
  the client price.
- The price list now accepts `.co.rw`, `.org.rw`, `.ac.rw`. They are added **switched off** with
  placeholder prices – set your real costs and switch them on in the dashboard.

## Deploy (this one HAS a database change)

On your computer, in the repo root:

```bash
unzip -o wamugii-domain-search-dashboard.zip
git add -A
git commit -m "feat: domain search (RDAP), online domain requests and domain dashboard"
git push
```

On the droplet:

```bash
cd /opt/wamugii && git checkout -- wamugii-frontend/package-lock.json && git pull

cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v10 .            # next version number
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v10 uvicorn app.main:app --host 127.0.0.1 --port 8001

docker exec wamugii-backend alembic upgrade head     # REQUIRED: new table + new extensions

# check the server can reach the registries (should print TAKEN / AVAILABLE, not UNKNOWN)
docker exec wamugii-backend python -m app.domain_check ricta.org.rw wamugii-test-123456.rw google.com

/opt/redeploy-wamugii.sh
```

Then:
1. Admin → **Domains** → **Price list**: enter your real registrar cost for each extension, switch on
   `.co.rw` etc. if you sell them.
2. Open `https://wamugii.kento.rw/domains` and search a name.
