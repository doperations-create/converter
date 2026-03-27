from flask import Flask, request, send_file, make_response
from PIL import Image
from docx import Document
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
import os
import zipfile
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 🌈 HOME PAGE
@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>File Converter</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family:Arial;text-align:center;background:linear-gradient(135deg,#ff7e5f,#feb47b);color:white;">

    <h1>🔥 File Converter Tool</h1>

    <form action="/convert/image" method="post" enctype="multipart/form-data">
        <h3>Convert Image</h3>
        <input type="file" name="file"><br>
        <select name="format">
            <option value="png">PNG</option>
            <option value="webp">WEBP</option>
        </select><br>
        <button>Convert</button>
    </form>

    <form action="/convert/image-to-pdf" method="post" enctype="multipart/form-data">
        <h3>Image → PDF</h3>
        <input type="file" name="file"><br>
        <button>Convert</button>
    </form>

    <form action="/convert/word-to-pdf" method="post" enctype="multipart/form-data">
        <h3>Word → PDF</h3>
        <input type="file" name="file"><br>
        <button>Convert</button>
    </form>

    <form action="/compress/image" method="post" enctype="multipart/form-data">
        <h3>Compress Image</h3>
        <input type="file" name="file"><br>
        <select name="level">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
        </select><br>
        <button>Compress</button>
    </form>

    <form action="/resize/image" method="post" enctype="multipart/form-data">
        <h3>Resize Image</h3>
        <input type="file" name="file"><br>
        Width:<input type="number" name="width">
        Height:<input type="number" name="height"><br>
        <button>Resize</button>
    </form>

    <form action="/convert/pdf-to-txt" method="post" enctype="multipart/form-data">
        <h3>PDF → Text</h3>
        <input type="file" name="file"><br>
        <button>Convert</button>
    </form>

    <form action="/convert/word-to-txt" method="post" enctype="multipart/form-data">
        <h3>Word → Text</h3>
        <input type="file" name="file"><br>
        <button>Convert</button>
    </form>

    <form action="/compress/zip" method="post" enctype="multipart/form-data">
        <h3>ZIP File</h3>
        <input type="file" name="file"><br>
        <button>Zip</button>
    </form>

    </body>
    </html>
    '''


# 🔐 SAFE FILE SAVE FUNCTION
def save_file(file):
    filename = secure_filename(file.filename)
    unique_name = str(uuid.uuid4()) + "_" + filename
    path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(path)
    return path


# 📦 SAFE SEND FILE
def safe_send(path):
    response = make_response(send_file(path, as_attachment=True))
    response.headers["Cache-Control"] = "no-cache"
    return response


# ---------------- IMAGE CONVERT ----------------
@app.route('/convert/image', methods=['POST'])
def convert_image():
    file = request.files['file']
    fmt = request.form.get('format', 'png')

    path = save_file(file)
    out = path.rsplit('.', 1)[0] + "." + fmt

    img = Image.open(path)
    img.load()
    img.save(out)

    return safe_send(out)


# ---------------- IMAGE TO PDF ----------------
@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf():
    file = request.files['file']

    path = save_file(file)
    out = path + ".pdf"

    img = Image.open(path)
    img.convert('RGB').save(out)

    return safe_send(out)


# ---------------- WORD TO PDF ----------------
@app.route('/convert/word-to-pdf', methods=['POST'])
def word_to_pdf():
    file = request.files['file']

    path = save_file(file)
    out = path + ".pdf"

    doc = Document(path)
    c = canvas.Canvas(out, pagesize=letter)

    y = 750
    for para in doc.paragraphs:
        c.drawString(40, y, para.text)
        y -= 20

    c.save()

    return safe_send(out)


# ---------------- IMAGE COMPRESS ----------------
@app.route('/compress/image', methods=['POST'])
def compress_image():
    file = request.files['file']
    level = request.form.get('level', 'medium')

    quality = {"low": 20, "medium": 50, "high": 80}[level]

    path = save_file(file)
    out = path + "_compressed.jpg"

    img = Image.open(path)
    img.save(out, optimize=True, quality=quality)

    return safe_send(out)


# ---------------- IMAGE RESIZE ----------------
@app.route('/resize/image', methods=['POST'])
def resize_image():
    file = request.files['file']
    w = int(request.form.get('width', 200))
    h = int(request.form.get('height', 200))

    path = save_file(file)
    out = path + "_resized.jpg"

    img = Image.open(path)
    img.resize((w, h)).save(out)

    return safe_send(out)


# ---------------- PDF TO TXT ----------------
@app.route('/convert/pdf-to-txt', methods=['POST'])
def pdf_to_txt():
    file = request.files['file']

    path = save_file(file)
    out = path + ".txt"

    reader = PdfReader(path)
    text = "".join([p.extract_text() or "" for p in reader.pages])

    with open(out, "w", encoding="utf-8") as f:
        f.write(text)

    return safe_send(out)


# ---------------- WORD TO TXT ----------------
@app.route('/convert/word-to-txt', methods=['POST'])
def word_to_txt():
    file = request.files['file']

    path = save_file(file)
    out = path + ".txt"

    doc = Document(path)

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join([p.text for p in doc.paragraphs]))

    return safe_send(out)


# ---------------- ZIP ----------------
@app.route('/compress/zip', methods=['POST'])
def zip_file():
    file = request.files['file']

    path = save_file(file)
    out = path + ".zip"

    with zipfile.ZipFile(out, 'w') as z:
        z.write(path, os.path.basename(path))

    return safe_send(out)


# 🔥 RUN APP
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
