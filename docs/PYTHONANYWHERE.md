# PythonAnywhere deployment checklist

If **www.dauletov.com** does not match what you see after `git pull`, something below is out of sync.

## 1. One repo folder only

Your **Web** tab **Source code** path must be the **same** folder where you run:

- `git pull`
- `pip install -r requirements.txt`
- `python manage.py collectstatic`
- `python manage.py migrate`

Example (adjust username):

```text
/home/dauletov/REALWEBSITE/Projects_Website
```

If `deploy.sh` used `~/Projects_Website` but you actually work in `~/REALWEBSITE/Projects_Website`, the site would keep serving **old code** from the other copy.  
`deploy.sh` now tries `REALWEBSITE/Projects_Website` first, then falls back to `~/Projects_Website`.

Optional: set explicitly in Bash before running deploy:

```bash
export PA_PROJECT_DIR=/home/dauletov/REALWEBSITE/Projects_Website
bash deploy.sh
```

## 2. Virtualenv

Activate the **same** venv your Web app uses (Web tab → Virtualenv path), then install deps:

```bash
cd /home/dauletov/REALWEBSITE/Projects_Website
source myenv/bin/activate   # or your venv path
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

If you see `ModuleNotFoundError: No module named 'tinymce'`, you are not using the venv that has `django-tinymce4-lite` installed.

## 3. Static files (CSS/JS)

Under **Web** → **Static files**:

| URL   | Directory (example) |
|-------|---------------------|
| `/static/` | `/home/dauletov/REALWEBSITE/Projects_Website/staticfiles/` |

Must match `STATIC_ROOT` in `settings.py` (project’s `staticfiles` folder **after** `collectstatic`).

## 4. Reload

After deploy: **Web** → **Reload** your `www.dauletov.com` app.

## 5. Two themes

- **Default (purple gradient)** is normal; that is the “light” theme.
- Click the **moon** button (bottom-right) for the **terminal / neon** theme.
- Preference is stored in `localStorage` per browser.

## 6. Browser cache

CSS is loaded as `custom.css?v=STATIC_ASSET_VERSION`. If styles look stale, bump `STATIC_ASSET_VERSION` in `settings.py`, deploy again, and reload.
