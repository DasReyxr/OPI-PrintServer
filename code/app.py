#!/usr/bin/env python3
"""Servidor web minimo: sube un archivo y lo imprime con CUPS (lp)."""
import os
import subprocess
import uuid
from flask import Flask, request, render_template_string, redirect, url_for, flash
from werkzeug.utils import secure_filename

PRINTER = os.environ.get("PRINTER_NAME", "HP_P2055dn")  # nombre en CUPS (lpstat -p)
UPLOAD_DIR = "/tmp/print-uploads"
ALLOWED = {"pdf", "txt", "png", "jpg", "jpeg"}
MAX_MB = 20

os.makedirs(UPLOAD_DIR, exist_ok=True)
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esto")
app.config["MAX_CONTENT_LENGTH"] = MAX_MB * 1024 * 1024

PAGE = """
<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Imprimir</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:480px;margin:3rem auto;padding:0 1rem}
 form{display:grid;gap:.8rem} button{padding:.7rem;font-size:1rem;cursor:pointer}
 .msg{padding:.6rem;background:#eef;border-radius:6px;margin-bottom:1rem}
</style></head><body>
<h2>Imprimir en HP LaserJet P2055dn</h2>
{% for m in get_flashed_messages() %}<div class="msg">{{ m }}</div>{% endfor %}
<form method="post" action="/print" enctype="multipart/form-data">
  <input type="file" name="file" required>
  <label>Copias <input type="number" name="copies" value="1" min="1" max="20"></label>
  <label><input type="checkbox" name="duplex"> Doble cara (duplex)</label>
  <button type="submit">Imprimir</button>
</form>
<p><a href="/queue">Ver cola de impresion</a></p>
</body></html>
"""


def allowed(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/print")
def do_print():
    f = request.files.get("file")
    if not f or not f.filename or not allowed(f.filename):
        flash("Archivo no valido. Permitidos: " + ", ".join(sorted(ALLOWED)))
        return redirect(url_for("index"))

    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{secure_filename(f.filename)}")
    f.save(path)

    try:
        copies = max(1, min(20, int(request.form.get("copies", 1))))
    except ValueError:
        copies = 1

    cmd = ["lp", "-d", PRINTER, "-n", str(copies)]
    if request.form.get("duplex"):
        cmd += ["-o", "sides=two-sided-long-edge"]
    cmd.append(path)

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        flash("Enviado: " + r.stdout.strip())
    else:
        flash("Error: " + r.stderr.strip())
    return redirect(url_for("index"))


@app.get("/queue")
def queue():
    r = subprocess.run(["lpstat", "-o", PRINTER], capture_output=True, text=True)
    return f"<pre>{r.stdout or 'Cola vacia'}</pre><a href='/'>Volver</a>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
