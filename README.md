# PDF → Safari Reader Converter

A tiny Flask web app that converts an uploaded **PDF** into a clean, semantic **HTML** page that Safari’s **Reader Mode** can parse.

## Features
- PDF → text-first HTML wrapped in `<article>`/`<section>` (Reader-friendly)
- Best-effort image extraction embedded as base64
- Simple UI and no database
- Works on Render, Railway, or Heroku

## Quick Start (Local)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
# open http://localhost:8000
```

## Deploy to Render (recommended)
1. Push this folder to a GitHub repo.
2. On Render, create a **Web Service** → Connect your repo.
3. Runtime: **Python**. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
5. After deploy, visit the public URL, upload a PDF, and then tap **Reader** in Safari.

## Deploy to Railway
1. New Project → Deploy from GitHub.
2. Add a service, pick your repo.
3. Set start command: `python app.py` (Railway auto-installs from `requirements.txt`).

## Deploy to Heroku
```bash
heroku create
git push heroku main
heroku ps:scale web=1
heroku open
```

## Notes & Limitations
- Extracted content depends on PDF structure; scanned PDFs (images of text) need OCR (not included).
- Reader Mode prefers text-dominant pages; heavy tables/layouts may be simplified.
- Max upload size is 50MB by default (adjust in `app.py`).

## Optional Enhancements
- Add OCR via `pytesseract` for scanned PDFs.
- Persist converted HTML to object storage (S3) and provide shareable links.
- Add a "Download HTML" button that returns the generated file.
```

