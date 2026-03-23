# iPad / Safari still shows “old” design — every cause (checklist)

Use this so you don’t redo work blindly. **Not a frontend “package” problem:** the Kaveen-style stuff is normal **CSS + vanilla JS** in `custom.css` and `header.html` (no React, no new CSS framework, no npm). **Pip packages** matter for **Django running** (`tinymce`, `whitenoise`) and **`collectstatic`**, not for “loading a different design language.”

---

## A. Confirm what the server is actually sending (1 minute)

On a Mac/PC terminal:

```bash
curl -sI "https://www.dauletov.com/" | head -5
curl -s "https://www.dauletov.com/" | grep -E "custom\.css|themeToggle|particle-canvas|STATIC" | head -5
curl -sI "https://www.dauletov.com/static/main/css/custom.css?v=7" | head -8
```

- HTML grep finds **`custom.css?v=`** and **`themeToggle`** → newest templates are deployed.
- CSS URL returns **200** → stylesheet is reachable.
- CSS returns **404** → static delivery is broken (see C–E below).

---

## B. iPad / Safari cache (very common)

Safari (especially iOS) caches aggressively.

1. **Settings → Safari → Clear History and Website Data** (nuclear), **or** long-press refresh if available.
2. Open **Private** tab → `https://www.dauletov.com/`
3. If Private looks new but normal window doesn’t → **cache**.

`?v=7` (or current `STATIC_ASSET_VERSION` in `settings.py`) is there so **one deploy** forces a new CSS URL — but only if the **HTML** is new too (old HTML = old `?v=`).

---

## C. Wrong repo folder on PythonAnywhere (classic)

**Web → Source code** must be the **same** directory where you:

- `git pull`
- `source myenv/bin/activate`
- `pip install -r requirements.txt`
- `python manage.py collectstatic --noinput`

If you deploy in `~/REALWEBSITE/Projects_Website` but the web app points at `~/Projects_Website`, the world sees **old code** forever.

---

## D. `tinymce` / venv (terminal error)

`ModuleNotFoundError: No module named 'tinymce'` means **`python` wasn’t your project venv**.

Always:

```bash
cd <same as Source code>
source myenv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

Then **Reload** the web app.

---

## E. PythonAnywhere **Static files** map vs **WhiteNoise** (why iPad looked “old”)

If **Web → Static files** maps `/static/` to a **folder that is wrong or not updated**, nginx serves **old or partial CSS** → site looks like an **older Materialize-heavy layout** (often reads as **more blue**), while localhost uses **live `main/static/...`** and looks **purple**.

**This repo now includes WhiteNoise** so that **with `DJANGO_DEBUG=false`**, Django can serve **`STATIC_ROOT`** through the WSGI app.

**You must pick one strategy (important):**

### Option 1 — WhiteNoise (recommended after `pip install`)

1. Set **Web → Environment variable:** `DJANGO_DEBUG=false`
2. **`pip install -r requirements.txt`** (installs `whitenoise`)
3. **`collectstatic`** in the correct project dir with venv active
4. **Delete** the **Static files** entry for **`/static/`** in the Web tab (so `/static/` is **not** served by nginx from an old path — it goes through Django + WhiteNoise).
5. **Reload** web app

### Option 2 — Only nginx static map (no WhiteNoise dependency)

1. Keep **`/static/` →** `/home/…/Projects_Website/staticfiles/`
2. That path **must** be the **`staticfiles`** folder next to **`manage.py`** you just ran **`collectstatic`** in
3. **`DJANGO_DEBUG`** can be false or true for this path; nginx doesn’t use WhiteNoise

**Do not** point `/static/` at `main/static/` (source tree). It must be **`staticfiles/`** after `collectstatic`.

---

## F. `DJANGO_DEBUG=false` and WhiteNoise

WhiteNoise middleware is **only inserted when `DEBUG` is False** (i.e. set `DJANGO_DEBUG=false` on PythonAnywhere).  
If you leave **`DJANGO_DEBUG=true`** on PA, you **won’t** get the WhiteNoise path — you rely entirely on the **Static files** map being correct.

---

## G. Custom domain / DNS

Rare, but if `dauletov.com` and `www.dauletov.com` pointed at different hosts, you’d see different sites. Usually both hit the same PA app — confirm in PA **Web** tab which domains are bound.

---

## H. “Kaveen” integration — what it actually is

- **Same stack** as the rest of the site: Django templates + one big **`custom.css`** + **inline `<script>`** in `header.html` (theme toggle + particles).
- **Not** a separate npm/React/tailwind pipeline.
- **No** extra browser “package” to install.

---

## Quick “done right” deploy sequence (copy-paste)

```bash
cd /home/dauletov/REALWEBSITE/Projects_Website   # MUST match Web → Source code
source myenv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

Web tab:

- `DJANGO_DEBUG=false`
- If using WhiteNoise: **remove** `/static/` static mapping → **Reload**
- If **not** using WhiteNoise: `/static/` → …/staticfiles → **Reload**

Then test iPad in **Private** window once.
