# Root cause analysis & operations (read this end-to-end)

This doc explains **why** things looked “broken” or inconsistent between Cursor, Safari/Firefox, and **www.dauletov.com**, and **exactly** what must be true for everything to line up.

---

## 1. “Purple gradient” is not automatically “old code”

The site has **two intentional themes**:

| Theme | What you see |
|--------|----------------|
| **Default (gradient)** | Purple hero, white cards, Inter font — this is the **current** default. |
| **Terminal (toggle)** | Dark grid, neon green/cyan, monospace — click **moon** bottom-right, then it becomes **sun** to go back. |

So: **Safari showing purple does not mean you’re on an old deploy.** It means you’re on the **default** theme. Cursor’s embedded browser may have had `localStorage.theme = 'terminal'` from testing, so it opened **already** in terminal mode — that alone can explain “Cursor looks different.”

**Check in any browser:** open dev tools → Application/Storage → Local Storage → `theme`. If it’s `terminal`, the site loads dark. Clear that key to reset.

---

## 2. Why Safari/Firefox looked “behind” Cursor (same `localhost:8000`)

Same URL can still show **different CSS** if one browser **cached** an older `custom.css`.

- **Cursor Simple Browser** often behaves like a fresh profile → fetches new CSS.
- **Safari** is aggressive about caching static URLs.

**Fix already in the repo:**

- `custom.css` is loaded as  
  `{% static 'main/css/custom.css' %}?v={{ STATIC_ASSET_VERSION }}`  
  Bump `STATIC_ASSET_VERSION` in `settings.py` after CSS changes so **every** browser is forced to download a “new” URL.
- When `DEBUG=True`, no-cache meta tags are added in `header.html` to reduce **HTML** caching during dev.

**How to verify:** View Page Source → search for `custom.css` → you should see `?v=5` (or current version). If Safari still looks wrong, hard refresh or clear site data for `localhost`.

---

## 3. Particles “missing” on purple theme (fixed)

Particles were `opacity: 0` on the default theme so they were **invisible** in gradient mode. Cursor tests might have been in terminal mode (higher opacity).  

**Now:** default theme uses a **low** opacity so motion is visible everywhere. Terminal theme stays stronger.

---

## 4. PythonAnywhere: the #1 real deployment bug — **two different folders**

Your console showed:

`~/REALWEBSITE/Projects_Website`

Older `deploy.sh` used:

`~/Projects_Website`

If the **Web** tab “Source code” points to **folder A** but you `git pull` / `collectstatic` in **folder B**, then:

- The live site keeps running **old code** from A.
- You think you deployed because B is up to date.

**Rule:** There must be **exactly one** canonical clone on PA, and **Web → Source code**, **bash `cd`**, and **static files directory** must all refer to **that** path.

`deploy.sh` now prefers `~/REALWEBSITE/Projects_Website` then falls back to `~/Projects_Website`. Override with:

```bash
export PA_PROJECT_DIR=/home/YOURUSER/REALWEBSITE/Projects_Website
bash deploy.sh
```

---

## 5. `ModuleNotFoundError: No module named 'tinymce'`

That error is **not** about your Mac vs PA being “linked.” It means:

- `collectstatic` (or `runserver`) was run with a Python that **does not** have `django-tinymce4-lite` installed (wrong venv, or system `python`).

**Fix:** Always:

```bash
cd /path/to/same/repo/as/web/tab
source myenv/bin/activate   # or whatever venv the Web app uses
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

The Web tab **Virtualenv** path must match that venv.

---

## 6. Static files on PythonAnywhere (must match `STATIC_ROOT`)

`STATIC_ROOT` = `<project>/staticfiles/`

Under **Web → Static files**, mapping must be:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/…/Projects_Website/staticfiles/` |

If this points at another clone’s `staticfiles`, styles will be wrong or stale.

After **every** deploy: **Reload** the web app.

---

## 7. `collectstatic` succeeded but site unchanged

Then one of these is still wrong:

1. Static mapping URL/directory (wrong path).
2. Web app source code path ≠ folder where you ran `collectstatic`.
3. Browser cache (less likely if `?v=` bumped).
4. You reloaded the wrong hostname (e.g. `username.pythonanywhere.com` vs custom domain) — both should use same app if configured that way.

---

## 8. Pip “dependency conflict” lines (numba / arviz / numpy)

Those messages mean **other** packages in that same environment want **different** numpy/typing-extensions versions. They may not break **this** Django app, but they can cause weird failures later.

**Best practice:** use a **dedicated** venv for this project only (what you’re doing with `myenv`), not a shared “kitchen sink” environment.

---

## 9. Security / production note: `DEBUG = True` in repo

With `DEBUG=True`, Django exposes stack traces and behaves differently. For production, set on PythonAnywhere (Web tab → **Environment variables**):

```text
DJANGO_DEBUG=false
```

(`settings.py` should read this — see current `settings.py` for the exact variable name.)

---

## 10. Quick verification checklist

**Local**

- [ ] One `runserver` on port 8000 (`lsof -i :8000`).
- [ ] View source: `custom.css?v=<number>` present.
- [ ] Bottom-right: theme toggle visible.
- [ ] Clear `localStorage` if themes confuse you.

**PythonAnywhere**

- [ ] `pwd` in bash = Web tab source code directory.
- [ ] `git log -1` shows latest commit.
- [ ] `ls staticfiles/main/css/custom.css` exists after `collectstatic`.
- [ ] Web → Static mapping → `staticfiles` path matches that project.
- [ ] Virtualenv matches `which python` after `activate`.
- [ ] **Reload** web app.

---

## Summary table

| Symptom | Most likely cause |
|--------|---------------------|
| Cursor dark, Safari purple | Different `localStorage` theme **or** Safari cached old CSS before `?v=` fix |
| Live site never updates | Deploying **wrong directory** on PA vs Web tab |
| `tinymce` missing | `collectstatic` / run without project venv |
| Styles wrong on live only | Static files mapping → wrong `staticfiles` folder |
| Purple + stats + Stock nav | **Current** homepage; not “old” — terminal is optional |

This is the full picture; if something still fails, run through section 10 line by line and note which step first diverges.
