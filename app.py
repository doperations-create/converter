from flask import Flask, request, send_file
from PIL import Image
from docx import Document
from PyPDF2 import PdfReader, PdfMerger, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import zipfile
import time

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper for unique filenames
def unique_path(filename):
    name, ext = os.path.splitext(filename)
    return os.path.join(UPLOAD_FOLDER, f"{name}_{int(time.time()*1000)}{ext}")

# 🌈 HOME PAGE
@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>File Converter</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial;
                background: linear-gradient(135deg, #ff7e5f, #feb47b);
                color: white;
                text-align: center;
                padding: 10px;
            }

            h1 {
                font-size: 28px;
                text-shadow: 0 0 10px #fff, 0 0 20px #ff7e5f;
            }

            .box {
                background: white;
                color: black;
                padding: 15px;
                margin: 10px auto;
                width: 90%;
                max-width: 400px;
                border-radius: 15px;
                animation: neonGlow 3s infinite alternate;
            }

            @keyframes neonGlow {
                0% { box-shadow: 0 0 10px #ff7e5f; }
                50% { box-shadow: 0 0 25px #feb47b; }
                100% { box-shadow: 0 0 40px #ff7e5f; }
            }

            button {
                background: #ff7e5f;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 8px;
                width: 100%;
            }

            select, input {
                width: 90%;
                padding: 5px;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>

    <h1>🔥 File Converter Tool</h1>

    <!-- EXISTING BOXES (UNCHANGED) -->

    <div class="box">
        <h3>Convert Image</h3>
        <form action="/convert/image" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <select name="format">
                <option value="png">PNG</option>
                <option value="webp">WEBP</option>
            </select><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>Image → PDF</h3>
        <form action="/convert/image-to-pdf" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>Word → PDF</h3>
        <form action="/convert/word-to-pdf" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>Compress Image</h3>
        <form action="/compress/image" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <select name="level">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
            </select><br>
            <button>Compress</button>
        </form>
    </div>

    <div class="box">
        <h3>Resize Image</h3>
        <form action="/resize/image" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            Width:<input type="number" name="width">
            Height:<input type="number" name="height">
            <button>Resize</button>
        </form>
    </div>

    <div class="box">
        <h3>PDF → Text</h3>
        <form action="/convert/pdf-to-txt" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>Word → Text</h3>
        <form action="/convert/word-to-txt" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>ZIP File</h3>
        <form action="/compress/zip" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <button>Zip</button>
        </form>
    </div>

    <!-- NEW FEATURES -->

    <div class="box">
        <h3>PDF Merger</h3>
        <form action="/merge/pdf" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <button>Merge</button>
        </form>
    </div>

    <div class="box">
        <h3>PDF Splitter</h3>
        <form action="/split/pdf" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <button>Split</button>
        </form>
    </div>

    <div class="box">
        <h3>Images → Single PDF</h3>
        <form action="/convert/images-to-single-pdf" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br>
            <button>Convert</button>
        </form>
    </div>

    </body>
    </html>
    '''

# ---------------- IMAGE CONVERT ----------------
@app.route('/convert/image', methods=['POST'])
def convert_image():
    files = request.files.getlist('file')
    fmt = request.form.get('format', 'png')

    outputs = []

    for file in files:
        path = unique_path(file.filename)
        out = path.rsplit('.', 1)[0] + "." + fmt

        file.save(path)
        Image.open(path).save(out)
        outputs.append(out)

    if len(outputs) == 1:
        return send_file(outputs[0], as_attachment=True, download_name=os.path.basename(outputs[0]))

    zip_path = os.path.join(UPLOAD_FOLDER, f"converted_{int(time.time())}.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in outputs:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True, download_name="converted.zip")

# ---------------- IMAGE TO PDF ----------------
@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf():
    files = request.files.getlist('file')

    outputs = []

    for file in files:
        path = unique_path(file.filename)
        out = path + ".pdf"

        file.save(path)
        Image.open(path).convert('RGB').save(out)
        outputs.append(out)

    if len(outputs) == 1:
        return send_file(outputs[0], as_attachment=True, download_name=os.path.basename(outputs[0]))

    zip_path = os.path.join(UPLOAD_FOLDER, f"images_pdf_{int(time.time())}.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in outputs:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True, download_name="images_pdf.zip")

# ---------------- WORD TO PDF ----------------
@app.route('/convert/word-to-pdf', methods=['POST'])
def word_to_pdf():
    files = request.files.getlist('file')
    outputs = []

    for file in files:
        path = unique_path(file.filename)
        out = path + ".pdf"

        file.save(path)

        doc = Document(path)
        c = canvas.Canvas(out, pagesize=letter)

        y = 750
        for para in doc.paragraphs:
            c.drawString(40, y, para.text)
            y -= 20

        c.save()
        outputs.append(out)

    if len(outputs) == 1:
        return send_file(outputs[0], as_attachment=True, download_name=os.path.basename(outputs[0]))

    zip_path = os.path.join(UPLOAD_FOLDER, f"word_pdf_{int(time.time())}.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in outputs:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True, download_name="word_pdf.zip")

# ---------------- IMAGE COMPRESS ----------------
@app.route('/compress/image', methods=['POST'])
def compress_image():
    files = request.files.getlist('file')
    level = request.form.get('level', 'medium')

    quality = {"low":20,"medium":50,"high":80}[level]
    outputs = []

    for file in files:
        path = unique_path(file.filename)
        out = path+"_compressed.jpg"

        file.save(path)
        Image.open(path).save(out, optimize=True, quality=quality)
        outputs.append(out)

    if len(outputs) == 1:
        return send_file(outputs[0], as_attachment=True, download_name=os.path.basename(outputs[0]))

    zip_path = os.path.join(UPLOAD_FOLDER, f"compressed_{int(time.time())}.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in outputs:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True, download_name="compressed.zip")

# ---------------- RESIZE ----------------
@app.route('/resize/image', methods=['POST'])
def resize_image():
    files = request.files.getlist('file')
    w = int(request.form.get('width',200))
    h = int(request.form.get('height',200))

    outputs = []

    for file in files:
        path = unique_path(file.filename)
        out = path+"_resized.jpg"

        file.save(path)
        Image.open(path).resize((w,h)).save(out)
        outputs.append(out)

    if len(outputs) == 1:
        return send_file(outputs[0], as_attachment=True, download_name=os.path.basename(outputs[0]))

    zip_path = os.path.join(UPLOAD_FOLDER, f"resized_{int(time.time())}.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in outputs:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True, download_name="resized.zip")

# ---------------- PDF TO TXT ----------------
@app.route('/convert/pdf-to-txt', methods=['POST'])
def pdf_to_txt():
    files = request.files.getlist('file')
    outputs = []

    for file in files:
        path = unique_path(file.filename)
        out = path+".txt"

        file.save(path)

        reader = PdfReader(path)
        text = "".join([p.extract_text() or "" for p in reader.pages])

        with open(out, "w", encoding="utf-8") as f:
            f.write(text)

        outputs.append(out)

    if len(outputs) == 1:
        return send_file(outputs[0], as_attachment=True, download_name=os.path.basename(outputs[0]))

    zip_path = os.path.join(UPLOAD_FOLDER, f"pdf_txt_{int(time.time())}.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in outputs:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True, download_name="pdf_txt.zip")

# ---------------- WORD TO TXT ----------------
@app.route('/convert/word-to-txt', methods=['POST'])
def word_to_txt():
    files = request.files.getlist('file')
    outputs = []

    for file in files:
        path = unique_path(file.filename)
        out = path+".txt"

        file.save(path)

        doc = Document(path)
        text = "\n".join([p.text for p in doc.paragraphs])

        with open(out, "w", encoding="utf-8") as f:
            f.write(text)

        outputs.append(out)

    if len(outputs) == 1:
        return send_file(outputs[0], as_attachment=True, download_name=os.path.basename(outputs[0]))

    zip_path = os.path.join(UPLOAD_FOLDER, f"word_txt_{int(time.time())}.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in outputs:
            z.write(f, os.path.basename(f))

    return send_file(zip_path, as_attachment=True, download_name="word_txt.zip")

# ---------------- ZIP ----------------
@app.route('/compress/zip', methods=['POST'])
def zip_file():
    files = request.files.getlist('file')
    zip_path = os.path.join(UPLOAD_FOLDER, f"files_{int(time.time())}.zip")

    with zipfile.ZipFile(zip_path, 'w') as z:
        for file in files:
            path = unique_path(file.filename)
            file.save(path)
            z.write(path, os.path.basename(path))

    return send_file(zip_path, as_attachment=True, download_name="files.zip")

# ---------------- NEW: PDF MERGE ----------------
@app.route('/merge/pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('file')
    merger = PdfMerger()

    for file in files:
        path = unique_path(file.filename)
        file.save(path)
        merger.append(path)

    out = os.path.join(UPLOAD_FOLDER, f"merged_{int(time.time())}.pdf")
    merger.write(out)
    merger.close()

    return send_file(out, as_attachment=True, download_name="merged.pdf")

# ---------------- NEW: PDF SPLIT ----------------
@app.route('/split/pdf', methods=['POST'])
def split_pdf():
    file = request.files['file']
    path = unique_path(file.filename)
    file.save(path)

    reader = PdfReader(path)

    zip_path = os.path.join(UPLOAD_FOLDER, f"split_{int(time.time())}.zip")

    with zipfile.ZipFile(zip_path, 'w') as z:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            out_path = os.path.join(UPLOAD_FOLDER, f"page_{i}.pdf")
            with open(out_path, "wb") as f:
                writer.write(f)

            z.write(out_path, f"page_{i}.pdf")

    return send_file(zip_path, as_attachment=True, download_name="split_pages.zip")

# ---------------- NEW: IMAGES TO SINGLE PDF ----------------
@app.route('/convert/images-to-single-pdf', methods=['POST'])
def images_to_single_pdf():
    files = request.files.getlist('file')

    images = []

    for file in files:
        path = unique_path(file.filename)
        file.save(path)

        img = Image.open(path).convert("RGB")
        images.append(img)

    pdf_path = os.path.join(UPLOAD_FOLDER, f"combined_{int(time.time())}.pdf")

    if images:
        images[0].save(pdf_path, save_all=True, append_images=images[1:])

    return send_file(pdf_path, as_attachment=True, download_name="combined.pdf")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
