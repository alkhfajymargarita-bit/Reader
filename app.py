from flask import Flask, render_template, request, redirect, url_for, abort, send_file, Response
import os
import uuid
import fitz  # PyMuPDF
from io import BytesIO
import base64
from markupsafe import Markup

# Basic config
UPLOAD_FOLDER = "uploads"
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_article_html(pdf_bytes, title="Converted PDF"):
    # Convert PDF bytes to clean, Reader-friendly HTML.
    # Focus on text-first extraction; embed images inline as base64 where possible.
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    sections = []

    for page_index, page in enumerate(doc):
        # Extract text
        text = page.get_text("text").strip()

        # Extract images (best-effort; Safari Reader may omit, but we embed anyway)
        images_html = []
        try:
            for img in page.get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n >= 5:  # CMYK or other
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                img_bytes = pix.tobytes("png")
                b64 = base64.b64encode(img_bytes).decode("ascii")
                images_html.append(f'<figure><img src="data:image/png;base64,{b64}" alt="Page {page_index+1} image"></figure>')
                pix = None
        except Exception:
            # If image extraction fails, we still deliver text.
            pass

        # Build a section per page
        safe_text = (text
                     .replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;"))
        # Convert newlines to paragraphs for readability
        paragraphs = [p.strip() for p in safe_text.split("\n") if p.strip()]
        p_html = "".join(f"<p>{p}</p>" for p in paragraphs)
        sec_html = f"<section aria-label='Page {page_index+1}'>{p_html}{''.join(images_html)}</section>"
        sections.append(sec_html)

    article_inner = "\n".join(sections)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="PDF converted to Reader Mode–friendly HTML.">
  <link rel="stylesheet" href="/static/styles.css">
  <!-- Minimal, semantic markup. Safari Reader looks for a main content area, esp. <article>. -->
</head>
<body>
  <main>
    <article>
      <header>
        <h1>{title}</h1>
        <p class="byline">Converted with PDF → Safari Reader</p>
      </header>
      {article_inner}
    </article>
  </main>
</body>
</html>"""
    return html

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    if "pdf" not in request.files:
        abort(400, "No file part named 'pdf' in form")
    file = request.files["pdf"]
    if file.filename == "":
        abort(400, "No selected file")
    if not allowed_file(file.filename):
        abort(400, "Only .pdf files are supported")

    pdf_bytes = file.read()
    safe_title = os.path.splitext(os.path.basename(file.filename))[0]
    html = pdf_to_article_html(pdf_bytes, title=safe_title)

    # Option A: display immediately
    return Response(html, mimetype="text/html")

@app.errorhandler(413)
def too_large(e):
    return "File is too large. Max 50MB.", 413

if __name__ == "__main__":
    # Bind to 0.0.0.0 for platform compatibility; let the host set PORT
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
