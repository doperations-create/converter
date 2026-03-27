from flask import Flask, request, send_file
from PIL import Image
from docx import Document
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🌈 BEAUTIFUL HOME PAGE
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
            h1 { font-size: 28px; }
            .box {
                background: white;
                color: black;
                padding: 15px;
                margin: 10px auto;
                width: 90%;
                max-width: 400px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
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

    <div class="box">
        <h3>Convert Image</h3>
        <form action="/convert/image" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
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
            <input type="file" name="file"><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>Word → PDF</h3>
        <form action="/convert/word-to-pdf" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>Compress Image</h3>
        <form action="/compress/image" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
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
            <input type="file" name="file"><br>
            Width:<input type="number" name="width">
            Height:<input type="number" name="height">
            <button>Resize</button>
        </form>
    </div>

    <div class="box">
        <h3>PDF → Text</h3>
        <form action="/convert/pdf-to-txt" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>Word → Text</h3>
        <form action="/convert/word-to-txt" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <button>Convert</button>
        </form>
    </div>

    <div class="box">
        <h3>ZIP File</h3>
        <form action="/compress/zip" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <button>Zip</button>
        </form>
    </div>

    </body>
    </html>
    '''

# ---------------- IMAGE CONVERT ----------------
@app.route('/convert/image', methods=['POST'])
def convert_image():
    file = request.files['file']
    fmt = request.form.get('format', 'png')
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    out = path.split('.')[0] + "." + fmt
    file.save(path)
    Image.open(path).save(out)
    return send_file(out, as_attachment=True)

# ---------------- IMAGE TO PDF ----------------
@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf():
    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    out = path + ".pdf"
    file.save(path)
    Image.open(path).convert('RGB').save(out)
    return send_file(out, as_attachment=True)

# ---------------- WORD TO PDF ----------------
@app.route('/convert/word-to-pdf', methods=['POST'])
def word_to_pdf():
    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    out = path + ".pdf"
    file.save(path)

    doc = Document(path)
    c = canvas.Canvas(out, pagesize=letter)

    y = 750
    for para in doc.paragraphs:
        c.drawString(40, y, para.text)
        y -= 20

    c.save()
    return send_file(out, as_attachment=True)

# ---------------- IMAGE COMPRESS ----------------
@app.route('/compress/image', methods=['POST'])
def compress_image():
    file = request.files['file']
    level = request.form.get('level', 'medium')
    quality = {"low":20,"medium":50,"high":80}[level]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    out = path+"_compressed.jpg"
    file.save(path)
    Image.open(path).save(out, optimize=True, quality=quality)
    return send_file(out, as_attachment=True)

# ---------------- IMAGE RESIZE ----------------
@app.route('/resize/image', methods=['POST'])
def resize_image():
    file = request.files['file']
    w = int(request.form.get('width',200))
    h = int(request.form.get('height',200))
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    out = path+"_resized.jpg"
    file.save(path)
    Image.open(path).resize((w,h)).save(out)
    return send_file(out, as_attachment=True)

# ---------------- PDF TO TXT ----------------
@app.route('/convert/pdf-to-txt', methods=['POST'])
def pdf_to_txt():
    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    out = path+".txt"
    file.save(path)
    reader = PdfReader(path)
    text = "".join([p.extract_text() or "" for p in reader.pages])
    open(out,"w").write(text)
    return send_file(out, as_attachment=True)

# ---------------- WORD TO TXT ----------------
@app.route('/convert/word-to-txt', methods=['POST'])
def word_to_txt():
    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    out = path+".txt"
    file.save(path)
    doc = Document(path)
    open(out,"w").write("\n".join([p.text for p in doc.paragraphs]))
    return send_file(out, as_attachment=True)

# ---------------- ZIP ----------------
@app.route('/compress/zip', methods=['POST'])
def zip_file():
    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    out = path+".zip"
    file.save(path)
    with zipfile.ZipFile(out,'w') as z:
        z.write(path)
    return send_file(out, as_attachment=True)

# 🔥 IMPORTANT: allow network access
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)